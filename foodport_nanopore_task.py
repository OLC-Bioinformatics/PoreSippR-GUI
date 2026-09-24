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
import time
from datetime import datetime, timezone
from pathlib import Path


PROGRAM_NAME = "foodport-nanopore-task"
WRAPPER_VERSION = "0.0.17"

MUTABLE_CLOUD_OUTPUT_SUFFIXES = (
    "/manifests/latest.json",
    "/manifests/publication-state.json",
    "/control/state.json",
    "/control/status.json",
    "/scheduler/state.json",
    "/scheduler/status.json",
)


def is_mutable_cloud_output(blob_name):
    """Return whether a cloud object is intentionally mutable."""
    normalized = str(blob_name).replace(
        "\\",
        "/",
    )

    if "/logs/" in normalized:
        return True

    return normalized.endswith(MUTABLE_CLOUD_OUTPUT_SUFFIXES)


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
        downloader = blob.download_blob(max_concurrency=4)
        with open(partial, "wb") as handle:
            for chunk in downloader.chunks():
                handle.write(chunk)
        os.replace(partial, destination)

    def upload_file(self, container, blob_name, source):
        source = Path(source)
        blob = self._blob_client(container, blob_name, writing=True)
        with open(source, "rb") as handle:
            blob.upload_blob(handle, overwrite=False)

    def blob_properties(self, container, blob_name):
        blob = self._blob_client(container, blob_name, writing=True)
        return blob.get_blob_properties()

    def blob_exists(self, container, blob_name):
        try:
            self._blob_client(container, blob_name).get_blob_properties()
            return True
        except Exception as exc:
            if exc.__class__.__name__ == "ResourceNotFoundError":
                return False
            raise

    def list_blob_names(self, container, prefix):
        container_client = (
            self.output_container if container == "__output__"
            else self.input_container
        )
        if container_client is not None:
            return sorted(
                blob.name for blob in container_client.list_blobs(
                    name_starts_with=prefix
                )
            )
        return sorted(
            blob.name for blob in self.client.get_container_client(
                container
            ).list_blobs(name_starts_with=prefix)
        )

    def publish_file(self, container, blob_name, source):
        """Publish an object according to its cloud path policy."""
        if is_mutable_cloud_output(blob_name):
            print("Publishing mutable cloud output: {}".format(blob_name))
            self.upload_mutable_file(container, blob_name, source)
            return True

        print("Publishing immutable cloud output: {}".format(blob_name))
        return self.upload_immutable_file(container, blob_name, source)

    def upload_immutable_file(self, container, blob_name, source):
        if is_mutable_cloud_output(blob_name):
            print("Redirecting mutable cloud output: {}".format(blob_name))
            self.upload_mutable_file(container, blob_name, source)
            return True

        source = Path(source)
        digest = sha256_file(source)
        try:
            blob = self._blob_client(container, blob_name, writing=True)
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

    def upload_mutable_file(self, container, blob_name, source):
        source = Path(source)
        blob = self._blob_client(container, blob_name, writing=True)
        with open(source, "rb") as handle:
            blob.upload_blob(handle, overwrite=True)


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
    """Copy one manifest generation into an isolated input directory."""
    input_directory = Path(input_directory)
    if input_directory.exists():
        shutil.rmtree(str(input_directory))

    pod5_directory = input_directory / "pod5"
    pod5_directory.mkdir(parents=True, exist_ok=False)
    materialized = []

    for entry in manifest["files"]:
        source = resolve_source(source_root, entry)
        expected_size = entry["size_bytes"]
        if source.stat().st_size != expected_size:
            raise ValueError(
                "POD5 size mismatch: {}".format(entry["relative_path"])
            )

        expected_sha256 = entry.get("sha256")
        if expected_sha256 and sha256_file(source) != expected_sha256:
            raise ValueError(
                "POD5 SHA-256 mismatch: {}".format(
                    entry["relative_path"]
                )
            )

        destination = pod5_directory / relative_path(
            entry["relative_path"],
            "relative_path",
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        partial = destination.with_name(destination.name + ".partial")
        shutil.copyfile(str(source), str(partial))
        os.replace(str(partial), str(destination))
        materialized.append(destination)

    return materialized


def write_scheduler_inputs(
        manifest, manifest_path, input_directory, output_directory):
    """Write scheduler CSV inputs for one isolated manifest generation."""
    scheduler_directory = Path(output_directory) / "scheduler"
    scheduler_directory.mkdir(parents=True, exist_ok=True)

    generation = int(manifest.get("generation") or 1)
    generation_name = "generation-{0:06d}".format(generation)
    control_directory = Path(input_directory) / "control"
    control_directory.mkdir(parents=True, exist_ok=True)

    run_csv = control_directory / (
        "scheduler-run-{0}.csv".format(generation_name)
    )
    metadata_csv = control_directory / (
        "scheduler-metadata-{0}.csv".format(generation_name)
    )
    reference = manifest["reference"]["path"]
    barcode_values = [
        str(item["barcode"])
        for item in manifest["barcodes"]
    ]

    with open(run_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "run_id",
                "reference",
                "pod5_dir",
                "output_dir",
                "barcode",
                "barcode_values",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "run_id": str(manifest["run_id"]),
            "reference": reference,
            "pod5_dir": str(Path(input_directory) / "pod5"),
            "output_dir": str(scheduler_directory),
            "barcode": manifest["dorado"]["barcode_kit"],
            "barcode_values": ",".join(barcode_values),
        })

    with open(metadata_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Barcode", "SEQID", "OLNID"],
        )
        writer.writeheader()
        for barcode in manifest["barcodes"]:
            writer.writerow({
                "Barcode": barcode["barcode"],
                "SEQID": barcode["seqid"],
                "OLNID": barcode["olnid"],
            })

    manifest_copy = control_directory / "finalized-manifest.json"
    if Path(manifest_path).resolve() != manifest_copy.resolve():
        shutil.copyfile(str(manifest_path), str(manifest_copy))

    completion_marker = control_directory / ".upload-complete"
    completion_marker.touch()
    return run_csv, metadata_csv, completion_marker


