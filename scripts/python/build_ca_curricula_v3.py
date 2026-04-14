"""
build_ca_curricula_v2.py
────────────────────────
Converts a registrar prerequisite file and a degree-plan spreadsheet into:
  1. One CA-format CSV per degree plan  (outputs/degree_plans/*.csv)
  2. An analytics JSON for the dashboard (outputs/degree_plans/analytics_data.json)

No column names, institution names, year/term vocabulary, or file structure
are hardcoded.  The script auto-detects columns from common naming patterns
and accepts a YAML/JSON config file (--config) for anything it cannot infer.

──────────────────────────────────────────────────────────────────────────────
Supported registrar CSV layouts (auto-detected column roles)
──────────────────────────────────────────────────────────────────────────────
  subject       course subject/department code  (e.g. CEM, MTH)
  number        course number                   (e.g. 141, 231)
  prereq_direct column listing direct prerequisite course codes
  prereq_list   column listing course-list prerequisites
  title         human-readable course title     (optional)
  department    department/org name             (optional)

──────────────────────────────────────────────────────────────────────────────
Supported majors spreadsheet layouts (auto-detected column roles)
──────────────────────────────────────────────────────────────────────────────
  plan          degree plan name  (groups rows into one plan)
  award_type    BS / BA / etc.
  course        course code per row  (e.g. CEM 141)
  year_level    year in sequence  (e.g. Freshman, Year 1, 1)
  term_season   term within year  (e.g. FS, Fall, Semester 1, 1)
  credits_max   max credit hours
  credits_min   min credit hours (fallback)
  major_title   display name for the major  (optional)
  major_code    internal major ID            (optional)

──────────────────────────────────────────────────────────────────────────────
Config file  (--config path/to/config.yaml or .json)
──────────────────────────────────────────────────────────────────────────────
Override any auto-detected column name or vocabulary map:

  institution: "My University"
  system_type: semester

  registrar_columns:
    subject:       SUBJ
    number:        CNUM
    prereq_direct: PREREQ_CRSE
    prereq_list:   CLIST
    title:         LONG_TITLE
    department:    DEPT_NAME

  majors_columns:
    plan:         Program Name
    award_type:   Degree
    course:       CourseCode
    year_level:   YearLevel
    term_season:  Semester
    credits_max:  Units

  year_map:
    "Year 1": 0
    "Year 2": 1
    "Year 3": 2
    "Year 4": 3

  term_map:
    Fall:   1
    Spring: 2
    Summer: 3

Usage:
    python build_ca_curricula_v2.py \\
        --registrar  data/registrar.csv \\
        --majors     data/majors.xlsx \\
        --output-dir outputs/degree_plans

    python build_ca_curricula_v2.py \\
        --registrar  data/registrar.csv \\
        --majors     data/majors.xlsx \\
        --output-dir outputs/degree_plans \\
        --grades     outputs/grades_enriched.json \\
        --config     config.yaml \\
        --institution "State University" \\
        --system-type semester
"""

import csv
import json
import os
import re
from collections import defaultdict

import pandas as pd


# ── Column candidates ─────────────────────────────────────────────────────────
# For each logical role: ordered list of column name candidates (case-insensitive).

REGISTRAR_CANDIDATES = {
    "subject":       ["subject_code", "subject", "subj", "dept_code",
                      "department_code"],
    "number":        ["crse_code", "course_code", "course_number", "course_num",
                      "number", "crse", "cnum", "num", "catalog_nbr"],
    "prereq_direct": ["rqdet_crse", "prereq_course", "prerequisite_course",
                      "req_course", "pre_crse"],
    "prereq_list":   ["courselist", "course_list", "prereq_list",
                      "prerequisite_list", "req_list"],
    "title":         ["course_title_long", "course_title", "title",
                      "long_title", "descr"],
    "department":    ["acad_org_u1_descrformal", "department", "dept_name",
                      "org_name", "acad_org"],
}

