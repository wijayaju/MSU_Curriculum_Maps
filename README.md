# MSU Curriculum Project

Arkesh Das
Samuel Abdul
Justin Wijaya
Zachary Kozlowski

CMSE 495 Data Science Capstone


## About

This repository contains an evolving data pipeline for transforming raw Michigan State University curriculum data into structured course dependency graphs.

The project standardizes registrar and major requirement datasets, constructs prerequisite networks, and prepares outputs for structural analysis and future integration with the Curricular Analytics ecosystem.

The long term objective is to support scalable curriculum analysis across semesters and colleges using a modular Python to Julia workflow.

This repository represents the active refactoring of prior exploratory work from previous semesters into a reproducible, script driven architecture, using the Curricular Analytics API.

## Install Instructions

Installation instructions are provided in [INSTALL.md](INSTALL.md)

## Repository Structure

```
MSU_Curriculum_Maps/
├── INSTALL.md
├── LICENSE.txt
├── Manifest.toml
├── Project.toml
├── README.md
├── data
│   ├── 20250919_Registrars_Data(in).csv
│   ├── CNS_Majors_Data.xlsx
│   ├── Fake_majors.csv
│   ├── Fake_registrar.csv
│   ├── Univ_of_Arizona-Aero.csv
│   └── ~$CNS_Majors_Data.xlsx
├── notebooks
│   └── test_install_notebook.ipynb
├── outputs
├── pyproject.toml
├── python
│   └── scripts
│       ├── build_ca_curricula.py
│       └── preprocess.py
├── uv.lock
└── webapi
    ├── Quick Run Instructions.pdf
    ├── curriculum_graph.html
    └── requirements_webapi.txt

```


## Data

The `data/` directory contains:

* Registrar course data exports
* College provided major requirement datasets
* Synthetic datasets for testing and reproducibility

The included real datasets correspond to Fall 2025. The pipeline is designed to operate on any similarly structured semester dataset placed in the `data/` directory.

This project does not scrape live MSU SIS systems. All data are static exports obtained from administrative sources.

However, the registrar datasets are structured in Oracle PeopleSoft format, which is the underlying system used by MSU SIS. As a result, the pipeline is compatible with PeopleSoft structured exports and could be extended in the future to support more direct SIS integrated workflows.

## __Current__ Pipeline Architecture

The workflow follows a staged design. This is mostly the pipeline from last semester. We will be redoing this pipeline based off of our work.

### Stage 1 — Data Cleaning (Python)

`src/scripts/clean_data.py`

* Standardizes course identifiers
* Normalizes prerequisite formatting
* Resolves structural inconsistencies
* Produces cleaned intermediate datasets

Cleaned outputs are written to the `outputs/` directory.


### Stage 2 — Graph Construction and Structured Access

`src/scripts/curriculum_api.py`

* Ingests cleaned curriculum data
* Constructs directed prerequisite relationships
* Builds structured course dependency representations
* Prepares data for export and downstream use

Outputs may include serialized graph structures or JSON representations suitable for analytics and visualization.


### Stage 3 — Visualization (Experimental)

`webapi/`

Contains an exploratory prototype for rendering curriculum graphs in a browser.

This component is experimental and not yet a finalized production interface.


### Stage 4 — Planned Julia Integration

Future development will introduce a Julia layer inside:

```
src/julia/
```

The goal is to transform cleaned Python outputs into a format compatible with CurricularAnalytics.jl for advanced structural metric computation and visualization.

Julia integration is planned but not yet implemented in this repository.


## How to Interact With This Repository

### Installation

All installation instructions are provided in:

```
INSTALL.md
```

The project uses a conda based environment to ensure cross platform reproducibility across macOS and Windows systems.

A local environment is created inside:

```
envs/
```


### Running the Pipeline

After installing the environment described in `INSTALL.md`:

1. Activate the project environment
2. Place the desired semester datasets inside `data/`
3. Run the cleaning stage:

```
python src/scripts/clean_data.py
```

4. Run the graph construction stage:

```
python src/scripts/curriculum_api.py
```

Generated artifacts will appear in:

```
outputs/
```


### Reproducibility and Figures

Figure level reproducibility instructions are documented in:

```
notebooks/reproducibility.ipynb
```

This notebook includes:

* Description of each figure
* Code used to generate intermediate data
* Graph construction logic
* Visualization formatting
* Export procedures

All figures used in final reports or presentations will have corresponding reproducibility instructions.


## Goals

* Refactor exploratory notebooks into modular scripts
* Standardize preprocessing of registrar and major datasets
* Construct reusable curriculum dependency graphs
* Enable semester and college level portability
* Prepare cleaned outputs for Julia based curricular analytics
* Deliver an MVP capable of structured curriculum graph generation


## Research Questions

* How can heterogeneous curriculum datasets be transformed into unified graph representations?
* What structural bottlenecks emerge from prerequisite networks?
* How do centrality and dependency depth vary across majors?
* Can structural metrics inform curriculum design decisions?


## Outputs

The `outputs/` directory contains generated artifacts such as:

* Cleaned intermediate datasets
* Serialized graph objects
* JSON exports
* Visualization data files

This directory is not version controlled except for minimal example files.

## Community Partner

Michigan State University academic units and administrative stakeholders.


## License

This project is licensed under the MIT License. See `LICENSE.txt` for details.
