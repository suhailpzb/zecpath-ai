# main.py
# ZecPath AI — Full Pipeline Entry Point
# Days 3–6 Deliverables Integration

import os
import re
import json

from parsers.resume_parser import extract_resume_text, clean_resume_text
from parsers.jd_parser     import parse_job_description, extract_skills, save_jd_output
from ats_engine.ats_scoring import calculate_score
from utils.logger           import log_info, log_warning, log_error


# ─────────────────────────────────────────────────────────────────
# PROCESS ONE RESUME
# ─────────────────────────────────────────────────────────────────

def process_resume(resume_path, jd_skills):
    """Extract, clean, score one resume against JD skills."""
    raw_text = extract_resume_text(resume_path)
    cleaned  = clean_resume_text(raw_text)

    resume_skills  = extract_skills(cleaned)
    matched_skills = [s for s in resume_skills if s in jd_skills]
    missing_skills = [s for s in jd_skills     if s not in resume_skills]

    exp_match  = re.search(r'(\d+)\s+year', cleaned)
    experience = int(exp_match.group(1)) if exp_match else 0

    edu_map            = {"phd": "phd", "master": "master", "bachelor": "bachelor",
                          "btech": "btech", "mtech": "master"}
    detected_education = "not found"
    for key, label in edu_map.items():
        if key in cleaned:
            detected_education = label
            break

    score = calculate_score(
        skill_match     = len(matched_skills),
        experience      = experience,
        education       = detected_education,
        total_jd_skills = len(jd_skills)
    )

    return {
        "resume_file":    os.path.basename(resume_path),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience":     experience,
        "education":      detected_education,
        "score":          score,
    }


# ─────────────────────────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────────────────────────

def main():

    log_info("=" * 50)
    log_info("ZecPath AI Pipeline Started")

    # ── 1. READ JD FILE ──────────────────────────────────────────
    jd_file = "data/job_descriptions/portfolio_manager.txt"

    if not os.path.exists(jd_file):
        log_error(f"JD file not found: {jd_file}")
        return

    with open(jd_file, "r") as f:
        jd_text = f.read()

    # ── 2. PARSE JD ───────────────────────────────────────────────
    jd_result     = parse_job_description(jd_text)
    jd_role       = jd_result["role"]
    jd_skills     = jd_result["skills"]
    jd_experience = jd_result["experience"]
    jd_education  = jd_result["education"]

    # Save parsed JD to output
    save_jd_output(jd_text, "data/output/jd_parsed_output.json")

    log_info(f"JD Parsed — Role: {jd_role} | Skills: {len(jd_skills)}")

    print("\n" + "=" * 55)
    print("  ZecPath AI — Job Description")
    print("=" * 55)
    print(f"  Role        : {jd_role}")
    print(f"  Experience  : {jd_experience.get('raw', 'not found')}")
    print(f"  Education   : {jd_education.get('degree_level', [])}")
    print(f"  Skills ({len(jd_skills)})  : {jd_skills}")

    # ── 3. PROCESS ALL RESUMES ────────────────────────────────────
    resume_dir   = "data/sample_resumes"
    resume_files = [
        os.path.join(resume_dir, f)
        for f in os.listdir(resume_dir)
        if f.endswith(".pdf") or f.endswith(".docx")
    ] if os.path.exists(resume_dir) else []

    if not resume_files:
        log_warning("No resume files found in data/sample_resumes/")
        return

    results = []
    for path in sorted(resume_files):
        try:
            result = process_resume(path, jd_skills)
            results.append(result)
            log_info(f"{result['resume_file']} | score={result['score']} | matched={result['matched_skills']}")
        except Exception as e:
            log_error(f"Failed to process {path}: {e}")

    # ── 4. DISPLAY RESULTS ────────────────────────────────────────
    print("\n" + "=" * 55)
    print(f"  Candidates screened for: {jd_role}")
    print("=" * 55)

    for i, r in enumerate(results, 1):
        print(f"\n  Candidate {i} — {r['resume_file']}")
        print(f"  Score          : {r['score']} / 100")
        print(f"  Experience     : {r['experience']} years")
        print(f"  Education      : {r['education']}")
        print(f"  Matched Skills : {r['matched_skills']}")
        print(f"  Missing Skills : {r['missing_skills']}")

    # ── 5. RANK CANDIDATES ────────────────────────────────────────
    if results:
        ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    print("\n" + "=" * 55)
    print("  Ranking — best match first")
    print("=" * 55)

    for rank, r in enumerate(ranked, 1):
        bar   = "█" * (r["score"] // 5)
        empty = "░" * (20 - r["score"] // 5)
        print(f"  #{rank}  {r['resume_file']:<20} {bar}{empty}  {r['score']}/100")

    print(f"\n  Top Candidate : {ranked[0]['resume_file']}")
    print(f"  Score         : {ranked[0]['score']} / 100")

    # ── 6. SAVE RESULTS TO JSON ───────────────────────────────────
    output_path = "data/output/screening_results.json"
    os.makedirs("data/output", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"jd_role": jd_role, "candidates": results}, f, indent=2)
    log_info(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()