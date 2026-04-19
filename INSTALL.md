# MSU Curriculum Analytics Install Tutorial

Welcome to the MSU Curriculum Analytics Install Tutorial! This tutorial entails:

1. Obtaining the data
2. Getting the Git repository
3. Moving the data to the correct spot
4. Moving to the repository in terminal
5. Install uv
6. Creating the uv virtual environment
7. Auto-installing Python packages
8. Downloading and installing Julia
9. Auto-installing Julia packages
10. Linking Julia to Jupyter Lab

Please follow these steps carefully and completely to ensure the entire pipeline is set up properly. **Skipping steps may break the pipeline and lead to you needing to restart the installation process!** 

## We will start with Mac install instructions

**Please scroll down for Windows Install**


### First Step: obtaining the data

**This step is only required if you want to run the full MSU pipeline. If you are just testing installation, you can skip this step and use the included demo dataset.**

Find the `CNS_Majors.csv` and `20250919_Registrars_Data(in).csv` from the Microsoft Teams "Data" folder. Download these and make sure you know where they are located.

#### NOTE: Demo Dataset

For demonstration purposes, the repository also includes a sample curriculum dataset:

```bash
data/Univ_of_Arizona-Aero.csv
```

This dataset allows the visualization notebooks to run **even if the preprocessing pipeline from the reproducibility notebook has not yet been executed**.


### Second Step: getting the Git repository

Open your preferred terminal and navigate to where you want the repository.

```bash
git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git
```


### Third Step: moving the data to the correct spot

Move the downloaded files into the `data/` folder inside the repository.


### Fourth Step: moving to the repository

Navigate into the repository folder:

```bash
cd MSU_Curriculum_Maps
```


### Fifth Step: installing uv

Check if uv is installed:

```bash
uv --version
```

If not, install it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then **close and reopen your terminal**, and navigate back to the repo.


### Sixth Step: install Python packages

We install all Python packages using `uv`, which reads from the project configuration files.

```bash
uv sync
```


### Seventh Step: install Julia

```bash
curl -fsSL https://install.julialang.org | sh
```

Use default settings.

Then restart your terminal and navigate back to the repo.


### Eighth Step: install Julia packages

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate(); Pkg.precompile()'
```


### Ninth Step: link Julia to Jupyter Lab

This allows Julia to be used as a notebook kernel.

```bash
julia -e 'using Pkg; Pkg.add("IJulia")'
```


### Tenth Step: register kernel

```bash
julia --project=. -e 'using IJulia; IJulia.installkernel("Julia", env=Dict("JULIA_PROJECT"=>pwd()))'
```


### Eleventh Step: open Jupyter Lab

```bash
uv run jupyter lab
```

You should see **Julia 1.x** as a kernel option.


## Testing that everything works

Run:

```
notebooks/test_install_notebook.ipynb
```

Expected result:

* `1 + 1` returns `2`
* Visualization opens in browser

You do not need MSU data for this step.

For full pipeline usage, see:

```
notebooks/reproducibility.ipynb
```


# Windows Install

(Same structure, only fixes applied below)


### First Step: obtaining the data

Same note applies:

**You can skip this step if you are only testing installation.**


### Second Step: clone repo

```bash
git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git
```


### Third Step: move data

Move files into:

```bash
data/
```


### Fourth Step: navigate

```bash
cd MSU_Curriculum_Maps
```

### Fifth Step: install uv

```powershell
-ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart PowerShell afterward.


### Sixth Step: install Python packages

```bash
uv sync
```


### Seventh Step: install Julia

Download from:

[https://julialang.org/downloads/](https://julialang.org/downloads/)

Ensure **Add to PATH** is checked.


### Eighth Step: install Julia packages

```bash
julia --project=. -e "using Pkg; Pkg.instantiate(); Pkg.precompile()"
```


### Ninth Step: link Julia

```bash
julia -e "using Pkg; Pkg.add(\"IJulia\")"
```


### Register kernel

```bash
$projectPath = (Get-Location).Path
julia --project=. -e "using IJulia; IJulia.installkernel('Julia', env=Dict('JULIA_PROJECT'=>'$projectPath'))"
```


### Tenth Step: open Jupyter

```bash
uv run jupyter lab
```


## Testing

Run:

```
notebooks/test_install_notebook.ipynb
```

Expected:

* `1+1 = 2`
* Graph visualization works


# Done

Everything should now be working and ready for use.