def output_snapshot(output_directory):
    """Return hashes and sizes for publishable shared output files."""
    output_directory = Path(output_directory)
    snapshot = {}

    if not output_directory.is_dir():
        return snapshot

    for path in sorted(output_directory.rglob("*")):
        if not path.is_file():
            continue

        relative = path.relative_to(output_directory).as_posix()
        if relative.startswith("manifests/"):
            continue
        if path.name == "result-manifest.json":
            continue

        snapshot[relative] = {
            "path": relative,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }

    return snapshot


def inventory_changed_outputs(output_directory, before):
    """Describe files created or changed during the current generation."""
    after = output_snapshot(output_directory)
    changed = []

    for relative in sorted(after):
        current = after[relative]
        previous = before.get(relative)
        if previous != current:
            changed.append(current)

    return changed

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



def publish_result_manifest(task_root, manifest, result, iteration=None):
    """Commit an immutable result manifest and mutable latest pointers."""
    task_root = Path(task_root)
    publication_directory = task_root / "output" / "manifests"
    latest_path = publication_directory / "latest.json"
    state_path = publication_directory / "publication-state.json"

    if iteration is None:
        result_path = publication_directory / "result-manifest.json"
        result_manifest_name = "manifests/result-manifest.json"
        publication_state_name = "manifests/publication-state.json"
    else:
        result_path = publication_directory / (
            "iteration-{0:06d}.json".format(iteration)
        )
        result_manifest_name = (
            "iterations/iteration-{0:06d}/manifests/"
            "iteration-{0:06d}.json"
        ).format(iteration)
        publication_state_name = (
            "iterations/iteration-{0:06d}/manifests/"
            "publication-state.json"
        ).format(iteration)

    atomic_write_json(result_path, result)
    published_at = utc_now()
    publication_state = {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "run_name": manifest["run_name"],
        "generation": iteration,
        "status": result["status"],
        "result_manifest": result_manifest_name,
        "published_at": published_at,
    }
    atomic_write_json(state_path, publication_state)
    atomic_write_json(latest_path, {
        "schema_version": 1,
        "run_id": manifest["run_id"],
        "run_name": manifest["run_name"],
        "generation": iteration,
        "result_manifest": result_manifest_name,
        "publication_state": publication_state_name,
        "published_at": published_at,
    })
    return result_path, state_path, latest_path

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



def publish_cloud_results(
        store, container, prefix, task_root, result, result_path,
        state_path, latest_path):
    """Publish one generation snapshot, then commit its pointers."""
    task_root = Path(task_root)
    output_directory = task_root / "output"
    prefix = prefix.strip("/")

    for output in result.get("outputs", []):
        relative = relative_path(output["path"], "output path")
        source = output_directory / relative
        if not source.is_file():
            raise FileNotFoundError(str(source))
        blob_name = "{0}/{1}".format(prefix, relative.as_posix())
        store.upload_immutable_file(container, blob_name, source)

    generation = int(result["generation"])
    manifest_blob = (
        "{0}/manifests/iteration-{1:06d}.json"
    ).format(prefix, generation)
    state_blob = "{}/manifests/publication-state.json".format(prefix)
    store.upload_immutable_file(container, manifest_blob, result_path)
    store.upload_mutable_file(container, state_blob, state_path)

    root_prefix = prefix.split("/iterations/", 1)[0]
    latest_blob = "{}/manifests/latest.json".format(root_prefix)
    store.upload_mutable_file(container, latest_blob, latest_path)

