#!/usr/bin/env python3
import os
import subprocess
import csv
import sys
import time
import argparse
import signal
import gzip
from multiprocessing import Process, Value

##### Author Mathu Malar C Mathu.Malar@inspection.gc.ca ######
##### Updated for Dorado + POD5 + CUDA-only + benchmark file #####

# Runtime defaults
MODEL = "fast"      # or "sup"
DEVICE = "cuda:all"   # CUDA only
BENCH_FILE = "/home/olcbio/PoreSippR-GUI/dorado_benchmarks.json"

# If True, refresh benchmarks each run (slower startup). Usually keep False.
RUN_BENCHMARK_REFRESH = False


def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e}")
        return False


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


def signal_handler(signum, frame):
    global terminate
    print("Signal received, terminating the script...")
    terminate = True


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
        f"--batchsize-benchmarks-file {BENCH_FILE} "
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
    global terminate

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

                # 1) Basecall (CUDA only)
                basecall_cmd = build_basecaller_command(
                    pod5_dir=pod5_dir,
                    barcode_kit=barcode_kit,
                    dorado_bam=dorado_bam
                )
                print(f"Running Dorado basecaller: {basecall_cmd}")
                basecall_ok = run_command(basecall_cmd)

                if (not basecall_ok) or (not os.path.exists(dorado_bam)) or os.path.getsize(dorado_bam) == 0:
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
                demux_ok = run_command(demux_cmd)
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
                    if not run_command(minimap2_command):
                        terminate = True
                        break

                    csv_out = os.path.join(output_dir, f"{seqid}_iteration{iteration.value}.csv")
                    samtools_command = (
                        f"samtools coverage {bam_file} | cut -f 1,4 | awk '$2 > 0' "
                        f"| sort -rnk 2,2 | sed 's/\\t/,/g' > {csv_out}"
                    )
                    print(f"Running Samtools command: {samtools_command}")
                    if not run_command(samtools_command):
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


if __name__ == "__main__":
    terminate = False
    complete = Value("b", False)
    iteration = Value("i", 1)

    p = Process(target=main_loop, args=(complete, iteration))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    p.start()

    while not complete.value:
        try:
            p.join(timeout=1)
        except SystemExit:
            print("Terminating subprocess...")
            p.terminate()
            p.join()
        if complete.value:
            break

    if terminate:
        print("Terminating subprocess...")
        p.terminate()
        p.join()
