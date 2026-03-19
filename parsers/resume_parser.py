# parsers/resume_parser.py
# Day 5 Deliverable – Resume Text Extraction Engine
# Handles PDF and DOCX, cleans text, normalizes layout

import re
import os
import json
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None


# ─────────────────────────────────────────────────────────────────
# 1. EXTRACT TEXT FROM PDF
# ─────────────────────────────────────────────────────────────────

def extract_pdf_text(file_path):
    """
    Extract raw text from a PDF resume.
    Handles multi-page, columnar, and table layouts.
    Returns empty string if file cannot be read.
    """
    if pdfplumber is None:
        raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            # Try normal text extraction
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                # Fallback: extract from words for columnar layouts
                words = page.extract_words()
                if words:
                    text += " ".join(w["text"] for w in words) + "\n"
    return text


# ─────────────────────────────────────────────────────────────────
# 2. EXTRACT TEXT FROM DOCX
# ─────────────────────────────────────────────────────────────────

def extract_docx_text(file_path):
    """Extract raw text from a DOCX resume."""
    if docx is None:
        raise ImportError("python-docx not installed. Run: pip install python-docx")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    doc = docx.Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)


# ─────────────────────────────────────────────────────────────────
# 3. AUTO-DETECT FILE TYPE AND EXTRACT
# ─────────────────────────────────────────────────────────────────

def extract_resume_text(file_path):
    """
    Auto-detect file type (PDF or DOCX) and extract text.
    Day 5 task: handle different layouts automatically.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_pdf_text(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_docx_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use PDF or DOCX.")


# ─────────────────────────────────────────────────────────────────
# 4. CLEAN AND NORMALIZE TEXT
# ─────────────────────────────────────────────────────────────────

def clean_resume_text(text):
    """
    Clean raw resume text:
    - Lowercase
    - Remove special characters (keep hyphens for compound skills)
    - Collapse whitespace and blank lines
    - Normalize bullet points and section headings
    """
    # Lowercase
    text = text.lower()

    # Normalize bullet characters → space
    text = re.sub(r'[•·▪▸◦‣➢➤→\-–—]{1}\s', ' ', text)

    # Remove special characters but keep hyphens and slashes
    text = re.sub(r'[^a-z0-9\s\-\/]', ' ', text)

    # Collapse multiple spaces and blank lines
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n{2,}', '\n', text)

    return text.strip()


# ─────────────────────────────────────────────────────────────────
# 5. EXTRACT STRUCTURED SECTIONS FROM RESUME TEXT
# ─────────────────────────────────────────────────────────────────

SECTION_KEYWORDS = {
    "experience":     ["experience", "work experience", "employment", "work history"],
    "education":      ["education", "academic", "qualification", "degree"],
    "skills":         ["skills", "technical skills", "competencies", "expertise"],
    "certifications": ["certification", "certifications", "licenses", "accreditation"],
    "summary":        ["summary", "profile", "objective", "about"],
    "projects":       ["projects", "project experience"],
}


def extract_sections(text):
    """
    Detect and separate resume sections by heading keywords.
    Returns dict with section name → section text.
    Day 5 task: normalize section headings.
    """
    lines = text.split('\n')
    sections = {}
    current_section = "other"
    sections[current_section] = []

    for line in lines:
        line_lower = line.lower().strip()
        matched = False
        for section, keywords in SECTION_KEYWORDS.items():
            if any(kw in line_lower for kw in keywords):
                current_section = section
                sections[current_section] = []
                matched = True
                break
        if not matched:
            sections[current_section].append(line)

    # Join lines per section
    return {k: ' '.join(v).strip() for k, v in sections.items() if v}


# ─────────────────────────────────────────────────────────────────
# 6. SAVE EXTRACTED TEXT TO OUTPUT FILE
# ─────────────────────────────────────────────────────────────────

def save_extracted_text(file_path, output_dir="data/output"):
    """
    Extract, clean, and save resume text to a .txt file.
    Day 5 task: store extracted text in structured files.
    Returns the cleaned text.
    """
    os.makedirs(output_dir, exist_ok=True)

    raw_text     = extract_resume_text(file_path)
    cleaned_text = clean_resume_text(raw_text)

    base_name   = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_cleaned.txt")

    with open(output_path, "w") as f:
        f.write(cleaned_text)

    return cleaned_text, output_path


# ─────────────────────────────────────────────────────────────────
# 7. BUILD CANDIDATE PROFILE OBJECT (Day 4 Schema)
# ─────────────────────────────────────────────────────────────────

def build_candidate_profile(file_path, candidate_id=None):
    """
    Extract resume and return a structured candidate profile dict
    matching the Day 4 resume schema.
    """
    raw_text     = extract_resume_text(file_path)
    cleaned_text = clean_resume_text(raw_text)
    sections     = extract_sections(raw_text)

    # Basic experience years detection
    exp_match = re.search(r'(\d+)\s+year', cleaned_text)
    years_exp = int(exp_match.group(1)) if exp_match else 0

    # Education detection
    edu_map = {"phd": "PhD", "master": "Master's", "bachelor": "Bachelor's",
               "btech": "B.Tech", "mtech": "M.Tech"}
    detected_edu = []
    for key, label in edu_map.items():
        if key in cleaned_text:
            detected_edu.append(label)

    return {
        "candidate_id": candidate_id or f"CAND-{os.path.basename(file_path)}",
        "source_file":  file_path,
        "sections":     sections,
        "experience": {
            "total_years": years_exp,
            "raw_section": sections.get("experience", "")
        },
        "education": {
            "detected_levels": detected_edu,
            "raw_section": sections.get("education", "")
        },
        "raw_text":  cleaned_text,
        "parsed_at": datetime.utcnow().isoformat() + "Z"
    }