def wrapper_identity():
    """Return the installed wrapper version and source-file digest."""
    wrapper_path = Path(__file__).resolve()
    return {
        "version": WRAPPER_VERSION,
        "path": str(wrapper_path),
        "sha256": sha256_file(wrapper_path),
    }


def manifest_generation(blob_name):
    """Return the generation encoded in an immutable manifest name."""
    name = Path(blob_name).name
    if not name.startswith("input-manifest-v") or not name.endswith(".json"):
        return None
    try:
        return int(name[len("input-manifest-v"):-len(".json")])
    except ValueError:
        return None


def resolve_model_path(model, models_directory="/opt/ont/models"):
    """Prefer the immutable model installed in the runtime image."""
    model_path = Path(model)
    if model_path.is_dir():
        return str(model_path)

    installed_model = Path(models_directory) / model
    if installed_model.is_dir():
        return str(installed_model)

    raise FileNotFoundError(
        "Dorado model is not installed: {} (checked {})".format(
            model, installed_model
        )
    )


def control_state(storage, container, control_blob):
    if not storage.blob_exists(container, control_blob):
        return "running"
    control_path = Path("/tmp/foodport-nanopore-control.json")
    storage.download_file(container, control_blob, control_path)
    with open(control_path, "r", encoding="utf-8") as handle:
        return json.load(handle).get("state", "running")


def available_manifest_generations(storage, container, manifest_prefix):
    generations = []
    for blob_name in storage.list_blob_names(container, manifest_prefix):
        generation = manifest_generation(blob_name)
        if generation is not None:
            generations.append((generation, blob_name))
    return sorted(generations)



