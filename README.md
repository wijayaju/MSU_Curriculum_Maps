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

This repository represents the active refactoring of prior exploratory work from previous semesters into a reproducible, script driven architecture, using the Curricular Analytics Julia package.

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
├── data/
│   └── Univ_of_Arizona-Aero.csv
├── notebooks/
│   ├── reproducibility.ipynb
│   └── test_install_notebook.ipynb
├── outputs/
├── pyproject.toml
├── python/
│   └── scripts
│       ├── build_ca_curricula_v1.py
│       └── build_ca_curricula_v2.py
├── uv.lock
└── webapi/
    ├── Quick Run Instructions.pdf
    ├── curriculum_graph.html
    └── requirements_webapi.txt
```


## Data

The `data/` directory is initially empty due to saftey reasons, but the user is able to add:

* Registrar course data exports
* College provided major requirement datasets
* Synthetic datasets for testing and reproducibility

**the repo comes with one sample dataset for the user to test functionality of packages and software**

The real datasets correspond to Fall 2025 and Fall ~2018. The pipeline is designed to operate on any similarly structured semester dataset placed in the `data/` directory.

This project does not scrape live MSU SIS systems. All data are static exports obtained from administrative sources.

However, the registrar datasets are structured in Oracle PeopleSoft format, which is the underlying system used by MSU SIS. As a result, the pipeline is compatible with PeopleSoft structured exports and could be extended in the future to support more direct SIS integrated workflows.

## __Current__ Pipeline Architecture

The workflow follows a staged design. The entire pipeline has been rebuilt as the previous semesters work/goals were different than ours.

### Stage 1 - Data Cleaning (Python)

`scripts/python/build_ca_curricula_v2.py`

* Parses the 2 datasets and extracts relevant columns
* Normalizes prerequisite formatting
* Builds CurricularAnalytics formatted datasets
* Resolves structural inconsistencies
* Crosschecks information across input data
* Produces ready to use CSVs for CurricularAnalytics

Cleaned outputs are written to the `outputs/` directory.


### Stage 2 - Data Loading

`/outputs/`

If everything worked correctly, the script will have created many CSV files to the output directory, the user is now able to browse through the files and find the curriculum they are interested in, they will be able to explore more about it in the Julia Notebooks


### Stage 3 - Julia Integration and Graph Building

`/notebooks/reproducibility.ipynb`

Once the user has found what they are interested in, they can use their chosen dataset with the notebook found in this repository, if everything is installed correctly, they will be able to generate graphs of curriculum plans using the CurricularAnalytics package.



### Stage 4 - Curriculum Insights

Using the notebook the user can also explore CurricularAnalytics statistics generated in the notebooks, the user is able to explore statistics such as blocking factor, delay factor, centrailtiy, and complexity, these are detailed in the notebook.

If there time is available, we plan to integrate data from MSUGrades, using the courses from our cleaning script, this allows us to access a different dataset that contains course information (grades, instructors, semesters) and use this in conjunction with CurriculumAnalytics.

## How to Interact With This Repository

### Installation

All installation instructions are provided in:

```
INSTALL.md
```


### Running the Pipeline

After installing the environment described in `INSTALL.md`:

1. Activate the project environment
2. Place the desired semester datasets inside `data/`
3. Run the cleaning stage:

```
python scripts/python/build_ca_curricula_v2.py
```


Generated CSV files will appear in:

```
outputs/
```


### Reproducibility and Figures

Figure level reproducibility instructions are documented in:

```
notebooks/reproducibility.ipynb
```

This notebook includes:

* Installation testing
* Data loading
* Data with CurricularAnalytics
* Graph Vizualization
* Curriculum Insights

All figures used in final reports or presentations will have corresponding reproducibility instructions.


## Goals

* Refactor exploratory notebooks into modular scripts
* Standardize preprocessing of registrar and major datasets
* Construct reusable curriculum dependency graphs
* Enable semester and college level portability
* Prepare cleaned outputs for Julia based curricular analytics
* Deliver an MVP capable of structured curriculum graph generation


## Research Questions

* What structural bottlenecks emerge from prerequisite networks?
* How do centrality and dependency depth vary across majors?
* Can structural metrics inform curriculum design decisions?


## Community Partner

Michigan State University academic units and administrative stakeholders.


## License

This project is licensed under the MIT License. See `LICENSE.txt` for details.
