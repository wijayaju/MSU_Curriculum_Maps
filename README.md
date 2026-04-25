# MSU Curriculum Maps

**Spring 2026 | CMSE 495 Data Science Capstone**
**Michigan State University**

*A pipeline for transforming MSU curriculum data into prerequisite graphs and analyzing them using the Curricular Analytics framework.*

**Authors / Contributors**
Arkesh Das
Samuel Abdul
Justin Wijaya
Zachary Kozlowski

## Overview

This repository contains the final deliverables for a **Spring 2026 CMSE 495 Data Science Capstone project** completed in partnership with **Dr. Stephen Thomas and Michigan State University curriculum stakeholders**.

The goal of this project was to build a pipeline that transforms raw MSU curriculum data into structured prerequisite networks that can be analyzed and visualized using the **Curricular Analytics** framework.

At a high level, this project:

* Cleans and standardizes registrar and major requirement datasets
* Converts them into Curricular Analytics–formatted CSVs
* Generates curriculum graphs and structural metrics
* Explores ways to enrich those graphs with additional data, for example grades

This repository represents the final state of the project at the end of the semester and is not under active development. It is intended as a clear starting point for future teams and stakeholders.

This repository is primarily intended for future student teams, curriculum researchers, and institutional stakeholders interested in curriculum structure analysis.

## Project Goals

* Create a reproducible pipeline for curriculum mapping
* Enable structural analysis of degree plans
* Provide tools for visualizing prerequisite pathways
* Support data-informed curriculum design decisions

## Recommended Workflow

If you are new to this project, follow this order:

1. **Install everything**
   → See [INSTALL.md](INSTALL.md)

2. **Verify your setup**
   → Run `notebooks/test_install_notebook.ipynb`

3. **Run the full pipeline and analysis**
   → Use `notebooks/reproducibility.ipynb`

You do not need MSU-specific datasets to complete steps 1 and 2. The included demo dataset is sufficient to test installation and visualization.

### Quick Start (TL;DR)

```
uv sync
uv run jupyter lab
```

Then open `notebooks/test_install_notebook.ipynb`

## Repository Structure

```
MSU_Curriculum_Maps/
├── INSTALL.md
├── README.md
├── data/
├── notebooks/
├── outputs/
├── scripts/
│   ├── python/
│   └── julia/
├── website/
├── upload_to_curricularanalytics.md
├── local_website_instructions.md
└── project configuration files
```

### Key Components

#### `data/`

Contains input datasets.

* **NOT included in repo:**

  * MSU Registrar data
  * CNS Majors dataset
  * These must be obtained through institutional access and placed manually

  Additionally, MSU Grades data is not included in this repository, but it can be accessed by following the instructions in section 6 of the [reproducibility notebook](notebooks/reproducibility.ipynb)

* **Included example datasets:**

  * `Univ_of_Arizona-Aero.csv`
    → Official example dataset from Curricular Analytics documentation, used for testing

#### `outputs/`

Generated curriculum CSV files in Curricular Analytics format.

* Includes example outputs:

  * `fake_data_sci.csv`
  * Variants showing different math entry points, for example MTH 103 vs MTH 132

These are **hand-crafted examples** to:

* Demonstrate what MSU outputs look like
* Allow visualization without restricted datasets
* Highlight structural differences such as starting math level bottlenecks
* Provide an MSU Data Science example that was not present in the provided datasets

#### `notebooks/`

* `test_install_notebook.ipynb`
  → Verifies environment setup using demo data

* `reproducibility.ipynb`
  → Main walkthrough of the pipeline, visualization, and analysis

#### `scripts/python/`

* `build_ca_curricula_v2.py`
  → **Primary pipeline script, recommended**

* `build_ca_curricula_v3.py`
  → Used for website prototype, adds analytics and JSON output

* `build_ca_curricula_v1.py`
  → Legacy prototype, retained for reference only

* `enrich_with_grades.py`
  → Integrates MSUGrades dataset, see [reproducibility notebook](notebooks/reproducibility.ipynb)

#### `scripts/julia/`

* `course_analyzer.jl`
  → Supporting analysis functions

* `orphanate.jl`
  → Removes disconnected courses to reveal core prerequisite structure

#### `website/`

Contains **local prototype dashboards** for curriculum exploration.

* Functional as a local prototype
* Not production-ready or maintained
* Intended as a concept for future development

#### `upload_to_curricularanalytics.md`

Alternative workflow for uploading generated curricula to:
[https://curricularanalytics.org](https://curricularanalytics.org)

Useful for:

* Sharing curricula
* Viewing graphs without full local setup

## Pipeline Overview

### Stage 1, Data Processing, Python

`build_ca_curricula_v2.py`

* Parses registrar and majors datasets
* Standardizes course and prerequisite structure
* Resolves inconsistencies
* Outputs Curricular Analytics–formatted CSVs

### Stage 2, Data Output

* CSV files are written to `outputs/`
* Each file represents a single degree plan

### Stage 3, Visualization, Julia

Using `reproducibility.ipynb`:

* Load a curriculum
* Generate interactive graphs
* Explore prerequisite structure

### Stage 4, Analysis

Metrics include:

* Blocking factor
* Delay factor
* Centrality
* Complexity

### Stage 5, Optional Enhancements

* MSU Grades integration
* Orphanate tool for cleaner graphs

---

## Website Prototype

We created a local dashboard to demonstrate how this data could be presented in a more user-friendly way.

This includes:

* Dropdown-based degree selection
* Interactive graph exploration
* Course-level statistics, for example GPA and DFW

Important notes:

* This is a prototype only
* Not intended for official or production use
* Serves as a starting point for future teams

See: `local_website_instructions.md`

## Data Notes

* Real MSU datasets are not included due to access restrictions
* Pipeline is designed for PeopleSoft-style exports
* Provided majors dataset was hand-constructed and not reproducible

Because of this:

* Re-running the entire pipeline requires institutional data access
* Example datasets are included to demonstrate functionality

## Limitations

* Heavy dependence on data quality and structure
* Majors dataset is not reproducible from source systems
* Ambiguous requirement groupings such as choose one of are not fully resolved
* Curricular Analytics package limits customization and extensibility
* Visualization layer is not easily extendable without modifying underlying tools

## Future Directions

This project is a strong starting point, but several improvements are needed for real-world use:

### 1. Automated Data Pipeline

* Build a scraper or extraction pipeline from MSU Registrar systems
* Use AI-assisted transformations to standardize curriculum data
* Eliminate reliance on manually curated datasets

### 2. Improved Accessibility

* Develop a fully hosted web platform similar to MSUGrades
* Allow non-technical users to explore curriculum maps

### 3. Additional Data Integration

* Overlay variables such as:

  * Course modality
  * Class size
  * Location
  * Failure rates

### 4. Tooling Improvements

* Modify or extend Curricular Analytics source code
* Explore the Python adaptation of Curricular Analytics to reduce setup complexity

## Videos

Project videos can be found here for additional details:

* [Final Project Video](https://www.youtube.com/watch?v=xyXR1YQDaTE)
* [MVP Video](https://www.youtube.com/watch?v=4PuFhvoS6lI)
* [Project Plan Video](https://youtu.be/M4_gURakRH0)

## Community Partner

Dr. Stephen Thomas
Michigan State University

## Acknowledgements

We would like to thank:

* Dr. Stephen Thomas for guidance and project support
* The CMSE 495 instructional team for feedback throughout the semester
* Prior project teams for foundational work, especially Lauryn Crandall

## License

This project is licensed under the MIT License. See `LICENSE.txt` for details.