MAJORS_CANDIDATES = {
    "plan":        ["plan title", "plan_title", "program", "program name",
                    "degree plan", "curriculum"],
    "award_type":  ["award type", "award_type", "degree type", "degree",
                    "credential", "award"],
    "course":      ["course", "course code", "course_code", "coursecode", "crse"],
    "year_level":  ["year", "year level", "year_level", "yearlevel", "academic year",
                    "class year", "yr"],
    "term_season": ["term", "semester", "term_season", "termseason", "season", "period"],
    "credits_max": ["credits max", "credits_max", "max credits", "units max",
                    "max_units", "credits", "units", "credit hours"],
    "credits_min": ["credits min", "credits_min", "min credits", "units min",
                    "min_units"],
    "major_title": ["major title", "major_title", "major name", "program title"],
    "major_code":  ["major", "major code", "major_code", "program code"],
    "college":     ["college", "college name", "school", "faculty"],
}

DEFAULT_YEAR_PATTERNS = [
    {"freshman": 0, "sophomore": 1, "junior": 2, "senior": 3, "fifth year": 4},
    {"first year": 0, "second year": 1, "third year": 2, "fourth year": 3,
     "fifth year": 4},
    {"year 1": 0, "year 2": 1, "year 3": 2, "year 4": 3, "year 5": 4},
    {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4},
]

DEFAULT_TERM_PATTERNS = [
    {"fs": 1, "ss": 2, "us": 3},
    {"fall": 1, "spring": 2, "summer": 3, "winter": 4},
    {"semester 1": 1, "semester 2": 2, "semester 3": 3},
    {"1": 1, "2": 2, "3": 3, "4": 4},
    {"s1": 1, "s2": 2, "s3": 3},
]


# ── Column detection ──────────────────────────────────────────────────────────

def _find_col(columns, candidates, role, required=True):
    lower_cols = {c.strip().lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lower_cols:
            return lower_cols[cand.lower()]
    if required:
        raise ValueError(
            f"Cannot find a column for role '{role}'.\n"
            f"  Tried: {candidates}\n"
            f"  Available: {list(columns)}\n"
            f"  Add a --config file with a registrar_columns.{role} entry."
        )
    return None


def _detect_cols(df, candidates_map, overrides, required_roles):
    result = {}
    for role, candidates in candidates_map.items():
        if role in overrides:
            col = overrides[role]
            if col not in df.columns:
                raise ValueError(
                    f"Config column '{col}' for role '{role}' not found.\n"
                    f"Available: {list(df.columns)}"
                )
            result[role] = col
        else:
            result[role] = _find_col(
                df.columns, candidates, role,
                required=(role in required_roles)
            )
    return result


def detect_registrar_cols(df, overrides):
    return _detect_cols(
        df, REGISTRAR_CANDIDATES, overrides,
        required_roles={"subject", "number"}
    )


def detect_majors_cols(df, overrides):
    return _detect_cols(
        df, MAJORS_CANDIDATES, overrides,
        required_roles={"plan", "award_type", "course",
                        "year_level", "term_season", "credits_max"}
    )


# ── Vocabulary detection ──────────────────────────────────────────────────────

def _build_map(values, patterns, role):
    lower_vals = {str(v).strip().lower() for v in values if pd.notna(v)}
    for pattern in patterns:
        if lower_vals.issubset(pattern.keys()):
            return {str(v).strip(): pattern[str(v).strip().lower()]
                    for v in values if pd.notna(v)}
    # Auto-assign
    sorted_vals = sorted(str(v).strip() for v in values
                         if pd.notna(v) and str(v).strip())
    auto = {v: i for i, v in enumerate(sorted_vals)}
    print(
        f"  Warning: {role} values {sorted_vals} did not match any known "
        f"pattern. Auto-assigned: {auto}.\n"
        f"  Add a '{role}_map' to your --config for explicit control.",
        flush=True,
    )
    return auto


def build_year_map(majors_df, year_col, config_map):
    if config_map:
        return {str(k): v for k, v in config_map.items()}
    return _build_map(majors_df[year_col].dropna().unique(),
                      DEFAULT_YEAR_PATTERNS, "year")


def build_term_map(majors_df, term_col, config_map):
    if config_map:
        return {str(k): v for k, v in config_map.items()}
    return _build_map(majors_df[term_col].dropna().unique(),
                      DEFAULT_TERM_PATTERNS, "term")


def term_to_number(year_val, term_val, year_map, term_map):
    y = str(year_val).strip()
    t = str(term_val).strip()
    if y not in year_map or t not in term_map:
        return ""
    return year_map[y] * len(term_map) + term_map[t]


# ── Helpers ───────────────────────────────────────────────────────────────────

def normalize_course_code(text):
    if not isinstance(text, str):
        return None
    text = text.strip().upper()
    m = re.fullmatch(r"([A-Z]{2,4})\s+([0-9]{3}[A-Z]?)", text)
    return f"{m.group(1)} {m.group(2)}" if m else None


def split_course_code(course):
    norm = normalize_course_code(course)
    if not norm:
        return "", ""
    parts = norm.split()
    return (parts[0], parts[1]) if len(parts) == 2 else ("", "")


def extract_course_codes(text):
    if not isinstance(text, str):
        return []
    matches = re.findall(r"\b([A-Z]{2,4})\s+([0-9]{3}[A-Z]?)\b", text.upper())
    seen, seen_set = [], set()
    for subj, num in matches:
        code = f"{subj} {num}"
        if code not in seen_set:
            seen.append(code)
            seen_set.add(code)
    return seen


def sanitize_filename(text):
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r"[^\w]+", "_", text).strip("_") + ".csv"


