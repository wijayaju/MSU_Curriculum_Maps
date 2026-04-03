import pandas as pd
import csv
import os
import re
from collections import defaultdict


# -----------------------------
# Helpers
# -----------------------------

def split_course_code(course):
    """
    Split only simple course codes like 'MTH 103' or 'MTH 491A'.
    Return ('', '') for placeholders like:
    - ISS 200-Level
    - IAH 211 or Higher
    - MTH 235 or MTH 340
    - Electives
    """
    normalized = normalize_course_code(course)
    if not normalized:
        return "", ""

    parts = normalized.split()
    if len(parts) == 2:
        return parts[0], parts[1]

    return "", ""


def normalize_course_code(text):
    """
    Normalize a simple course code to 'SUBJ NUM', for example:
    'mth 103' -> 'MTH 103'
    'MTH   491A' -> 'MTH 491A'

    Returns None if the text is not a simple single course code.
    """
    if not isinstance(text, str):
        return None

    text = text.strip().upper()
    m = re.fullmatch(r"([A-Z]{2,4})\s+([0-9]{3}[A-Z]?)", text)
    if not m:
        return None

    return f"{m.group(1)} {m.group(2)}"


def extract_course_codes(text):
    """
    Extract all simple course codes from a messy registrar field.

    Examples:
    'ACC 201 (100090-...) , ACC 202 (100091-...)' -> ['ACC 201', 'ACC 202']
    """
    if not isinstance(text, str):
        return []

    matches = re.findall(r"\b([A-Z]{2,4})\s+([0-9]{3}[A-Z]?)\b", text.upper())
    seen = []
    seen_set = set()

    for subj, num in matches:
        code = f"{subj} {num}"
        if code not in seen_set:
            seen.append(code)
            seen_set.add(code)

    return seen


def term_to_number(year, term):
    """
    Convert Freshman/Sophomore/etc + FS/SS to CA term number.
    """
    year_map = {
        "Freshman": 0,
        "Sophomore": 1,
        "Junior": 2,
        "Senior": 3,
        "Fifth Year": 4,
    }

    term_map = {
        "FS": 1,
        "SS": 2,
    }

    if year not in year_map or term not in term_map:
        return ""

    return year_map[year] * 2 + term_map[term]


def sanitize_filename(text):
    """
    Convert plan title into a filesystem-safe filename.
    """
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r"[^\w]+", "_", text).strip("_") + ".csv"


def pad_row(values, total_cols=11):
    """
    Pad metadata rows so every row in the CSV has the same number of columns.
    """
    values = list(values)
    if len(values) < total_cols:
        values += [""] * (total_cols - len(values))
    return values


def read_registrar_csv(path):
    """
    Try common encodings used in registrar exports. 
    (This is basically cause Oracle's SQL Developer defaults to cp1252 encoding for CSV exports, 
    which can cause issues if the data contains characters that aren't valid in that encoding.)
    """
    encodings_to_try = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

    last_error = None
    for enc in encodings_to_try:
        try:
            print(f"Trying registrar CSV encoding: {enc}", flush=True)
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except UnicodeDecodeError as e:
            last_error = e

    raise last_error


def parse_prereq_courses(registrar_df):
    """
    Build dict:
    'ACC 300' -> {'ACC 201', 'ACC 202', ...}

    Uses:
    - SUBJECT + CRSE_CODE as the target course
    - RQDET_CRSE for direct course references
    - CourseList for course-list style prereqs

    Intentionally does NOT parse DESCR254A because that plain-language field
    mixes prerequisites with restrictions and other noisy text.
    """
    prereqs = defaultdict(set)

    for _, row in registrar_df.iterrows():
        subject = row.get("SUBJECT", "")
        crse_code = row.get("CRSE_CODE", "")

        if pd.isna(subject) or pd.isna(crse_code):
            continue

        target_course = normalize_course_code(
            f"{str(subject).strip()} {str(crse_code).strip()}"
        )
        if not target_course:
            continue

        rqdet = row.get("RQDET_CRSE", "")
        for prereq_code in extract_course_codes(rqdet):
            if prereq_code != target_course:
                prereqs[target_course].add(prereq_code)

        course_list = row.get("CourseList", "")
        for prereq_code in extract_course_codes(course_list):
            if prereq_code != target_course:
                prereqs[target_course].add(prereq_code)

    return prereqs


# -----------------------------
# Main builder
# -----------------------------

