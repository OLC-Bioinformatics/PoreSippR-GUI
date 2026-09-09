"""Tests for the FoodPort manifest-driven task wrapper."""

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "foodport_nanopore_task.py"
SPEC = importlib.util.spec_from_file_location("foodport_nanopore_task", MODULE_PATH)
wrapper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wrapper)


def make_manifest(reference):
    return {
        "schema_version": 1,
        "run_id": 42,
        "run_name": "260825-nanopore",
        "finalized": True,
        "dorado": {
            "model": "dna_r10.4.1_e8.2_400bps_fast@v5.2.0",
            "barcode_kit": "SQK-RBK114-24",
        },
        "reference": {"path": str(reference)},
        "barcodes": [{"barcode": 12, "seqid": "sample-12", "olnid": "OLN12"}],
        "files": [{
            "relative_path": "pass/sample-001.pod5",
            "blob_name": "runs/260825-nanopore/pod5/pass/sample-001.pod5",
            "size_bytes": 4,
        }],
    }


def test_manifest_materialization_and_csv_generation(tmp_path):
    reference = tmp_path / "reference.fasta"
    reference.write_text(">target\nACGT\n", encoding="utf-8")
    source = tmp_path / "source" / "pass" / "sample-001.pod5"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"pod5")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(make_manifest(reference)), encoding="utf-8")

    manifest = wrapper.load_manifest(manifest_path)
    input_directory = tmp_path / "task" / "input"
    wrapper.materialize_inputs(manifest, tmp_path / "source", input_directory)
    run_csv, metadata_csv = wrapper.write_scheduler_inputs(
        manifest, manifest_path, input_directory, tmp_path / "task" / "output"
    )

    assert (input_directory / "pod5/pass/sample-001.pod5").read_bytes() == b"pod5"
    assert "42" in run_csv.read_text(encoding="utf-8")
    assert "sample-12" in metadata_csv.read_text(encoding="utf-8")
    assert (input_directory / ".upload-complete").is_file()


def test_manifest_rejects_path_traversal(tmp_path):
    manifest = make_manifest(tmp_path / "reference.fasta")
    manifest["files"][0]["relative_path"] = "../outside.pod5"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(wrapper.ManifestError):
        wrapper.load_manifest(manifest_path)


def test_publish_result_manifest_writes_latest_after_state(tmp_path):
    manifest = make_manifest(tmp_path / "reference.fasta")
    result = {
        "status": "completed",
        "outputs": [],
    }

    result_path = wrapper.publish_result_manifest(tmp_path, manifest, result)

    assert result_path == tmp_path / "output/manifests/result-manifest.json"
    publication_state = json.loads(
        (tmp_path / "output/manifests/publication-state.json").read_text(
            encoding="utf-8"
        )
    )
    latest = json.loads(
        (tmp_path / "output/manifests/latest.json").read_text(encoding="utf-8")
    )
    assert publication_state["result_manifest"] == "result-manifest.json"
    assert latest["publication_state"] == "publication-state.json"


def test_publish_immutable_file_rejects_divergent_retry(tmp_path):
    source = tmp_path / "source.txt"
    destination = tmp_path / "published/source.txt"
    source.write_text("first\n", encoding="utf-8")

    assert wrapper.publish_immutable_file(source, destination) is True
    assert wrapper.publish_immutable_file(source, destination) is False

    source.write_text("different\n", encoding="utf-8")
    with pytest.raises(ValueError, match="immutable output conflict"):
        wrapper.publish_immutable_file(source, destination)


def test_inventory_outputs_is_relative_to_output_directory(tmp_path):
    output_directory = tmp_path / "task" / "output"
    output_file = output_directory / "results" / "sample.csv"
    output_file.parent.mkdir(parents=True)
    output_file.write_text("result\n", encoding="utf-8")
    (tmp_path / "task" / "input.txt").write_text("input\n", encoding="utf-8")

    assert wrapper.inventory_outputs(output_directory) == [{
        "path": "results/sample.csv",
        "size_bytes": 7,
        "sha256": wrapper.sha256_file(output_file),
    }]


class FakeBlobStore:
    def __init__(self, files):
        self.files = files
        self.downloads = []
        self.uploads = []

    def download_file(self, container, blob_name, destination):
        self.downloads.append((container, blob_name))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(self.files[blob_name])

    def upload_immutable_file(self, container, blob_name, source):
        self.uploads.append((container, blob_name))
        return True


def test_download_manifest_inputs_uses_blob_names_and_local_paths(tmp_path):
    reference = tmp_path / "reference.fasta"
    manifest = make_manifest(reference)
    manifest_blob = "runs/260825-nanopore/manifests/finalized-manifest.json"
    store = FakeBlobStore({
        manifest_blob: json.dumps(manifest).encode("utf-8"),
        manifest["files"][0]["blob_name"]: b"pod5",
    })
    manifest_path = tmp_path / "task/input/finalized-manifest.json"
    source_root = tmp_path / "source"

    wrapper.download_manifest_inputs(
        store, "nanopore-raw", manifest_blob, manifest_path, source_root
    )

    assert (source_root / "pass/sample-001.pod5").read_bytes() == b"pod5"
    assert store.downloads == [
        ("nanopore-raw", manifest_blob),
        ("nanopore-raw", manifest["files"][0]["blob_name"]),
    ]


def test_publish_cloud_results_uploads_latest_last(tmp_path):
    output = tmp_path / "task/output"
    (output / "results").mkdir(parents=True)
    (output / "manifests").mkdir(parents=True)
    (output / "results/sample.csv").write_text("result\n", encoding="utf-8")
    (output / "manifests/publication-state.json").write_text(
        "{}\n", encoding="utf-8"
    )
    (output / "manifests/latest.json").write_text("{}\n", encoding="utf-8")
    store = FakeBlobStore({})

    wrapper.publish_cloud_results(
        store, "nanopore-results", "runs/example", tmp_path, {}, {}
    )

    assert store.uploads[-1] == (
        "nanopore-results", "runs/example/manifests/latest.json"
    )
