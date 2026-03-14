from parsers.resume_parser import extract_pdf_text, clean_resume_text
from ats_engine.ats_scoring import calculate_score
from utils.logger import log_info
import re

def main():

    file_path = "data/sample_resumes/resume1.pdf"

    log_info("Starting Zecpath AI pipeline")

    # Extract resume text
    raw_text = extract_pdf_text(file_path)
    cleaned = clean_resume_text(raw_text)

    # Skill list
    skills_list = ["python", "sql", "machine learning", "java", "c++", "data analysis"]

    detected_skills = []

    for skill in skills_list:
        if skill in cleaned:
            detected_skills.append(skill)

    skill_match = len(detected_skills)

    # Detect experience
    experience_match = re.search(r'(\d+)\s+year', cleaned)

    if experience_match:
        experience = int(experience_match.group(1))
    else:
        experience = 0

    # Detect education
    education_keywords = ["bachelor", "master", "btech", "mtech", "phd"]

    detected_education = "Not Found"

    for edu in education_keywords:
        if edu in cleaned:
            detected_education = edu
            break

    # Calculate ATS score
    score = calculate_score(skill_match, experience)

    # Display results
    print("\n----- Candidate Resume Summary -----\n")

    print("Skills:", detected_skills)
    print("Experience:", experience, "years")
    print("Education:", detected_education)

    print("\nCandidate Score:", score)

    log_info(f"Skills: {detected_skills}")
    log_info(f"Experience: {experience}")
    log_info(f"Education: {detected_education}")
    log_info(f"Candidate Score: {score}")


if __name__ == "__main__":
    main()