def build_curricula(registrar_csv, majors_xlsx, output_dir):
    print("Loading input files...", flush=True)

    os.makedirs(output_dir, exist_ok=True)

    registrar = read_registrar_csv(registrar_csv)
    majors = pd.read_excel(majors_xlsx)

    required_registrar_cols = {"SUBJECT", "CRSE_CODE"}
    required_majors_cols = {
        "Plan Title",
        "Award Type",
        "Course",
        "Year",
        "Term",
        "Credits Max",
        "Credits Min",
    }

    missing_registrar = required_registrar_cols - set(registrar.columns)
    missing_majors = required_majors_cols - set(majors.columns)

    if missing_registrar:
        raise ValueError(
            f"Registrar file is missing required columns: {sorted(missing_registrar)}"
        )

    if missing_majors:
        raise ValueError(
            f"Majors file is missing required columns: {sorted(missing_majors)}"
        )

    plan_titles = majors["Plan Title"].dropna().unique()
    prereq_map = parse_prereq_courses(registrar)

    print(
        f"Loaded registrar rows: {len(registrar):,}, "
        f"major rows: {len(majors):,}, "
        f"plans: {len(plan_titles):,}, "
        f"registrar courses with extracted prereqs: {len(prereq_map):,}",
        flush=True,
    )
    print("Generating CA curriculum CSV files...", flush=True)

    summary = []
    files_written = 0

    for i, plan in enumerate(plan_titles, start=1):
        plan_df = majors[majors["Plan Title"] == plan].copy()

        if plan_df.empty:
            continue

        curriculum_name = str(plan).strip()
        degree_type = str(plan_df["Award Type"].iloc[0]).strip()

        filename = sanitize_filename(curriculum_name)
        out_path = os.path.join(output_dir, filename)

        rows = []
        course_id_map = {}
        course_term_map = {}
        next_id = 1

        for _, r in plan_df.iterrows():
            course = r["Course"]

            if pd.isna(course):
                continue

            course = str(course).strip()
            normalized_course = normalize_course_code(course)
            prefix, number = split_course_code(course)
            term = term_to_number(r["Year"], r["Term"])

            credits = r["Credits Max"]
            if pd.isna(credits):
                credits = r["Credits Min"]
            if pd.isna(credits):
                credits = ""

            if isinstance(credits, float) and credits.is_integer():
                credits = int(credits)

            course_id = next_id
            next_id += 1

            rows.append({
                "Course ID": course_id,
                "Course Name": course,
                "Normalized Course": normalized_course,
                "Prefix": prefix,
                "Number": number,
                "Prerequisites": "",
                "Corequisites": "",
                "Strict-Corequisites": "",
                "Credit Hours": credits,
                "Institution": "",
                "Canonical Name": "",
                "Term": term,
            })

            if normalized_course:
                course_id_map[normalized_course] = course_id
                course_term_map[normalized_course] = term

        # Fill prereqs/coreqs based on relative term position
        for row in rows:
            normalized_course = row["Normalized Course"]

            if normalized_course and normalized_course in prereq_map:
                prereq_ids = []
                coreq_ids = []

                for related_course in sorted(prereq_map[normalized_course]):
                    if related_course in course_id_map and related_course in course_term_map:
                        related_id = course_id_map[related_course]
                        related_term = course_term_map[related_course]
                        target_term = row["Term"]

                        if isinstance(related_term, int) and isinstance(target_term, int):
                            if related_term < target_term:
                                prereq_ids.append(str(related_id))
                            elif related_term == target_term:
                                coreq_ids.append(str(related_id))

                if prereq_ids:
                    row["Prerequisites"] = ";".join(prereq_ids)

                if coreq_ids:
                    row["Corequisites"] = ";".join(coreq_ids)

        assigned_prereq_count = sum(1 for row in rows if row["Prerequisites"])
        assigned_coreq_count = sum(1 for row in rows if row["Corequisites"])

        # Sort rows by final term order before writing.
        # This helps if the visualization is reading CSV rows sequentially.
        rows.sort(
            key=lambda r: (
                r["Term"] if isinstance(r["Term"], int) else 999,
                r["Course ID"],
            )
        )

        # Write CA-format CSV
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)

            w.writerow(pad_row(["Curriculum", curriculum_name]))
            w.writerow(pad_row(["Institution", "Michigan State University"]))
            w.writerow(pad_row(["Degree Type", degree_type]))
            w.writerow(pad_row(["System Type", "semester"]))
            w.writerow(pad_row(["CIP", ""]))
            w.writerow(pad_row(["Courses"]))
            w.writerow([
                "Course ID",
                "Course Name",
                "Prefix",
                "Number",
                "Prerequisites",
                "Corequisites",
                "Strict-Corequisites",
                "Credit Hours",
                "Institution",
                "Canonical Name",
                "Term",
            ])

            for r in rows:
                w.writerow([
                    r["Course ID"],
                    r["Course Name"],
                    r["Prefix"],
                    r["Number"],
                    r["Prerequisites"],
                    r["Corequisites"],
                    r["Strict-Corequisites"],
                    r["Credit Hours"],
                    r["Institution"],
                    r["Canonical Name"],
                    r["Term"],
                ])

        summary.append([
            curriculum_name,
            filename,
            len(rows),
            assigned_prereq_count,
            assigned_coreq_count,
        ])
        files_written += 1

        if i <= 5:
            print(
                f"{curriculum_name}: "
                f"{assigned_prereq_count} courses with prereqs, "
                f"{assigned_coreq_count} courses with coreqs",
                flush=True,
            )

        if i % 50 == 0:
            print(f"Processed {i:,} of {len(plan_titles):,} plans...", flush=True)

    summary_path = os.path.join(output_dir, "_summary.csv")
    pd.DataFrame(
        summary,
        columns=[
            "Plan",
            "File",
            "Row Count",
            "Courses With Prereqs",
            "Courses With Coreqs",
        ],
    ).to_csv(summary_path, index=False)

    print(
        f"Done. Wrote {files_written:,} curriculum files to '{output_dir}'.",
        flush=True,
    )
    print(f"Summary written to: {summary_path}", flush=True)


# -----------------------------
# CLI
# -----------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--registrar", required=True)
    parser.add_argument("--majors", required=True)
    parser.add_argument("--output-dir", required=True)

    args = parser.parse_args()

    build_curricula(
        args.registrar,
        args.majors,
        args.output_dir
    )