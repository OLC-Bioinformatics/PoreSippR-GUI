#!/usr/bin/env python3
"""Run the FoodPort manifest-driven Nanopore scheduler task."""

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


class ManifestError(ValueError):
    """Raised when a finalized FoodPort manifest is invalid."""


class AzureBlobStore:
    """Small Azure Blob boundary used by the task wrapper."""

    def __init__(self, account_name=None, account_key=None,
                 input_sas_url=None, output_sas_url=None):
        try:
            from azure.storage.blob import BlobServiceClient, ContainerClient
        except ImportError:
            raise RuntimeError("azure-storage-blob is required for cloud storage")
        self.input_container = None
        self.output_container = None
        if input_sas_url or output_sas_url:
            if not input_sas_url or not output_sas_url:
                raise ValueError(
                    "input and output SAS URLs must be supplied together"
                )
            self.input_container = ContainerClient.from_container_url(
                input_sas_url
            )
            self.output_container = ContainerClient.from_container_url(
                output_sas_url
            )
            self.client = None
        else:
            if not account_name or not account_key:
                raise ValueError(
                    "storage account and key must be supplied together"
                )
            account_url = "https://{}.blob.core.windows.net".format(account_name)
            self.client = BlobServiceClient(
                account_url=account_url, credential=account_key
            )

    def _blob_client(self, container, blob_name, writing=False):
        container_prefix = "{}/".format(container)
        if blob_name.startswith(container_prefix):
            blob_name = blob_name[len(container_prefix):]
        container_client = (
            self.output_container if writing else self.input_container
        )
        if container_client is not None:
            return container_client.get_blob_client(blob_name)
        return self.client.get_blob_client(container=container, blob=blob_name)

    def download_file(self, container, blob_name, destination):
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name(destination.name + ".partial")
        blob = self._blob_client(container, blob_name)
        with open(partial, "wb") as handle:
            handle.write(blob.download_blob().readall())
        os.replace(partial, destination)

    def upload_file(self, container, blob_name, source):
        source = Path(source)
        blob = self._blob_client(container, blob_name, writing=True)
        with open(source, "rb") as handle:
            blob.upload_blob(handle, overwrite=False)

    def blob_properties(self, container, blob_name):
        blob = self._blob_client(container, blob_name, writing=True)
        return blob.get_blob_properties()

    def upload_immutable_file(self, container, blob_name, source):
        source = Path(source)
        digest = sha256_file(source)
        try:
            blob = self.client.get_blob_client(
                container=container, blob=blob_name
            )
            with open(source, "rb") as handle:
                blob.upload_blob(
                    handle, overwrite=False, metadata={"sha256": digest}
                )
            return True
        except Exception as exc:
            if exc.__class__.__name__ != "ResourceExistsError":
                raise
        properties = self.blob_properties(container, blob_name)
        metadata = getattr(properties, "metadata", {}) or {}
        if metadata.get("sha256") == digest:
            return False
        raise ValueError("immutable cloud output conflict: {}".format(blob_name))


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ManifestError("{} must be a non-empty string".format(field_name))
    normalized = value.replace("\\", "/")
    path = Path(normalized)
    if path.is_absolute() or ".." in path.parts:
        raise ManifestError("{} must be a relative path".format(field_name))
    if normalized.startswith("/") or "//" in normalized:
        raise ManifestError("{} contains an invalid path".format(field_name))
    return Path(*path.parts)


