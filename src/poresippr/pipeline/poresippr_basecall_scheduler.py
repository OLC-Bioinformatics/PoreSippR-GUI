#!/usr/bin/env python3
import os
import subprocess
import csv
import sys
import time
import argparse
import signal
import gzip
import glob
from multiprocessing import Process, Value

##### Author Mathu Malar C Mathu.Malar@inspection.gc.ca ######
##### Updated for Dorado + POD5 + CUDA-only + benchmark file #####

# Runtime defaults
MODEL = "fast"      # or "sup"
DEVICE = "cuda:all"   # CUDA only
BENCH_FILE = "/home/olcbio/PoreSippR-GUI/dorado_benchmarks.json"

# If True, refresh benchmarks each run (slower startup). Usually keep False.
RUN_BENCHMARK_REFRESH = False

# POD5 wait settings
POLL_INTERVAL = 30     # seconds between checks for POD5 files
STABLE_SECONDS = 120   # newest file must be unmodified this long


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        err_out = (e.stderr or "") + "\n" + (e.stdout or "")
        print(f"Error executing command: {command}")
        print(f"Error message: {e}")
        if err_out.strip():
            print(err_out.strip())
        return False, (e.stdout or ""), (e.stderr or "")


def wait_for_pod5(pod5_dir):
    """
    Block until at least one .pod5 file exists and none are still being
    written. Retries forever if the folder is missing or empty.
    """
    print(f"Waiting for POD5 files in {pod5_dir} ...")
    while True:
        files = glob.glob(os.path.join(pod5_dir, "**", "*.pod5"), recursive=True)
        if files:
            newest = max(os.path.getmtime(f) for f in files)
            if time.time() - newest >= STABLE_SECONDS:
                print(f"Found {len(files)} POD5 file(s); starting basecalling.")
                return True
            print(f"{len(files)} POD5 file(s) found, still being written...")
        else:
            print("No POD5 files yet, waiting...")
        time.sleep(POLL_INTERVAL)


def concatenate_fastq_files(barcode_path, output_file):
    """
    Concatenate .fastq and .fastq.gz files into a single uncompressed FASTQ.
    """
    fastq_files = [
        f for f in os.listdir(barcode_path)
        if f.endswith(".fastq") or f.endswith(".fastq.gz")
    ]
    fastq_files.sort()

    with open(output_file, "w") as outfile:
        for fq in fastq_files:
            fq_path = os.path.join(barcode_path, fq)
            if fq.endswith(".gz"):
                with gzip.open(fq_path, "rt") as infile:
                    outfile.write(infile.read())
            else:
                with open(fq_path, "r") as infile:
                    outfile.write(infile.read())


def flatten_demux_to_pass_root(pass_dir):
    """
    Dorado may write nested output:
      pass/<run>/<unknown>/<chunk>/fastq_pass/barcodeXX/*.fastq.gz
    Flatten to:
      pass/barcodeXX/*.fastq(.gz)
    """
    for root, _, files in os.walk(pass_dir):
        base = os.path.basename(root)
        if base.startswith("barcode"):
            dest_dir = os.path.join(pass_dir, base)
            os.makedirs(dest_dir, exist_ok=True)

            for fname in files:
                if not (fname.endswith(".fastq") or fname.endswith(".fastq.gz")):
                    continue

                src = os.path.join(root, fname)
                dst = os.path.join(dest_dir, fname)

                # Avoid overwrite collisions
                if os.path.exists(dst):
                    if fname.endswith(".fastq.gz"):
                        stem = fname[:-9]
                        ext = ".fastq.gz"
                    else:
                        stem, ext = os.path.splitext(fname)

                    i = 1
                    while True:
                        candidate = os.path.join(dest_dir, f"{stem}_{i}{ext}")
                        if not os.path.exists(candidate):
                            dst = candidate
                            break
                        i += 1

                if os.path.abspath(src) != os.path.abspath(dst):
                    os.replace(src, dst)


def print_usage():
    if "SINGULARITY_NAME" in os.environ:
        print("Usage: singularity run --nv mycontainer.sif <input.csv> <metadata.csv>")
    else:
        print("Usage: python poresippr_basecall_scheduler.py <input.csv> <metadata.csv>")


