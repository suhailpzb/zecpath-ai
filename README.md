# Zecpath AI — ATS Scoring Engine

## 📌 Project Overview
This module is part of the Zecpath AI Job Portal system.

It implements an **ATS (Applicant Tracking System) Scoring Engine** that evaluates candidate resumes based on skill match and experience.

---

## ⚙️ Features

- Resume skill match scoring
- Experience weightage scoring
- Automated score calculation
- Unit testing with pytest
- Modular microservice structure

---

## 🏗️ Project Structure

```
zecpath ai/
│
├── ats_engine/
│   ├── __init__.py
│   └── ats_scoring.py
│
├── tests/
│   ├── __init__.py
│   └── test_ats.py
│
├── utils/
│   └── logger.py
│
├── parsers/
├── screening_ai/
├── interview_ai/
│
├── main.py
└── README.md
```

---

## 🧮 ATS Scoring Logic

```
Score = (Skill Match × 10) + Experience
```

Example:

```
Skill Match = 8
Experience = 2

Score = 82
```

---

## ▶️ How to Run Project

Activate environment:

```bash
source zecpath_env/bin/activate
```

Run main file:

```bash
python main.py
```

---

## 🧪 How to Run Tests

```bash
python -m pytest
```

Expected output:

```
1 passed
```

---

## 🛠️ Tech Stack

- Python 3.13
- Pytest
- Virtual Environment (venv)
- VS Code

---

## 📊 Module Role in AI Architecture

This ATS engine is used in:

```
Resume Upload → Parsing → ATS Scoring → Candidate Ranking
```

---
Developed as part of **Zecpath AI System Architecture — Day 3 Tasks**.