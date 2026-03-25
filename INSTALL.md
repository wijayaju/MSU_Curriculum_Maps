# MSU Curriculum Analytics Install Tutorial

Welcome to the MSU Curriculum Analytics Install Tutorial! This tutorial entails:

1. Obtaining the data
2. Getting the Git repository
3. Moving the data to the correct spot
4. Moving to the repository in terminal
5. install uv
6. creating the uv virtual enviroment
7. Auto-Installing the required python packages with the requirements.txt
8. downloading and installing Julia
9. Auto-Installing the required Julia packages with the Project.toml and Manifest.Toml
10. Linking Julia to Jupyter Lab

## We will start with Mac install instructions
**Please scroll down for Windows Install**

### First Step: obtaining the data

Find the `CNS_Majors.csv` and `20250919_Registrars_Data(in).csv` from the Microsoft teams "Data" folder. download these and make sure you have them ready and know where they are located after you download them. 

#### NOTE: Demo Dataset

For demonstration purposes, the repository also includes a sample curriculum dataset:
```bash
data/Univ_of_Arizona-Aero.csv
```
This dataset represents an example aerospace engineering curriculum and allows the visualization notebooks to run **even if the preprocessing pipeline from the reproducability notebook has not yet been executed**.

The demo notebook uses this Aerospace dataset to test that the installation was successful and that the `CurricularAnalytics` visualization tools are working correctly.


### Second Step: getting the Git repository

Open your prefered terminal app and navigate (cd) somewhere where you want to keep the repository.

then use our link to clone our repository

`git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git`

XCode may ask you to download command line tools if you have never used Git before

### Third Step: moving the data to the correct spot

you should now have a folder with all of the project materials, the next goal is to move the data downloaded in step one to the "data" folder inside of the project repository.

There is a folder in the repository called "Data", move the two files from **step one** to this folder

there are multiple ways to move the data
1. Copy (or cut) the 2 data files in your Finder and pasting in the destination folder
2. using `mv` in the terminal
3. opening 2 finder windows and dragging the data to the correct folder 

### Fourth Step: moving to the repository

Now we will be working in the repository for the rest of this tutorial make sure your terminal is working in the repository

a quick way to move to the repository in your terminal:
1. open finder
2. find the git repository folder
3. right click the folder (two finger click on trackpad)
4. hold `option`
5. look for **copy as pathname** and click it
6. open your terminal and type `cd` then paste the pathname
7. press enter

your terminal should now look like `<Computer name> MSU_Curriculum_Maps %` to the left of where you type

### Fifth Step: installing uv

`uv` is a fast and modern python package manager, we will be using this to install the packages and Jupyter lab.

to see if you have uv installed try

`uv --version`

if you see **command uv not found** we will install uv

paste this command into the terminal to install uv

`curl -LsSf https://astral.sh/uv/install.sh | sh`


if you get "command not found" you will need to reload your terminal environment by closing out and reopening

*OR*

**uv will tell you a command after install to add to the path it may look something like**

`source $HOME/.local.bin/env`

**make sure you navigate back to the repository with `cd` before continuing!!**


### Sixth Step: download python packages with uv

We will install all packages using the provided requirements txt file, this includes all of the Python packages we used for our scripts, we will have to install Julia packages later.

This also installs Jupyter lab, which we will link to Julia 

`uv sync`

the packages include 

1. ipykernel
2. ipywidgets
3. jupyter
4. jupyterlab>4.0.0
5. notebook==6.5.7
6. numpy
7. pandas
8. webio-jupyter-extension==0.1.0

### Seventh Step: download and install Julia

we will install Julia system wide 

`curl -fsSL https://install.Julialang.org | sh`

**it will ask you a question during install, just continue with the defualt configuration**

you may have to restart or open a new terminal window for Julia to be added to your PATH

OR 

**Julia will ask you to one of the commands to reload the path. I would reccomend running both just to be sure**

`source ~/.profile`

`source ~/.zshrc`

`source ~/.bash_profile`

**make sure you navigate back to the repository with `cd` before continuing!!**

### Eighth Step: auto install Julia packages

This will install all of the packages required for our project using the toml files, these are basically the same concept as python packages

`julia --project=. -e 'using Pkg; Pkg.instantiate(); Pkg.precompile()'`

### Ninth Step: link Julia to Jupyter lab

*did you know the JU in Jupyter stands for Julia?*

we can actually link Julia to Jupyter Lab to Julia, having a different language but in a familiar enviroment
this package is called IJulia this will make Julia work inside of Jupyter Lab

`julia -e 'using Pkg; Pkg.add("IJulia")'`

### Tenth Step: register the kernel with the project path
`julia --project=. -e 'using IJulia; IJulia.installkernel("Julia", env=Dict("JULIA_PROJECT"=>pwd()))'`


### Eleventh Step: opening Jupyter Lab

you should now be able to run 

`uv run jupyter lab` 

in your terminal, this will open up the familiar jupyter lab for working with our notebooks 
When creating a new notebook, you should see **Julia 1.x** in the kernel list. 

## Testing that everything works

You can test if everything works with the 
[test_install notebook](notebooks/test_install_notebook.ipynb). 
This notebook contains the commands needed to generate the Demo Degree plan visualization using the `Univ_of_Arizona-Aero.csv` dataset.

