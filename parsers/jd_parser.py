# parsers/jd_parser.py
# Day 6 Deliverable – Job Description Parsing System
# Converts employer JDs into structured AI-readable job requirement objects

import re
import json
import os
from datetime import datetime


# ─────────────────────────────────────────────────────────────────
# 1. ALL 18 ROLE DEFINITIONS  (canonical name + variations)
# ─────────────────────────────────────────────────────────────────

ROLE_DEFINITIONS = [
    ("chief investment officer",
     ["chief investment officer", "cio", "head of investments"]),

    ("head of portfolio management",
     ["head of portfolio management", "head pm"]),

    ("head of investment strategy",
     ["head of investment strategy", "investment strategist"]),

    ("senior portfolio manager",
     ["senior portfolio manager", "senior pm", "lead portfolio manager"]),

    ("strategic portfolio manager",
     ["strategic portfolio manager"]),

    ("quantitative portfolio manager",
     ["quantitative portfolio manager", "quant pm"]),

    ("multi-asset portfolio manager",
     ["multi-asset portfolio manager", "multi asset portfolio manager"]),

    ("portfolio operations manager",
     ["portfolio operations manager", "portfolio ops manager"]),

    ("investment operations analyst",
     ["investment operations analyst", "inv operations analyst"]),

    ("assistant portfolio manager",
     ["assistant portfolio manager", "junior portfolio manager", "junior pm"]),

    ("associate portfolio manager",
     ["associate portfolio manager", "associate pm"]),

    ("equity research analyst",
     ["equity research analyst", "equity analyst"]),

    ("fixed income analyst",
     ["fixed income analyst", "bond analyst"]),

    ("investment analyst",
     ["investment analyst", "inv analyst"]),

    ("portfolio analyst",
     ["portfolio analyst", "port analyst"]),

    ("quantitative analyst",
     ["quantitative analyst", "quant analyst", "quant researcher", "quant"]),

    ("portfolio manager",
     ["portfolio manager", "pm", "investment manager"]),

    ("fund manager",
     ["fund manager", "mutual fund manager", "hedge fund manager", "fund mgr"]),

    ("risk analyst",
     ["risk analyst", "portfolio risk analyst"]),

    ("risk manager",
     ["risk manager", "risk officer", "risk mgr"]),

    ("investment advisor",
     ["investment advisor", "investment adviser"]),

    ("wealth manager",
     ["wealth manager", "wealth advisor"]),

    ("relationship manager",
     ["relationship manager", "client relationship manager", "rm"]),

    ("financial planner",
     ["financial planner", "financial advisor", "financial consultant"]),

    ("compliance officer",
     ["compliance officer", "compliance manager", "regulatory compliance officer"]),

    ("portfolio management system specialist",
     ["pms specialist", "pms analyst", "portfolio systems analyst"]),

    ("tech analyst",
     ["tech analyst", "investment technology analyst"]),
]


# ─────────────────────────────────────────────────────────────────
# 2. ALL SKILLS WITH SYNONYMS
# ─────────────────────────────────────────────────────────────────

