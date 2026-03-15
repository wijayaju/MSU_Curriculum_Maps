"""
Convert MSU CNS Majors Data + Registrar Prerequisites Data
to CurricularAnalytics.jl CSV format (Degree Plan format).

CurricularAnalytics.jl Degree Plan CSV Format:
  Line 1:  Curriculum,<plan name>
  Line 2:  Institution,<institution name>
  Line 3:  Degree Type,<BS|BA|...>
  Line 4:  System Type,<semester|quarter>
  Line 5:  CIP,<optional>
  Line 6:  Courses
  Line 7+: Course ID,Course Name,Prefix,Number,Prerequisites,Corequisites,
            Strict-Corequisites,Credit Hours,Institution Credit Hours,
            Canonical Name,Term

One CSV file is produced per unique Plan Title in the source data.

Expected project layout (run from MSU_Curriculum_Maps/):
  MSU_Curriculum_Maps/
  ├── data/
  │   ├── CNS_Majors_Data.csv
  │   └── 20250919_Registrars_Data(in).csv
  ├── outputs/
  │   └── ca_degree_plans/          <- generated here
  └── python/scripts/
      └── preprocess.py   <- this file
"""

import pandas as pd

import re
import csv
from pathlib import Path

# Paths
SCRIPT_DIR   = Path(__file__).resolve().parent                  # MSU_Curriculum_Maps/python/scripts/
PROJECT_ROOT = SCRIPT_DIR.parents[1]                            # MSU_Curriculum_Maps/
DATA_DIR     = PROJECT_ROOT / "data"                            # MSU_Curriculum_Maps/data
OUTPUT_DIR   = PROJECT_ROOT / "outputs" / "ca_degree_plans"     # MSU_Curriculum_Maps/outputs/ca_degree_plans

# Load data
plans_df = pd.read_excel(DATA_DIR / "CNS_Majors_Data.xlsx", sheet_name="Sheet1")
reqs_df  = pd.read_csv(DATA_DIR / "20250919_Registrars_Data(in).csv",
                       encoding='latin1')

# Build prerequisite lookup from registrar data
# Each row with REQUISITE_TYPE == 'PRE' and a non-null RQDET_CRSE is a prereq edge.
# RQDET_CRSE looks like "MTH 116 (120644-College of Natural Science Mathematics)"
# We extract just "SUBJECT CODE" e.g. "MTH 116".
def parse_course_key(raw):
    """Extract 'SUBJ CODE' from a RQDET_CRSE string, e.g. 'MTH 116 (12345-...)'."""
    if pd.isna(raw):
        return None
    m = re.match(r'^([A-Z]+)\s+(\w+)', str(raw).strip())
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return None

# Convert term ordering
def term_number(year_str, term_str):
    """Convert Year+Term to a sequential 1-based term number."""
    y = YEAR_ORDER.get(year_str, 5)
    t = TERM_ORDER.get(term_str, 1)
    # 3 terms per year
    return (y - 1) * 3 + t

# Helper: clean course name for use as a course key
def clean_key(course_str):
    """Normalise a course string like 'MTH 132' for lookup."""
    return str(course_str).strip()

# Build dict: course_key -> list of prereq course_keys (PRE only)
prereq_map = {}   # course_key -> set of prereq keys
coreq_map  = {}   # course_key -> set of coreq keys
title_map  = {}   # course key -> COURSE_TITLE_LONG

for _, row in reqs_df.iterrows():
    subj = str(row['SUBJECT']).strip()
    code = str(row['CRSE_CODE']).strip()
    course_key = f"{subj} {code}"
    # Store the long title (first non-null value wins)
    if course_key not in title_map:
        raw_title = row.get('COURSE_TITLE_LONG')
        if pd.notna(raw_title) and str(raw_title).strip():
            title_map[course_key] = str(raw_title).strip()
    req_type = str(row.get('REQUISITE_TYPE', '')).strip()
    rqdet = parse_course_key(row.get('RQDET_CRSE'))
    if rqdet is None:
        continue
    if req_type == 'PRE':
        prereq_map.setdefault(course_key, set()).add(rqdet)
    elif req_type == 'CO':
        coreq_map.setdefault(course_key, set()).add(rqdet)

# Term ordering
YEAR_ORDER = {'Freshman': 1, 'Sophomore': 2, 'Junior': 3, 'Senior': 4}
TERM_ORDER = {'FS': 1, 'SS': 2, 'US': 3}   # Fall, Spring, Summer

# Build CurricularAnalytics CSV for each plan
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plan_titles = plans_df['Plan Title'].dropna().unique()
print(f"Found {len(plan_titles)} unique plan titles. Converting…")

