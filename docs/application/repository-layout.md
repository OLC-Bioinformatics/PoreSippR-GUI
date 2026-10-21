# Repository layout

Application code is in `src/poresippr/`

```text
src/poresippr/
    main.py                         main file to run the gui
    methods.py
    version.py
    ui_main.py
    files_rc.py
    pipeline/
    integrations/                   FoodPort related files
    resources/
        ui/
        icons/
        fonts/
        images/
        templates/
scripts/                            setup files
references/                         reference FASTA databases
examples/
config/                             settings
tests/
    fixtures/config/
    fixtures/test_files/
    helpers/                        testbench for the GUI
docs/application/                   docs
packaging/
runs/                               runs output directory
```

## Local files

`.env` holds the Conda environment. `.tools` holds downloaded tools and models.
Local settings go in `config/`, and generated analysis output goes in `runs/`.