def run_task(args):
    """Process local or cloud manifests until the run is drained."""
    task_root = Path(args.task_root).resolve()
    storage = None

    if args.input_sas_url or args.output_sas_url:
        storage = AzureBlobStore(
            input_sas_url=args.input_sas_url,
            output_sas_url=args.output_sas_url,
        )
    elif args.storage_account or args.storage_key:
        storage = AzureBlobStore(
            args.storage_account,
            args.storage_key,
        )

    local_manifest_path = (
        Path(args.manifest).resolve()
        if args.manifest
        else task_root / "input" / "finalized-manifest.json"
    )
    source_root = Path(args.source_root).resolve()
    output_directory = task_root / "output"
    logs_directory = output_directory / "logs"
    iterations_directory = task_root / "iterations"
    state_directory = task_root / "state"

    for directory in (
            output_directory, logs_directory, iterations_directory,
            state_directory):
        directory.mkdir(parents=True, exist_ok=True)

    identity = wrapper_identity()
    print(
        "FoodPort Nanopore wrapper {} ({})".format(
            identity["version"],
            identity["sha256"],
        ),
        file=sys.stderr,
        flush=True,
    )

    streaming = bool(args.manifest_blob)
    if streaming:
        if storage is None or not args.input_container:
            raise ValueError(
                "cloud manifest mode requires input storage credentials"
            )
        if not args.output_container:
            raise ValueError(
                "cloud manifest mode requires an output container"
            )
        if not args.manifest_prefix or not args.control_blob:
            raise ValueError(
                "cloud streaming mode requires a manifest prefix and "
                "control blob"
            )
    else:
        load_manifest(local_manifest_path)

    processed_path = state_directory / ".processed-generations.json"
    if processed_path.exists():
        processed_values = json.loads(
            processed_path.read_text(encoding="utf-8")
        )
        if not isinstance(processed_values, list):
            raise ValueError("processed generation state must be a list")
        processed = set(int(value) for value in processed_values)
    else:
        processed = set()

    next_manifest_blob = args.manifest_blob or "__local_manifest__"
    final_return_code = 0

    while True:
        if next_manifest_blob is None:
            generations = available_manifest_generations(
                storage,
                args.input_container,
                args.manifest_prefix,
            )
            next_items = [
                item
                for item in generations
                if item[0] not in processed
            ]
            if not next_items:
                state = control_state(
                    storage,
                    args.input_container,
                    args.control_blob,
                )
                if state in ("stopping", "error"):
                    if state == "error":
                        return 1
                    return final_return_code
                time.sleep(args.poll_seconds)
                continue
            generation, next_manifest_blob = next_items[0]
        else:
            generation = manifest_generation(next_manifest_blob) or 1

        generation_root = iterations_directory / (
            "iteration-{0:06d}".format(generation)
        )
        input_directory = generation_root / "input"
        generation_root.mkdir(parents=True, exist_ok=True)

        if streaming:
            manifest_path = generation_root / (
                "input-manifest-v{0:06d}.json".format(generation)
            )
            manifest = download_manifest_inputs(
                storage,
                args.input_container,
                next_manifest_blob,
                manifest_path,
                source_root,
            )
        else:
            manifest_path = local_manifest_path
            manifest = load_manifest(manifest_path)

        manifest["generation"] = generation
        materialize_inputs(manifest, source_root, input_directory)
        run_csv, metadata_csv, completion_marker = (
            write_scheduler_inputs(
                manifest,
                manifest_path,
                input_directory,
                output_directory,
            )
        )

        before_outputs = output_snapshot(output_directory)
        stdout_path = logs_directory / (
            "scheduler-generation-{0:06d}-stdout.log".format(generation)
        )
        stderr_path = logs_directory / (
            "scheduler-generation-{0:06d}-stderr.log".format(generation)
        )
        command = [
            args.python,
            str(args.scheduler),
            str(run_csv),
            str(metadata_csv),
            "--model",
            resolve_model_path(manifest["dorado"]["model"]),
            "--device",
            args.device,
            "--once",
            "--keep-mapping-bam",
            "--completion-marker",
            str(completion_marker),
        ]

        started_at = utc_now()
        with open(stdout_path, "w", encoding="utf-8") as stdout, open(
                stderr_path, "w", encoding="utf-8") as stderr:
            completed = subprocess.run(
                command,
                stdout=stdout,
                stderr=stderr,
                check=False,
            )

        print(
            "Scheduler generation {0} exited with code {1}".format(
                generation,
                completed.returncode,
            ),
            file=sys.stderr,
            flush=True,
        )
        exit_code_path = logs_directory / (
            "scheduler-generation-{0:06d}-exit-code.txt".format(
                generation
            )
        )
        exit_code_path.write_text(
            "{}\n".format(completed.returncode),
            encoding="utf-8",
        )

        result = {
            "schema_version": 1,
            "wrapper": identity,
            "run_id": manifest["run_id"],
            "run_name": manifest["run_name"],
            "generation": generation,
            "iteration": generation,
            "status": (
                "completed"
                if completed.returncode == 0
                else "failed"
            ),
            "started_at": started_at,
            "finished_at": utc_now(),
            "scheduler_exit_code": completed.returncode,
            "input_manifest": {
                "path": str(manifest_path),
                "sha256": sha256_file(manifest_path),
            },
            "scheduler_run_csv_sha256": sha256_file(run_csv),
            "scheduler_metadata_csv_sha256": sha256_file(metadata_csv),
            "outputs": inventory_changed_outputs(
                output_directory,
                before_outputs,
            ),
        }
        result_path, state_path, latest_path = publish_result_manifest(
            task_root,
            manifest,
            result,
            generation,
        )

        if storage is not None:
            output_prefix = (
                args.output_prefix
                or "runs/{}".format(manifest["run_name"])
            )
            generation_prefix = (
                "{0}/iterations/iteration-{1:06d}"
            ).format(output_prefix, generation)
            publish_cloud_results(
                storage,
                args.output_container,
                generation_prefix,
                task_root,
                result,
                result_path,
                state_path,
                latest_path,
            )

        final_return_code = completed.returncode
        if completed.returncode != 0:
            try:
                scheduler_stderr = stderr_path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            except OSError:
                scheduler_stderr = ""
            if scheduler_stderr:
                print(
                    "Scheduler stderr tail:\n{}".format(
                        scheduler_stderr[-8000:]
                    ),
                    file=sys.stderr,
                    flush=True,
                )
            return completed.returncode

        processed.add(generation)
        atomic_write_json(processed_path, sorted(processed))
        next_manifest_blob = None
        if not streaming:
            return final_return_code


def parse_arguments(argv=None):
    """Parse wrapper command-line arguments."""
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description=__doc__,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {}".format(WRAPPER_VERSION),
    )
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--manifest-blob")
    parser.add_argument("--manifest-prefix")
    parser.add_argument("--control-blob")
    parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--task-root", required=True, type=Path)
    parser.add_argument("--input-container")
    parser.add_argument("--output-container")
    parser.add_argument("--output-prefix")
    parser.add_argument("--storage-account")
    parser.add_argument("--storage-key")
    parser.add_argument(
        "--input-sas-url",
        default=os.environ.get("FOODPORT_INPUT_SAS_URL"),
    )
    parser.add_argument(
        "--output-sas-url",
        default=os.environ.get("FOODPORT_OUTPUT_SAS_URL"),
    )
    parser.add_argument("--scheduler", required=True, type=Path)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--device",
        default=os.environ.get("DORADO_DEVICE", "cuda:all"),
    )
    return parser.parse_args(argv)

def main(argv=None):
    try:
        return run_task(parse_arguments(argv))
    except (
        ManifestError,
        FileNotFoundError,
        OSError,
        RuntimeError,
        ValueError,
    ) as exc:
        print("Nanopore task failed: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
