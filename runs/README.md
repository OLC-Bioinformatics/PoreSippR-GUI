# Analysis outputs

For setup and the application source tree, see the [installation guide](../INSTALL.md)
and [repository layout](../docs/application/repository-layout.md).

Each analysis has its own folder:

```text
runs/<MinKNOW-run-name>/analysis_<YYYYMMDD_HHMMSS>/
    input.csv          # Reference, input paths, kit, and selected barcodes
    metadata.csv       # Barcode-to-SEQID/OLNID assignments
    state.json         # Processed POD5 files and completed batches
    status.json        # Scheduler status and last batch
    fastq/             # Retained reads, grouped by barcode and batch
    results/           # Original <SEQID>_iteration<N>.csv files
    images/            # GUI tables: iteration_<N>.html
    reports/           # PDF: <run-name>_report.pdf
    output/processed/  # Copies of CSVs already handled by the GUI
    working/           # Temporary basecalling files
    mapping/           # Temporary alignment files
```

The first successful configuration validation creates the folder. Revalidating
for the same run before processing starts reuses that draft, including saved
sample entries. Validate sequence information again after editing configuration.
A different run name, or configuration validated after processing has started,
creates a new folder. Draft reuse applies only within the current GUI session;
restarting the GUI does not automatically resume an existing analysis.

The console log is `run_poresippr.log` in the repository root and is overwritten
on each launch. Generated analysis folders are ignored by Git; this README is tracked.

The PDF filename is reused across iterations. The current report loop can revisit
older iterations while waiting, so check PDF values against the latest iteration
CSV and HTML before using it as a final report.

Stop the GUI and its scheduler before cleanup. These commands permanently delete
outputs; run them from the repository root:

```bash
# List analysis folders.
make list-runs

# Delete one analysis; replace the example with a listed folder.
make clean-analysis ANALYSIS=MIN-20260421/analysis_20261026_100000

# Delete all timestamped analyses under runs/.
make clean-runs

# Delete outputs from the old GUI layout at the repository root and in references/.
make clean
```

See the [Makefile](../Makefile) for the exact cleanup paths. `make clean` leaves
`runs/` analyses in place. The cleanup targets preserve MinKNOW's raw POD5 data,
the reference database, and the installed environment and models.
