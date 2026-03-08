### Welcome to the MSU Curriculum Analytics Install Tutorial

This tutorial entails

1. Getting the data
2. Getting the Git repository
3. Moving the data to the correct spot
4. Moving to the repository in terminal
5. install UV
6. creating the UV virtual enviroment
7. Auto-Installing the required python packages with the requirements.txt
8. downloading and installing Julia
9. Auto-Installing the required Julia packages with the Project.toml and Manifest.Toml
10. Linking Julia to Jupyter Lab

## We will start with Mac install instructions
**Please scroll down for Windows Install**

### First step: 

Find the CNS_Majors.csv and 20250919_Registrars_Data(in).csv from the Microsoft teams "Data" folder. download these and make sure you have them ready and know where they are located after you download them.

## Demo Dataset

For demonstration purposes, the repository also includes a sample curriculum dataset:


`data/Univ_of_Arizona-Aero.csv`

This dataset represents an example aerospace engineering curriculum and allows the visualization notebooks to run **even if the preprocessing pipeline has not yet been executed**.

The demo notebook uses this Aerospace dataset to test that the installation was successful and that the `CurricularAnalytics` visualization tools are working correctly.


### Second step, getting the Git repository: 

Open your prefered terminal app and navigate (cd) somewhere where you want to keep the repository.

then use our link to clone our repository

`git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git`

XCode may ask you to download command line tools if you have never used Git before

### Third step, Moving the data to the correct spot:

you should now have a folder with all of the project materials, the next goal is to move the data downloaded in step one to the "data" folder inside of the project repository.

There is a folder in the repository called "Data", move the two files from **step one** to this folder

there are multiple ways to move the data
1. Copy (or cut) the 2 data files in your Finder and pasting in the destination folder
2. using `mv` in the terminal
3. opening 2 finder windows and dragging the data to the correct folder 

### Fourth step, moving to the repository:

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

### Fifth step, Installing UV:

UV is a fast and modern python package manager, we will be using this to install the packages and Jupyter lab.

to install uv use 

`curl -LsSf https://astral.sh/uv/install.sh | sh`

to see if you have uv installed try

`uv --version`

if you get "command not found" you will need to reload your terminal environment by closing out and reopening

*OR*

**uv will tell you a command after install to add to the path it may look something like**

`source $HOME/.local.bin/env`

**make sure you navigate back to the repository with `cd` before continuing!!**

### Sixth step, Creating the uv virtual environment:

create the virtual environment with 

`uv venv --python 3.14`

and activate it with 

`source .venv/bin/activate`

(uv will tell you the command to activate it it may differ)

Your terminal prompt will change to show (.venv) at the start, this means the environment is active.

`(MSU_Curriculum_Maps) <Computer name> MSU_Curriculum_Maps %`

### Seventh Step, download python packages with uv:

We will install all packages using the provided requirements txt file, this includes all of the Python packages we used for our scripts, we will have to install Julia packages later.

This also installs Jupyter lab, which we will link to Julia 

`uv pip install -r requirements.txt`

the packages include 
1. numpy==2.4.2
2. pandas==3.0.1
3. python-dateutil==2.9.0.post0
4. six==1.17.0

5. jupyterlab>=4.0.0
6. webio-jupyter-extension==0.1.0

### Eighth step, download and install Julia:

we will install Julia system wide 

`curl -fsSL https://install.Julialang.org | sh`

**it will ask you a question during install, just continue with the defualt configuration**

you may have to restart or open a new terminal window for Julia to be added to your PATH

OR 

**Julia will ask you to one of the commands to reload the path. I would reccomend running both just to be sure**

`. /Users/<Computer name>/.profile`

`. /Users/<Computer name>/.zshrc`

**make sure you navigate back to the repository with `cd` before continuing!!**

### Ninth step: auto install Julia packages

This will install all of the packages required for our project using the toml files, these are basically the same concept as python packages

`julia --project=. -e 'using Pkg; Pkg.instantiate(); Pkg.precompile()'`

### Tenth step, link Julia to Jupyter lab:

*did you know the JU in Jupyter stands for Julia?*

we can actually link Julia to Jupyter Lab to Julia, having a different language but in a familiar enviroment
this package is called IJulia this will make Julia work inside of Jupyter Lab

`julia -e 'using Pkg; Pkg.add("IJulia")'`

### Register the kernel with the project path
`julia --project=. -e 'using IJulia; IJulia.installkernel("Julia", env=Dict("JULIA_PROJECT"=>"'$(pwd)'"))'`



### Eleventh step, opening Jupyter Lab:

you should now be able to run (make sure you are in the venv!)

`jupyter lab`