def pad_row(values, total_cols=11):
    values = list(values)
    if len(values) < total_cols:
        values += [""] * (total_cols - len(values))
    return values


def read_file(path):
    """Read CSV or Excel; try multiple encodings for CSV."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm", ".xls", ".ods"):
        return pd.read_excel(path)
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin1"):
        try:
            print(f"  Trying encoding {enc}...", flush=True)
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except UnicodeDecodeError:
            pass
    raise ValueError(f"Could not read {path} with any supported encoding.")


def load_config(path):
    """Load YAML or JSON config file. Returns {} if path is None."""
    if not path:
        return {}
    ext = os.path.splitext(path)[1].lower()
    with open(path, encoding="utf-8") as f:
        if ext in (".yaml", ".yml"):
            try:
                import yaml
                return yaml.safe_load(f) or {}
            except ImportError:
                raise ImportError(
                    "PyYAML needed for YAML configs:  pip install pyyaml\n"
                    "Or use a .json config file instead."
                )
        return json.load(f)


# ── Prerequisite extraction ───────────────────────────────────────────────────

def parse_prereq_courses(registrar_df, cols):
    prereqs = defaultdict(set)
    col_subj   = cols["subject"]
    col_num    = cols["number"]
    col_direct = cols.get("prereq_direct")
    col_list   = cols.get("prereq_list")

    if not col_direct and not col_list:
        print(
            "  Warning: no prerequisite columns detected. "
            "Degree plans will have no prereq edges.\n"
            "  Add prereq_direct / prereq_list to your --config.",
            flush=True,
        )
        return prereqs

    for _, row in registrar_df.iterrows():
        subj = row.get(col_subj, "")
        num  = row.get(col_num,  "")
        if pd.isna(subj) or pd.isna(num):
            continue
        target = normalize_course_code(
            f"{str(subj).strip()} {str(num).strip()}"
        )
        if not target:
            continue
        for col in filter(None, [col_direct, col_list]):
            for prereq in extract_course_codes(str(row.get(col, ""))):
                if prereq != target:
                    prereqs[target].add(prereq)

    return prereqs


# ── CA CSV writer ─────────────────────────────────────────────────────────────

def build_curricula(registrar_path, majors_path, output_dir,
                    config=None, institution="", system_type="semester"):
    config = config or {}
    os.makedirs(output_dir, exist_ok=True)

    print("Loading files...", flush=True)
    registrar = read_file(registrar_path)
    majors    = read_file(majors_path)

    reg_cols = detect_registrar_cols(registrar, config.get("registrar_columns", {}))
    maj_cols = detect_majors_cols(majors, config.get("majors_columns", {}))
    year_map = build_year_map(majors, maj_cols["year_level"], config.get("year_map"))
    term_map = build_term_map(majors, maj_cols["term_season"], config.get("term_map"))

    print(f"  Registrar columns: {reg_cols}", flush=True)
    print(f"  Majors columns:    {maj_cols}", flush=True)
    print(f"  Year map: {year_map}", flush=True)
    print(f"  Term map: {term_map}", flush=True)

    inst = config.get("institution", institution) or ""
    syst = config.get("system_type", system_type) or "semester"

    prereq_map  = parse_prereq_courses(registrar, reg_cols)
    plan_col    = maj_cols["plan"]
    plan_titles = majors[plan_col].dropna().unique()

    print(
        f"  Registrar rows: {len(registrar):,} | "
        f"Majors rows: {len(majors):,} | "
        f"Plans: {len(plan_titles):,} | "
        f"Courses with prereqs: {len(prereq_map):,}",
        flush=True,
    )
    print("Generating CA CSVs...", flush=True)

    summary = []
    files_written = 0

    for i, plan in enumerate(plan_titles, 1):
        plan_df = majors[majors[plan_col] == plan].copy()
        if plan_df.empty:
            continue

        curriculum_name = str(plan).strip()
        degree_type     = str(plan_df[maj_cols["award_type"]].iloc[0]).strip()
        out_path        = os.path.join(output_dir, sanitize_filename(curriculum_name))

        rows = []
        course_id_map   = {}
        course_term_map = {}
        next_id = 1

        for _, r in plan_df.iterrows():
            raw = r[maj_cols["course"]]
            if pd.isna(raw):
                continue
            course = str(raw).strip()
            norm   = normalize_course_code(course)
            prefix, number = split_course_code(course)
            term_n = term_to_number(
                r[maj_cols["year_level"]], r[maj_cols["term_season"]],
                year_map, term_map
            )
            cred = r[maj_cols["credits_max"]] if maj_cols["credits_max"] else None
            if cred is None or pd.isna(cred):
                cred = r[maj_cols["credits_min"]] if maj_cols.get("credits_min") else None
            if cred is None or pd.isna(cred):
                cred = ""
            if isinstance(cred, float) and cred == int(cred):
                cred = int(cred)

            cid = next_id
            next_id += 1
            rows.append({
                "Course ID": cid, "Course Name": course,
                "Normalized Course": norm, "Prefix": prefix, "Number": number,
                "Prerequisites": "", "Corequisites": "",
                "Strict-Corequisites": "", "Credit Hours": cred,
                "Institution": "", "Canonical Name": "", "Term": term_n,
            })
            if norm:
                course_id_map[norm]   = cid
                course_term_map[norm] = term_n

        for row in rows:
            norm = row["Normalized Course"]
            if not norm or norm not in prereq_map:
                continue
            pre_ids, co_ids = [], []
            for rel in sorted(prereq_map[norm]):
                if rel in course_id_map and rel in course_term_map:
                    r_trm = course_term_map[rel]
                    t_trm = row["Term"]
                    if isinstance(r_trm, int) and isinstance(t_trm, int):
                        if r_trm < t_trm:
                            pre_ids.append(str(course_id_map[rel]))
                        elif r_trm == t_trm:
                            co_ids.append(str(course_id_map[rel]))
            if pre_ids: row["Prerequisites"] = ";".join(pre_ids)
            if co_ids:  row["Corequisites"]  = ";".join(co_ids)

        n_pre  = sum(1 for r in rows if r["Prerequisites"])
        n_co   = sum(1 for r in rows if r["Corequisites"])
        rows.sort(key=lambda r: (
            r["Term"] if isinstance(r["Term"], int) else 999, r["Course ID"]
        ))

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(pad_row(["Curriculum",  curriculum_name]))
            w.writerow(pad_row(["Institution", inst]))
            w.writerow(pad_row(["Degree Type", degree_type]))
            w.writerow(pad_row(["System Type", syst]))
            w.writerow(pad_row(["CIP",         ""]))
            w.writerow(pad_row(["Courses"]))
            w.writerow(["Course ID","Course Name","Prefix","Number",
                         "Prerequisites","Corequisites","Strict-Corequisites",
                         "Credit Hours","Institution","Canonical Name","Term"])
            for r in rows:
                w.writerow([r["Course ID"],r["Course Name"],r["Prefix"],
                             r["Number"],r["Prerequisites"],r["Corequisites"],
                             r["Strict-Corequisites"],r["Credit Hours"],
                             r["Institution"],r["Canonical Name"],r["Term"]])

        summary.append([curriculum_name, os.path.basename(out_path),
                         len(rows), n_pre, n_co])
        files_written += 1
        if i <= 5:
            print(f"  {curriculum_name}: {n_pre} prereqs, {n_co} coreqs",
                  flush=True)
        if i % 50 == 0:
            print(f"  Processed {i:,} / {len(plan_titles):,}...", flush=True)

    summary_path = os.path.join(output_dir, "_summary.csv")
    pd.DataFrame(summary, columns=["Plan","File","Row Count",
                                    "Courses With Prereqs","Courses With Coreqs"]
                 ).to_csv(summary_path, index=False)
    print(f"Done. Wrote {files_written:,} files to '{output_dir}'.", flush=True)
    print(f"Summary → {summary_path}", flush=True)


# ── Analytics JSON builder ────────────────────────────────────────────────────

def build_analytics_json(registrar_path, majors_path, output_dir,
                          grades_json=None, config=None):
    import networkx as nx
    config = config or {}
    os.makedirs(output_dir, exist_ok=True)

    print("Building analytics JSON...", flush=True)
    registrar = read_file(registrar_path)
    majors    = read_file(majors_path)

    reg_cols = detect_registrar_cols(registrar, config.get("registrar_columns", {}))
    maj_cols = detect_majors_cols(majors, config.get("majors_columns", {}))
    year_map = build_year_map(majors, maj_cols["year_level"], config.get("year_map"))
    term_map = build_term_map(majors, maj_cols["term_season"], config.get("term_map"))

    prereq_map  = parse_prereq_courses(registrar, reg_cols)
    col_subj    = reg_cols["subject"]
    col_num     = reg_cols["number"]
    col_title   = reg_cols.get("title")
    col_dept    = reg_cols.get("department")

    # Course title + department lookup
    course_info = {}
    for _, row in registrar.drop_duplicates(subset=[col_subj, col_num]).iterrows():
        subj = row.get(col_subj, ""); num = row.get(col_num, "")
        if pd.isna(subj) or pd.isna(num):
            continue
        code = normalize_course_code(f"{str(subj).strip()} {str(num).strip()}")
        if not code or code in course_info:
            continue
        title = str(row[col_title]) if col_title and not pd.isna(row.get(col_title)) else ""
        dept  = str(row[col_dept])  if col_dept  and not pd.isna(row.get(col_dept))  else ""
        course_info[code] = {"title": title, "dept": dept}

    plan_col    = maj_cols["plan"]
    plan_titles = majors[plan_col].dropna().unique()
    plans_data  = {}
    course_plan_membership = defaultdict(set)

    for plan in plan_titles:
        plan_df = majors[majors[plan_col] == plan].copy()
        if plan_df.empty:
            continue
        courses_in_plan = []
        for _, r in plan_df.iterrows():
            raw = r[maj_cols["course"]]
            if pd.isna(raw):
                continue
            norm = normalize_course_code(str(raw).strip())
            if not norm:
                continue
            year_val = str(r[maj_cols["year_level"]]).strip()
            term_val = str(r[maj_cols["term_season"]]).strip()
            term_n   = term_to_number(year_val, term_val, year_map, term_map)
            cred = r[maj_cols["credits_max"]] if maj_cols["credits_max"] else None
            if cred is None or pd.isna(cred):
                cred = r[maj_cols["credits_min"]] if maj_cols.get("credits_min") else None
            if cred is None or pd.isna(cred):
                cred = 3
            if isinstance(cred, float) and cred == int(cred):
                cred = int(cred)
            courses_in_plan.append({
                "code": norm, "year": year_val, "term": term_val,
                "term_num": term_n, "credits": cred,
            })
            course_plan_membership[norm].add(plan)

        award_val   = str(plan_df[maj_cols["award_type"]].iloc[0]).strip()
        mt_col      = maj_cols.get("major_title")
        mc_col      = maj_cols.get("major_code")
        coll_col    = maj_cols.get("college")
        major_title = (str(plan_df[mt_col].iloc[0])
                       if mt_col and not pd.isna(plan_df[mt_col].iloc[0])
                       else str(plan))
        major_code  = (str(plan_df[mc_col].iloc[0])
                       if mc_col and not pd.isna(plan_df[mc_col].iloc[0])
                       else "")
        college     = (str(plan_df[coll_col].iloc[0])
                       if coll_col and not pd.isna(plan_df[coll_col].iloc[0])
                       else "")
        plans_data[plan] = {
            "award_type": award_val, "major_title": major_title,
            "major_code": major_code, "college": college,
            "courses": courses_in_plan,
        }

    all_courses = set(
        c["code"] for d in plans_data.values() for c in d["courses"]
    )

    # Full prereq graph for chain depth (includes external prereqs as roots)
    G_full = nx.DiGraph()
    for code in all_courses:
        G_full.add_node(code)
        for prereq in prereq_map.get(code, []):
            G_full.add_edge(prereq, code)

    G_dag = G_full.copy()
    for _ in range(20):
        try:
            G_dag.remove_edge(*nx.find_cycle(G_dag)[0])
        except nx.NetworkXNoCycle:
            break

    chain_depth = {}
    try:
        for node in nx.topological_sort(G_dag):
            preds = list(G_dag.predecessors(node))
            chain_depth[node] = (
                max(chain_depth.get(p, 0) for p in preds) + 1 if preds else 0
            )
    except nx.NetworkXUnfeasible:
        chain_depth = {n: 0 for n in G_dag.nodes}

    # Internal graph (only edges between courses in the dataset)
    G_int = nx.DiGraph()
    for code in all_courses:
        G_int.add_node(code)
    for code in all_courses:
        for prereq in prereq_map.get(code, []):
            if prereq in all_courses:
                G_int.add_edge(prereq, code)

    in_degree   = dict(G_int.in_degree())
    out_degree  = dict(G_int.out_degree())
    betweenness = nx.betweenness_centrality(G_int)
    cross_count = {c: len(p) for c, p in course_plan_membership.items()}

    # Optional grades enrichment
    grades = {}
    if grades_json and os.path.exists(grades_json):
        with open(grades_json, encoding="utf-8") as f:
            grades = json.load(f)
        matched = sum(1 for c in all_courses if c in grades)
        print(f"  Grades: {matched}/{len(all_courses)} courses matched",
              flush=True)
    elif grades_json:
        print(f"  Warning: grades file not found at {grades_json}.", flush=True)

    course_analytics = {}
    for code in all_courses:
        entry = {
            "title":             course_info.get(code, {}).get("title", ""),
            "dept":              course_info.get(code, {}).get("dept",  ""),
            "in_degree":         in_degree.get(code, 0),
            "out_degree":        out_degree.get(code, 0),
            "chain_depth":       chain_depth.get(code, 0),
            "cross_major_count": cross_count.get(code, 0),
            "betweenness":       round(betweenness.get(code, 0), 4),
            "prereqs":           sorted(prereq_map.get(code, [])),
            "plans":             sorted(course_plan_membership.get(code, [])),
        }
        if code in grades:
            g = grades[code]
            entry["avg_gpa"]              = g.get("avg_gpa")
            entry["dfw_rate"]             = g.get("dfw_rate")
            entry["total_students"]       = g.get("total_students")
            entry["sections"]             = g.get("sections")
            entry["most_recent_semester"] = g.get("most_recent_semester", "")
            entry["trend_gpa"]            = g.get("trend_gpa", [])
            for k, v in g.items():
                if k.startswith("pct_"):
                    entry[k] = v
        course_analytics[code] = entry

    output = {
        "plans":            plans_data,
        "course_analytics": course_analytics,
        "graph_edges":      [[u, v] for u, v in G_int.edges()],
        "summary": {
            "total_plans":   len(plans_data),
            "total_courses": len(all_courses),
            "total_edges":   G_int.number_of_edges(),
            "has_grades":    bool(grades),
        },
    }

    out_path = os.path.join(output_dir, "analytics_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, separators=(",", ":"))
    size_kb = os.path.getsize(out_path) // 1024
    print(f"Analytics JSON → {out_path}  ({size_kb:,} KB)", flush=True)
    return output


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--registrar",   required=True,
                        help="Registrar CSV or Excel (prerequisite data)")
    parser.add_argument("--majors",      required=True,
                        help="Majors CSV or Excel (degree plan data)")
    parser.add_argument("--output-dir",  required=True,
                        help="Output directory")
    parser.add_argument("--grades",      default=None,
                        help="grades_enriched.json from enrich_with_grades.py")
    parser.add_argument("--config",      default=None,
                        help="YAML or JSON config for column overrides, "
                             "institution name, term maps, etc.")
    parser.add_argument("--institution", default="",
                        help="Institution name written to CA CSV headers")
    parser.add_argument("--system-type", default="semester",
                        choices=["semester", "quarter"],
                        help="Academic system type (default: semester)")
    args = parser.parse_args()

    cfg = load_config(args.config)

    build_curricula(
        args.registrar, args.majors, args.output_dir,
        config=cfg,
        institution=args.institution,
        system_type=args.system_type,
    )
    build_analytics_json(
        args.registrar, args.majors, args.output_dir,
        grades_json=args.grades,
        config=cfg,
    )
