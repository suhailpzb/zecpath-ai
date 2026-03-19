# ZecPath AI — Intelligent ATS Scoring Engine

## Project Overview

ZecPath AI is a modular, Python-based **Applicant Tracking System (ATS)** that automatically:
- Extracts text from PDF and DOCX resumes
- Parses job descriptions into structured AI-readable objects
- Matches candidate skills against JD requirements
- Scores candidates using a weighted formula (out of 100)
- Ranks all candidates best-to-worst
- Logs every event to a log file
- Saves all results as JSON output

Built across **Days 1–6** as part of the ZecPath AI System Architecture.

---

## Project Structure

```
zecpath_ai/
│
├── data/
│   ├── sample_resumes/
│   │   ├── resume1.pdf              ← Liam Johnson   (Data Scientist)
│   │   ├── resume2.pdf              ← Robert Cooper  (Security Guard)
│   │   └── resume3.pdf              ← First Last     (Data Scientist)
│   ├── job_descriptions/
│   │   └── portfolio_manager.txt    ← JD input file (edit this to change role)
│   └── output/
│       ├── jd_parsed_output.json    ← Auto-generated: parsed JD object
│       └── screening_results.json  ← Auto-generated: all candidate scores
│
├── parsers/
│   ├── __init__.py
│   ├── resume_parser.py             ← Day 5: PDF/DOCX extraction + cleaning
│   └── jd_parser.py                 ← Day 6: JD parsing, 18 roles, 70+ skills
│
├── ats_engine/
│   ├── __init__.py
│   └── ats_scoring.py               ← Weighted ATS scoring (skills+exp+edu)
│
├── screening_ai/
│   └── __init__.py                  ← Placeholder for Day 7+ AI screening
│
├── interview_ai/
│   └── __init__.py                  ← Placeholder for Day 8+ AI interviews
│
├── scoring/
│   └── __init__.py                  ← Placeholder for advanced scoring models
│
├── schemas/
│   ├── resume_schema.json           ← Day 4: Standard resume data schema
│   └── jd_schema.json               ← Day 4: Standard JD data schema
│
├── utils/
│   ├── __init__.py
│   └── logger.py                    ← Day 3: Logging system → ai_system.log
│
├── tests/
│   ├── __init__.py
│   ├── test_parser.py               ← 7 tests for resume_parser.py
│   ├── test_ats.py                  ← 6 tests for ats_scoring.py
│   └── test_jd_parser.py            ← 13 tests for jd_parser.py
│
├── main.py                          ← Entry point: runs full pipeline
├── ai_system.log                    ← Auto-generated: all log events
└── README.md
```

---

## Days Completed

| Day | Task | Deliverables |
|-----|------|-------------|
| Day 3 | Environment & Repository Setup | Folder structure, logger, `__init__.py` files, test scripts, README |
| Day 4 | Data Understanding & Structuring | `resume_schema.json`, `jd_schema.json`, AI data entity design |
| Day 5 | Resume Text Extraction Engine | `resume_parser.py` — PDF/DOCX reader, cleaner, section extractor |
| Day 6 | Job Description Parsing System | `jd_parser.py` — 18 roles, 70+ skills, synonyms, structured JD output |
| Day 7 | AI Data Pipeline & Storage Design — pipeline diagram, storage structure, metadata standards | Done |
---

## How the Pipeline Works

```
portfolio_manager.txt  (your JD input)
         │
         ▼
   jd_parser.py
   ┌──────────────────────────────┐
   │ extract_role()               │  → "portfolio manager"
   │ extract_skills()             │  → ["financial modeling", "bloomberg" ...]
   │ extract_experience()         │  → {min: 3, max: 7}
   │ extract_education()          │  → {degree: ["master"], certs: ["CFA"]}
   │ detect_skill_synonyms()      │  → {"bbg": "bloomberg", "dcf": "dcf valuation"}
   └──────────────────────────────┘
         │
         ▼
   resume_parser.py  (for each resume)
   ┌──────────────────────────────┐
   │ extract_resume_text()        │  → raw PDF/DOCX text
   │ clean_resume_text()          │  → normalized lowercase text
   │ extract_sections()           │  → {experience, education, skills ...}
   └──────────────────────────────┘
         │
         ▼
   ats_scoring.py
   ┌──────────────────────────────┐
   │ Skills score  (60 pts max)   │  → matched skills / total JD skills × 60
   │ Experience score (30 pts max)│  → based on years detected
   │ Education score (10 pts max) │  → degree level detected
   │ Total (capped at 100)        │
   └──────────────────────────────┘
         │
         ▼
   Ranked Output + JSON saved to data/output/
```