If you would like to generate visualizations using MSU Registrar and Majors data, please follow the instructions in the 
[reproducibility notebook](notebooks/reproducibility.ipynb).

# Everything now should be working and ready for our project notebooks! (Continue down for Windows Install)

## Windows Install 

### First Step: obtaining the data

Find the `CNS_Majors.csv` and `20250919_Registrars_Data(in).csv` from the Microsoft teams "Data" folder. download these and make sure you have them ready and know where they are located after you download them. 

#### NOTE: Demo Dataset

For demonstration purposes, the repository also includes a sample curriculum dataset:
```bash
data/Univ_of_Arizona-Aero.csv
```
This dataset represents an example aerospace engineering curriculum and allows the visualization notebooks to run **even if the preprocessing pipeline from the reproducability notebook has not yet been executed**.


The demo notebook uses this Aerospace dataset to test that the installation was successful and that the `CurricularAnalytics` visualization tools are working correctly.

### Second Step: getting the Git repository

Open **PowerShell** (search for it in the Start menu) and navigate (`cd`) somewhere where you want to keep the repository.

Then use our link to clone our repository:


`git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git`

If you have never used Git before, download it from [https://git-scm.com/download/win](https://git-scm.com/download/win) and install it first. Make sure to check **"Add Git to PATH"** during setup, then close and reopen PowerShell.

### Third Step: moving the data to the correct spot

You should now have a folder with all of the project materials. The next goal is to move the data downloaded in step one to the "Data" folder inside of the project repository.

There is a folder in the repository called Data move the two files from **step one** into this folder.

There are multiple ways to move the data:
1. Copy (or cut) the 2 data files in File Explorer and paste them into the destination folder
2. Use `Move-Item` in PowerShell
3. Open 2 File Explorer windows and drag the files to the correct folder

### Fourth Step: moving to the repository

From now on we will be working inside the repository for the rest of this tutorial. Make sure your terminal is working in the repository folder.

A quick way to get the path and navigate to the repository in PowerShell:
1. Open **File Explorer**
2. Find the git repository folder
3. Hold **Shift** and right-click the folder
4. Click **"Copy as path"**
5. Open PowerShell and type `cd` then paste the path
6. Press Enter

If the path has spaces, make sure it is wrapped in quotes, e.g. `cd "C:\Users\you\MSU_Curriculum_Maps"`

Your terminal should now look like this to the left of where you type:


`PS C:\...\MSU_Curriculum_Maps>`


### Fifth Step: installing uv

`uv` is a fast and modern Python package manager. We will use it to install packages and Jupyter Lab.

to see if you have uv installed try

`uv --version`

if you see **command uv not found** we will install uv

To install `uv`, run this in PowerShell:

 `-ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`


To check if `uv` installed correctly, **close and reopen PowerShell**, then run:


`uv --version`

If you get "command not found", close PowerShell completely and reopen it, the PATH needs to reload.

**Make sure you navigate back to the repository with `cd` before continuing!!**

### Sixth Step: download python packages with uv

We will install all packages using the provided requirements txt file, this includes all of the Python packages we used for our scripts, we will have to install Julia packages later.

This also installs Jupyter lab, which we will link to Julia 

`uv sync`

the packages include 

1. ipykernel
2. ipywidgets
3. jupyter
4. jupyterlab>4.0.0
5. notebook==6.5.7
6. numpy
7. pandas
8. webio-jupyter-extension==0.1.0

### Seventh Step: download and install Julia

We will install Julia system-wide (not inside the virtual environment).

Go to https://Julialang.org/downloads/manual-downloads// and use the windows installer

Run the installer and make sure to check **"Add Julia to PATH"** during setup.

After the install finishes, **close and reopen PowerShell**, then verify:

`Julia --version`

**Make sure you navigate back to the repository with `cd` before continuing!!**

### Eighth Step: auto-install Julia packages

This will install all of the packages required for our project using the TOML files. These are basically the same concept as Python packages.


`julia --project=. -e "using Pkg; Pkg.instantiate(); Pkg.precompile()"`

This may take a few minutes the first time as Julia downloads and compiles everything.


### Ninth Step: link Julia to Jupyter Lab

*Did you know the JU in Jupyter stands for Julia?*

We can actually link Julia to Jupyter Lab to Julia, having a different language but in a familiar enviroment
this package is called IJulia this will make Julia work inside of Jupyter Lab


`julia -e "using Pkg; Pkg.add('IJulia')"`

### Register the kernel with the project path
`$projectPath = (Get-Location).Path`

`julia --project=. -e "using IJulia; IJulia.installkernel('Julia', env=Dict('JULIA_PROJECT'=>'$projectPath'))"`



### Tenth Step: opening Jupyter Lab

You should now be able to run the following (make sure you are in the venv you should see `(.venv)` in your prompt!):

`jupyter lab`

This will open Jupyter Lab in your browser. When creating a new notebook, you should see **Julia 1.x** in the kernel list.

## Testing that everything works

You can test if everything works with the 
[test_install notebook](notebooks/test_install_notebook.ipynb). 
This notebook contains the commands needed to generate the Demo Degree plan visualization using the `Univ_of_Arizona-Aero.csv` dataset.

If you would like to generate visualizations using MSU Registrar and Majors data, please follow the instructions in the 
[reproducibility notebook](notebooks/reproducibility.ipynb).

# Everything should now be working and ready for our project notebooks!