def load_manifest(path):
    with open(path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ManifestError("manifest must be a JSON object")
    if manifest.get("schema_version") != 1:
        raise ManifestError("unsupported manifest schema_version")
    if manifest.get("finalized") is not True:
        raise ManifestError("manifest is not finalized")
    run_id = str(manifest.get("run_id", "")).strip()
    run_name = manifest.get("run_name")
    if not run_id or not isinstance(run_name, str) or not run_name.strip():
        raise ManifestError("manifest requires run_id and run_name")

    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ManifestError("manifest requires at least one file")
    seen = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise ManifestError("manifest file entries must be objects")
        entry_path = relative_path(entry.get("relative_path"), "relative_path")
        if entry_path.suffix.lower() != ".pod5":
            raise ManifestError("manifest contains a non-POD5 file")
        key = entry_path.as_posix()
        if key in seen:
            raise ManifestError("manifest contains duplicate relative_path")
        seen.add(key)
        relative_path(entry.get("blob_name"), "blob_name")
        size_bytes = entry.get("size_bytes")
        if not isinstance(size_bytes, int) or size_bytes < 0:
            raise ManifestError("manifest file size_bytes must be non-negative")

    dorado = manifest.get("dorado", {})
    reference = manifest.get("reference", {})
    if not isinstance(dorado, dict) or not dorado.get("model"):
        raise ManifestError("manifest requires dorado.model")
    if not isinstance(dorado.get("barcode_kit"), str) or not dorado.get("barcode_kit"):
        raise ManifestError("manifest requires dorado.barcode_kit")
    if not isinstance(reference, dict) or not reference.get("path"):
        raise ManifestError("manifest requires reference.path")

    barcodes = manifest.get("barcodes")
    if not isinstance(barcodes, list) or not barcodes:
        raise ManifestError("manifest requires barcode metadata")
    barcode_numbers = set()
    for barcode in barcodes:
        if not isinstance(barcode, dict):
            raise ManifestError("barcode entries must be objects")
        number = barcode.get("barcode")
        if not isinstance(number, int) or number < 0 or number in barcode_numbers:
            raise ManifestError("barcode values must be unique non-negative integers")
        if not barcode.get("seqid") or not barcode.get("olnid"):
            raise ManifestError("barcode entries require seqid and olnid")
        barcode_numbers.add(number)
    return manifest


def resolve_source(source_root, entry):
    relative = relative_path(entry["relative_path"], "relative_path")
    blob_name = relative_path(entry["blob_name"], "blob_name")
    candidates = (
        source_root / relative,
        source_root / "pod5" / relative,
        source_root / blob_name,
    )
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate.is_file() and source_root.resolve() in candidate.parents:
            return candidate
    raise FileNotFoundError("POD5 input is missing: {}".format(relative))


def materialize_inputs(manifest, source_root, input_directory):
    pod5_directory = input_directory / "pod5"
    pod5_directory.mkdir(parents=True, exist_ok=True)
    materialized = []
    for entry in manifest["files"]:
        source = resolve_source(source_root, entry)
        expected_size = entry["size_bytes"]
        if source.stat().st_size != expected_size:
            raise ValueError("POD5 size mismatch: {}".format(entry["relative_path"]))
        expected_sha256 = entry.get("sha256")
        if expected_sha256 and sha256_file(source) != expected_sha256:
            raise ValueError("POD5 SHA-256 mismatch: {}".format(entry["relative_path"]))
        destination = pod5_directory / relative_path(
            entry["relative_path"], "relative_path"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name(destination.name + ".partial")
        shutil.copyfile(source, partial)
        os.replace(partial, destination)
        materialized.append(destination)
    return materialized


def write_scheduler_inputs(manifest, manifest_path, input_directory, output_directory):
    scheduler_directory = output_directory / "scheduler"
    scheduler_directory.mkdir(parents=True, exist_ok=True)
    run_csv = scheduler_directory / "scheduler-run.csv"
    metadata_csv = scheduler_directory / "scheduler-metadata.csv"
    reference = manifest["reference"]["path"]
    barcode_values = [str(item["barcode"]) for item in manifest["barcodes"]]

    with open(run_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "run_id", "reference", "pod5_dir", "output_dir",
                "barcode", "barcode_values",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "run_id": str(manifest["run_id"]),
            "reference": reference,
            "pod5_dir": str(input_directory / "pod5"),
            "output_dir": str(scheduler_directory),
            "barcode": manifest["dorado"]["barcode_kit"],
            "barcode_values": ",".join(barcode_values),
        })

    with open(metadata_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Barcode", "SEQID", "OLNID"])
        writer.writeheader()
        for barcode in manifest["barcodes"]:
            writer.writerow({
                "Barcode": barcode["barcode"],
                "SEQID": barcode["seqid"],
                "OLNID": barcode["olnid"],
            })

    shutil.copyfile(manifest_path, input_directory / "finalized-manifest.json")
    (input_directory / ".upload-complete").touch()
    return run_csv, metadata_csv


def inventory_outputs(output_directory):
    outputs = []
    for path in sorted(output_directory.rglob("*")):
        if not path.is_file() or path.name in ("result-manifest.json",):
            continue
        outputs.append({
            "path": path.relative_to(output_directory).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return outputs


def atomic_write_json(path, value):
    """Write a JSON document without exposing a partially written file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def publish_immutable_file(source, destination):
    """Publish one file once, rejecting divergent retry output."""
    source = Path(source)
    destination = Path(destination)
    if not source.is_file():
        raise FileNotFoundError(str(source))
    if destination.exists():
        if (
            destination.stat().st_size != source.stat().st_size or
            sha256_file(destination) != sha256_file(source)
        ):
            raise ValueError(
                "immutable output conflict: {}".format(destination)
            )
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".partial")
    shutil.copyfile(source, partial)
    os.replace(partial, destination)
    return True


def publish_result_manifest(task_root, manifest, result):
    """Commit the result manifest and latest pointer in publication order."""
    task_root = Path(task_root)
    publication_directory = task_root / "output" / "manifests"
    result_path = publication_directory / "result-manifest.json"
    latest_path = publication_directory / "latest.json"
    publication_state_path = publication_directory / "publication-state.json"

    for output in result.get("outputs", []):
        source = task_root / "output" / output["path"]
        publish_immutable_file(source, task_root / "output" / output["path"])

    atomic_write_json(result_path, result)
    publication_state = {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "run_name": manifest["run_name"],
        "status": result["status"],
        "result_manifest": result_path.name,
        "published_at": utc_now(),
    }
    atomic_write_json(publication_state_path, publication_state)
    atomic_write_json(latest_path, {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "run_name": manifest["run_name"],
        "result_manifest": result_path.name,
        "publication_state": publication_state_path.name,
        "published_at": publication_state["published_at"],
    })
    return result_path


def download_manifest_inputs(store, container, manifest_blob, manifest_path,
                             source_root):
    """Download and verify the immutable manifest inputs into a task root."""
    store.download_file(container, manifest_blob, manifest_path)
    manifest = load_manifest(manifest_path)
    for entry in manifest["files"]:
        destination = source_root / relative_path(
            entry["relative_path"], "relative_path"
        )
        store.download_file(container, entry["blob_name"], destination)
    return manifest


def publish_cloud_results(store, container, prefix, task_root, manifest, result):
    """Publish outputs first and commit the result pointers last."""
    output_directory = Path(task_root) / "output"
    files = sorted(path for path in output_directory.rglob("*") if path.is_file())
    latest = output_directory / "manifests" / "latest.json"
    for path in files:
        if path == latest:
            continue
        blob_name = "{}/{}".format(prefix.strip("/"), path.relative_to(
            output_directory
        ).as_posix())
        store.upload_immutable_file(container, blob_name, path)
    blob_name = "{}/manifests/latest.json".format(prefix.strip("/"))
    store.upload_immutable_file(container, blob_name, latest)


def run_task(args):
    task_root = Path(args.task_root).resolve()
    storage = None
    if args.input_sas_url or args.output_sas_url:
        storage = AzureBlobStore(
            input_sas_url=args.input_sas_url,
            output_sas_url=args.output_sas_url,
        )
    elif args.storage_account or args.storage_key:
        storage = AzureBlobStore(args.storage_account, args.storage_key)
    manifest_path = Path(args.manifest).resolve() if args.manifest else (
        task_root / "input" / "finalized-manifest.json"
    )
    source_root = Path(args.source_root).resolve()
    input_directory = task_root / "input"
    output_directory = task_root / "output"
    logs_directory = task_root / "logs"
    output_directory.mkdir(parents=True, exist_ok=True)
    logs_directory.mkdir(parents=True, exist_ok=True)

    if args.manifest_blob:
        if storage is None or not args.input_container:
            raise ValueError(
                "cloud manifest mode requires storage credentials and input container"
            )
        manifest = download_manifest_inputs(
            storage, args.input_container, args.manifest_blob,
            manifest_path, source_root
        )
    else:
        manifest = load_manifest(manifest_path)
    materialize_inputs(manifest, source_root, input_directory)
    run_csv, metadata_csv = write_scheduler_inputs(
        manifest, manifest_path, input_directory, output_directory
    )
    command = [
        args.python,
        args.scheduler,
        str(run_csv),
        str(metadata_csv),
        "--model", manifest["dorado"]["model"],
        "--device", args.device,
        "--once",
        "--keep-mapping-bam",
        "--completion-marker", str(input_directory / ".upload-complete"),
    ]
    started_at = utc_now()
    stdout_path = logs_directory / "scheduler-stdout.log"
    stderr_path = logs_directory / "scheduler-stderr.log"
    with open(stdout_path, "w", encoding="utf-8") as stdout, open(
        stderr_path, "w", encoding="utf-8"
    ) as stderr:
        completed = subprocess.run(command, stdout=stdout, stderr=stderr, check=False)
    (logs_directory / "exit-code.txt").write_text(
        "{}\n".format(completed.returncode), encoding="utf-8"
    )
    result = {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "run_name": manifest["run_name"],
        "status": "completed" if completed.returncode == 0 else "failed",
        "started_at": started_at,
        "finished_at": utc_now(),
        "scheduler_exit_code": completed.returncode,
        "input_manifest": {
            "path": str(manifest_path),
            "sha256": sha256_file(manifest_path),
        },
        "scheduler_run_csv_sha256": sha256_file(run_csv),
        "scheduler_metadata_csv_sha256": sha256_file(metadata_csv),
        "outputs": inventory_outputs(output_directory),
    }
    publish_result_manifest(task_root, manifest, result)
    if storage is not None and args.output_container:
        publish_cloud_results(
            storage,
            args.output_container,
            args.output_prefix or "runs/{}/".format(manifest["run_name"]),
            task_root,
            manifest,
            result,
        )
    return completed.returncode


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--manifest-blob")
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--task-root", required=True, type=Path)
    parser.add_argument("--input-container")
    parser.add_argument("--output-container")
    parser.add_argument("--output-prefix")
    parser.add_argument("--storage-account")
    parser.add_argument("--storage-key")
    parser.add_argument("--input-sas-url")
    parser.add_argument("--output-sas-url")
    parser.add_argument("--scheduler", required=True, type=Path)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--device", default=os.environ.get("DORADO_DEVICE", "cuda:all"))
    return parser.parse_args(argv)


def main(argv=None):
    try:
        return run_task(parse_arguments(argv))
    except (ManifestError, FileNotFoundError, OSError, ValueError) as exc:
        print("Nanopore task failed: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