SKILL_DEFINITIONS = [
    # Technical
    ("financial analysis",       ["financial analysis"]),
    ("financial modeling",       ["financial modeling", "financial model", "fin modeling"]),
    ("portfolio construction",   ["portfolio construction"]),
    ("asset allocation",         ["asset allocation", "asset mix"]),
    ("risk management",          ["risk management", "risk mgmt"]),
    ("risk assessment",          ["risk assessment"]),
    ("investment analysis",      ["investment analysis"]),
    ("performance attribution",  ["performance attribution", "return attribution"]),
    ("security analysis",        ["security analysis", "securities research"]),
    ("portfolio optimization",   ["portfolio optimization"]),
    ("quantitative modeling",    ["quantitative modeling", "quant modeling"]),
    ("statistical analysis",     ["statistical analysis"]),
    ("econometrics",             ["econometrics", "econometric analysis"]),
    ("backtesting",              ["backtesting", "backtest"]),
    ("algorithmic trading",      ["algorithmic trading", "algo trading", "systematic trading"]),
    ("machine learning",         ["machine learning", " ml "]),
    ("dcf valuation",            ["dcf", "discounted cash flow"]),
    ("comparable analysis",      ["comparable analysis", "comps"]),
    ("fundamental analysis",     ["fundamental analysis", "bottom-up analysis"]),
    ("technical analysis",       ["technical analysis"]),
    ("scenario analysis",        ["scenario analysis"]),
    ("stress testing",           ["stress testing", "stress test"]),
    ("risk analytics",           ["risk analytics", "risk analysis"]),
    ("sensitivity analysis",     ["sensitivity analysis"]),
    ("hedging",                  ["hedging", "hedge"]),
    ("nav calculation",          ["nav", "net asset value"]),
    ("trade settlement",         ["trade settlement"]),
    ("portfolio accounting",     ["portfolio accounting"]),
    ("reconciliation",           ["reconciliation", "recon"]),
    ("compliance monitoring",    ["compliance monitoring"]),
    ("strategic asset allocation", ["strategic asset allocation", "saa"]),
    ("macroeconomic analysis",   ["macroeconomic analysis", "macro analysis", "top-down analysis"]),
    ("financial planning",       ["financial planning"]),
    ("tax planning",             ["tax planning"]),
    ("retirement planning",      ["retirement planning"]),
    ("estate planning",          ["estate planning"]),
    # Domain
    ("equities",                 ["equities", "equity", "stocks"]),
    ("fixed income",             ["fixed income", "bonds", "debt instruments"]),
    ("alternative investments",  ["alternative investments", "alternatives", "alts"]),
    ("derivatives",              ["derivatives", "options", "futures"]),
    ("mutual funds",             ["mutual funds"]),
    ("hedge funds",              ["hedge funds"]),
    ("private equity",           ["private equity"]),
    ("multi-asset",              ["multi-asset", "multi asset"]),
    ("market risk",              ["market risk"]),
    ("credit risk",              ["credit risk"]),
    ("liquidity risk",           ["liquidity risk"]),
    ("operational risk",         ["operational risk"]),
    # Soft skills
    ("client communication",     ["client communication", "client relations"]),
    ("leadership",               ["leadership", "team management"]),
    ("analytical thinking",      ["analytical thinking", "analytical skills"]),
    ("attention to detail",      ["attention to detail"]),
    ("problem-solving",          ["problem-solving", "problem solving"]),
    ("communication",            ["communication"]),
    # Tools
    ("excel",                    ["excel", "ms excel"]),
    ("bloomberg",                ["bloomberg", "bbg", "bloomberg terminal"]),
    ("factset",                  ["factset"]),
    ("python",                   ["python"]),
    ("r",                        [" r programming", " r language"]),
    ("matlab",                   ["matlab"]),
    ("sql",                      ["sql"]),
    ("blackrock aladdin",        ["blackrock aladdin", "aladdin"]),
    ("bloomberg aim",            ["bloomberg aim"]),
    ("simcorp",                  ["simcorp"]),
    # Certifications
    ("cfa",                      ["cfa", "chartered financial analyst"]),
    ("caia",                     ["caia"]),
    ("cfp",                      ["cfp", "certified financial planner"]),
    ("frm",                      ["frm", "financial risk manager"]),
    ("cams",                     ["cams"]),
    # General tech/data
    ("data analysis",            ["data analysis", "data analytics"]),
    ("reporting",                ["reporting"]),
    ("accounting",               ["accounting"]),
]


# ─────────────────────────────────────────────────────────────────
# 3. NORMALIZE TEXT
# ─────────────────────────────────────────────────────────────────

def normalize_text(text):
    """Clean and normalize JD text for matching."""
    text = text.lower().strip()
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[^a-z0-9\s\-\/]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


# ─────────────────────────────────────────────────────────────────
# 4. EXTRACT ROLE
# ─────────────────────────────────────────────────────────────────

def extract_role(text):
    """
    Match the role from JD text using canonical names and synonyms.
    Checks longer role names first to avoid partial matches.
    """
    for canonical_name, variations in ROLE_DEFINITIONS:
        for variation in variations:
            if variation in text:
                return canonical_name
    return "unknown"


# ─────────────────────────────────────────────────────────────────
# 5. EXTRACT EXPERIENCE
# ─────────────────────────────────────────────────────────────────

def extract_experience(text):
    """
    Extract experience requirements.
    Handles: '3-7 years', '5+ years', 'minimum 3 years', '5 years of experience'
    """
    # Range: "3-7 years"
    match = re.search(r'(\d+)\s*[-–]\s*(\d+)\s*years?', text)
    if match:
        return {"min_years": int(match.group(1)), "max_years": int(match.group(2)),
                "raw": match.group()}

    # Plus: "5+ years"
    match = re.search(r'(\d+)\s*\+\s*years?', text)
    if match:
        return {"min_years": int(match.group(1)), "max_years": None, "raw": match.group()}

    # Minimum: "minimum 5 years"
    match = re.search(r'(?:minimum|at least|min)\s+(\d+)\s*years?', text)
    if match:
        return {"min_years": int(match.group(1)), "max_years": None, "raw": match.group()}

    # Plain: "5 years of experience"
    match = re.search(r'(\d+)\s*years?\s*(?:of)?\s*experience', text)
    if match:
        return {"min_years": int(match.group(1)), "max_years": None, "raw": match.group()}

    return {"min_years": None, "max_years": None, "raw": "not found"}


