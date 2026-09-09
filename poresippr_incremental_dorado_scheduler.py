#!/usr/bin/env python3
"""Run incremental Dorado basecalling and target mapping for PoreSippR.

The scheduler watches one or more POD5 input directories described by an input
CSV. Stable POD5 files are processed exactly once in bounded batches. Per-batch
FASTQ files are retained so each mapping iteration includes all reads produced
for the run so far.

Required input CSV columns:
    reference,pod5_dir,output_dir,barcode,barcode_values

Optional input CSV columns:
    run_id

Required metadata CSV columns:
    Barcode,SEQID,OLNID

The scheduler exits after all uploads are marked complete, after an idle
period, after its wall-clock limit, after a one-time processing pass, or after
receiving SIGINT or SIGTERM.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import logging
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import FrameType
from typing import Any, BinaryIO

LOGGER = logging.getLogger("poresippr.scheduler")

DEFAULT_MODEL_DIRECTORY = (
    "/opt/ont/models/"
    "dna_r10.4.1_e8.2_400bps_fast@v5.2.0"
)
DEFAULT_BENCHMARK_FILE = (
    "/opt/ont/benchmarks/dorado-batch-size-benchmarks.json"
)
FASTQ_SUFFIXES = (".fastq", ".fastq.gz")
STATE_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class RunConfiguration:
    """Configuration for one row in the scheduler input CSV.

    Attributes:
        run_id: Unique identifier for this run definition.
        reference: Target reference FASTA passed to minimap2.
        pod5_directory: Directory watched for incoming POD5 files.
        output_directory: Durable output and checkpoint directory.
        barcode_kit: Dorado barcode kit name.
        barcode_values: Barcode numbers included in downstream mapping.
    """

    run_id: str
    reference: Path
    pod5_directory: Path
    output_directory: Path
    barcode_kit: str
    barcode_values: tuple[int, ...]


@dataclass(frozen=True)
class Pod5Candidate:
    """A stable POD5 file eligible for a processing batch.

    Attributes:
        path: Absolute path to the POD5 file.
        key: Durable ledger key for the file.
        fingerprint: Size and modification-time fingerprint.
        size_bytes: File size in bytes.
        modified_time_ns: Modification time in nanoseconds.
    """

    path: Path
    key: str
    fingerprint: str
    size_bytes: int
    modified_time_ns: int


@dataclass
class FileObservation:
    """In-memory stability observation for an unprocessed POD5 file.

    Attributes:
        fingerprint: Last observed file fingerprint.
        poll_count: Consecutive polls with the same fingerprint.
    """

    fingerprint: str
    poll_count: int


class SchedulerRuntime:
    """Track shutdown state and currently active child processes."""

    def __init__(self) -> None:
        """Initialise an active scheduler runtime."""
        self.stop_requested = False
        self.active_processes: list[subprocess.Popen[Any]] = []

    def request_stop(
        self,
        signum: int,
        _frame: FrameType | None,
    ) -> None:
        """Request shutdown and terminate active child processes.

        Args:
            signum: Signal number delivered by the operating system.
            _frame: Python frame supplied to signal handlers. It is unused.
        """
        self.stop_requested = True
        LOGGER.warning("Received signal %s; requesting shutdown", signum)
        self.terminate_active_processes()

    def register_process(self, process: subprocess.Popen[Any]) -> None:
        """Register a child process for signal-aware cleanup.

        Args:
            process: Running subprocess to track.
        """
        self.active_processes.append(process)

    def unregister_process(self, process: subprocess.Popen[Any]) -> None:
        """Stop tracking a completed child process.

        Args:
            process: Previously registered subprocess.
        """
        if process in self.active_processes:
            self.active_processes.remove(process)

    def terminate_active_processes(self) -> None:
        """Terminate every tracked child process that is still running."""
        for process in list(self.active_processes):
            if process.poll() is None:
                LOGGER.warning(
                    "Terminating active subprocess with PID %s",
                    process.pid,
                )
                process.terminate()


def utc_now() -> str:
    """Return the current UTC time in ISO 8601 format.

    Returns:
        Current UTC timestamp without fractional seconds.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def atomic_write_json(*, path: Path, data: Mapping[str, Any]) -> None:
    """Write a JSON document atomically.

    Args:
        path: Destination JSON path.
        data: JSON-serialisable mapping to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp-{uuid.uuid4().hex}")

    try:
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_json(
    *,
    path: Path,
    default: dict[str, Any],
) -> dict[str, Any]:
    """Load a JSON object or return a default object.

    Args:
        path: JSON file to read.
        default: Value returned if ``path`` does not exist.

    Returns:
        Parsed JSON object or ``default``.

    Raises:
        json.JSONDecodeError: If the file does not contain valid JSON.
        TypeError: If the JSON document is not an object.
    """
    if not path.is_file():
        return default

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise TypeError(
            f"Expected a JSON object in {path} but found {type(data).__name__}"
        )
    return data


def run_command(
    *,
    runtime: SchedulerRuntime,
    arguments: Sequence[str | Path],
    stdout_path: Path | None = None,
    cwd: Path | None = None,
) -> None:
    """Run a command without a shell.

    Args:
        runtime: Scheduler child-process tracker.
        arguments: Command and arguments to execute.
        stdout_path: Optional binary file receiving standard output.
        cwd: Optional child-process working directory.

    Raises:
        InterruptedError: If scheduler shutdown interrupts the command.
        subprocess.CalledProcessError: If the command returns a nonzero
            exit status.
    """
    command = [str(item) for item in arguments]
    LOGGER.info("Running command: %s", " ".join(command))

    output_handle: BinaryIO | None = None
    process: subprocess.Popen[Any] | None = None

    try:
        if stdout_path is not None:
            stdout_path.parent.mkdir(parents=True, exist_ok=True)
            output_handle = stdout_path.open("wb")

        process = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd else None,
            stdout=output_handle,
        )
        runtime.register_process(process)
        return_code = process.wait()

        if runtime.stop_requested:
            raise InterruptedError("Command interrupted by scheduler shutdown")

        if return_code != 0:
            raise subprocess.CalledProcessError(
                return_code,
                command,
            )
    finally:
        if process is not None:
            runtime.unregister_process(process)
        if output_handle is not None:
            output_handle.close()


def run_mapping_pipeline(
    *,
    runtime: SchedulerRuntime,
    minimap2: str,
    samtools: str,
    reference: Path,
    fastq_files: Sequence[Path],
    output_bam: Path,
    threads: int,
) -> None:
    """Map retained FASTQ files and create a sorted, indexed BAM.

    Args:
        runtime: Scheduler child-process tracker.
        minimap2: Minimap2 executable or path.
        samtools: Samtools executable or path.
        reference: Mapping reference FASTA.
        fastq_files: Cumulative FASTQ fragments for one barcode.
        output_bam: Final sorted BAM path.
        threads: Number of samtools sorting threads.

    Raises:
        InterruptedError: If scheduler shutdown interrupts the pipeline.
        subprocess.CalledProcessError: If minimap2 or samtools exits
            unsuccessfully.
        RuntimeError: If the pipeline creates an empty BAM.
    """
    output_bam.parent.mkdir(parents=True, exist_ok=True)
    temporary_bam = output_bam.with_suffix(".tmp.bam")
    temporary_bam.unlink(missing_ok=True)

    minimap_command = [
        minimap2,
        "-ax",
        "map-ont",
        str(reference),
        *(str(path) for path in fastq_files),
    ]
    sort_command = [
        samtools,
        "sort",
        "-@",
        str(threads),
        "-o",
        str(temporary_bam),
        "-",
    ]

    LOGGER.info(
        "Running mapping pipeline for %d FASTQ fragments",
        len(fastq_files),
    )

    minimap_process = subprocess.Popen(
        minimap_command,
        stdout=subprocess.PIPE,
    )
    runtime.register_process(minimap_process)

    # Initialise process state before starting the mapping pipeline so cleanup
    # and exit-status validation remain safe when process creation fails.
    sort_process: subprocess.Popen[Any] | None = None
    sort_return_code: int | None = None
    minimap_return_code: int | None = None
    pipeline_finished = False

    try:
        sort_process = subprocess.Popen(
            sort_command,
            stdin=minimap_process.stdout,
        )
        runtime.register_process(sort_process)

        if minimap_process.stdout is not None:
            minimap_process.stdout.close()

        sort_return_code = sort_process.wait()
        minimap_return_code = minimap_process.wait()
        pipeline_finished = True
    finally:
        if minimap_process.stdout is not None:
            minimap_process.stdout.close()

        if sort_process is not None and sort_process.poll() is None:
            sort_process.terminate()
            sort_process.wait()

        if minimap_process.poll() is None:
            minimap_process.terminate()
            minimap_process.wait()

        runtime.unregister_process(minimap_process)

        if sort_process is not None:
            runtime.unregister_process(sort_process)

        if not pipeline_finished:
            temporary_bam.unlink(missing_ok=True)

    if runtime.stop_requested:
        temporary_bam.unlink(missing_ok=True)
        raise InterruptedError(
            "Mapping pipeline interrupted by scheduler shutdown"
        )

    if minimap_return_code is None or sort_return_code is None:
        temporary_bam.unlink(missing_ok=True)
        raise RuntimeError(
            "Mapping pipeline did not report both process exit statuses"
        )

    if minimap_return_code != 0:
        temporary_bam.unlink(missing_ok=True)
        raise subprocess.CalledProcessError(
            minimap_return_code,
            minimap_command,
        )

    if sort_return_code != 0:
        temporary_bam.unlink(missing_ok=True)
        raise subprocess.CalledProcessError(
            sort_return_code,
            sort_command,
        )

    if not temporary_bam.is_file() or temporary_bam.stat().st_size == 0:
        raise RuntimeError(
            f"Mapping pipeline produced an empty BAM: {temporary_bam}"
        )

    os.replace(temporary_bam, output_bam)

    output_index = Path(f"{output_bam}.bai")
    output_index.unlink(missing_ok=True)

    run_command(
        runtime=runtime,
        arguments=[
            samtools,
            "index",
            "-@",
            str(threads),
            output_bam,
        ],
    )


def parse_barcode_values(*, value: str) -> tuple[int, ...]:
    """Parse comma-separated barcode numbers.

    Args:
        value: Comma-separated barcode string.

    Returns:
        Parsed barcode numbers in input order.

    Raises:
        ValueError: If no barcodes are supplied or a value is invalid.
    """
    barcodes = tuple(
        int(item.strip().replace('"', ""))
        for item in value.split(",")
        if item.strip().replace('"', "")
    )

    if not barcodes:
        raise ValueError("barcode_values contains no barcode numbers")
    if len(barcodes) != len(set(barcodes)):
        raise ValueError("barcode_values contains duplicate barcode numbers")
    return barcodes


def load_metadata(*, path: Path) -> dict[int, dict[str, str]]:
    """Load barcode metadata from CSV.

    Args:
        path: Metadata CSV containing Barcode, SEQID, and OLNID.

    Returns:
        Mapping from barcode number to metadata fields.

    Raises:
        ValueError: If columns are missing or barcodes are duplicated.
    """
    mapping: dict[int, dict[str, str]] = {}

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"Barcode", "SEQID", "OLNID"}
        missing = required.difference(reader.fieldnames or [])

        if missing:
            columns = ", ".join(sorted(missing))
            raise ValueError(f"Metadata CSV is missing columns: {columns}")

        for row in reader:
            barcode = int(row["Barcode"])
            if barcode in mapping:
                raise ValueError(
                    f"Metadata CSV contains duplicate barcode {barcode}"
                )

            mapping[barcode] = {
                "seqid": row["SEQID"].strip(),
                "olnid": row["OLNID"].strip(),
            }

    return mapping


def load_runs(*, path: Path) -> list[RunConfiguration]:
    """Load and validate run definitions from CSV.

    Args:
        path: Input CSV containing run configuration rows.

    Returns:
        Validated run configurations.

    Raises:
        ValueError: If required columns are missing, no rows are supplied, or
            run identifiers are duplicated.
    """
    runs: list[RunConfiguration] = []

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "reference",
            "pod5_dir",
            "output_dir",
            "barcode",
            "barcode_values",
        }
        missing = required.difference(reader.fieldnames or [])

        if missing:
            columns = ", ".join(sorted(missing))
            raise ValueError(f"Input CSV is missing columns: {columns}")

        for index, row in enumerate(reader, start=1):
            runs.append(
                RunConfiguration(
                    run_id=(
                        row.get("run_id", "").strip()
                        or f"run-{index:03d}"
                    ),
                    reference=Path(row["reference"]).resolve(),
                    pod5_directory=Path(row["pod5_dir"]).resolve(),
                    output_directory=Path(row["output_dir"]).resolve(),
                    barcode_kit=row["barcode"].strip(),
                    barcode_values=parse_barcode_values(
                        value=row["barcode_values"]
                    ),
                )
            )

    if not runs:
        raise ValueError("Input CSV contains no run definitions")

    run_ids = [run.run_id for run in runs]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("Input CSV run_id values must be unique")
    return runs


def initial_state(*, run: RunConfiguration) -> dict[str, Any]:
    """Create an empty durable processing state.

    Args:
        run: Run configuration associated with the state.

    Returns:
        Initial scheduler state object.
    """
    timestamp = utc_now()
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "run_id": run.run_id,
        "created_at": timestamp,
        "updated_at": timestamp,
        "next_batch_number": 1,
        "next_iteration": 1,
        "processed_pod5": {},
        "batches": [],
    }


def validate_state(
    *,
    state: dict[str, Any],
    run: RunConfiguration,
) -> None:
    """Validate a loaded state file against its run configuration.

    Args:
        state: Loaded durable scheduler state.
        run: Run configuration expected to own the state.

    Raises:
        TypeError: If a required state field has the wrong type.
        ValueError: If the state schema, run identifier, or counter value is
            invalid.
    """
    if state.get("schema_version") != STATE_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported state schema in {run.output_directory}: "
            f"{state.get('schema_version')}"
        )
    if state.get("run_id") != run.run_id:
        raise ValueError(
            f"State run_id {state.get('run_id')!r} does not match "
            f"{run.run_id!r}"
        )

    # Validate that required fields exist and have the expected types.
    required_fields = {
        "next_batch_number": int,
        "next_iteration": int,
        "processed_pod5": dict,
        "batches": list,
    }

    for field, expected_type in required_fields.items():
        value = state.get(field)

        if not isinstance(value, expected_type):
            raise TypeError(
                f"State field {field!r} must be "
                f"{expected_type.__name__}, not "
                f"{type(value).__name__}"
            )

    # Validate that numeric fields are positive.
    if state["next_batch_number"] < 1:
        raise ValueError("State next_batch_number must be positive")

    if state["next_iteration"] < 1:
        raise ValueError("State next_iteration must be positive")


def discover_pod5_files(
    *,
    run: RunConfiguration,
    state: Mapping[str, Any],
    observations: dict[str, FileObservation],
    stable_seconds: int,
    stable_polls: int,
) -> tuple[list[Pod5Candidate], int]:
    """Discover stable and pending unprocessed POD5 files.

    Args:
        run: Run whose POD5 directory will be scanned.
        state: Durable processing ledger.
        observations: In-memory file stability observations.
        stable_seconds: Required age since the last modification.
        stable_polls: Required consecutive unchanged polls.

    Returns:
        A tuple containing stable candidates and the total number of pending
        unprocessed POD5 files.
    """
    discovered: list[Pod5Candidate] = []
    seen: set[str] = set()
    pending_count = 0

    if not run.pod5_directory.is_dir():
        return discovered, pending_count

    processed_files = state.get("processed_pod5", {})
    if not isinstance(processed_files, dict):
        raise TypeError(
            "processed_pod5 must be a JSON object, not "
            f"{type(processed_files).__name__}"
        )

    for path in sorted(run.pod5_directory.rglob("*.pod5")):
        try:
            stat_result = path.stat()
        except FileNotFoundError:
            continue

        key = str(path.resolve())
        seen.add(key)
        fingerprint = (
            f"{stat_result.st_size}:{stat_result.st_mtime_ns}"
        )
        processed = processed_files.get(key)

        if (
            isinstance(processed, dict)
            and processed.get("fingerprint") == fingerprint
        ):
            continue

        pending_count += 1
        observation = observations.get(key)

        if observation and observation.fingerprint == fingerprint:
            observation.poll_count += 1
        else:
            observation = FileObservation(
                fingerprint=fingerprint,
                poll_count=1,
            )
            observations[key] = observation

        age_seconds = time.time() - stat_result.st_mtime
        is_stable = (
            observation.poll_count >= stable_polls
            and age_seconds >= stable_seconds
            and stat_result.st_size > 0
        )

        if is_stable:
            discovered.append(
                Pod5Candidate(
                    path=path,
                    key=key,
                    fingerprint=fingerprint,
                    size_bytes=stat_result.st_size,
                    modified_time_ns=stat_result.st_mtime_ns,
                )
            )

    for key in list(observations):
        if key not in seen:
            observations.pop(key, None)

    return discovered, pending_count


def stage_batch(
    *,
    batch_files: Sequence[Pod5Candidate],
    batch_directory: Path,
) -> Path:
    """Stage only the current POD5 batch using symbolic links.

    Args:
        batch_files: Stable POD5 files selected for the batch.
        batch_directory: Batch-specific working directory.

    Returns:
        Directory containing staged POD5 symbolic links.
    """
    input_directory = batch_directory / "pod5"
    input_directory.mkdir(parents=True, exist_ok=False)

    for index, candidate in enumerate(batch_files, start=1):
        link_name = f"{index:04d}-{candidate.path.name}"
        os.symlink(candidate.path, input_directory / link_name)

    return input_directory


def is_fastq(path: Path) -> bool:
    """Return whether a path has a supported FASTQ suffix.

    Args:
        path: Candidate file path.

    Returns:
        ``True`` for ``.fastq`` and ``.fastq.gz`` files.
    """
    return path.name.endswith(FASTQ_SUFFIXES)


def find_demux_fastq(
    *,
    demux_directory: Path,
    barcode_name: str,
) -> list[Path]:
    """Find FASTQ files for one barcode in a Dorado demux tree.

    Args:
        demux_directory: Root of the Dorado demultiplexing output.
        barcode_name: Barcode directory name, such as ``barcode01``.

    Returns:
        Sorted FASTQ paths associated with the requested barcode.
    """
    files: list[Path] = []
    barcode_pattern = re.compile(
        rf"(^|[^A-Za-z0-9]){re.escape(barcode_name)}([^0-9]|$)"
    )

    for path in demux_directory.rglob("*"):
        if not path.is_file() or not is_fastq(path):
            continue
        if barcode_name in path.parts or barcode_pattern.search(path.name):
            files.append(path)

    return sorted(files)


def retain_fastq_fragments(
    *,
    demux_directory: Path,
    retained_root: Path,
    batch_id: str,
    barcode_values: Sequence[int],
) -> dict[int, list[Path]]:
    """Move demultiplexed FASTQ files into durable batch directories.

    Args:
        demux_directory: Dorado demultiplexing output directory.
        retained_root: Durable root for retained FASTQ fragments.
        batch_id: Identifier assigned to the current batch.
        barcode_values: Configured barcode numbers.

    Returns:
        Mapping from barcode number to retained FASTQ paths.
    """
    retained: dict[int, list[Path]] = {}

    for barcode_number in barcode_values:
        barcode_name = f"barcode{barcode_number:02d}"
        source_files = find_demux_fastq(
            demux_directory=demux_directory,
            barcode_name=barcode_name,
        )
        destination = retained_root / barcode_name / batch_id
        destination.mkdir(parents=True, exist_ok=True)
        retained[barcode_number] = []

        for index, source in enumerate(source_files, start=1):
            destination_name = f"{index:04d}-{source.name}"
            target = destination / destination_name
            shutil.move(source, target)
            retained[barcode_number].append(target)

    return retained


def cumulative_fastq_files(
    *,
    retained_root: Path,
    barcode_number: int,
) -> list[Path]:
    """Return all retained FASTQ fragments for one barcode.

    Args:
        retained_root: Durable root for retained FASTQ fragments.
        barcode_number: Barcode number to retrieve.

    Returns:
        Sorted cumulative FASTQ fragment paths.
    """
    barcode_root = retained_root / f"barcode{barcode_number:02d}"
    if not barcode_root.is_dir():
        return []

    return sorted(
        path
        for path in barcode_root.rglob("*")
        if path.is_file() and is_fastq(path)
    )


def count_fastq_handle_bases(*, handle: Iterable[str]) -> int:
    """Count sequence bases from an open FASTQ text stream.

    FASTQ records contain four lines. The second line in each record contains
    the nucleotide sequence.

    Args:
        handle: Open text stream containing FASTQ records.

    Returns:
        Number of bases in all FASTQ sequence lines.
    """
    return sum(
        len(line.rstrip("\r\n"))
        for line_number, line in enumerate(handle)
        if line_number % 4 == 1
    )


def count_fastq_bases(*, paths: Iterable[Path]) -> int:
    """Count sequence bases in FASTQ files.

    Args:
        paths: Uncompressed or gzip-compressed FASTQ paths.

    Returns:
        Total number of bases in all sequence lines.
    """
    total_bases = 0

    for path in paths:
        if path.name.endswith(".gz"):
            with gzip.open(
                path,
                mode="rt",
                encoding="utf-8",
                errors="replace",
            ) as handle:
                total_bases += count_fastq_handle_bases(
                    handle=handle,
                )
        else:
            with path.open(
                mode="r",
                encoding="utf-8",
                errors="replace",
            ) as handle:
                total_bases += count_fastq_handle_bases(
                    handle=handle,
                )

    return total_bases


def write_coverage_csv(
    *,
    samtools: str,
    bam_path: Path,
    output_path: Path,
    genome_size: int,
    total_bases: int,
) -> None:
    """Create a PoreSippR iteration CSV from samtools coverage.

    Args:
        samtools: Samtools executable or path.
        bam_path: Sorted mapping BAM.
        output_path: Destination iteration CSV.
        genome_size: Genome size used for the legacy coverage estimate.
        total_bases: Cumulative sequenced bases for the barcode.
    """
    result = subprocess.run(
        [samtools, "coverage", str(bam_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    rows: list[tuple[str, int]] = []
    reader = csv.DictReader(
        result.stdout.splitlines(),
        delimiter="\t",
    )

    for row in reader:
        reference_name = row.get("#rname") or row.get("rname")
        read_count = int(row.get("numreads", "0"))

        if reference_name and read_count > 0:
            rows.append((reference_name, read_count))

    rows.sort(key=lambda item: (-item[1], item[0]))
    temporary = output_path.with_suffix(".tmp.csv")

    try:
        with temporary.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.writer(handle)
            writer.writerow(
                ["gene_name", "number_of_reads_mapped"]
            )
            writer.writerows(rows)

            if genome_size > 0:
                coverage = total_bases / genome_size
                writer.writerow(
                    ["genome_coverage", f"{coverage:.6f}X"]
                )

        os.replace(temporary, output_path)
    finally:
        temporary.unlink(missing_ok=True)


def safe_output_name(value: str) -> str:
    """Return a filesystem-safe output stem.

    Args:
        value: Metadata value used to name an output.

    Returns:
        Sanitised filename stem.
    """
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned or "unnamed"


def process_mapping(
    *,
    runtime: SchedulerRuntime,
    run: RunConfiguration,
    metadata: Mapping[int, Mapping[str, str]],
    retained_root: Path,
    iteration: int,
    args: argparse.Namespace,
) -> list[str]:
    """Map cumulative FASTQ fragments for every configured barcode.

    Args:
        runtime: Scheduler child-process tracker.
        run: Current run configuration.
        metadata: Barcode metadata mapping.
        retained_root: Durable retained FASTQ root.
        iteration: Iteration number used in result filenames.
        args: Parsed scheduler arguments.

    Returns:
        Paths to generated iteration CSV files.

    Raises:
        InterruptedError: If scheduler shutdown interrupts mapping.
        subprocess.CalledProcessError: If minimap2 or samtools exits
            unsuccessfully.
        RuntimeError: If the mapping pipeline produces an empty BAM.
    """
    mapping_directory = run.output_directory / "mapping"
    results_directory = run.output_directory / "results"
    mapping_directory.mkdir(parents=True, exist_ok=True)
    results_directory.mkdir(parents=True, exist_ok=True)
    outputs: list[str] = []

    for barcode_number in run.barcode_values:
        if runtime.stop_requested:
            raise InterruptedError("Shutdown requested")

        fastq_files = cumulative_fastq_files(
            retained_root=retained_root,
            barcode_number=barcode_number,
        )
        if not fastq_files:
            LOGGER.info(
                "No retained reads for barcode%02d",
                barcode_number,
            )
            continue

        metadata_entry = metadata.get(
            barcode_number,
            {
                "seqid": f"barcode{barcode_number:02d}",
                "olnid": f"OLN{barcode_number:02d}",
            },
        )
        seqid = safe_output_name(metadata_entry["seqid"])
        bam_path = mapping_directory / f"{seqid}.sorted.bam"

        run_mapping_pipeline(
            runtime=runtime,
            minimap2=args.minimap2,
            samtools=args.samtools,
            reference=run.reference,
            fastq_files=fastq_files,
            output_bam=bam_path,
            threads=args.mapping_threads,
        )

        total_bases = count_fastq_bases(paths=fastq_files)
        csv_path = (
            results_directory / f"{seqid}_iteration{iteration}.csv"
        )
        write_coverage_csv(
            samtools=args.samtools,
            bam_path=bam_path,
            output_path=csv_path,
            genome_size=args.genome_size,
            total_bases=total_bases,
        )
        outputs.append(str(csv_path))

        if not args.keep_mapping_bam:
            bam_path.unlink(missing_ok=True)
            Path(f"{bam_path}.bai").unlink(missing_ok=True)

    return outputs


def prepare_batch_directories(
    *,
    run: RunConfiguration,
    batch_id: str,
) -> tuple[Path, Path]:
    """Prepare clean working and retained-FASTQ paths for a batch retry.

    Args:
        run: Current run configuration.
        batch_id: Batch identifier being prepared.

    Returns:
        A tuple containing the working directory and retained FASTQ root.
    """
    working_directory = run.output_directory / "working" / batch_id
    retained_root = run.output_directory / "fastq"

    if working_directory.exists():
        LOGGER.warning(
            "Removing incomplete prior working directory: %s",
            working_directory,
        )
        shutil.rmtree(working_directory)

    for barcode_number in run.barcode_values:
        retained_batch = (
            retained_root
            / f"barcode{barcode_number:02d}"
            / batch_id
        )
        if retained_batch.exists():
            LOGGER.warning(
                "Removing incomplete retained FASTQ directory: %s",
                retained_batch,
            )
            shutil.rmtree(retained_batch)

    working_directory.mkdir(parents=True, exist_ok=False)
    return working_directory, retained_root


def process_batch(
    *,
    runtime: SchedulerRuntime,
    run: RunConfiguration,
    state: dict[str, Any],
    metadata: Mapping[int, Mapping[str, str]],
    batch_files: Sequence[Pod5Candidate],
    args: argparse.Namespace,
) -> None:
    """Basecall, demultiplex, map, and checkpoint one POD5 batch.

    Args:
        runtime: Scheduler child-process tracker.
        run: Current run configuration.
        state: Mutable durable scheduler state.
        metadata: Barcode metadata mapping.
        batch_files: Stable POD5 files selected for this batch.
        args: Parsed scheduler arguments.

    Raises:
        InterruptedError: If scheduler shutdown interrupts processing.
        subprocess.CalledProcessError: If Dorado, minimap2, or samtools
            exits unsuccessfully.
        RuntimeError: If basecalling, demultiplexing, or mapping produces
            invalid or empty output.
    """
    batch_number = int(state["next_batch_number"])
    iteration = int(state["next_iteration"])
    batch_id = f"batch-{batch_number:06d}"
    working_directory, retained_root = prepare_batch_directories(
        run=run,
        batch_id=batch_id,
    )
    input_directory = stage_batch(
        batch_files=batch_files,
        batch_directory=working_directory,
    )
    batch_bam = working_directory / "basecalls.bam"
    demux_directory = working_directory / "demux"
    demux_directory.mkdir()
    started_at = utc_now()

    LOGGER.info(
        "Processing %s with %d POD5 files",
        batch_id,
        len(batch_files),
    )

    basecaller_command = [
        args.dorado,
        "basecaller",
        args.model,
        str(input_directory),
        "--recursive",
        "--device",
        args.device,
        "--kit-name",
        run.barcode_kit,
    ]

    if args.benchmark_file:
        benchmark_path = Path(args.benchmark_file)
        if benchmark_path.is_file():
            basecaller_command.extend(
                ["--batchsize-benchmarks-file", args.benchmark_file]
            )
        else:
            LOGGER.warning(
                "Dorado benchmark file not found; continuing without it: "
                "%s",
                args.benchmark_file,
            )

    if args.refresh_benchmarks:
        basecaller_command.extend(
            ["--run-batchsize-benchmarks", "continue"]
        )

    run_command(
        runtime=runtime,
        arguments=basecaller_command,
        stdout_path=batch_bam,
    )

    if not batch_bam.is_file() or batch_bam.stat().st_size == 0:
        raise RuntimeError(
            f"Dorado produced an empty BAM for {batch_id}"
        )

    run_command(
        runtime=runtime,
        arguments=[
            args.dorado,
            "demux",
            "--emit-fastq",
            "--no-classify",
            "--output-dir",
            demux_directory,
            batch_bam,
        ],
    )

    retained = retain_fastq_fragments(
        demux_directory=demux_directory,
        retained_root=retained_root,
        batch_id=batch_id,
        barcode_values=run.barcode_values,
    )
    retained_count = sum(len(paths) for paths in retained.values())

    if retained_count == 0:
        raise RuntimeError(
            "Dorado demux produced no configured-barcode FASTQ files"
        )

    result_files = process_mapping(
        runtime=runtime,
        run=run,
        metadata=metadata,
        retained_root=retained_root,
        iteration=iteration,
        args=args,
    )
    finished_at = utc_now()
    batch_record = {
        "batch_id": batch_id,
        "iteration": iteration,
        "started_at": started_at,
        "finished_at": finished_at,
        "pod5_count": len(batch_files),
        "pod5_bytes": sum(item.size_bytes for item in batch_files),
        "retained_fastq_count": retained_count,
        "result_files": result_files,
    }

    processed_files = state["processed_pod5"]
    for candidate in batch_files:
        processed_files[candidate.key] = {
            "fingerprint": candidate.fingerprint,
            "bytes": candidate.size_bytes,
            "mtime_ns": candidate.modified_time_ns,
            "processed_at": finished_at,
            "batch_id": batch_id,
        }

    state["batches"].append(batch_record)
    state["next_batch_number"] = batch_number + 1
    state["next_iteration"] = iteration + 1
    state["updated_at"] = finished_at

    atomic_write_json(
        path=run.output_directory / "state.json",
        data=state,
    )
    atomic_write_json(
        path=run.output_directory / "status.json",
        data={
            "status": "running",
            "run_id": run.run_id,
            "last_batch": batch_record,
            "updated_at": finished_at,
        },
    )

    if not args.keep_batch_work:
        shutil.rmtree(working_directory)

    LOGGER.info("Completed %s", batch_id)


def completion_requested(
    *,
    run: RunConfiguration,
    global_marker: str | None,
) -> bool:
    """Return whether an upload-completion marker exists.

    Args:
        run: Current run configuration.
        global_marker: Optional command-line completion marker path.

    Returns:
        ``True`` when any supported completion marker exists.
    """
    markers = [
        run.pod5_directory / ".upload-complete",
        run.output_directory / ".upload-complete",
    ]
    if global_marker:
        markers.append(Path(global_marker))
    return any(marker.is_file() for marker in markers)


def resolve_executable(*, command: str) -> Path:
    """Resolve and validate an executable.

    Args:
        command: Executable name or explicit path.

    Returns:
        Resolved executable path.

    Raises:
        RuntimeError: If the executable cannot be found or run.
    """
    resolved = (
        shutil.which(command)
        if os.path.sep not in command
        else command
    )
    if not resolved:
        raise RuntimeError(f"Required executable is missing: {command}")

    path = Path(resolved)
    if not path.is_file() or not os.access(path, os.X_OK):
        raise RuntimeError(
            f"Required executable is not executable: {path}"
        )
    return path.resolve()


def validate_runtime(
    *,
    args: argparse.Namespace,
    runs: Sequence[RunConfiguration],
) -> None:
    """Validate executables, references, directories, and arguments.

    Args:
        args: Parsed scheduler arguments.
        runs: Validated run configurations.

    Raises:
        RuntimeError: If required runtime inputs are unavailable.
        ValueError: If numeric configuration values are invalid.
    """
    for command in (args.dorado, args.minimap2, args.samtools):
        path = resolve_executable(command=command)
        LOGGER.info("Resolved executable %s to %s", command, path)

    if os.path.sep in args.model and not Path(args.model).is_dir():
        raise RuntimeError(
            f"Dorado model directory is missing: {args.model}"
        )

    numeric_values = {
        "poll_seconds": args.poll_seconds,
        "stable_seconds": args.stable_seconds,
        "stable_polls": args.stable_polls,
        "idle_timeout_seconds": args.idle_timeout_seconds,
        "max_walltime_seconds": args.max_walltime_seconds,
        "max_batch_files": args.max_batch_files,
        "mapping_threads": args.mapping_threads,
        "genome_size": args.genome_size,
    }
    invalid = [name for name, value in numeric_values.items() if value < 1]
    if invalid:
        names = ", ".join(sorted(invalid))
        raise ValueError(f"Runtime values must be positive: {names}")

    output_directories: dict[Path, str] = {}
    for run in runs:
        if not run.reference.is_file():
            raise RuntimeError(
                f"Reference file is missing: {run.reference}"
            )
        if not run.barcode_kit:
            raise ValueError(
                f"Run {run.run_id} has an empty barcode kit"
            )

        existing_run = output_directories.get(run.output_directory)
        if existing_run:
            raise ValueError(
                f"Runs {existing_run!r} and {run.run_id!r} share output "
                f"directory {run.output_directory}"
            )
        output_directories[run.output_directory] = run.run_id
        run.output_directory.mkdir(parents=True, exist_ok=True)


def environment_int(*, name: str, default: int) -> int:
    """Read an integer environment variable.

    Args:
        name: Environment variable name.
        default: Value used when the variable is unset.

    Returns:
        Parsed integer value.

    Raises:
        ValueError: If the environment value is not an integer.
    """
    value = os.environ.get(name)
    return default if value is None else int(value)


def parse_arguments(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Optional argument sequence. Uses ``sys.argv`` when omitted.

    Returns:
        Parsed scheduler arguments.
    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "csv_file_path",
        type=Path,
        help=(
            "CSV describing references, POD5 directories, output "
            "directories, barcode kits, and barcode values"
        ),
    )
    parser.add_argument(
        "metadata_csv_path",
        type=Path,
        help="CSV mapping Barcode values to SEQID and OLNID",
    )
    parser.add_argument(
        "--dorado",
        default=os.environ.get("DORADO_PATH", "dorado"),
        help="Dorado executable name or absolute path",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get(
            "DORADO_MODEL_DIRECTORY",
            DEFAULT_MODEL_DIRECTORY,
        ),
        help="Dorado model alias or installed model directory",
    )
    parser.add_argument(
        "--device",
        default=os.environ.get("DORADO_DEVICE", "cuda:all"),
        help="Dorado device selector; no CPU fallback is attempted",
    )
    parser.add_argument(
        "--benchmark-file",
        default=os.environ.get(
            "DORADO_BENCHMARK_FILE",
            DEFAULT_BENCHMARK_FILE,
        ),
        help=(
            "Optional Dorado batch-size benchmark file; missing files "
            "produce a warning and are ignored"
        ),
    )
    parser.add_argument(
        "--refresh-benchmarks",
        action="store_true",
        help="Ask Dorado to continue batch-size benchmarking",
    )
    parser.add_argument(
        "--minimap2",
        default=os.environ.get("MINIMAP2_PATH", "minimap2"),
        help="Minimap2 executable name or absolute path",
    )
    parser.add_argument(
        "--samtools",
        default=os.environ.get("SAMTOOLS_PATH", "samtools"),
        help="Samtools executable name or absolute path",
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=environment_int(
            name="PORESIPPR_POLL_INTERVAL_SECONDS",
            default=60,
        ),
        help="Seconds between POD5 directory scans",
    )
    parser.add_argument(
        "--stable-seconds",
        type=int,
        default=environment_int(
            name="PORESIPPR_STABLE_SECONDS",
            default=120,
        ),
        help="Minimum age of an unchanged POD5 file before processing",
    )
    parser.add_argument(
        "--stable-polls",
        type=int,
        default=environment_int(
            name="PORESIPPR_STABLE_POLLS",
            default=2,
        ),
        help="Consecutive unchanged observations required for a POD5 file",
    )
    parser.add_argument(
        "--idle-timeout-seconds",
        type=int,
        default=environment_int(
            name="PORESIPPR_IDLE_TIMEOUT_SECONDS",
            default=3600,
        ),
        help="Seconds without a completed batch before scheduler shutdown",
    )
    parser.add_argument(
        "--max-walltime-seconds",
        type=int,
        default=environment_int(
            name="PORESIPPR_MAX_WALLTIME_SECONDS",
            default=57600,
        ),
        help="Maximum scheduler wall-clock runtime in seconds",
    )
    parser.add_argument(
        "--max-batch-files",
        type=int,
        default=environment_int(
            name="PORESIPPR_MAX_BATCH_FILES",
            default=4,
        ),
        help="Maximum number of stable POD5 files in one Dorado batch",
    )
    parser.add_argument(
        "--completion-marker",
        help=(
            "Optional global upload-completion marker path; run-local "
            ".upload-complete files are always recognised"
        ),
        default=os.environ.get("PORESIPPR_COMPLETION_MARKER"),
    )
    parser.add_argument(
        "--mapping-threads",
        type=int,
        default=environment_int(
            name="PORESIPPR_MAPPING_THREADS",
            default=5,
        ),
        help="Samtools sorting thread count",
    )
    parser.add_argument(
        "--genome-size",
        type=int,
        default=environment_int(
            name="PORESIPPR_GENOME_SIZE",
            default=5_000_000,
        ),
        help="Genome size used for the legacy sequenced-bases estimate",
    )
    parser.add_argument(
        "--keep-mapping-bam",
        action="store_true",
        help="Retain sorted mapping BAM and BAI files",
    )
    parser.add_argument(
        "--keep-batch-work",
        action="store_true",
        help="Retain temporary Dorado BAM and demultiplexing outputs",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help=(
            "Process files observed during this invocation, waiting for "
            "stability when necessary, then exit"
        ),
    )
    parser.add_argument(
        "--log-level",
        default=os.environ.get("PORESIPPR_LOG_LEVEL", "INFO"),
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Scheduler logging threshold",
    )
    return parser.parse_args(argv)


def write_status(
    *,
    run: RunConfiguration,
    status: str,
    **details: Any,
) -> None:
    """Write a durable run status document.

    Args:
        run: Run whose status will be updated.
        status: High-level status value.
        **details: Additional JSON-serialisable status fields.
    """
    data = {
        "status": status,
        "run_id": run.run_id,
        "updated_at": utc_now(),
        **details,
    }
    atomic_write_json(
        path=run.output_directory / "status.json",
        data=data,
    )


def finalise_runs(
    *,
    runs: Sequence[RunConfiguration],
    states: Mapping[str, dict[str, Any]],
    exit_reason: str,
) -> None:
    """Write final state and status documents for every run.

    Args:
        runs: Run configurations being finalised.
        states: Current durable state objects keyed by run identifier.
        exit_reason: Scheduler lifecycle exit reason.
    """
    final_status = (
        "completed"
        if exit_reason in ("upload-complete", "once-complete")
        else "stopped"
    )

    for run in runs:
        state = states[run.run_id]
        state["updated_at"] = utc_now()
        atomic_write_json(
            path=run.output_directory / "state.json",
            data=state,
        )
        write_status(
            run=run,
            status=final_status,
            reason=exit_reason,
            processed_pod5_count=len(state["processed_pod5"]),
            batch_count=len(state["batches"]),
        )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the incremental PoreSippR scheduler.

    Args:
        argv: Optional command-line arguments for testing and embedding.

    Returns:
        Process exit status. Zero indicates an orderly scheduler exit.
    """
    args = parse_arguments(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)sZ %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    runtime = SchedulerRuntime()
    signal.signal(signal.SIGINT, runtime.request_stop)
    signal.signal(signal.SIGTERM, runtime.request_stop)

    metadata = load_metadata(path=args.metadata_csv_path)
    runs = load_runs(path=args.csv_file_path)
    validate_runtime(args=args, runs=runs)

    states: dict[str, dict[str, Any]] = {}
    observations: dict[str, dict[str, FileObservation]] = {}

    for run in runs:
        state_path = run.output_directory / "state.json"
        state = load_json(
            path=state_path,
            default=initial_state(run=run),
        )
        validate_state(state=state, run=run)
        states[run.run_id] = state
        observations[run.run_id] = {}
        write_status(run=run, status="starting")

    started_monotonic = time.monotonic()
    last_activity = started_monotonic
    exit_reason = "completed"

    try:
        while not runtime.stop_requested:
            processed_any = False
            all_complete = True
            pending_files = 0

            for run in runs:
                state = states[run.run_id]

                stable_files, run_pending = discover_pod5_files(
                    run=run,
                    state=state,
                    observations=observations[run.run_id],
                    stable_seconds=args.stable_seconds,
                    stable_polls=args.stable_polls,
                )

                pending_files += run_pending
                processed_file_count = 0

                if stable_files:
                    batch_files = stable_files[: args.max_batch_files]

                    process_batch(
                        runtime=runtime,
                        run=run,
                        state=state,
                        metadata=metadata,
                        batch_files=batch_files,
                        args=args,
                    )

                    processed_file_count = len(batch_files)
                    processed_any = True
                    last_activity = time.monotonic()

                pending_after = run_pending - processed_file_count
                pending_files -= processed_file_count

                if (
                    not completion_requested(
                        run=run,
                        global_marker=args.completion_marker,
                    )
                    or pending_after > 0
                ):
                    all_complete = False

            if processed_any:
                continue

            if args.once and pending_files == 0:
                exit_reason = "once-complete"
                break

            if all_complete:
                exit_reason = "upload-complete"
                break

            current = time.monotonic()
            if current - started_monotonic >= args.max_walltime_seconds:
                exit_reason = "walltime"
                break

            if current - last_activity >= args.idle_timeout_seconds:
                exit_reason = "idle-timeout"
                break

            time.sleep(args.poll_seconds)

        if runtime.stop_requested:
            exit_reason = "signal"
    except InterruptedError:
        if not runtime.stop_requested:
            LOGGER.exception("Scheduler operation was unexpectedly interrupted")
            for run in runs:
                write_status(
                    run=run,
                    status="failed",
                    reason="unexpected-interruption",
                )
            return 1

        LOGGER.warning("Scheduler processing interrupted by shutdown request")
        exit_reason = "signal"

    except (
        csv.Error,
        json.JSONDecodeError,
        OSError,
        RuntimeError,
        subprocess.SubprocessError,
        TypeError,
        ValueError,
    ) as error:
        LOGGER.exception("Scheduler failed")

        for run in runs:
            write_status(
                run=run,
                status="failed",
                reason="exception",
                error_type=type(error).__name__,
                error_message=str(error),
            )

        return 1

    finalise_runs(
        runs=runs,
        states=states,
        exit_reason=exit_reason,
    )
    LOGGER.info("Scheduler exiting: %s", exit_reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
