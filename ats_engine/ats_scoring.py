# ats_engine/ats_scoring.py

def calculate_score(skill_match, experience, education="not found", total_jd_skills=None):

    # Skills score (60 points max)
    if total_jd_skills and total_jd_skills > 0:
        skill_score = (skill_match / total_jd_skills) * 60
    else:
        skill_score = min(skill_match * 8, 60)

    # Experience score (30 points max)
    if experience >= 7:       exp_score = 30
    elif experience >= 5:     exp_score = 25
    elif experience >= 3:     exp_score = 18
    elif experience >= 1:     exp_score = 10
    else:                     exp_score = 0

    # Education score (10 points max)
    edu = education.lower() if education else ""
    if "phd" in edu:                           edu_score = 10
    elif "master" in edu or "mtech" in edu:    edu_score = 10
    elif "bachelor" in edu or "btech" in edu:  edu_score = 7
    else:                                      edu_score = 0

    return min(round(skill_score + exp_score + edu_score), 100)