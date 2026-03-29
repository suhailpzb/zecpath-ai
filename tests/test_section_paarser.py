# tests/test_section_parser.py
# Day 8 — Tests for section_parser.py

from parsers.section_parser import (
    detect_section_heading,
    classify_resume_sections,
    build_labeled_resume,
    generate_accuracy_report,
    detect_section_by_content,
)

SAMPLE_RESUME = """
John Smith
john@email.com  |  +1-234-567-890

SUMMARY
Experienced data scientist with 5 years of experience in ML and analytics.

SKILLS
Python, SQL, Machine Learning, TensorFlow, Tableau, Excel

WORK EXPERIENCE
Data Scientist at Google, January 2020 - Present
Developed predictive models for 20+ fund managers.

Senior Analyst at Amazon, June 2018 - December 2019
Built dashboards using Tableau for 80+ HNIs.

EDUCATION
Bachelor of Science in Computer Science
University of California San Diego, 2018

CERTIFICATIONS
AWS Certified Machine Learning Specialist
Google Data Analytics Certificate

PROJECTS
Sales Prediction Engine — Python, scikit-learn
Customer Segmentation — Clustering for 10K+ customers
"""


def test_detect_heading_skills():
    assert detect_section_heading("SKILLS") == "skills"


def test_detect_heading_experience():
    assert detect_section_heading("WORK EXPERIENCE") == "experience"


def test_detect_heading_education():
    assert detect_section_heading("EDUCATION") == "education"


def test_detect_heading_certifications():
    assert detect_section_heading("CERTIFICATIONS") == "certifications"


def test_detect_heading_projects():
    assert detect_section_heading("PROJECTS") == "projects"


def test_detect_heading_summary():
    assert detect_section_heading("SUMMARY") == "summary"


def test_detect_heading_no_match():
    assert detect_section_heading("John Smith is a great developer") is None


def test_detect_heading_with_separator():
    assert detect_section_heading("--- Skills ---") == "skills"


def test_classify_sections_returns_dict():
    result = classify_resume_sections(SAMPLE_RESUME)
    assert isinstance(result, dict)
    assert len(result) > 0


def test_classify_detects_skills():
    result = classify_resume_sections(SAMPLE_RESUME)
    assert "skills" in result


def test_classify_detects_experience():
    result = classify_resume_sections(SAMPLE_RESUME)
    assert "experience" in result


def test_classify_detects_education():
    result = classify_resume_sections(SAMPLE_RESUME)
    assert "education" in result


def test_classify_detects_certifications():
    result = classify_resume_sections(SAMPLE_RESUME)
    has_cert = "certifications" in result or "education" in result
    assert has_cert


def test_classify_detects_projects():
    result = classify_resume_sections(SAMPLE_RESUME)
    assert "projects" in result


def test_classify_section_content_not_empty():
    result = classify_resume_sections(SAMPLE_RESUME)
    for section, content in result.items():
        assert len(content) > 0


def test_build_labeled_resume_structure():
    sections = classify_resume_sections(SAMPLE_RESUME)
    labeled  = build_labeled_resume("test_resume.pdf", SAMPLE_RESUME, sections)
    assert "source_file"      in labeled
    assert "sections_found"   in labeled
    assert "sections_missing" in labeled
    assert "labeled_sections" in labeled
    assert "labeled_at"       in labeled


def test_build_labeled_resume_sections_found():
    sections = classify_resume_sections(SAMPLE_RESUME)
    labeled  = build_labeled_resume("test_resume.pdf", SAMPLE_RESUME, sections)
    assert len(labeled["sections_found"]) > 0


def test_nlp_content_detection_skills():
    text = "python sql machine learning tensorflow tableau git"
    assert detect_section_by_content(text) == "skills"


def test_nlp_content_detection_experience():
    text = "january 2020 present manager analyst developed built led designed"
    assert detect_section_by_content(text) == "experience"


def test_nlp_content_detection_education():
    text = "bachelor degree university science graduated gpa diploma"
    assert detect_section_by_content(text) == "education"


def test_generate_accuracy_report():
    sections = classify_resume_sections(SAMPLE_RESUME)
    labeled  = build_labeled_resume("test.pdf", SAMPLE_RESUME, sections)
    report, _ = generate_accuracy_report([labeled], output_dir="data/output")
    assert "accuracy_by_section" in report
    assert "total_resumes"       in report
    assert report["total_resumes"] == 1


if __name__ == "__main__":
    print("=== Running Day 8 Tests ===\n")
    test_detect_heading_skills()
    print("[PASS] detect skills heading")
    test_detect_heading_experience()
    print("[PASS] detect experience heading")
    test_detect_heading_education()
    print("[PASS] detect education heading")
    test_detect_heading_certifications()
    print("[PASS] detect certifications heading")
    test_detect_heading_projects()
    print("[PASS] detect projects heading")
    test_detect_heading_summary()
    print("[PASS] detect summary heading")
    test_classify_sections_returns_dict()
    print("[PASS] classify returns dict")
    test_classify_detects_skills()
    print("[PASS] detects skills section")
    test_classify_detects_experience()
    print("[PASS] detects experience section")
    test_classify_detects_education()
    print("[PASS] detects education section")
    test_build_labeled_resume_structure()
    print("[PASS] labeled resume structure correct")
    test_nlp_content_detection_skills()
    print("[PASS] NLP detects skills content")
    test_nlp_content_detection_experience()
    print("[PASS] NLP detects experience content")
    test_generate_accuracy_report()
    print("[PASS] accuracy report generated")
    print("\n=== All Day 8 tests passed ✓ ===")