def build_basecaller_command(pod5_dir, barcode_kit, dorado_bam):
    """
    Build Dorado basecaller command with benchmark file support.
    """
    bench_refresh_flag = ""
    if RUN_BENCHMARK_REFRESH:
        bench_refresh_flag = "--run-batchsize-benchmarks continue "

    cmd = (
        f"dorado basecaller "
        f"--device {DEVICE} "
        f"{MODEL} "
        #f"--batchsize-benchmarks-file {BENCH_FILE} "
        f"--batchsize 640 "
        f"{bench_refresh_flag}"
        f"{pod5_dir} "
        f"--kit-name {barcode_kit} "
        f"> {dorado_bam}"
    )
    return cmd


# Argument parsing
parser = argparse.ArgumentParser(
    description="Run Dorado basecalling/demux and downstream minimap2/samtools analysis."
)
parser.add_argument("csv_file_path", help="Path to the input CSV file.")
parser.add_argument("metadata_csv_path", help="Path to the metadata CSV file.")
args = parser.parse_args()

if len(sys.argv) != 3:
    print_usage()
    sys.exit(1)

csv_file_path = args.csv_file_path
metadata_csv_path = args.metadata_csv_path

# Metadata mapping: barcode -> SEQID/OLNID
barcode_to_seqid = {}
barcode_to_olnid = {}
with open(metadata_csv_path, "r") as metafile:
    meta_reader = csv.DictReader(metafile)
    header = meta_reader.fieldnames
    print(f"Metadata CSV columns: {header}")
    for row in meta_reader:
        barcode_to_seqid[int(row["Barcode"])] = row["SEQID"]
        barcode_to_olnid[int(row["Barcode"])] = row["OLNID"]