# ─────────────────────────────────────────────────────────────────
# 6. EXTRACT SKILLS  (with synonym detection)
# ─────────────────────────────────────────────────────────────────

def extract_skills(text):
    """
    Extract all skills from JD or resume text.
    Uses canonical names + synonym matching.
    Returns list of matched canonical skill names.
    """
    found = []
    for canonical_name, synonyms in SKILL_DEFINITIONS:
        for synonym in synonyms:
            if synonym in text:
                found.append(canonical_name)
                break
    return found


def detect_skill_synonyms(text):
    """
    Returns dict showing which synonym in the text mapped to which skill.
    Example: {"bbg": "bloomberg", "dcf": "dcf valuation"}
    """
    synonym_map = {}
    for canonical_name, synonyms in SKILL_DEFINITIONS:
        for synonym in synonyms:
            if synonym in text and synonym != canonical_name:
                synonym_map[synonym.strip()] = canonical_name
    return synonym_map


# ─────────────────────────────────────────────────────────────────
# 7. EXTRACT EDUCATION
# ─────────────────────────────────────────────────────────────────

def extract_education(text):
    """
    Extract education requirements from JD text.
    Returns structured dict with degree_level, fields, certifications.
    """
    result = {"degree_level": [], "fields": [], "certifications": []}

    if "phd" in text or "doctorate" in text:
        result["degree_level"].append("phd")
    if "master" in text or "msc" in text:
        result["degree_level"].append("master")
    if "bachelor" in text or "btech" in text or "undergraduate" in text:
        result["degree_level"].append("bachelor")
    if not result["degree_level"]:
        result["degree_level"] = ["not specified"]

    for field in ["finance", "economics", "accounting", "mathematics",
                  "statistics", "computer science", "business", "law"]:
        if field in text:
            result["fields"].append(field)

    cert_map = {"CFA": ["cfa"], "CAIA": ["caia"], "CFP": ["cfp"],
                "FRM": ["frm"], "PRM": ["prm"], "CAMS": ["cams"]}
    for cert, keywords in cert_map.items():
        if any(kw in text for kw in keywords):
            result["certifications"].append(cert)

    return result


# ─────────────────────────────────────────────────────────────────
# 8. BUILD STRUCTURED JD OBJECT  (Day 4 Schema)
# ─────────────────────────────────────────────────────────────────

def build_jd_object(text, jd_id=None):
    """
    Build a fully structured, AI-readable JD profile object.
    Matches the Day 4 JD schema.
    """
    normalized = normalize_text(text)
    role       = extract_role(normalized)
    skills     = extract_skills(normalized)
    experience = extract_experience(normalized)
    education  = extract_education(normalized)
    synonyms   = detect_skill_synonyms(normalized)

    min_exp = experience.get("min_years")
    if min_exp is None:     seniority = "unknown"
    elif min_exp >= 12:     seniority = "executive"
    elif min_exp >= 8:      seniority = "senior"
    elif min_exp >= 3:      seniority = "mid"
    else:                   seniority = "junior"

    return {
        "jd_id":                  jd_id or f"JD-{role.upper().replace(' ', '-')[:20]}",
        "role_name":              role,
        "experience_requirements": experience,
        "education_requirements": education,
        "required_skills":        skills,
        "skill_synonyms":         synonyms,
        "normalized_skill_tags":  [s.lower().replace(" ", "-") for s in skills],
        "ai_profile": {
            "seniority_level":    seniority,
            "total_skills_found": len(skills),
        },
        "parsed_at": datetime.utcnow().isoformat() + "Z"
    }


# ─────────────────────────────────────────────────────────────────
# 9. MAIN PARSER FUNCTION
# ─────────────────────────────────────────────────────────────────

def parse_job_description(text, jd_id=None):
    """
    Main entry point. Takes raw JD text, returns structured dict.
    Used by main.py and tests.
    """
    normalized = normalize_text(text)
    return {
        "role":       extract_role(normalized),
        "skills":     extract_skills(normalized),
        "experience": extract_experience(normalized),
        "education":  extract_education(normalized),
    }


# ─────────────────────────────────────────────────────────────────
# 10. SAVE JD OUTPUT TO FILE
# ─────────────────────────────────────────────────────────────────

def save_jd_output(text, output_path="data/output/jd_parsed_output.json", jd_id=None):
    """Parse JD and save structured output to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    jd_object = build_jd_object(text, jd_id)
    with open(output_path, "w") as f:
        json.dump(jd_object, f, indent=2)
    print(f"[✓] JD output saved to {output_path}")
    return jd_object


# ─────────────────────────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample = """
    Portfolio Manager — 3-7 years experience in investment analysis.
    Skills: financial modeling, asset allocation, risk management, bloomberg, excel.
    Bachelor or Master in Finance or Economics. CFA preferred.
    """
    print(json.dumps(parse_job_description(sample), indent=2))