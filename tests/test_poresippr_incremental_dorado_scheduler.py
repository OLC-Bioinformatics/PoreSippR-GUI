"""Tests for the incremental Dorado scheduler."""

from __future__ import annotations

import csv
import gzip
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


SCHEDULER_PATH = (
    Path(__file__).resolve().parents[1]
    / "poresippr_incremental_dorado_scheduler.py"
)
MODULE_NAME = "poresippr_incremental_dorado_scheduler"


def load_scheduler() -> Any:
    """Load the scheduler module from the repository root.

    Returns:
        Loaded scheduler module.

    Raises:
        RuntimeError: If the module import specification cannot be created.
    """
    specification = importlib.util.spec_from_file_location(
        MODULE_NAME,
        SCHEDULER_PATH,
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Unable to import scheduler from {SCHEDULER_PATH}")

    module = importlib.util.module_from_spec(specification)
    sys.modules[MODULE_NAME] = module
    specification.loader.exec_module(module)
    return module


scheduler = load_scheduler()


@pytest.fixture
def run_configuration(tmp_path: Path) -> Any:
    """Create a minimal run configuration.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        Scheduler run configuration.
    """
    reference = tmp_path / "reference.fasta"
    reference.write_text(">target\nACGT\n", encoding="utf-8")
    pod5_directory = tmp_path / "pod5"
    pod5_directory.mkdir()

    return scheduler.RunConfiguration(
        run_id="run-001",
        reference=reference,
        pod5_directory=pod5_directory,
        output_directory=tmp_path / "output",
        barcode_kit="SQK-RBK114-24",
        barcode_values=(1, 2),
    )


@pytest.fixture
def scheduler_args(tmp_path: Path) -> SimpleNamespace:
    """Create arguments used by batch-processing tests.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        Namespace containing scheduler runtime options.
    """
    benchmark = tmp_path / "benchmarks.json"
    benchmark.write_text("{}\n", encoding="utf-8")

    return SimpleNamespace(
        benchmark_file=str(benchmark),
        device="cuda:0",
        dorado="dorado",
        genome_size=100,
        keep_batch_work=False,
        keep_mapping_bam=False,
        mapping_threads=2,
        minimap2="minimap2",
        model="model",
        refresh_benchmarks=False,
        samtools="samtools",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write dictionaries to a CSV file.

    Args:
        path: Destination CSV path.
        rows: Rows to write. At least one row is required.
    """
    if not rows:
        raise ValueError("At least one CSV row is required")

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_old_file(path: Path, content: bytes = b"pod5") -> None:
    """Create a nonempty file with an old modification time.

    Args:
        path: File to create.
        content: Binary file content.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    old_time = time.time() - 600
    os.utime(path, (old_time, old_time))


def test_parse_barcode_values() -> None:
    """Parse one or more comma-separated barcode values."""
    assert scheduler.parse_barcode_values(value="1") == (1,)
    assert scheduler.parse_barcode_values(value='1, "2", 3') == (1, 2, 3)


@pytest.mark.parametrize("value", ["", " , ", '""'])
def test_parse_barcode_values_rejects_empty(value: str) -> None:
    """Reject barcode strings containing no values.

    Args:
        value: Invalid barcode string.
    """
    with pytest.raises(ValueError, match="contains no barcode"):
        scheduler.parse_barcode_values(value=value)


def test_parse_barcode_values_rejects_duplicates() -> None:
    """Reject duplicate barcode values."""
    with pytest.raises(ValueError, match="duplicate"):
        scheduler.parse_barcode_values(value="1,2,1")


def test_load_metadata(tmp_path: Path) -> None:
    """Load metadata rows by barcode number.

    Args:
        tmp_path: Pytest temporary directory.
    """
    path = tmp_path / "metadata.csv"
    write_csv(
        path,
        [
            {"Barcode": 1, "SEQID": "sample-1", "OLNID": "OLN-1"},
            {"Barcode": 2, "SEQID": "sample-2", "OLNID": "OLN-2"},
        ],
    )

    metadata = scheduler.load_metadata(path=path)

    assert metadata[1] == {"seqid": "sample-1", "olnid": "OLN-1"}
    assert metadata[2] == {"seqid": "sample-2", "olnid": "OLN-2"}


def test_load_metadata_rejects_duplicate_barcode(tmp_path: Path) -> None:
    """Reject duplicate metadata barcode rows.

    Args:
        tmp_path: Pytest temporary directory.
    """
    path = tmp_path / "metadata.csv"
    write_csv(
        path,
        [
            {"Barcode": 1, "SEQID": "sample-1", "OLNID": "OLN-1"},
            {"Barcode": 1, "SEQID": "sample-2", "OLNID": "OLN-2"},
        ],
    )

    with pytest.raises(ValueError, match="duplicate barcode"):
        scheduler.load_metadata(path=path)


def test_load_runs_assigns_default_run_id(tmp_path: Path) -> None:
    """Assign a default run identifier when the column is absent.

    Args:
        tmp_path: Pytest temporary directory.
    """
    reference = tmp_path / "reference.fasta"
    reference.write_text(">target\nACGT\n", encoding="utf-8")
    path = tmp_path / "runs.csv"
    write_csv(
        path,
        [
            {
                "reference": reference,
                "pod5_dir": tmp_path / "pod5",
                "output_dir": tmp_path / "output",
                "barcode": "SQK-RBK114-24",
                "barcode_values": "1,2",
            }
        ],
    )

    runs = scheduler.load_runs(path=path)

    assert len(runs) == 1
    assert runs[0].run_id == "run-001"
    assert runs[0].barcode_values == (1, 2)


def test_load_runs_rejects_duplicate_run_ids(tmp_path: Path) -> None:
    """Reject duplicate explicit run identifiers.

    Args:
        tmp_path: Pytest temporary directory.
    """
    path = tmp_path / "runs.csv"
    common = {
        "reference": tmp_path / "reference.fasta",
        "pod5_dir": tmp_path / "pod5",
        "barcode": "SQK-RBK114-24",
        "barcode_values": "1",
    }
    write_csv(
        path,
        [
            {**common, "run_id": "same", "output_dir": tmp_path / "one"},
            {**common, "run_id": "same", "output_dir": tmp_path / "two"},
        ],
    )

    with pytest.raises(ValueError, match="run_id values must be unique"):
        scheduler.load_runs(path=path)


def test_initial_state_and_validation(run_configuration: Any) -> None:
    """Create and validate a new state document.

    Args:
        run_configuration: Scheduler run configuration fixture.
    """
    state = scheduler.initial_state(run=run_configuration)

    scheduler.validate_state(state=state, run=run_configuration)
    assert state["schema_version"] == 1
    assert state["next_batch_number"] == 1
    assert state["next_iteration"] == 1
    assert state["processed_pod5"] == {}
    assert state["batches"] == []


@pytest.mark.parametrize(
    ("field", "value", "exception"),
    [
        ("schema_version", 2, ValueError),
        ("run_id", "other-run", ValueError),
        ("next_batch_number", "1", TypeError),
        ("next_iteration", None, TypeError),
        ("processed_pod5", [], TypeError),
        ("batches", {}, TypeError),
        ("next_batch_number", 0, ValueError),
        ("next_iteration", -1, ValueError),
    ],
)
def test_validate_state_rejects_invalid_fields(
    run_configuration: Any,
    field: str,
    value: object,
    exception: type[Exception],
) -> None:
    """Reject invalid state values and types.

    Args:
        run_configuration: Scheduler run configuration fixture.
        field: State field to modify.
        value: Invalid field value.
        exception: Expected exception type.
    """
    state = scheduler.initial_state(run=run_configuration)
    state[field] = value

    with pytest.raises(exception):
        scheduler.validate_state(state=state, run=run_configuration)


def test_atomic_write_and_load_json(tmp_path: Path) -> None:
    """Atomically write and reload a JSON object.

    Args:
        tmp_path: Pytest temporary directory.
    """
    path = tmp_path / "state.json"
    expected = {"value": 1, "nested": {"ready": True}}

    scheduler.atomic_write_json(path=path, data=expected)

    assert scheduler.load_json(path=path, default={}) == expected
    assert not list(tmp_path.glob("state.json.tmp-*"))


def test_load_json_rejects_non_object(tmp_path: Path) -> None:
    """Reject a JSON document whose root is not an object.

    Args:
        tmp_path: Pytest temporary directory.
    """
    path = tmp_path / "state.json"
    path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(TypeError, match="Expected a JSON object"):
        scheduler.load_json(path=path, default={})


def test_discover_requires_distinct_stability_polls(
    run_configuration: Any,
) -> None:
    """Require the configured number of unchanged observations.

    Args:
        run_configuration: Scheduler run configuration fixture.
    """
    pod5_path = run_configuration.pod5_directory / "reads.pod5"
    make_old_file(pod5_path)
    state = scheduler.initial_state(run=run_configuration)
    observations: dict[str, Any] = {}

    first, first_pending = scheduler.discover_pod5_files(
        run=run_configuration,
        state=state,
        observations=observations,
        stable_seconds=120,
        stable_polls=2,
    )
    second, second_pending = scheduler.discover_pod5_files(
        run=run_configuration,
        state=state,
        observations=observations,
        stable_seconds=120,
        stable_polls=2,
    )

    assert first == []
    assert first_pending == 1
    assert len(second) == 1
    assert second_pending == 1
    assert second[0].path == pod5_path


def test_discover_resets_poll_count_after_file_change(
    run_configuration: Any,
) -> None:
    """Reset observations when a POD5 fingerprint changes.

    Args:
        run_configuration: Scheduler run configuration fixture.
    """
    pod5_path = run_configuration.pod5_directory / "reads.pod5"
    make_old_file(pod5_path, b"first")
    state = scheduler.initial_state(run=run_configuration)
    observations: dict[str, Any] = {}

    scheduler.discover_pod5_files(
        run=run_configuration,
        state=state,
        observations=observations,
        stable_seconds=0,
        stable_polls=2,
    )
    make_old_file(pod5_path, b"changed-content")
    discovered, pending = scheduler.discover_pod5_files(
        run=run_configuration,
        state=state,
        observations=observations,
        stable_seconds=0,
        stable_polls=2,
    )

    key = str(pod5_path.resolve())
    assert discovered == []
    assert pending == 1
    assert observations[key].poll_count == 1


def test_discover_skips_processed_fingerprint(
    run_configuration: Any,
) -> None:
    """Skip a POD5 file whose current fingerprint is in the ledger.

    Args:
        run_configuration: Scheduler run configuration fixture.
    """
    pod5_path = run_configuration.pod5_directory / "reads.pod5"
    make_old_file(pod5_path)
    stat_result = pod5_path.stat()
    key = str(pod5_path.resolve())
    fingerprint = f"{stat_result.st_size}:{stat_result.st_mtime_ns}"
    state = scheduler.initial_state(run=run_configuration)
    state["processed_pod5"][key] = {"fingerprint": fingerprint}

    discovered, pending = scheduler.discover_pod5_files(
        run=run_configuration,
        state=state,
        observations={},
        stable_seconds=0,
        stable_polls=1,
    )

    assert discovered == []
    assert pending == 0


def test_discover_reconsiders_changed_processed_file(
    run_configuration: Any,
) -> None:
    """Reconsider a processed path after its fingerprint changes.

    Args:
        run_configuration: Scheduler run configuration fixture.
    """
    pod5_path = run_configuration.pod5_directory / "reads.pod5"
    make_old_file(pod5_path, b"new-content")
    key = str(pod5_path.resolve())
    state = scheduler.initial_state(run=run_configuration)
    state["processed_pod5"][key] = {"fingerprint": "1:1"}

    discovered, pending = scheduler.discover_pod5_files(
        run=run_configuration,
        state=state,
        observations={},
        stable_seconds=0,
        stable_polls=1,
    )

    assert len(discovered) == 1
    assert pending == 1


def test_discover_ignores_empty_files(run_configuration: Any) -> None:
    """Do not process empty POD5 files.

    Args:
        run_configuration: Scheduler run configuration fixture.
    """
    pod5_path = run_configuration.pod5_directory / "empty.pod5"
    make_old_file(pod5_path, b"")

    discovered, pending = scheduler.discover_pod5_files(
        run=run_configuration,
        state=scheduler.initial_state(run=run_configuration),
        observations={},
        stable_seconds=0,
        stable_polls=1,
    )

    assert discovered == []
    assert pending == 1


def test_discover_removes_deleted_observations(
    run_configuration: Any,
) -> None:
    """Remove observations when an input file disappears.

    Args:
        run_configuration: Scheduler run configuration fixture.
    """
    pod5_path = run_configuration.pod5_directory / "reads.pod5"
    make_old_file(pod5_path)
    observations: dict[str, Any] = {}
    state = scheduler.initial_state(run=run_configuration)

    scheduler.discover_pod5_files(
        run=run_configuration,
        state=state,
        observations=observations,
        stable_seconds=0,
        stable_polls=2,
    )
    pod5_path.unlink()
    scheduler.discover_pod5_files(
        run=run_configuration,
        state=state,
        observations=observations,
        stable_seconds=0,
        stable_polls=2,
    )

    assert observations == {}


def test_stage_batch_creates_symlinks(
    tmp_path: Path,
    run_configuration: Any,
) -> None:
    """Stage selected POD5 files as symbolic links.

    Args:
        tmp_path: Pytest temporary directory.
        run_configuration: Scheduler run configuration fixture.
    """
    pod5_path = run_configuration.pod5_directory / "reads.pod5"
    make_old_file(pod5_path)
    stat_result = pod5_path.stat()
    candidate = scheduler.Pod5Candidate(
        path=pod5_path,
        key=str(pod5_path.resolve()),
        fingerprint=f"{stat_result.st_size}:{stat_result.st_mtime_ns}",
        size_bytes=stat_result.st_size,
        modified_time_ns=stat_result.st_mtime_ns,
    )
    batch_directory = tmp_path / "batch"
    batch_directory.mkdir()

    staged = scheduler.stage_batch(
        batch_files=[candidate],
        batch_directory=batch_directory,
    )

    links = list(staged.iterdir())
    assert len(links) == 1
    assert links[0].is_symlink()
    assert links[0].resolve() == pod5_path.resolve()


def test_find_demux_fastq_uses_exact_barcode(tmp_path: Path) -> None:
    """Do not match barcode01 files as barcode010 files.

    Args:
        tmp_path: Pytest temporary directory.
    """
    demux = tmp_path / "demux"
    barcode_one = demux / "barcode01" / "reads.fastq"
    barcode_ten = demux / "barcode010" / "reads.fastq"
    barcode_one.parent.mkdir(parents=True)
    barcode_ten.parent.mkdir(parents=True)
    barcode_one.write_text("@r\nAC\n+\n!!\n", encoding="utf-8")
    barcode_ten.write_text("@r\nGT\n+\n!!\n", encoding="utf-8")

    found = scheduler.find_demux_fastq(
        demux_directory=demux,
        barcode_name="barcode01",
    )

    assert found == [barcode_one]


def test_retain_and_collect_fastq_fragments(tmp_path: Path) -> None:
    """Retain per-batch FASTQ files and collect them cumulatively.

    Args:
        tmp_path: Pytest temporary directory.
    """
    retained_root = tmp_path / "retained"

    for batch_number in (1, 2):
        demux = tmp_path / f"demux-{batch_number}"
        source = demux / "barcode01" / "reads.fastq"
        source.parent.mkdir(parents=True)
        source.write_text(
            f"@r{batch_number}\nACGT\n+\n!!!!\n",
            encoding="utf-8",
        )
        scheduler.retain_fastq_fragments(
            demux_directory=demux,
            retained_root=retained_root,
            batch_id=f"batch-{batch_number:06d}",
            barcode_values=(1,),
        )

    retained = scheduler.cumulative_fastq_files(
        retained_root=retained_root,
        barcode_number=1,
    )

    assert len(retained) == 2
    assert all(path.is_file() for path in retained)


def test_count_fastq_bases_for_plain_and_gzip(tmp_path: Path) -> None:
    """Count bases in plain and gzip-compressed FASTQ files.

    Args:
        tmp_path: Pytest temporary directory.
    """
    plain = tmp_path / "reads.fastq"
    compressed = tmp_path / "reads.fastq.gz"
    plain.write_text(
        "@r1\nACGT\n+\n!!!!\n@r2\nAAA\n+\n!!!\n",
        encoding="utf-8",
    )
    with gzip.open(compressed, "wt", encoding="utf-8") as handle:
        handle.write("@r3\nCCCCC\n+\n!!!!!\n")

    assert scheduler.count_fastq_bases(paths=[plain]) == 7
    assert scheduler.count_fastq_bases(paths=[compressed]) == 5
    assert scheduler.count_fastq_bases(paths=[plain, compressed]) == 12


def test_safe_output_name() -> None:
    """Sanitize unsafe output filename characters."""
    assert scheduler.safe_output_name("sample 1/alpha") == "sample_1_alpha"
    assert scheduler.safe_output_name("  ") == "unnamed"


def test_completion_requested_for_local_and_global_markers(
    tmp_path: Path,
    run_configuration: Any,
) -> None:
    """Recognize local and global completion markers.

    Args:
        tmp_path: Pytest temporary directory.
        run_configuration: Scheduler run configuration fixture.
    """
    assert not scheduler.completion_requested(
        run=run_configuration,
        global_marker=None,
    )

    marker = run_configuration.pod5_directory / ".upload-complete"
    marker.touch()
    assert scheduler.completion_requested(
        run=run_configuration,
        global_marker=None,
    )

    marker.unlink()
    global_marker = tmp_path / "complete"
    global_marker.touch()
    assert scheduler.completion_requested(
        run=run_configuration,
        global_marker=str(global_marker),
    )


def test_prepare_batch_directories_removes_incomplete_outputs(
    run_configuration: Any,
) -> None:
    """Remove incomplete working and retained files before retrying.

    Args:
        run_configuration: Scheduler run configuration fixture.
    """
    batch_id = "batch-000001"
    working = run_configuration.output_directory / "working" / batch_id
    retained = (
        run_configuration.output_directory
        / "fastq"
        / "barcode01"
        / batch_id
    )
    working.mkdir(parents=True)
    retained.mkdir(parents=True)
    (working / "stale.txt").write_text("stale", encoding="utf-8")
    (retained / "stale.fastq").write_text("stale", encoding="utf-8")

    created_working, retained_root = scheduler.prepare_batch_directories(
        run=run_configuration,
        batch_id=batch_id,
    )

    assert created_working.is_dir()
    assert not (created_working / "stale.txt").exists()
    assert not (retained_root / "barcode01" / batch_id).exists()


def test_run_command_writes_binary_stdout(tmp_path: Path) -> None:
    """Write child-process standard output to a binary file.

    Args:
        tmp_path: Pytest temporary directory.
    """
    runtime = scheduler.SchedulerRuntime()
    output = tmp_path / "output.bin"

    scheduler.run_command(
        runtime=runtime,
        arguments=[
            sys.executable,
            "-c",
            "import sys; sys.stdout.buffer.write(b'BAM')",
        ],
        stdout_path=output,
    )

    assert output.read_bytes() == b"BAM"
    assert runtime.active_processes == []


def test_run_command_raises_for_nonzero_exit() -> None:
    """Raise CalledProcessError for a failed child process."""
    runtime = scheduler.SchedulerRuntime()

    with pytest.raises(subprocess.CalledProcessError):
        scheduler.run_command(
            runtime=runtime,
            arguments=[sys.executable, "-c", "raise SystemExit(7)"],
        )

    assert runtime.active_processes == []


def test_run_command_raises_when_stop_requested() -> None:
    """Raise InterruptedError after a controlled shutdown request."""
    runtime = scheduler.SchedulerRuntime()
    runtime.stop_requested = True

    with pytest.raises(InterruptedError):
        scheduler.run_command(
            runtime=runtime,
            arguments=[sys.executable, "-c", "pass"],
        )


def test_write_coverage_csv(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Sort mapped-read counts and append genome coverage.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        tmp_path: Pytest temporary directory.
    """
    output = tmp_path / "coverage.csv"

    def fake_run(*_args: object, **_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(
            stdout=(
                "#rname\tstartpos\tendpos\tnumreads\tcovbases\tcoverage"
                "\tmeandepth\tmeanbaseq\tmeanmapq\n"
                "gene-b\t1\t100\t2\t50\t50\t2\t40\t60\n"
                "gene-a\t1\t100\t5\t80\t80\t5\t40\t60\n"
                "gene-c\t1\t100\t0\t0\t0\t0\t0\t0\n"
            )
        )

    monkeypatch.setattr(scheduler.subprocess, "run", fake_run)

    scheduler.write_coverage_csv(
        samtools="samtools",
        bam_path=tmp_path / "reads.bam",
        output_path=output,
        genome_size=100,
        total_bases=250,
    )

    assert output.read_text(encoding="utf-8").splitlines() == [
        "gene_name,number_of_reads_mapped",
        "gene-a,5",
        "gene-b,2",
        "genome_coverage,2.500000X",
    ]


def test_process_batch_checkpoints_only_after_success(
    monkeypatch: pytest.MonkeyPatch,
    run_configuration: Any,
    scheduler_args: SimpleNamespace,
) -> None:
    """Checkpoint a processed POD5 only after every processing stage succeeds.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        run_configuration: Scheduler run configuration fixture.
        scheduler_args: Scheduler argument fixture.
    """
    pod5_path = run_configuration.pod5_directory / "reads.pod5"
    make_old_file(pod5_path)
    stat_result = pod5_path.stat()
    candidate = scheduler.Pod5Candidate(
        path=pod5_path,
        key=str(pod5_path.resolve()),
        fingerprint=f"{stat_result.st_size}:{stat_result.st_mtime_ns}",
        size_bytes=stat_result.st_size,
        modified_time_ns=stat_result.st_mtime_ns,
    )
    state = scheduler.initial_state(run=run_configuration)

    def fake_run_command(
        *,
        runtime: Any,
        arguments: Sequence[str | Path],
        stdout_path: Path | None = None,
        cwd: Path | None = None,
    ) -> None:
        del runtime, cwd
        command = [str(item) for item in arguments]
        if "basecaller" in command:
            assert stdout_path is not None
            stdout_path.write_bytes(b"BAM")
        elif "demux" in command:
            output_index = command.index("--output-dir") + 1
            fastq = Path(command[output_index]) / "barcode01" / "reads.fastq"
            fastq.parent.mkdir(parents=True)
            fastq.write_text("@r\nACGT\n+\n!!!!\n", encoding="utf-8")

    def fake_process_mapping(**_kwargs: object) -> list[str]:
        result = run_configuration.output_directory / "results" / "result.csv"
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text("gene_name,number_of_reads_mapped\n", encoding="utf-8")
        return [str(result)]

    monkeypatch.setattr(scheduler, "run_command", fake_run_command)
    monkeypatch.setattr(scheduler, "process_mapping", fake_process_mapping)

    scheduler.process_batch(
        runtime=scheduler.SchedulerRuntime(),
        run=run_configuration,
        state=state,
        metadata={},
        batch_files=[candidate],
        args=scheduler_args,
    )

    assert candidate.key in state["processed_pod5"]
    assert state["next_batch_number"] == 2
    assert state["next_iteration"] == 2
    assert len(state["batches"]) == 1
    assert (run_configuration.output_directory / "state.json").is_file()
    assert not (
        run_configuration.output_directory / "working" / "batch-000001"
    ).exists()


def test_process_batch_does_not_checkpoint_after_mapping_failure(
    monkeypatch: pytest.MonkeyPatch,
    run_configuration: Any,
    scheduler_args: SimpleNamespace,
) -> None:
    """Leave state counters unchanged when cumulative mapping fails.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
        run_configuration: Scheduler run configuration fixture.
        scheduler_args: Scheduler argument fixture.
    """
    pod5_path = run_configuration.pod5_directory / "reads.pod5"
    make_old_file(pod5_path)
    stat_result = pod5_path.stat()
    candidate = scheduler.Pod5Candidate(
        path=pod5_path,
        key=str(pod5_path.resolve()),
        fingerprint=f"{stat_result.st_size}:{stat_result.st_mtime_ns}",
        size_bytes=stat_result.st_size,
        modified_time_ns=stat_result.st_mtime_ns,
    )
    state = scheduler.initial_state(run=run_configuration)

    def fake_run_command(
        *,
        runtime: Any,
        arguments: Sequence[str | Path],
        stdout_path: Path | None = None,
        cwd: Path | None = None,
    ) -> None:
        del runtime, cwd
        command = [str(item) for item in arguments]
        if "basecaller" in command:
            assert stdout_path is not None
            stdout_path.write_bytes(b"BAM")
        elif "demux" in command:
            output_index = command.index("--output-dir") + 1
            fastq = Path(command[output_index]) / "barcode01" / "reads.fastq"
            fastq.parent.mkdir(parents=True)
            fastq.write_text("@r\nACGT\n+\n!!!!\n", encoding="utf-8")

    def fail_mapping(**_kwargs: object) -> list[str]:
        raise RuntimeError("mapping failed")

    monkeypatch.setattr(scheduler, "run_command", fake_run_command)
    monkeypatch.setattr(scheduler, "process_mapping", fail_mapping)

    with pytest.raises(RuntimeError, match="mapping failed"):
        scheduler.process_batch(
            runtime=scheduler.SchedulerRuntime(),
            run=run_configuration,
            state=state,
            metadata={},
            batch_files=[candidate],
            args=scheduler_args,
        )

    assert candidate.key not in state["processed_pod5"]
    assert state["next_batch_number"] == 1
    assert state["next_iteration"] == 1
    assert state["batches"] == []


def test_finalise_runs_writes_completed_status(
    run_configuration: Any,
) -> None:
    """Write final completed state and status documents.

    Args:
        run_configuration: Scheduler run configuration fixture.
    """
    run_configuration.output_directory.mkdir(parents=True)
    state = scheduler.initial_state(run=run_configuration)

    scheduler.finalise_runs(
        runs=[run_configuration],
        states={run_configuration.run_id: state},
        exit_reason="once-complete",
    )

    status = json.loads(
        (run_configuration.output_directory / "status.json").read_text(
            encoding="utf-8"
        )
    )
    assert status["status"] == "completed"
    assert status["reason"] == "once-complete"
    assert status["processed_pod5_count"] == 0
    assert status["batch_count"] == 0


def test_parse_arguments_supports_test_argv() -> None:
    """Parse supplied arguments without reading process arguments."""
    arguments = scheduler.parse_arguments(
        [
            "runs.csv",
            "metadata.csv",
            "--poll-seconds",
            "5",
            "--stable-polls",
            "3",
            "--once",
        ]
    )

    assert arguments.csv_file_path == Path("runs.csv")
    assert arguments.metadata_csv_path == Path("metadata.csv")
    assert arguments.poll_seconds == 5
    assert arguments.stable_polls == 3
    assert arguments.once is True
