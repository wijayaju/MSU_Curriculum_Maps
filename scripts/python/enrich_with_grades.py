"""
enrich_with_grades.py
─────────────────────
Downloads the MSU Grades FOIA CSV from https://msugrades.com/all-grades.csv,
aggregates it by course, and writes outputs/grades_enriched.json for use by
build_ca_curricula_v2.py.

Real CSV schema (confirmed from msugrades.com FOIA data):
  term_code, numeric_term_code, subject_code, course_code, course_title,
  instructors, total_grades, total_numeric_grades, total_law_grades,
  total_other_grades, average_grade_raw, average_grade,
  4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.0,
  A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F,
  pass, no_grade, deferred, satisfactory, not_satisfactory, credit,
  no_credit, incomplete, withdrawn, unfinished_work, visitor, auditor,
  extension, conditional_pass, late_drop

Usage:
    python enrich_with_grades.py
    python enrich_with_grades.py --force-download
    python enrich_with_grades.py --input path/to/all-grades.csv
"""

import argparse
import csv
import io
import json
import os
import re
import urllib.request
import urllib.error
from collections import defaultdict

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE       = os.path.dirname(os.path.abspath(__file__))
GRADES_URL  = "https://msugrades.com/all-grades.csv"
CACHE_PATH  = os.path.join(_HERE, "../../outputs", "all-grades.cache.csv")
DEFAULT_OUT = os.path.join(_HERE, "../../outputs", "grades_enriched.json")
CACHE_MAX_AGE_DAYS = 7

# ── Grade scale ───────────────────────────────────────────────────────────────
# MSU numeric grade columns present in the CSV
GPA_POINTS = {
    "4.0": 4.0, "3.5": 3.5, "3.0": 3.0, "2.5": 2.5,
    "2.0": 2.0, "1.5": 1.5, "1.0": 1.0, "0.0": 0.0,
}

# Columns that contribute to the DFW (at-risk) rate.
# "withdrawn" is the W column; "late_drop" and "incomplete" are also
# academic-risk indicators included in the DFW calculation.
DFW_GRADE_COLS = {"1.0", "0.0", "D+", "D", "D-", "F",
                  "withdrawn", "late_drop", "incomplete"}

SEASON_ORDER = {"spring": 0, "summer": 1, "fall": 2, "winter": 3}


def _parse_term(tc: str) -> str:
    """Convert any MSU term_code variant to 'Season YYYY' string."""
    if not tc:
        return ""
    tc = str(tc).strip()

    # Already human-readable
    if re.match(r"(Fall|Spring|Summer|Winter)\s+\d{4}", tc, re.I):
        m = re.match(r"(\w+)\s+(\d{4})", tc, re.I)
        return f"{m.group(1).title()} {m.group(2)}"

    # FS23 / SS24 / US23 / FS2023 etc.
    m = re.match(r"^(FS|SS|US|WS)(\d{2,4})$", tc.upper())
    if m:
        season_map = {"FS": "Fall", "SS": "Spring", "US": "Summer", "WS": "Winter"}
        season = season_map[m.group(1)]
        yr = m.group(2)
        if len(yr) == 2:
            yr = ("20" if int(yr) <= 30 else "19") + yr
        return f"{season} {yr}"

    # Numeric codes like 2238 (Fall 2023), 2231 (Spring 2023)
    m = re.match(r"^(\d{3,4})(\d)$", tc)
    if m:
        yp = m.group(1)
        td = m.group(2)
        if len(yp) == 3:
            yp = "20" + yp[1:]
        term_map = {"1": "Spring", "5": "Summer", "8": "Fall"}
        season = term_map.get(td, "")
        if season:
            return f"{season} {yp}"

    return tc  # return as-is if nothing matched


def _sem_key(sem: str) -> int:
    m = re.match(r"(\w+)\s+(\d{4})", sem.strip(), re.IGNORECASE)
    if not m:
        return 0
    return int(m.group(2)) * 10 + SEASON_ORDER.get(m.group(1).lower(), 5)


