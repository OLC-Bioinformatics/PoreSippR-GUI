"""Tests for the FoodPort manifest-driven task wrapper."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "foodport_nanopore_task.py"
SPEC = importlib.util.spec_from_file_location("foodport_nanopore_task", MODULE_PATH)
wrapper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wrapper)


def test_wrapper_parser_accepts_foodport_streaming_options():
    arguments = wrapper.parse_arguments([
        "--manifest-blob", "260916-nanopore/input/manifests/input-manifest-v000001.json",
        "--manifest-prefix", "260916-nanopore/input/manifests/input-manifest-v",
        "--control-blob", "260916-nanopore/input/control/state.json",
        "--source-root", "/tmp/source",
        "--task-root", "/tmp/task",
        "--scheduler", "/tmp/scheduler.py",
    ])

    assert arguments.manifest_prefix == (
        "260916-nanopore/input/manifests/input-manifest-v"
    )
    assert arguments.control_blob == (
        "260916-nanopore/input/control/state.json"
    )


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


def test_scheduler_input_generation_accepts_manifest_in_input_directory(tmp_path):
    reference = tmp_path / "reference.fasta"
    manifest_path = tmp_path / "task" / "input" / "finalized-manifest.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(
        json.dumps(make_manifest(reference)), encoding="utf-8"
    )

    wrapper.write_scheduler_inputs(
        make_manifest(reference), manifest_path, manifest_path.parent,
        tmp_path / "task" / "output"
    )

    assert manifest_path.is_file()


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


def test_manifest_generation_accepts_only_immutable_generation_names():
    assert wrapper.manifest_generation(
        "1745/input/manifests/input-manifest-v000007.json"
    ) == 7
    assert wrapper.manifest_generation("1745/input/manifest.json") is None
    assert wrapper.manifest_generation(
        "1745/input/manifests/input-manifest-vlatest.json"
    ) is None


def test_resolve_model_path_prefers_installed_model_directory(tmp_path):
    model = tmp_path / "dna_r10.4.1_e8.2_400bps_fast@v5.2.0"
    model.mkdir()

    assert wrapper.resolve_model_path(
        model.name, str(tmp_path)
    ) == str(model)


def test_resolve_model_path_accepts_explicit_directory(tmp_path):
    model = tmp_path / "model"
    model.mkdir()

    assert wrapper.resolve_model_path(str(model), str(tmp_path)) == str(model)


def test_resolve_model_path_rejects_missing_model(tmp_path):
    with pytest.raises(FileNotFoundError, match="Dorado model is not installed"):
        wrapper.resolve_model_path("missing-model", str(tmp_path))


def test_publish_result_manifest_uses_iteration_path(tmp_path):
    result_path = wrapper.publish_result_manifest(
        tmp_path,
        {"run_id": 42, "run_name": "260825-nanopore"},
        {"status": "completed", "outputs": []},
        iteration=7,
    )

    assert result_path == (
        tmp_path / "output/manifests/iteration-000007.json"
    )
    latest = json.loads(
        (tmp_path / "output/manifests/latest.json").read_text(
            encoding="utf-8"
        )
    )
    assert latest["result_manifest"] == (
        "iterations/iteration-000007/manifests/iteration-000007.json"
    )


def test_publish_immutable_file_rejects_divergent_retry(tmp_path):
    source = tmp_path / "source.txt"
    destination = tmp_path / "published/source.txt"
    source.write_text("first\n", encoding="utf-8")

    assert wrapper.publish_immutable_file(source, destination) is True
    assert wrapper.publish_immutable_file(source, destination) is False

    source.write_text("different\n", encoding="utf-8")
    with pytest.raises(ValueError, match="immutable output conflict"):
        wrapper.publish_immutable_file(source, destination)


def test_sas_store_uploads_immutable_file_through_output_container(tmp_path):
    class FakeBlob:
        def __init__(self):
            self.metadata = None

        def upload_blob(self, handle, overwrite, metadata):
            assert overwrite is False
            assert handle.read() == b"result\n"
            self.metadata = metadata

    class FakeContainer:
        def __init__(self, blob):
            self.blob = blob

        def get_blob_client(self, blob_name):
            assert blob_name == "runs/example/result.txt"
            return self.blob

    source = tmp_path / "result.txt"
    source.write_bytes(b"result\n")
    blob = FakeBlob()
    store = wrapper.AzureBlobStore.__new__(wrapper.AzureBlobStore)
    store.client = None
    store.input_container = None
    store.output_container = FakeContainer(blob)

    assert store.upload_immutable_file(
        "nanopore-results", "runs/example/result.txt", source
    ) is True
    assert blob.metadata["sha256"] == wrapper.sha256_file(source)


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
        self.mutable_uploads = []
        self.immutable_uploads = []

    def download_file(
        self,
        container,
        blob_name,
        destination,
    ):
        self.downloads.append((container, blob_name))
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        destination.write_bytes(self.files[blob_name])

    def upload_immutable_file(
        self,
        container,
        blob_name,
        source,
    ):
        upload = (
            container,
            blob_name,
        )
        self.uploads.append(upload)
        self.immutable_uploads.append(upload)
        return True

    def upload_mutable_file(
        self,
        container,
        blob_name,
        source,
    ):
        upload = (
            container,
            blob_name,
        )
        self.uploads.append(upload)
        self.mutable_uploads.append(upload)
        return True

    def publish_file(
        self,
        container,
        blob_name,
        source,
    ):
        if wrapper.is_mutable_cloud_output(blob_name):
            self.upload_mutable_file(
                container,
                blob_name,
                source,
            )
            return True

        return self.upload_immutable_file(
            container,
            blob_name,
            source,
        )


def test_streaming_wrapper_processes_generations_in_one_workspace(tmp_path):
    reference = tmp_path / "reference.fasta"
    reference.write_text(">target\nACGT\n", encoding="utf-8")
    first_manifest = make_manifest(reference)
    second_manifest = make_manifest(reference)
    second_manifest["files"][0]["relative_path"] = "pass/sample-002.pod5"
    second_manifest["files"][0]["blob_name"] = (
        "runs/260825-nanopore/input/pod5/pass/sample-002.pod5"
    )
    first_manifest["files"][0]["size_bytes"] = 6
    second_manifest["files"][0]["size_bytes"] = 6
    manifest_blobs = {
        "runs/260825-nanopore/input/manifests/input-manifest-v000001.json":
            json.dumps(first_manifest).encode("utf-8"),
        "runs/260825-nanopore/input/manifests/input-manifest-v000002.json":
            json.dumps(second_manifest).encode("utf-8"),
        first_manifest["files"][0]["blob_name"]: b"pod5-1",
        second_manifest["files"][0]["blob_name"]: b"pod5-2",
        "runs/260825-nanopore/input/control/state.json": (
            b'{"state": "stopping"}'
        ),
    }

    class StreamingStore(FakeBlobStore):
        def list_blob_names(self, container, prefix):
            return [
                name for name in self.files
                if name.startswith(prefix)
            ]

        def blob_exists(self, container, blob_name):
            return True

    store = StreamingStore(manifest_blobs)
    arguments = SimpleNamespace(
        manifest=None,
        manifest_blob=(
            "runs/260825-nanopore/input/manifests/"
            "input-manifest-v000001.json"
        ),
        manifest_prefix=(
            "runs/260825-nanopore/input/manifests/input-manifest-v"
        ),
        control_blob="runs/260825-nanopore/input/control/state.json",
        poll_seconds=0,
        source_root=tmp_path / "source",
        task_root=tmp_path / "task",
        input_container="nanopore-runs",
        output_container="nanopore-results",
        output_prefix="runs/260825-nanopore",
        input_sas_url="input-sas",
        output_sas_url="output-sas",
        storage_account=None,
        storage_key=None,
        scheduler=tmp_path / "scheduler.py",
        python="python",
        device="cuda:0",
    )

    def run_scheduler(command, stdout, stderr, check):
        output = arguments.task_root / "output" / "scheduler" / "reads.fastq"
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("a", encoding="utf-8") as handle:
            handle.write("generation\n")
        return SimpleNamespace(returncode=0)

    with mock.patch.object(wrapper, "AzureBlobStore", return_value=store), \
            mock.patch.object(wrapper, "resolve_model_path", return_value="model"), \
            mock.patch.object(wrapper.subprocess, "run", side_effect=run_scheduler):
        assert wrapper.run_task(arguments) == 0

    scheduler_calls = [
        upload for upload in store.uploads
        if upload[1].endswith("/scheduler/reads.fastq")
    ]
    assert len(scheduler_calls) == 2
    assert (
        arguments.task_root / "output" / "scheduler" / "reads.fastq"
    ).read_text(encoding="utf-8") == "generation\ngeneration\n"
    assert json.loads(
        (arguments.task_root / "input" / ".processed-generations.json")
        .read_text(encoding="utf-8")
    ) == [1, 2]


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


def test_publish_cloud_results_uploads_latest_last(
    tmp_path,
):
    task_root = tmp_path / "task"
    output = task_root / "output"

    (output / "results").mkdir(parents=True)
    (output / "manifests").mkdir(parents=True)

    (output / "results/sample.csv").write_text(
        "result\n",
        encoding="utf-8",
    )

    (output / "manifests/publication-state.json").write_text(
        "{}\n",
        encoding="utf-8",
    )

    (output / "manifests/latest.json").write_text(
        "{}\n",
        encoding="utf-8",
    )

    store = FakeBlobStore({})

    wrapper.publish_cloud_results(
        store,
        "nanopore-results",
        "runs/example/",
        task_root,
        {},
        {},
    )

    latest_upload = (
        "nanopore-results",
        "runs/example/manifests/latest.json",
    )

    publication_state_upload = (
        "nanopore-results",
        "runs/example/manifests/publication-state.json",
    )

    result_upload = (
        "nanopore-results",
        "runs/example/results/sample.csv",
    )

    assert store.uploads[-1] == latest_upload

    assert latest_upload in store.mutable_uploads
    assert latest_upload not in store.immutable_uploads

    assert publication_state_upload in store.mutable_uploads
    assert publication_state_upload not in store.immutable_uploads

    assert result_upload in store.immutable_uploads
    assert result_upload not in store.mutable_uploads

def test_publish_cloud_results_updates_latest_pointer(
    tmp_path,
):
    task_root = tmp_path / "task"
    output = task_root / "output"

    (output / "manifests").mkdir(parents=True)

    (output / "manifests/latest.json").write_text(
        "{}\n",
        encoding="utf-8",
    )

    store = FakeBlobStore({})

    wrapper.publish_cloud_results(
        store,
        "nanopore-results",
        ("runs/example/iterations/iteration-000002"),
        task_root,
        {},
        {},
    )

    assert store.uploads[-1] == (
        "nanopore-results",
        "runs/example/manifests/latest.json",
    )


def test_mutable_cloud_output_matches_run_prefixed_latest():
    assert wrapper.is_mutable_cloud_output("runs/260921-nanopore/manifests/latest.json")


def test_mutable_cloud_output_matches_iteration_publication_state():
    assert wrapper.is_mutable_cloud_output(
        "runs/260921-nanopore/iterations/iteration-000002/"
        "manifests/publication-state.json"
    )


def test_scheduler_state_is_mutable():
    assert wrapper.is_mutable_cloud_output(
        "runs/260921-nanopore/iterations/iteration-000002/scheduler/state.json"
    )


def test_iteration_result_manifest_remains_immutable():
    assert not wrapper.is_mutable_cloud_output(
        "runs/260921-nanopore/iterations/iteration-000002/"
        "manifests/iteration-000002.json"
    )


def test_fastq_remains_immutable():
    assert not wrapper.is_mutable_cloud_output(
        "runs/260921-nanopore/iterations/iteration-000002/"
        "fastq/barcode01/batch-000001/0001-reads.fastq.gz"
    )


class RecordingStore(object):
    def __init__(self):
        self.mutable = []
        self.immutable = []

    def upload_mutable_file(self, container, blob_name, source):
        self.mutable.append((container, blob_name, Path(source)))

    def upload_immutable_file(self, container, blob_name, source):
        self.immutable.append((container, blob_name, Path(source)))
        return True

    def publish_file(
        self,
        container,
        blob_name,
        source,
    ):
        if wrapper.is_mutable_cloud_output(blob_name):
            print(
                "TEST publishing mutable cloud output: {}".format(
                    blob_name
                )
            )

            self.upload_mutable_file(
                container,
                blob_name,
                source,
            )

            return True

        print(
            "TEST publishing immutable cloud output: {}".format(
                blob_name
            )
        )

        return self.upload_immutable_file(
            container,
            blob_name,
            source,
        )


def test_publish_cloud_results_commits_root_latest_as_mutable(tmp_path):
    output = tmp_path / "output"
    manifests = output / "manifests"
    results = output / "results"
    manifests.mkdir(parents=True)
    results.mkdir(parents=True)

    (manifests / "latest.json").write_text(
        '{"latest_iteration": 2}\n', encoding="utf-8"
    )
    (manifests / "iteration-000002.json").write_text(
        '{"iteration": 2}\n', encoding="utf-8"
    )
    (results / "sample_iteration2.csv").write_text(
        "gene_name,number_of_reads_mapped\n", encoding="utf-8"
    )

    store = RecordingStore()

    wrapper.publish_cloud_results(
        store=store,
        container="nanopore-results",
        prefix=("runs/260921-nanopore/iterations/iteration-000002"),
        task_root=tmp_path,
        manifest={"run_id": 1, "run_name": "260921-nanopore"},
        result={"status": "completed"},
    )

    mutable_names = [item[1] for item in store.mutable]
    immutable_names = [item[1] for item in store.immutable]

    assert mutable_names == ["runs/260921-nanopore/manifests/latest.json"]
    assert "runs/260921-nanopore/manifests/latest.json" not in immutable_names
    assert any(name.endswith("iteration-000002.json") for name in immutable_names)
    assert any(name.endswith("sample_iteration2.csv") for name in immutable_names)


def test_immutable_upload_redirects_known_mutable_path(tmp_path):
    source = tmp_path / "latest.json"
    source.write_text('{"iteration": 2}\n', encoding="utf-8")

    store = object.__new__(wrapper.AzureBlobStore)
    calls = []

    def mutable(container, blob_name, source_path):
        calls.append((container, blob_name, Path(source_path)))

    store.upload_mutable_file = mutable

    result = store.upload_immutable_file(
        "nanopore-results",
        "runs/260921-nanopore/manifests/latest.json",
        source,
    )

    assert result is True
    assert calls == [
        (
            "nanopore-results",
            "runs/260921-nanopore/manifests/latest.json",
            source,
        )
    ]
