# MSU Curriculum Analytics for [CurricularAnalytics.org](https://curricularanalytics.org/home)

**Welcome to the CurricularAnalytics.org setup!**

This tutorial is different from the [INSTALL.md](INSTALL.md) because it does **not require a full local environment setup**.

Instead, this workflow focuses on:

* Generating curriculum CSV files
* Uploading them to CurricularAnalytics.org for visualization and sharing

> **Note:** If you have already completed the full setup in [INSTALL.md](INSTALL.md), you can skip to Step 7.


## Why are there two different tutorials?

This tutorial is a simplified workflow for generating curriculum files and viewing them using the **CurricularAnalytics.org website**.

This website allows you to:

* Upload curriculum files
* Visualize prerequisite graphs
* Share curriculum structures with others

However, it does **not include**:

* MSU Grades integration
* Orphanate filtering
* Custom metric explanations from the full project

For full functionality, the team **recommends using the complete setup in [INSTALL.md](INSTALL.md)**.


## Important Note on Scripts

This tutorial uses:

```bash
scripts/python/build_ca_curricula_v2.py
```

This script generates **Curricular Analytics–compatible CSV files** that can be uploaded directly to the website.

The `v3` script is used for the **local website prototype** and is not required for this workflow.


## We will start with Mac install instructions

**Please scroll down for Windows Install**


### Step 1: Obtaining the data

Find the following files from the Microsoft Teams “Data” folder:

* `CNS_Majors.csv`
* `20250919_Registrars_Data(in).csv`

Download them and make sure you know where they are located.


### Step 2: Getting the Git repository

Open the terminal app.

Move somewhere convenient:

```bash
cd Downloads
```

Create a folder:

```bash
mkdir MSUCA
cd MSUCA
```

Clone the repository:

```bash
git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git
```


### Step 3: Moving the data to the correct spot

Move the downloaded files into the `data/` folder inside the repository.

There are multiple ways to do this:

1. Copy and paste in Finder
2. Use `mv` in the terminal
3. Drag and drop between windows


### Step 4: Moving to the repository

Navigate into the repository:

```bash
cd MSU_Curriculum_Maps
```


### Step 5: Installing uv

Check if uv is installed:

```bash
uv --version
```

If not, install it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If needed, **close and reopen your terminal**, then return to the repository.


### Step 6: Install Python packages

Install required packages:

```bash
uv sync
```


### Step 7: Run the script to generate data files

Run the following command:

```bash
uv run python scripts/python/build_ca_curricula_v2.py \
  --registrar "data/20250919_Registrars_Data(in).csv" \
  --majors "data/CNS_Majors_Data.xlsx" \
  --output-dir outputs
```

This will:

* Process the input datasets
* Generate one CSV file per degree plan
* Save them in the `outputs/` folder


### Step 8: Create an account

Go to:

[https://curricularanalytics.org/home](https://curricularanalytics.org/home)

Click **Sign Up** in the top right.


### Step 9: Upload curriculum files

Once logged in:

* Click **Bulk Upload**
* Select all files in the `outputs/` folder

These files are already formatted correctly and can be uploaded directly.


### Step 10: View the curriculum

After uploading:

* Click **Curricula** at the top
* Select a curriculum to view the graph


# Windows Install Instructions


### Step 1: Obtain the data

Download:

* `CNS_Majors.csv`
* `20250919_Registrars_Data(in).csv`


### Step 2: Get the repository

Open Command Prompt.

```bash
cd %USERPROFILE%\Downloads
mkdir MSUCA
cd MSUCA
git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git
```


### Step 3: Move the data

Move files into:

```bash
data/
```


### Step 4: Navigate to repository

```bash
cd MSU_Curriculum_Maps
```


### Step 5: Install uv

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart Command Prompt afterward.


### Step 6: Install Python packages

```bash
uv sync
```


### Step 7: Run the script

```bash
uv run python scripts/python/build_ca_curricula_v2.py --registrar "data/20250919_Registrars_Data(in).csv" --majors "data/CNS_Majors_Data.xlsx" --output-dir outputs
```


### Step 8: Create account

[https://curricularanalytics.org/home](https://curricularanalytics.org/home)


### Step 9: Upload files

Use **Bulk Upload** and select all files in `outputs/`.


### Step 10: View

Click **Curricula** and explore the graphs.


# Done

You should now be able to:

* Generate curriculum CSV files
* Upload them to CurricularAnalytics.org
* View and share curriculum graphs