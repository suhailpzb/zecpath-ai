# parsers/section_parser.py
# Day 8 – Resume Section Segmentation
# Automatically identifies and separates major resume sections

import re
import json
import os
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────────
# SECTION HEADING KEYWORDS
# Rule-based detection — covers all common resume heading styles
# ─────────────────────────────────────────────────────────────────

SECTION_KEYWORDS = {
    "skills": [
        "skills", "technical skills", "core skills", "key skills",
        "competencies", "expertise", "technologies", "tools",
        "hard skills", "soft skills", "skill set", "proficiencies"
    ],
    "experience": [
        "experience", "work experience", "employment history",
        "professional experience", "work history", "career history",
        "job history", "positions held", "employment", "work"
    ],
    "education": [
        "education", "academic background", "academic history",
        "educational qualification", "qualifications", "academics",
        "schooling", "degrees", "university", "college"
    ],
    "certifications": [
        "certifications", "certification", "certificates", "certificate",
        "licenses", "accreditations", "professional certifications",
        "credentials", "certified", "training"
    ],
    "projects": [
        "projects", "project experience", "personal projects",
        "academic projects", "key projects", "portfolio",
        "project work", "project history"
    ],
    "summary": [
        "summary", "profile", "professional summary", "career summary",
        "objective", "career objective", "about", "about me",
        "professional profile", "overview", "introduction"
    ],
    "achievements": [
        "achievements", "accomplishments", "awards", "honors",
        "recognition", "key achievements", "highlights"
    ],
    "languages": [
        "languages", "language skills", "spoken languages"
    ],
    "contact": [
        "contact", "contact information", "personal information",
        "personal details", "contact details"
    ],
}

# Flattened map: keyword → section name (for fast lookup)
KEYWORD_TO_SECTION = {}
for section, keywords in SECTION_KEYWORDS.items():
    for kw in keywords:
        KEYWORD_TO_SECTION[kw.lower()] = section


# ─────────────────────────────────────────────────────────────────
# 1. DETECT SECTION HEADING IN A LINE
# ─────────────────────────────────────────────────────────────────

def detect_section_heading(line):
    """
    Check if a line is a section heading.
    Returns section name if matched, else None.

    Handles:
    - ALL CAPS headings: "EXPERIENCE"
    - Title Case headings: "Work Experience"
    - Headings with separators: "--- Skills ---"
    - Short lines that match keywords
    """
    # Clean the line — remove separators like ---, ===, bullets
    cleaned = re.sub(r'[-=_*•|#]{2,}', '', line).strip()
    cleaned_lower = cleaned.lower().strip()

    if not cleaned_lower:
        return None

    # Must be reasonably short to be a heading (not a sentence)
    if len(cleaned_lower) > 50:
        return None

    # Direct keyword match
    if cleaned_lower in KEYWORD_TO_SECTION:
        return KEYWORD_TO_SECTION[cleaned_lower]

    # Partial match — heading contains a keyword
    for keyword, section in KEYWORD_TO_SECTION.items():
        if keyword in cleaned_lower and len(keyword) > 4:
            return section

    return None


# ─────────────────────────────────────────────────────────────────
# 2. RULE-BASED SECTION SPLITTER
# ─────────────────────────────────────────────────────────────────

def split_into_sections_rule_based(raw_text):
    """
    Split resume text into sections using rule-based heading detection.
    Returns dict: { section_name: [lines] }
    """
    lines = raw_text.split('\n')
    sections = {}
    current_section = "other"
    sections[current_section] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        heading = detect_section_heading(stripped)

        if heading:
            current_section = heading
            if current_section not in sections:
                sections[current_section] = []
        else:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append(stripped)

    return sections


# ─────────────────────────────────────────────────────────────────
# 3. NLP-BASED ENHANCEMENT (pattern matching)
# ─────────────────────────────────────────────────────────────────

def detect_section_by_content(text_block):
    """
    NLP-style content-based section detection.
    Analyzes content patterns when heading detection fails.
    Returns best-guess section name.
    """
    text_lower = text_block.lower()

    # Skills signals: programming languages, tools, bullet lists of nouns
    skill_signals = ["python", "sql", "excel", "java", "machine learning",
                     "tableau", "bloomberg", "tensorflow", "git", "hadoop"]
    skill_hits = sum(1 for s in skill_signals if s in text_lower)
    if skill_hits >= 2:
        return "skills"

    # Experience signals: job titles, dates, company names, bullet points
    exp_signals = ["january", "february", "march", "april", "may", "june",
                   "july", "august", "september", "october", "november", "december",
                   "present", "intern", "manager", "analyst", "engineer",
                   "developed", "managed", "led", "built", "designed"]
    exp_hits = sum(1 for s in exp_signals if s in text_lower)
    if exp_hits >= 3:
        return "experience"

    # Education signals: degree words, institutions
    edu_signals = ["bachelor", "master", "phd", "degree", "university",
                   "college", "diploma", "gpa", "graduated", "science"]
    edu_hits = sum(1 for s in edu_signals if s in text_lower)
    if edu_hits >= 2:
        return "education"

    # Certification signals
    cert_signals = ["certified", "certification", "cfa", "cpa", "aws",
                    "google", "microsoft", "oracle", "license", "accredited"]
    cert_hits = sum(1 for s in cert_signals if s in text_lower)
    if cert_hits >= 1:
        return "certifications"

    # Project signals
    proj_signals = ["project", "built", "developed", "created", "github",
                    "implemented", "designed", "application", "system"]
    proj_hits = sum(1 for s in proj_signals if s in text_lower)
    if proj_hits >= 2:
        return "projects"

    return "other"


