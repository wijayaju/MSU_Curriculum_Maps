# To check out what a possible website with this data could look like, we created a mockup through AI. Run the following commands in the root directory of the project in your terminal:
## Clone Repository
```bash
git clone https://github.com/wijayaju/MSU_Curriculum_Maps.git
cd MSU_Curriculum_Maps
```

## Set Up Environment
```bash
uv sync
```

## Fetch MSU Grades Data
```bash
uv run scripts/python/enrich_with_grades.py
```

## Generate Degree Plan CSVs and Analytics JSON
```bash
uv run python python/scripts/build_ca_curricula_v3.py 
--registrar data/20250919_Registrars_Data_in_.csv 
--majors data/CNS_Majors_Data.xlsx 
--output-dir outputs/degree_plans 
--grades outputs/grades_enriched.json
# outputs/degree_plans/*.csv CA-format degree plan CSVs
# outputs/degree_plans/analytics_data.json embedded in dashboard
```
The --grades flag is optional; omit it to skip grade enrichment.

## Open the Analytics Dashboard
Double-click either `curriculum_analytics_ALL.html` (to see dashboard for all colleges) or `curriculum_analytics_CNS.html` (to see dashboard for only the College of Natural Science) in Finder / Explorer (or your your file browser of choice).

** Note that average GPA doesn't work in `curriculum_analytics_ALL.html`. Both of these websites are also only mockups of what a website for this data could look like. They are best used as a reference for developing a website for this project in the future.