---

## ATS Scoring Formula

### Skill Score — 60 points
```
skill_score = (matched_skills / total_jd_skills) × 60
```

### Experience Score — 30 points
| Years of Experience | Points |
|---------------------|--------|
| 7+ years            | 30     |
| 5–6 years           | 25     |
| 3–4 years           | 18     |
| 1–2 years           | 10     |
| 0 years             | 0      |

### Education Score — 10 points
| Degree Detected     | Points |
|---------------------|--------|
| PhD / Doctorate     | 10     |
| Master's / M.Tech   | 10     |
| Bachelor's / B.Tech | 7      |
| Not found           | 0      |

### Total
```
Total Score = skill_score + exp_score + edu_score   (max 100)
```

### Example
```
JD Skills Required  : 8
Resume Matched      : 5   → skill_score  = (5/8) × 60 = 37.5
Experience          : 5 years            → exp_score   = 25
Education           : Master's           → edu_score   = 10
                                           Total       = 72 / 100
```

---

## JD Parser — Supported Roles (All 18)

| # | Role |
|---|------|
| 1 | Portfolio Manager |
| 2 | Senior Portfolio Manager / Head of Portfolio Management |
| 3 | Assistant / Associate Portfolio Manager |
| 4 | Fund Manager |
| 5 | Equity Research Analyst / Fixed Income Analyst |
| 6 | Investment Analyst / Portfolio Analyst |
| 7 | Quantitative Analyst / Quant Researcher |
| 8 | Risk Analyst / Risk Manager |
| 9 | Investment Advisor / Wealth Manager |
| 10 | Relationship Manager |
| 11 | Financial Planner |
| 12 | Chief Investment Officer (CIO) |
| 13 | Head of Investment Strategy / Strategic Portfolio Manager |
| 14 | Quantitative Portfolio Manager |
| 15 | Multi-Asset Portfolio Manager |
| 16 | Portfolio Operations Manager / Investment Operations Analyst |
| 17 | Compliance Officer |
| 18 | Portfolio Management System Specialist / Tech Analyst |

Each role supports **synonyms and variations** — e.g. "Senior PM", "Head PM", "Lead Portfolio Manager" all match role #2.

---

## Skill Synonym Detection

The parser detects 70+ skills and maps common abbreviations to canonical names:

| Synonym in JD/Resume | Canonical Skill Name |
|----------------------|----------------------|
| `BBG`                | Bloomberg |
| `DCF`                | DCF valuation |
| `Comps`              | Comparable analysis |
| `AA`                 | Asset allocation |
| `Algo trading`       | Algorithmic trading |
| `Macro analysis`     | Macroeconomic analysis |
| `SAA`                | Strategic asset allocation |
| `Recon`              | Reconciliation |
| `NAV`                | NAV calculation |
| `ML`                 | Machine learning |

---

## How to Run

### Step 1 — Activate virtual environment
```bash
source zecpath_env/bin/activate
```

### Step 2 — Install dependencies
```bash
pip install pdfplumber python-docx pytest
```

### Step 3 — Add your resumes
Place PDF or DOCX resume files inside:
```
data/sample_resumes/
```

### Step 4 — Set the job description
Edit the JD file at:
```
data/job_descriptions/portfolio_manager.txt
```
Replace it with any job description text you want to screen against.

### Step 5 — Run the pipeline
```bash
python main.py
```

### Expected Output
```
=======================================================
  ZecPath AI — Job Description
=======================================================
  Role        : portfolio manager
  Experience  : 3-7 years
  Skills (11) : ['financial analysis', 'asset allocation', ...]

=======================================================
  Candidates screened for: portfolio manager
=======================================================

  Candidate 1 — resume1.pdf
  Score          : 72 / 100
  Experience     : 5 years
  Education      : master
  Matched Skills : ['financial modeling', 'asset allocation', 'bloomberg']
  Missing Skills : ['cfa', 'risk management']

=======================================================
  Ranking — best match first
=======================================================
  #1  resume1.pdf  →  Score: 72 / 100
  #2  resume3.pdf  →  Score: 45 / 100
  #3  resume2.pdf  →  Score: 12 / 100
```

