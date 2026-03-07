# MSU Curriculum Analytics – Installation Instructions

This document explains how to install the software required to reproduce the MSU Curriculum Analytics project and run the example notebooks.

The installation process consists of:

1. Downloading the raw data
2. Cloning the project repository
3. Creating the Python environment
4. Installing Julia and project packages
5. Registering the Julia Jupyter kernel
6. Running the demo notebook

These instructions were tested on macOS but should also work on Linux.
Windows users may need to adjust shell commands accordingly.


# 1. Download the Data

The full project workflow uses raw institutional datasets that are **not included in the Git repository**.

Download the following files from the Microsoft Teams **Data** folder:

```

CNS_Majors.csv
20250919_Registrars_Data(in).csv

```

After downloading, place them in the repository's `data/` directory.

Expected structure:

```

MSU_Curriculum_Maps/
│
├── data/
│   ├── CNS_Majors.csv
│   └── 20250919_Registrars_Data(in).csv

```

These datasets are used as inputs to the Python preprocessing scripts that generate curriculum CSV files for individual majors.


## Demo Dataset

For demonstration purposes, the repository also includes a sample curriculum dataset:

```

data/Univ_of_Arizona-Aero.csv

```

This dataset represents an example aerospace engineering curriculum and allows the visualization notebooks to run **even if the preprocessing pipeline has not yet been executed**.

The demo notebook uses this Aerospace dataset to test that the installation was successful and that the `CurricularAnalytics` visualization tools are working correctly.



# 2. Clone the Repository

Open a terminal and run:

```
git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git
cd MSU_Curriculum_Maps
```


# 3. Install UV (Python Environment Manager)

We use **UV** to create a reproducible Python environment.

Install UV:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:

```bash
uv --version
```


# 4. Create the Python Environment

From the repository root:

```bash
uv venv --python 3.11
source .venv/bin/activate
```

Your prompt should now show:

```
(MSU_Curriculum_Maps)
```


# 5. Install Python Dependencies

Install all Python packages from `requirements.txt`:

```bash
uv pip install -r requirements.txt
```

Important packages include:

* numpy
* pandas
* jupyter
* notebook<7
* jupyterlab<4
* webio-jupyter-extension

These versions are required for compatibility with Julia WebIO visualizations.


# 6. Install Julia

Install Julia using the official installer:

```bash
curl -fsSL https://install.julialang.org | sh
```

Verify installation:

```bash
julia --version
```


# 7. Install Julia Project Packages

The Julia environment for this project lives in the `julia/` folder.

Install all Julia dependencies:

```bash
julia --project=julia -e 'using Pkg; Pkg.instantiate()'
```

This installs packages listed in:

```
julia/Project.toml
julia/Manifest.toml
```

# 8. Register the Julia Jupyter Kernel

We install a project-specific Julia kernel for Jupyter.

Navigate to the Julia project directory:

```bash
cd julia
julia --project=.
````

Inside the Julia REPL run:

```julia
using IJulia
installkernel("MSUCA-Julia", "--project=$(pwd())")
```

This registers a Jupyter kernel that always uses the Julia environment stored in the `julia/` directory. Exit the Julia REPL using Ctrl + D.

You can verify that the kernel was installed by running:

```bash
python -m jupyter kernelspec list
```

You should see an entry similar to:

```
msuca-julia-1.12
```


# 9. Launch Jupyter Notebook

Start Jupyter from the repository root:

```bash
python -m jupyter notebook
```

This will open Jupyter in your web browser.



# IMPORTANT: Use Browser Jupyter (Not VS Code)

Interactive curriculum visualizations depend on **Julia WebIO**.

During testing we found that:

- Browser Jupyter Notebook works
- JupyterLab 3 works
- VS Code notebook renderer does NOT render WebIO visualizations

Therefore, curriculum visualization notebooks must be run in **browser Jupyter**.



# 10. Run the Demo Notebook

Navigate to the `notebooks/` directory in Jupyter and open a demo notebook.

Example workflow:

1. Select the **MSUCA-Julia** kernel
2. Load curriculum data
3. Run the visualization cells

Example test cell:

```julia
using CurricularAnalytics
using CurricularVisualization
using CSV
using DataFrames
```

If this runs without errors, the installation was successful.