in your terminal, this will open up the familiar jupyter lab for working with our notebooks 
When creating a new notebook, you should see **Julia 1.x** in the kernel list.

## you can test if everything works with the test_notebook.ipynb

# Everything now should be working and ready for our project notebooks! (Continue down for Windows Install)

## Windows Install 

### First step: 

Find the CNS_Majors.csv and 20250919_Registrars_Data(in).csv from the Microsoft teams "Data" folder. download these and make sure you have them ready and know where they are located after you download them.

## Demo Dataset

For demonstration purposes, the repository also includes a sample curriculum dataset:


`data/Univ_of_Arizona-Aero.csv`

This dataset represents an example aerospace engineering curriculum and allows the visualization notebooks to run **even if the preprocessing pipeline has not yet been executed**.

The demo notebook uses this Aerospace dataset to test that the installation was successful and that the `CurricularAnalytics` visualization tools are working correctly.

### Second step, getting the Git repository:

Open **PowerShell** (search for it in the Start menu) and navigate (`cd`) somewhere where you want to keep the repository.

Then use our link to clone our repository:


`git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git`

If you have never used Git before, download it from [https://git-scm.com/download/win](https://git-scm.com/download/win) and install it first. Make sure to check **"Add Git to PATH"** during setup, then close and reopen PowerShell.

### Third step, moving the data to the correct spot:

You should now have a folder with all of the project materials. The next goal is to move the data downloaded in step one to the "Data" folder inside of the project repository.

There is a folder in the repository called Data move the two files from **step one** into this folder.

There are multiple ways to move the data:
1. Copy (or cut) the 2 data files in File Explorer and paste them into the destination folder
2. Use `Move-Item` in PowerShell
3. Open 2 File Explorer windows and drag the files to the correct folder

### Fourth step, moving to the repository:

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


### Fifth step, installing UV:

UV is a fast and modern Python package manager. We will use it to install packages and Jupyter Lab.

To install UV, run this in PowerShell:

 `-ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`


To check if UV installed correctly, **close and reopen PowerShell**, then run:


`uv --version`

If you get "command not found", close PowerShell completely and reopen it, the PATH needs to reload.

**Make sure you navigate back to the repository with `cd` before continuing!!**

### Sixth step, creating the UV virtual environment:

Create the virtual environment with:

`uv venv --python 3.14`

Then activate it with:

`.venv\Scripts\activate`

*UV will tell you the activation command after creating the environment, use whatever it shows if it differs from above.*

Your terminal prompt will change to show (.venv) at the start, which means the environment is active:

`(.venv) PS C:\...\MSU_Curriculum_Maps>`

**Every time you open a new PowerShell window you will need to `cd` back into the repository and run `.venv\Scripts\activate` again before doing any work.**

### Seventh step, download Python packages with UV:

We will install all packages using the provided requirements.txt file. This includes all of the Python packages used in our scripts, as well as Jupyter Lab and the WebIO extension which we will link to Julia.

`uv pip install -r requirements.txt`

### Eighth step, download and install Julia:

We will install Julia system-wide (not inside the virtual environment).

Go to https://Julialang.org/downloads/manual-downloads// and use the windows installer

Run the installer and make sure to check **"Add Julia to PATH"** during setup.

After the install finishes, **close and reopen PowerShell**, then verify:

`Julia --version`

**Make sure you navigate back to the repository with `cd` before continuing!!**

### Ninth step, auto-install Julia packages:

This will install all of the packages required for our project using the TOML files. These are basically the same concept as Python packages.


`julia --project=. -e "using Pkg; Pkg.instantiate(); Pkg.precompile()"`

This may take a few minutes the first time as Julia downloads and compiles everything.


### Tenth step, link Julia to Jupyter Lab:

*Did you know the JU in Jupyter stands for Julia?*

We can actually link Julia to Jupyter Lab to Julia, having a different language but in a familiar enviroment
this package is called IJulia this will make Julia work inside of Jupyter Lab


`julia -e "using Pkg; Pkg.add('IJulia')"`

### Register the kernel with the project path
`$projectPath = (Get-Location).Path`

`julia --project=. -e "using IJulia; IJulia.installkernel('Julia', env=Dict('JULIA_PROJECT'=>'$projectPath'))"`



### Eleventh step, opening Jupyter Lab:

You should now be able to run the following (make sure you are in the venv you should see `(.venv)` in your prompt!):

`jupyter lab`

This will open Jupyter Lab in your browser. When creating a new notebook, you should see **Julia 1.x** in the kernel list.

## you can test if everything works with the test_notebook.ipynb

# Everything should now be working and ready for our project notebooks!


```python

```
