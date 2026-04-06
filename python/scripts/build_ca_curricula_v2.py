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
# Analytics JSON builder
# Produces the data blob that gets embedded in curriculum_analytics.html.
# Optionally merges in grade data from enrich_with_grades.py output.
# -----------------------------

def build_analytics_json(registrar_csv, majors_xlsx, output_dir,
                          grades_json=None):
    """
    Build outputs/analytics_data.json, which is the single data file
    consumed by curriculum_analytics.html.

    If grades_json points to the output of enrich_with_grades.py, each
    course entry is enriched with avg_gpa, dfw_rate, total_students,
    sections, most_recent_semester, trend_gpa, and grade-bucket pct_*.
    """
    import json
    import networkx as nx

    print("Building analytics JSON ...", flush=True)

    registrar = read_registrar_csv(registrar_csv)
    majors    = pd.read_excel(majors_xlsx)

    prereq_map    = parse_prereq_courses(registrar)
    course_info   = {}
    for _, row in registrar.iterrows():
        s = row.get("SUBJECT", ""); c = row.get("CRSE_CODE", "")
        if pd.isna(s) or pd.isna(c):
            continue
        code = normalize_course_code(f"{str(s).strip()} {str(c).strip()}")
        if code and code not in course_info:
            title = row.get("COURSE_TITLE_LONG", "")
            dept  = row.get("ACAD_ORG_U1_DESCRFORMAL", "")
            course_info[code] = {
                "title": "" if pd.isna(title) else str(title),
                "dept":  "" if pd.isna(dept)  else str(dept),
            }

    plan_titles = majors["Plan Title"].dropna().unique()

    # Build per-plan course lists
    plans_data = {}
    course_plan_membership = defaultdict(set)

    for plan in plan_titles:
        plan_df = majors[majors["Plan Title"] == plan].copy()
        if plan_df.empty:
            continue
        courses_in_plan = []
        for _, r in plan_df.iterrows():
            course = str(r["Course"]).strip() if not pd.isna(r["Course"]) else ""
            norm   = normalize_course_code(course)
            if not norm:
                continue
            year = str(r.get("Year", ""))
            term = str(r.get("Term", ""))
            tn   = term_to_number(year, term)
            cred = r.get("Credits Max")
            if pd.isna(cred):
                cred = r.get("Credits Min", 3)
            if pd.isna(cred):
                cred = 3
            if isinstance(cred, float) and cred == int(cred):
                cred = int(cred)
            courses_in_plan.append({
                "code": norm, "year": year, "term": term,
                "term_num": tn, "credits": cred,
            })
            course_plan_membership[norm].add(plan)

        plans_data[plan] = {
            "award_type":  str(plan_df["Award Type"].iloc[0]),
            "major_title": (str(plan_df["Major Title"].iloc[0])
                            if not pd.isna(plan_df["Major Title"].iloc[0])
                            else str(plan)),
            "major_code":  str(plan_df["Major"].iloc[0]),
            "courses":     courses_in_plan,
        }

    all_cns_courses = set(
        c["code"] for pd_data in plans_data.values() for c in pd_data["courses"]
    )

    # Build directed graph (full prereq graph for chain depth,
    # CNS-only graph for edges shown in dashboard)
    G_full = nx.DiGraph()
    for code in all_cns_courses:
        G_full.add_node(code)
        for prereq in prereq_map.get(code, []):
            G_full.add_edge(prereq, code)

    # Remove cycles to get DAG for chain depth
    G_dag = G_full.copy()
    for _ in range(10):
        try:
            cycle = nx.find_cycle(G_dag)
            G_dag.remove_edge(*cycle[0])
        except nx.NetworkXNoCycle:
            break

    chain_depth = {}
    try:
        for node in nx.topological_sort(G_dag):
            preds = list(G_dag.predecessors(node))
            chain_depth[node] = (
                max(chain_depth.get(p, 0) for p in preds) + 1
                if preds else 0
            )
    except nx.NetworkXUnfeasible:
        chain_depth = {n: 0 for n in G_dag.nodes}

    G_cns = nx.DiGraph()
    for code in all_cns_courses:
        G_cns.add_node(code)
    for code in all_cns_courses:
        for prereq in prereq_map.get(code, []):
            if prereq in all_cns_courses:
                G_cns.add_edge(prereq, code)

    in_degree    = dict(G_cns.in_degree())
    out_degree   = dict(G_cns.out_degree())
    betweenness  = nx.betweenness_centrality(G_cns)
    cross_major  = {c: len(p) for c, p in course_plan_membership.items()}

    # Load grades enrichment if provided
    grades: dict = {}
    if grades_json and os.path.exists(grades_json):
        with open(grades_json, encoding="utf-8") as f:
            grades = json.load(f)
        matched = sum(1 for c in all_cns_courses if c in grades)
        print(f"  Grades data: {matched}/{len(all_cns_courses)} CNS courses matched",
              flush=True)
    elif grades_json:
        print(f"  Warning: grades file not found: {grades_json}", flush=True)
        print("  Run enrich_with_grades.py first to add GPA/DFW data.", flush=True)

    # Assemble final analytics object
    course_analytics = {}
    for code in all_cns_courses:
        entry = {
            "title":             course_info.get(code, {}).get("title", ""),
            "dept":              course_info.get(code, {}).get("dept",  ""),
            "in_degree":         in_degree.get(code, 0),
            "out_degree":        out_degree.get(code, 0),
            "chain_depth":       chain_depth.get(code, 0),
            "cross_major_count": cross_major.get(code, 0),
            "betweenness":       round(betweenness.get(code, 0), 4),
            "prereqs":           sorted(prereq_map.get(code, [])),
            "plans":             sorted(course_plan_membership.get(code, [])),
        }
        if code in grades:
            g = grades[code]
            entry["avg_gpa"]             = g.get("avg_gpa")
            entry["dfw_rate"]            = g.get("dfw_rate")
            entry["total_students"]      = g.get("total_students")
            entry["sections"]            = g.get("sections")
            entry["most_recent_semester"]= g.get("most_recent_semester", "")
            entry["trend_gpa"]           = g.get("trend_gpa", [])
            # pass through all pct_* bucket fractions
            for k, v in g.items():
                if k.startswith("pct_"):
                    entry[k] = v
        course_analytics[code] = entry

    output = {
        "plans":            plans_data,
        "course_analytics": course_analytics,
        "graph_edges":      [[u, v] for u, v in G_cns.edges()],
        "summary": {
            "total_plans":   len(plans_data),
            "total_courses": len(all_cns_courses),
            "total_edges":   G_cns.number_of_edges(),
            "has_grades":    bool(grades),
        },
    }

    out_path = os.path.join(output_dir, "analytics_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, separators=(",", ":"))

    size_kb = os.path.getsize(out_path) // 1024
    print(f"Analytics JSON written → {out_path}  ({size_kb:,} KB)", flush=True)
    return output


# -----------------------------
# CLI
# -----------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate CA-format degree plan CSVs and analytics JSON."
    )
    parser.add_argument("--registrar",   required=True,
                        help="Path to registrar CSV (prerequisite data)")
    parser.add_argument("--majors",      required=True,
                        help="Path to majors XLSX (CNS course lists)")
    parser.add_argument("--output-dir",  required=True,
                        help="Directory for output CSVs and analytics JSON")
    parser.add_argument("--grades",      default=None,
                        help="Path to grades_enriched.json from "
                             "enrich_with_grades.py (optional)")

    args = parser.parse_args()

    # 1. Write per-plan CA-format CSVs
    build_curricula(args.registrar, args.majors, args.output_dir)

    # 2. Write analytics_data.json (with optional grades enrichment)
    build_analytics_json(
        args.registrar,
        args.majors,
        args.output_dir,
        grades_json=args.grades,
    )