def main_loop(complete, iteration):
    terminate = False

    try:
        while not terminate:
            print(f"\n\nIteration: {iteration.value}\n\n")

            with open(csv_file_path, "r") as csvfile:
                csv_reader = csv.DictReader(csvfile)

                for row in csv_reader:
                    reference = row["reference"]
                    pod5_dir = row["pod5_dir"]
                    output_dir = row["output_dir"]
                    barcode_kit = row["barcode"].strip()
                    barcode_values = [
                        int(x.strip().replace('"', ""))
                        for x in row["barcode_values"].split(",")
                    ]

                    try:
                        os.makedirs(output_dir, exist_ok=True)
                    except OSError as e:
                        print(f"Error creating output directory: {output_dir}")
                        print(f"Error message: {e}")
                        terminate = True
                        break

                    dorado_bam = os.path.join(output_dir, "dorado_basecalls.bam")
                    demux_dir = os.path.join(output_dir, "pass")
                    os.makedirs(demux_dir, exist_ok=True)

                    # 0) Wait for stable POD5 files (retries, never fails)
                    wait_for_pod5(pod5_dir)

                    # 1) Basecall (CUDA only) with retry if CUDA is temporarily busy
                    basecall_cmd = build_basecaller_command(
                        pod5_dir=pod5_dir,
                        barcode_kit=barcode_kit,
                        dorado_bam=dorado_bam
                    )
                    print(f"Running Dorado basecaller: {basecall_cmd}")

                    max_cuda_retries = 10
                    retry_wait_seconds = 45

                    basecall_ok = False
                    for attempt in range(1, max_cuda_retries + 1):
                        ok, _out, err = run_command(basecall_cmd)
                        if ok and os.path.exists(dorado_bam) and os.path.getsize(dorado_bam) > 0:
                            basecall_ok = True
                            break

                        err_l = (err or "").lower()
                        if "cuda-capable device(s) is/are busy or unavailable" in err_l:
                            print(
                                f"CUDA busy/unavailable (attempt {attempt}/{max_cuda_retries}). "
                                f"Retrying in {retry_wait_seconds}s..."
                            )
                            time.sleep(retry_wait_seconds)
                            continue
                        else:
                            break

                    if not basecall_ok:
                        print("CUDA basecalling failed. Exiting without CPU fallback.")
                        terminate = True
                        break

                    # 2) Demux
                    demux_cmd = (
                        f"dorado demux "
                        f"--emit-fastq "
                        f"--no-classify "
                        f"--output-dir {demux_dir} "
                        f"{dorado_bam}"
                    )
                    print(f"Running Dorado demux: {demux_cmd}")
                    demux_ok, _demux_out, _demux_err = run_command(demux_cmd)
                    if not demux_ok:
                        print("Demux failed.")
                        terminate = True
                        break

                    # 3) Flatten nested demux tree into pass/barcodeXX
                    flatten_demux_to_pass_root(demux_dir)

                    # 4) Per barcode downstream
                    for barcode_num in barcode_values:
                        barcode_dir = f"barcode{barcode_num:02d}"
                        barcode_path = os.path.join(demux_dir, barcode_dir)

                        if not os.path.isdir(barcode_path):
                            print(f"No barcode directory found for {barcode_dir}")
                            continue

                        seqid = barcode_to_seqid.get(barcode_num, f"barcode{barcode_num:02d}")
                        _olnid = barcode_to_olnid.get(barcode_num, f"OLN{barcode_num:02d}")

                        concatenated_fastq_file = os.path.join(output_dir, f"{seqid}.fastq")
                        concatenate_fastq_files(barcode_path, concatenated_fastq_file)

                        if (not os.path.exists(concatenated_fastq_file)) or os.path.getsize(concatenated_fastq_file) == 0:
                            print(f"No reads found for {barcode_dir}; skipping.")
                            continue

                        bam_file = os.path.join(output_dir, f"{seqid}_sorted.bam")
                        minimap2_command = (
                            f"minimap2 -ax map-ont {reference} {concatenated_fastq_file} "
                            f"| samtools view -@ 5 -bS - | samtools sort -o {bam_file} -"
                        )
                        print(f"Running Minimap2 command: {minimap2_command}")
                        mm_ok, _mm_out, _mm_err = run_command(minimap2_command)
                        if not mm_ok:
                            terminate = True
                            break

                        csv_out = os.path.join(output_dir, f"{seqid}_iteration{iteration.value}.csv")
                        samtools_command = (
                            f"samtools coverage {bam_file} | cut -f 1,4 | awk '$2 > 0' "
                            f"| sort -rnk 2,2 | sed 's/\\t/,/g' > {csv_out}"
                        )
                        print(f"Running Samtools command: {samtools_command}")
                        st_ok, _st_out, _st_err = run_command(samtools_command)
                        if not st_ok:
                            terminate = True
                            break

                        # Add header to iteration CSV (KEEP these files)
                        with open(csv_out, "r+") as f:
                            content = f.read()
                            f.seek(0, 0)
                            f.write("gene_name,number_of_reads_mapped\n" + content)

                        # Add genome coverage
                        file_size = os.path.getsize(concatenated_fastq_file)
                        if file_size > 0:
                            genome_coverage_value = file_size / 5000000
                            with open(csv_out, mode="a", newline="") as file:
                                writer = csv.writer(file)
                                writer.writerow(["genome_coverage", f"{genome_coverage_value}X"])

                        # Cleanup temp per-barcode files
                        if os.path.exists(concatenated_fastq_file):
                            os.remove(concatenated_fastq_file)
                        if os.path.exists(bam_file):
                            os.remove(bam_file)

                    if terminate:
                        break

                    # Cleanup temporary Dorado BAM after all barcode CSVs are produced
                    if os.path.exists(dorado_bam):
                        try:
                            os.remove(dorado_bam)
                            print(f"Removed temporary Dorado BAM: {dorado_bam}")
                        except OSError as e:
                            print(f"Warning: could not remove {dorado_bam}: {e}")

            iteration.value += 1
            if terminate:
                break

            print("Waiting for 30 minutes before running Dorado again...")
            time.sleep(1800)
    finally:
        # Lets the parent know the worker is done
        complete.value = True


if __name__ == "__main__":
    complete = Value("b", False)
    iteration = Value("i", 1)

    p = Process(target=main_loop, args=(complete, iteration))

    def handler(signum, frame):
        print("Signal received, terminating...")
        if p.is_alive():
            p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    p.start()
    p.join()   # parent exits as soon as the child exits