def safe_filename(name):
    """Turn a plan title into a safe filename."""
    return re.sub(r'[^\w\s\-]', '', name).replace(' ', '_')[:80] + '.csv'

records = []  # summary of what we produced

for plan_title in sorted(plan_titles):
    plan_rows = plans_df[plans_df['Plan Title'] == plan_title].copy()

    # Metadata from the first row
    first = plan_rows.iloc[0]
    institution  = "Michigan State University"
    degree_type  = str(first.get('Award Type', 'BS')).strip()
    system_type  = "semester"

    # Assign sequential term numbers
    plan_rows = plan_rows.copy()
    plan_rows['term_num'] = plan_rows.apply(
        lambda r: term_number(r['Year'], r['Term']), axis=1
    )

    # Sort by term
    plan_rows = plan_rows.sort_values(['term_num', 'Course']).reset_index(drop=True)

    # Assign unique Course IDs (1-based, within this plan)
    course_list = plan_rows['Course'].tolist()
    # Build a stable mapping course_name -> course_id
    course_id_map = {}
    for i, course in enumerate(course_list, start=1):
        key = clean_key(course)
        if key not in course_id_map:
            course_id_map[key] = i

    # Build output rows
    course_rows = []
    for _, row in plan_rows.iterrows():
        raw_course  = clean_key(row['Course'])
        course_id   = course_id_map[raw_course]
        term_num    = int(row['term_num'])
        credit_hrs  = row.get('Credits Min', 3)
        if pd.isna(credit_hrs):
            credit_hrs = 3
        credit_hrs = int(credit_hrs)

        # Parse prefix and number from course string like "MTH 132" or "ISS 200-Level"
        m = re.match(r'^([A-Z]+)\s+(\S+)', raw_course)
        if m:
            prefix = m.group(1)
            number = m.group(2)
        else:
            prefix = ''
            number = raw_course

        # Look up prerequisites for this course (by its key e.g. "MTH 132")
        prereq_ids = []
        for prereq_key in prereq_map.get(raw_course, []):
            if prereq_key in course_id_map:
                prereq_ids.append(str(course_id_map[prereq_key]))

        coreq_ids = []
        for coreq_key in coreq_map.get(raw_course, []):
            if coreq_key in course_id_map:
                coreq_ids.append(str(course_id_map[coreq_key]))

        # Use long title from registrar data; fall back to raw course string
        course_name = title_map.get(raw_course, raw_course)

        course_rows.append({
            'Course ID':                  course_id,
            'Course Name':                course_name,
            'Prefix':                     prefix,
            'Number':                     number,
            'Prerequisites':              ';'.join(prereq_ids),
            'Corequisites':               ';'.join(coreq_ids),
            'Strict-Corequisites':        '',
            'Credit Hours':               credit_hrs,
            'Institution Credit Hours':   '',
            'Canonical Name':             raw_course,
            'Term':                       term_num,
        })

    # Write CurricularAnalytics CSV
    fname = safe_filename(plan_title)
    fpath = OUTPUT_DIR / fname

    with open(fpath, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        # Header block (no leading comma — CA format uses plain key,value rows)
        w.writerow(['Curriculum', plan_title])
        w.writerow(['Institution', institution])
        w.writerow(['Degree Type', degree_type])
        w.writerow(['System Type', system_type])
        w.writerow(['CIP', ''])
        # Courses section header
        w.writerow(['Courses'])
        w.writerow([
            'Course ID', 'Course Name', 'Prefix', 'Number',
            'Prerequisites', 'Corequisites', 'Strict-Corequisites',
            'Credit Hours', 'Institution Credit Hours', 'Canonical Name', 'Term'
        ])
        for cr in course_rows:
            w.writerow([
                cr['Course ID'],
                cr['Course Name'],
                cr['Prefix'],
                cr['Number'],
                cr['Prerequisites'],
                cr['Corequisites'],
                cr['Strict-Corequisites'],
                cr['Credit Hours'],
                cr['Institution Credit Hours'],
                cr['Canonical Name'],
                cr['Term'],
            ])

    records.append({
        'Plan Title': plan_title,
        'File': fname,
        'Courses': len(course_rows),
        'Terms': plan_rows['term_num'].nunique(),
    })
    print(f"{plan_title}  ->  {fname}  ({len(course_rows)} courses)")

# Write summary index
summary_df = pd.DataFrame(records)
summary_path = OUTPUT_DIR / '_summary.csv'
summary_df.to_csv(summary_path, index=False)

print(f"\nDone! {len(records)} curriculum CSVs written to: {OUTPUT_DIR}")
print(f"Summary written to: {summary_path}")