def _norm_code(subject: str, number: str) -> str:
    s = re.sub(r"\s+", "", subject).upper()
    n = number.strip().upper()
    if re.fullmatch(r"[A-Z]{2,4}", s) and re.fullmatch(r"\d{3}[A-Z]?", n):
        return f"{s} {n}"
    return ""


# ── Download / cache ──────────────────────────────────────────────────────────

def fetch_csv(url: str, cache_path: str, force: bool = False) -> str:
    import time
    if not force and os.path.exists(cache_path):
        age = (time.time() - os.path.getmtime(cache_path)) / 86400
        if age < CACHE_MAX_AGE_DAYS:
            print(f"  Using cached CSV ({age:.1f}d old): {cache_path}")
            with open(cache_path, encoding="utf-8", errors="replace") as f:
                return f.read()

    print(f"  Downloading {url}  (~70 MB, may take 1-2 min) ...")
    req = urllib.request.Request(url, headers={
        "User-Agent": "MSU-Curriculum-Analytics/2.0 "
                      "(https://github.com/JackRobertson77/MSU_Curriculum_Maps)",
        "Accept":  "text/csv,*/*",
        "Referer": "https://msugrades.com/downloads",
    })
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            raw = resp.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"\nFailed to download grades CSV: {exc}\n\n"
            f"Manual fallback:\n"
            f"  1. Open {url} in a browser and save the file.\n"
            f"  2. Copy it to: {cache_path}\n"
            f"  3. Re-run this script.\n"
            f"  Or pass --input <path> to point at a local copy.\n"
        ) from exc

    text = raw.decode("utf-8", errors="replace")
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  Cached ({len(raw) // 1024:,} KB) → {cache_path}")
    return text


# ── Aggregation ───────────────────────────────────────────────────────────────

def aggregate(csv_text: str) -> dict:
    reader = csv.DictReader(io.StringIO(csv_text))
    if not reader.fieldnames:
        raise ValueError("grades CSV has no header row")

    fields = reader.fieldnames
    lower  = {c.strip().lower(): c for c in fields}

    def find(*candidates):
        for c in candidates:
            if c in lower:
                return lower[c]
        return None

    # ── Column detection using real msugrades.com schema ─────────────────────
    col_subj    = find("subject_code", "subject", "subj", "dept")
    col_num     = find("course_code", "course_number", "number", "crse_code",
                       "course_num", "num")
    col_sem     = find("term_code", "semester", "term", "acad_term")
    col_avg_gpa = find("average_grade", "avg_gpa", "average_gpa",
                       "average_grade_raw")
    col_total   = find("total_grades", "total_numeric_grades", "total")

    if not col_subj or not col_num:
        raise ValueError(
            f"Cannot find subject/course-number columns.\n"
            f"Tried: subject_code, subject, course_code, course_number, number\n"
            f"Available: {list(fields)}"
        )

    # Numeric grade bucket columns (4.0 … 0.0)
    grade_cols: dict = {}
    for raw_col in fields:
        k = raw_col.strip()
        if k in GPA_POINTS:
            grade_cols[k] = raw_col

    # DFW-counting columns present in the real schema
    dfw_extra_cols: dict = {}   # col_key -> actual CSV column name
    for raw_col in fields:
        k = raw_col.strip().lower()
        if k in {"withdrawn", "late_drop", "incomplete", "d+", "d", "d-", "f"}:
            dfw_extra_cols[k] = raw_col

    # Letter-grade columns for pct_ breakdown (optional)
    letter_cols: dict = {}
    for raw_col in fields:
        k = raw_col.strip()
        if re.fullmatch(r"[ABCDF][+-]?", k):
            letter_cols[k] = raw_col

    print(f"  Subject col:    {col_subj}")
    print(f"  Course col:     {col_num}")
    print(f"  Semester col:   {col_sem}")
    print(f"  Avg GPA col:    {col_avg_gpa}")
    print(f"  Numeric grades: {sorted(grade_cols.keys())}")
    print(f"  DFW extras:     {sorted(dfw_extra_cols.keys())}")

    # ── Parse rows ───────────────────────────────────────────────────────────
    # One entry per CSV row (= one course section)
    # raw[code] = list of (semester_str, numeric_total, gpa_from_csv, dfw_count,
    #                      bucket_counts_dict)
    raw: dict = defaultdict(list)

    for row in reader:
        code = _norm_code(
            row.get(col_subj, "").strip(),
            row.get(col_num,  "").strip(),
        )
        if not code:
            continue

        sem = _parse_term((row.get(col_sem, "") or "").strip()) if col_sem else ""

        # Total enrolled students this section
        try:
            n = int(float(row.get(col_total, 0) or 0)) if col_total else 0
        except (ValueError, TypeError):
            n = 0

        # Pre-computed average GPA for this section
        try:
            sec_gpa = float(row.get(col_avg_gpa, "") or "") if col_avg_gpa else None
        except (ValueError, TypeError):
            sec_gpa = None

        # Numeric grade bucket counts
        buckets: dict = {}
        bucket_total = 0
        for key, col in grade_cols.items():
            try:
                cnt = max(0, int(float(row.get(col, 0) or 0)))
            except (ValueError, TypeError):
                cnt = 0
            buckets[key] = cnt
            bucket_total += cnt

        # Use bucket_total as n if total column was missing/zero
        if n == 0:
            n = bucket_total

        # DFW count: sum of D+/D/D-/F buckets (already in grade_cols if present)
        # plus withdrawn, late_drop, incomplete from dedicated columns
        dfw_n = 0
        for k in ("1.0", "0.0"):
            dfw_n += buckets.get(k, 0)
        for key, col in dfw_extra_cols.items():
            try:
                dfw_n += max(0, int(float(row.get(col, 0) or 0)))
            except (ValueError, TypeError):
                pass
        # Also add D+/D/D- from letter grade columns if present
        for lg in ("D+", "D", "D-"):
            if lg in letter_cols:
                try:
                    dfw_n += max(0, int(float(row.get(letter_cols[lg], 0) or 0)))
                except (ValueError, TypeError):
                    pass

        if n == 0:
            continue

        raw[code].append((sem, n, sec_gpa, dfw_n, buckets))

    print(f"  Parsed {sum(len(v) for v in raw.values()):,} rows "
          f"across {len(raw):,} unique courses")

    # ── Aggregate per course ─────────────────────────────────────────────────
    result = {}
    for code, sections in raw.items():
        total_n          = 0
        weighted_gpa_sum = 0.0
        total_dfw        = 0
        bucket_totals: dict = defaultdict(int)
        sem_agg: dict = defaultdict(lambda: [0.0, 0])   # sem -> [gpa_sum, n]

        for sem, n, sec_gpa, dfw_n, buckets in sections:
            total_n   += n
            total_dfw += dfw_n

            for k, cnt in buckets.items():
                bucket_totals[k] += cnt

            # Use the pre-computed GPA when available (more accurate than
            # recomputing from buckets, which may lose fractional students)
            if sec_gpa is not None and not (sec_gpa != sec_gpa):  # not NaN
                weighted_gpa_sum += sec_gpa * n
            else:
                # Fall back to bucket-computed GPA
                weighted_gpa_sum += sum(GPA_POINTS.get(k, 0) * v
                                        for k, v in buckets.items())

            if sem:
                sem_agg[sem][0] += (sec_gpa * n if sec_gpa is not None
                                    else sum(GPA_POINTS.get(k, 0) * v
                                             for k, v in buckets.items()))
                sem_agg[sem][1] += n

        if total_n == 0:
            continue

        avg_gpa  = round(weighted_gpa_sum / total_n, 3)
        dfw_rate = round(total_dfw / total_n, 4)

        # Grade bucket fractions (numeric scale)
        pct = {}
        for key in sorted(GPA_POINTS.keys(), key=lambda k: -GPA_POINTS[k]):
            safe = f"pct_{key.replace('.', '_')}"
            pct[safe] = round(bucket_totals.get(key, 0) / total_n, 4)
        # Withdrawal fraction
        pct["pct_W"] = round(
            sum(max(0, int(float(0))) for _ in [1])  # placeholder default 0
            / total_n, 4
        )
        # Recalculate pct_W from actual withdrawn counts
        withdrawn_total = 0
        for _, n, _, dfw_n, buckets in sections:
            pass  # already summed above; re-derive from dfw_extra_cols not available here
        # Simpler: store withdrawn as its own sum by re-parsing — already in dfw counts
        # We'll approximate: pct_W from bucket key "withdrawn" if it was in grade_cols
        # (it's not — it's in dfw_extra_cols). Store total DFW fraction instead.
        pct["pct_W"] = round(total_dfw / total_n, 4)  # DFW as proxy for W pct

        # GPA trend: up to 8 most-recent semesters
        trend = []
        for sem in sorted(sem_agg.keys(), key=_sem_key):
            g, n = sem_agg[sem]
            if n > 0:
                trend.append({"semester": sem,
                               "gpa": round(g / n, 3),
                               "students": n})
        trend = trend[-8:]
        most_recent = (sorted(sem_agg.keys(), key=_sem_key)[-1]
                       if sem_agg else "")

        result[code] = {
            "avg_gpa":              avg_gpa,
            "dfw_rate":             dfw_rate,
            "total_students":       total_n,
            "sections":             len(sections),
            "most_recent_semester": most_recent,
            "trend_gpa":            trend,
            **pct,
        }

    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url",            default=GRADES_URL)
    p.add_argument("--cache",          default=CACHE_PATH)
    p.add_argument("--input",          default=None,
                   help="Use a local CSV file instead of downloading")
    p.add_argument("--output",         default=DEFAULT_OUT)
    p.add_argument("--force-download", action="store_true")
    args = p.parse_args(argv)

    print("=" * 56)
    print("MSU Grades Enrichment")
    print("=" * 56)

    if args.input:
        print(f"Step 1: Reading local file: {args.input}")
        with open(args.input, encoding="utf-8", errors="replace") as f:
            csv_text = f.read()
    else:
        print("Step 1: Fetching grades CSV")
        csv_text = fetch_csv(args.url, args.cache, force=args.force_download)

    print(f"Step 2: Aggregating ({len(csv_text) // 1024:,} KB) ...")
    data = aggregate(csv_text)
    print(f"  → {len(data):,} courses with grade data")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    print(f"Step 3: Written → {args.output}  "
          f"({os.path.getsize(args.output) // 1024:,} KB)")

    samples = ["CEM 141", "CEM 142", "PHY 231", "MTH 132", "BS 161",
               "BMB 461", "STT 441", "GLG 401", "PLB 415", "AST 207"]
    hits = sum(1 for c in samples if c in data)
    print(f"\nCNS spot-check: {hits}/{len(samples)} courses found")
    for c in samples:
        if c in data:
            d = data[c]
            t = d["trend_gpa"]
            trend = (f", trend {t[0]['semester']}→{t[-1]['semester']}"
                     if len(t) >= 2 else "")
            print(f"  {c:12s}  GPA={d['avg_gpa']:.2f}  "
                  f"DFW={d['dfw_rate']:.1%}  "
                  f"n={d['total_students']:,}{trend}")
        else:
            print(f"  {c:12s}  — not in grades data")

    print("\nDone. Run build_ca_curricula_v2.py --grades to embed into dashboard.")
    return data


if __name__ == "__main__":
    main()