Results are also saved automatically to:
```
data/output/jd_parsed_output.json    ← Structured JD object
data/output/screening_results.json  ← All candidate scores
ai_system.log                        ← All events logged
```

---

## How to Run Tests

```bash
python -m pytest tests/ -v
```

### Expected Test Results
```
tests/test_parser.py::test_pdf_reader_resume1                PASSED
tests/test_parser.py::test_pdf_reader_resume2                PASSED
tests/test_parser.py::test_pdf_reader_resume3                PASSED
tests/test_parser.py::test_clean_resume_lowercase            PASSED
tests/test_parser.py::test_clean_resume_removes_special_chars PASSED
tests/test_parser.py::test_clean_resume_keeps_hyphens        PASSED
tests/test_parser.py::test_extract_sections_detects_experience PASSED

tests/test_ats.py::test_score_basic                          PASSED
tests/test_ats.py::test_score_perfect                        PASSED
tests/test_ats.py::test_score_zero                           PASSED
tests/test_ats.py::test_score_capped_at_100                  PASSED
tests/test_ats.py::test_education_phd_higher_than_bachelor   PASSED
tests/test_ats.py::test_more_experience_higher_score         PASSED

tests/test_jd_parser.py::test_parse_returns_all_keys         PASSED
tests/test_jd_parser.py::test_role_portfolio_manager         PASSED
tests/test_jd_parser.py::test_skills_found                   PASSED
tests/test_jd_parser.py::test_skill_synonym_bbg              PASSED
tests/test_jd_parser.py::test_extract_role_risk_manager      PASSED
tests/test_jd_parser.py::test_extract_role_unknown           PASSED
tests/test_jd_parser.py::test_experience_range               PASSED
tests/test_jd_parser.py::test_experience_plus                PASSED
tests/test_jd_parser.py::test_experience_not_found           PASSED
tests/test_jd_parser.py::test_education_dict_structure       PASSED
tests/test_jd_parser.py::test_education_certifications       PASSED
tests/test_jd_parser.py::test_synonym_detection              PASSED
tests/test_jd_parser.py::test_normalize_lowercase            PASSED

26 passed
```

---

## Output Files

### `data/output/jd_parsed_output.json`
```json
{
  "jd_id": "JD-PORTFOLIO-MANAGER",
  "role_name": "portfolio manager",
  "experience_requirements": {
    "min_years": 3,
    "max_years": 7,
    "raw": "3-7 years"
  },
  "required_skills": ["financial analysis", "asset allocation", "bloomberg"],
  "skill_synonyms": { "bbg": "bloomberg" },
  "ai_profile": {
    "seniority_level": "mid",
    "total_skills_found": 11
  }
}
```

### `data/output/screening_results.json`
```json
{
  "jd_role": "portfolio manager",
  "candidates": [
    {
      "resume_file": "resume1.pdf",
      "score": 72,
      "matched_skills": ["financial modeling", "bloomberg"],
      "missing_skills": ["cfa", "risk management"],
      "experience": 5,
      "education": "master"
    }
  ]
}
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.13 | Core language |
| pdfplumber | PDF text extraction |
| python-docx | DOCX resume parsing |
| pytest | Unit testing (26 tests) |
| logging | Event logging to `ai_system.log` |
| json | Structured output files |
| venv | Virtual environment |
| VS Code | Development IDE |

---

## Module Responsibilities

| File | Day | Purpose |
|------|-----|---------|
| `utils/logger.py` | Day 3 | Logs all events with timestamp to `ai_system.log` |
| `schemas/resume_schema.json` | Day 4 | Defines standard structure for candidate profile data |
| `schemas/jd_schema.json` | Day 4 | Defines standard structure for job description data |
| `parsers/resume_parser.py` | Day 5 | Extracts, cleans, and sections resume text from PDF/DOCX |
| `parsers/jd_parser.py` | Day 6 | Parses JD text into role, skills, experience, education |
| `ats_engine/ats_scoring.py` | Day 3 | Calculates weighted ATS score out of 100 |
| `main.py` | All days | Orchestrates the full pipeline end to end |
| `tests/test_parser.py` | Day 3/5 | 7 tests for resume extraction and cleaning |
| `tests/test_ats.py` | Day 3 | 6 tests for scoring formula |
| `tests/test_jd_parser.py` | Day 6 | 13 tests for JD parsing, roles, skills, synonyms |

---

*Developed as part of ZecPath AI System Architecture — Days 1 to 6.*