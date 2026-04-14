# MSU Curriculum Analytics for [CurricularAnalytics.org](https://curricularanalytics.org/home$0)
 **welcome to the CurricularAnalytics.org setup!**

this tutorial is different from the INSTALL.md as we will not have a full environment setup.

the process for this tutorial will be simpler this tutorial covers:

**if you have already completed the [INSTALL.md](INSTALL.md) please skip to step 8**

1. Obtaining the data
2. Getting the Git repository
3. Moving the data to the correct spot
4. Moving to the repository in terminal
5. install uv
6. Download packages for script
7. Running the script
1. Create an account 
4. Upload Curricula to CurricularAnalytics.org 
5. Viewing

## Why are there two different tutorials?
This tutorial serves as a way to use our data with the CurricularAnalytics.org website. This website is a way to visualize the generated curriculums without the setup and installation of anything on the user side, once Curriculum are uploaded to the website, they are able to be shared with other users of the site.

### Issues with CurricularAnalytics.org
The major flaw with the website is there is no way to customize the expirence, the website allows the viewing of degree plan graphs, but lacks our custom implementations like course insights using MSUGrades.com and explinations of the different metrics inside of the full project. **The team highly reccomends using the full setup guide in [INSTALL.md](INSTALL.md)**

## We will start with Mac install instructions
**Please scroll down for Windows Install**

### First Step: obtaining the data

Find the `CNS_Majors.csv` and `20250919_Registrars_Data(in).csv` from the Microsoft teams "Data" folder. download these and make sure you have them ready and know where they are located after you download them. 


### Second Step: getting the Git repository
**open the terminal app**

first we will move somewhere where we can see the files

`cd Downloads`

create a new folder with


`mkdir MSUCA`

then move inside of the directory with

`cd MSUCA`

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

`uv` is a fast and modern python package manager, we will be using this to install the packages to run the script

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

We will install all packages using the provided files in the github, this includes all of the Python packages we used for our scripts.

`uv sync`

## Seventh Step: Run the Script to generate data files

Copy this and paste into the terminal and press enter. 

This code takes the relevant features from the two different downloaded datasets and creates a new file for each seperate degreee in the College of Natural Science at MSU

```bash
uv run python python/scripts/build_ca_curricula_v2.py \
  --registrar "data/20250919_Registrars_Data(in).csv" \
  --majors "data/CNS_Majors_Data.xlsx" \
  --output-dir outputs
```

## Eigth Step: Making an account 

Go to https://curricularanalytics.org/home and press "Sign Up" in the top right. 

## Ninth Step: Uploading Curriulum
Once you are logged in, you can press the bulk upload button in the top right and select all of the generated data in the `outputs` folder and upload them to the website.

## Tenth Step: Viewing the Curriculum 

now that you have uploaded all of the files, you can now view the graphs using the "curricula" button on the top


## Windows Install Instructions
 
### First Step: Obtaining the Data
 
Find the `CNS_Majors.csv` and `20250919_Registrars_Data(in).csv` from the Microsoft Teams "Data" folder. Download these and make sure you have them ready and know where they are located.
 
### Second Step: Getting the Git Repository
 
**Open Command Prompt** by pressing `Windows Key + R`, typing `cmd`, and pressing Enter.
 
First, move to your Downloads folder:
 
```
cd %USERPROFILE%\Downloads
```
 
Create a new folder:
 
```
mkdir MSUCA
```
 
Move inside the new directory:
 
```
cd MSUCA
```
 
Clone the repository:
 
```
git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git
```
 
> **Note:** If Git is not installed, download and install it from [https://git-scm.com/download/win](https://git-scm.com/download/win), then reopen Command Prompt and try again.
 
### Third Step: Moving the Data to the Correct Spot
 
You should now have a folder with all of the project materials. Move the two data files downloaded in Step One into the `Data` folder inside the project repository.
 
There are multiple ways to do this:
1. Copy (or cut) the 2 data files in File Explorer and paste them into the destination folder
2. Use the `move` command in Command Prompt
3. Open 2 File Explorer windows and drag the files to the correct folder
 
### Fourth Step: Navigating to the Repository
 
For the rest of this tutorial, your Command Prompt needs to be working inside the repository.
 
A quick way to navigate there:
1. Open File Explorer
2. Find the cloned repository folder (`MSUCA\MSU_Curriculum_Maps`)
3. Click on the address bar at the top of the File Explorer window
4. The full path will be highlighted — copy it
5. In Command Prompt, type `cd ` then paste the path and press Enter
 
Your Command Prompt should now show something like `C:\Users\YourName\Downloads\MSUCA\MSU_Curriculum_Maps>` on the left.
 
### Fifth Step: Installing uv
 
`uv` is a fast and modern Python package manager. We will use it to install the packages needed to run the script.
 
First, check if you already have it:
 
```
uv --version
```
 
If you see **'uv' is not recognized**, install it by running this in Command Prompt:
 
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
 
After installation, **close and reopen Command Prompt** to refresh your environment, then navigate back to the repository using `cd` before continuing.
 
### Sixth Step: Download Python Packages with uv
 
Install all required packages using the provided files in the GitHub repository:
 
```
uv sync
```
 
### Seventh Step: Run the Script to Generate Data Files
 
Copy and paste the following into Command Prompt and press Enter.
 
This script pulls the relevant features from the two downloaded datasets and creates a new file for each separate degree in the College of Natural Science at MSU:
 
```
uv run python python/scripts/build_ca_curricula_v2.py --registrar "data/20250919_Registrars_Data(in).csv" --majors "data/CNS_Majors_Data.xlsx" --output-dir outputs
```
 
### Eighth Step: Making an Account
 
Go to [https://curricularanalytics.org/home](https://curricularanalytics.org/home) and press **Sign Up** in the top right.
 
### Ninth Step: Uploading the Curriculum
 
Once logged in, press the **Bulk Upload** button in the top right and select all of the generated files from the `outputs` folder inside the repository.
 
### Tenth Step: Viewing the Curriculum
 
Now that you have uploaded all of the files, you can view the graphs by clicking the **Curricula** button at the top of the page.