# ─────────────────────────────────────────────────────────────────
# 4. MAIN CLASSIFIER FUNCTION
# ─────────────────────────────────────────────────────────────────

def classify_resume_sections(raw_text):
    """
    Main function — classifies all resume sections.
    Combines rule-based + NLP-based detection.
    Returns structured dict with section name → text content.
    """
    # Step 1: Rule-based split
    sections = split_into_sections_rule_based(raw_text)

    # Step 2: NLP enhancement for "other" section
    if "other" in sections and sections["other"]:
        other_text = " ".join(sections["other"])
        guessed_section = detect_section_by_content(other_text)
        if guessed_section != "other":
            if guessed_section not in sections:
                sections[guessed_section] = []
            sections[guessed_section].extend(sections["other"])
            del sections["other"]

    # Step 3: Join lines into clean text per section
    result = {}
    for section, lines in sections.items():
        joined = " ".join(lines).strip()
        if joined:
            result[section] = joined

    return result


# ─────────────────────────────────────────────────────────────────
# 5. BUILD LABELED RESUME OBJECT
# ─────────────────────────────────────────────────────────────────

def build_labeled_resume(file_path, raw_text, sections):
    """
    Build a fully labeled resume object with sections tagged.
    This is the 'Labeled Resume Sample' deliverable.
    """
    # Count which sections were detected
    detected   = list(sections.keys())
    expected   = ["skills", "experience", "education",
                  "certifications", "projects", "summary"]
    found      = [s for s in expected if s in detected]
    not_found  = [s for s in expected if s not in detected]

    return {
        "source_file":       os.path.basename(file_path),
        "labeled_at":        datetime.now(timezone.utc).isoformat(),
        "total_sections":    len(detected),
        "sections_found":    found,
        "sections_missing":  not_found,
        "detection_method":  "rule-based + nlp-pattern",
        "labeled_sections":  sections,
        "raw_text_length":   len(raw_text),
    }


# ─────────────────────────────────────────────────────────────────
# 6. SAVE LABELED RESUME TO OUTPUT
# ─────────────────────────────────────────────────────────────────

def save_labeled_resume(labeled_resume, output_dir="data/output/labeled"):
    """
    Save labeled resume JSON to output folder.
    Creates the folder if it does not exist.
    """
    os.makedirs(output_dir, exist_ok=True)
    base  = labeled_resume["source_file"].replace(".pdf","").replace(".docx","")
    fname = f"{base}_labeled.json"
    path  = os.path.join(output_dir, fname)

    with open(path, "w") as f:
        json.dump(labeled_resume, f, indent=2)

    return path


# ─────────────────────────────────────────────────────────────────
# 7. ACCURACY REPORT
# ─────────────────────────────────────────────────────────────────

def generate_accuracy_report(labeled_resumes, output_dir="data/output"):
    """
    Generate section detection accuracy report across all resumes.
    Counts how often each section was detected.
    """
    os.makedirs(output_dir, exist_ok=True)

    expected_sections = ["skills", "experience", "education",
                         "certifications", "projects", "summary"]
    total = len(labeled_resumes)

    section_counts = {s: 0 for s in expected_sections}
    for resume in labeled_resumes:
        for section in resume["sections_found"]:
            if section in section_counts:
                section_counts[section] += 1

    accuracy = {}
    for section, count in section_counts.items():
        pct = round((count / total) * 100) if total > 0 else 0
        accuracy[section] = {
            "detected_in": count,
            "total_resumes": total,
            "detection_rate": f"{pct}%"
        }

    report = {
        "report_name":      "Section Detection Accuracy Report",
        "generated_at":     datetime.now(timezone.utc).isoformat(),
        "total_resumes":    total,
        "detection_method": "rule-based + nlp-pattern",
        "accuracy_by_section": accuracy,
        "summary": [
            f"{s}: {accuracy[s]['detection_rate']} ({accuracy[s]['detected_in']}/{total})"
            for s in expected_sections
        ]
    }

    report_path = os.path.join(output_dir, "section_detection_accuracy_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report, report_path


# ─────────────────────────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
    John Smith
    john@email.com

    SUMMARY
    Experienced data scientist with 5 years in ML and analytics.

    SKILLS
    Python, SQL, Machine Learning, TensorFlow, Tableau

    WORK EXPERIENCE
    Data Scientist at Google, 2020 - Present
    Developed predictive models for 20+ clients.

    Senior Analyst at Amazon, 2018 - 2020
    Built dashboards using Tableau.

    EDUCATION
    Bachelor of Science in Computer Science
    University of California, 2018

    CERTIFICATIONS
    AWS Certified Machine Learning Specialist
    Google Data Analytics Certificate

    PROJECTS
    Sales Prediction Engine - Built using Python and scikit-learn
    Customer Segmentation - Clustering model for 10K+ customers
    """

    sections = classify_resume_sections(sample)
    print("Detected sections:", list(sections.keys()))
    for name, content in sections.items():
        print(f"\n[{name.upper()}]")
        print(content[:150])