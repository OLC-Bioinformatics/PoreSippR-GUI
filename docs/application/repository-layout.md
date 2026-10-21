# Repository layout

Application code is in `src/poresippr/`. Supporting files are grouped by
purpose: resources, references, examples, tests, and documentation.

```text
src/poresippr/
    main.py                         GUI entry point
    methods.py                      Application functions
    version.py                      Application version
    ui_main.py                      Generated Qt interface code
    files_rc.py                     Generated Qt resource code
    pipeline/                       Preparation and both schedulers
    integrations/                   FoodPort task
    resources/
        ui/                         Qt Designer and resource source files
        icons/
        fonts/
        images/
        templates/                  HTML report template
scripts/                            Setup and shell helpers
references/                         Reference FASTA databases
examples/                           Existing input and metadata examples
config/                             Local run settings
tests/
    fixtures/config/                Configuration test data
    fixtures/test_files/            Test inputs and example output
    helpers/                        Placeholder output generator
docs/application/                   Application guides
packaging/                          PyInstaller specification
runs/                               Local analysis outputs
```

## Local files

`.env` holds the Conda environment. `.tools` holds downloaded tools and models.
Local settings go in `config/`, and generated analysis output goes in `runs/`.
These local files are ignored by Git.
