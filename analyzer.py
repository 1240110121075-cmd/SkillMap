import re
from io import BytesIO
from xml.sax.saxutils import escape


SKILL_ALIASES = {
    "Python": ["python", "python3"],
    "Java": ["java", "core java"],
    "C": ["c language", "c programming"],
    "C++": ["c++", "cpp"],
    "SQL": ["sql", "structured query language"],
    "MySQL": ["mysql"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "JavaScript": ["javascript", "js"],
    "React": ["react", "reactjs", "react.js"],
    "Flask": ["flask"],
    "Django": ["django"],
    "Streamlit": ["streamlit"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "NLP": ["nlp", "natural language processing"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Scikit-learn": ["scikit-learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Data Science": ["data science"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel", "ms excel"],
    "Git": ["git"],
    "GitHub": ["github"],
    "AWS": ["aws", "amazon web services"],
    "Communication Skills": ["communication skills"],
    "Problem Solving": ["problem solving"],
    "Teamwork": ["teamwork", "team work"],
    "Cybersecurity": ["cybersecurity", "cyber security"],
    "Docker": ["docker"],
    "Linux": ["linux"],
    "Computer Networks": ["computer networks", "networking"],
    "REST API": ["rest api", "restful api", "rest apis"],
    "API Development": ["api development", "api integration"],
    "FastAPI": ["fastapi", "fast api"],
    "Node.js": ["node.js", "nodejs"],
    "MongoDB": ["mongodb"],
    "Data Structures": ["data structures", "dsa"],
    "OOP": ["object oriented programming", "oops", "oop"],
}


COURSE_RECOMMENDATIONS = {
    "Python": {
        "course": "Python for Everybody",
        "link": "https://www.py4e.com/"
    },
    "Java": {
        "course": "W3Schools Java Tutorial",
        "link": "https://www.w3schools.com/java/"
    },
    "SQL": {
        "course": "SQLBolt - Learn SQL",
        "link": "https://sqlbolt.com/"
    },
    "Machine Learning": {
        "course": "Google Machine Learning Crash Course",
        "link": "https://developers.google.com/machine-learning/crash-course"
    },
    "Data Analysis": {
        "course": "Kaggle Learn",
        "link": "https://www.kaggle.com/learn"
    },
    "Pandas": {
        "course": "Kaggle Learn - Pandas",
        "link": "https://www.kaggle.com/learn/pandas"
    },
    "NumPy": {
        "course": "NumPy Learn",
        "link": "https://numpy.org/learn/"
    },
    "Flask": {
        "course": "Flask Official Tutorial",
        "link": "https://flask.palletsprojects.com/en/stable/tutorial/"
    },
    "Django": {
        "course": "Django Official Tutorial",
        "link": "https://docs.djangoproject.com/en/stable/intro/tutorial01/"
    },
    "React": {
        "course": "React Official Learn",
        "link": "https://react.dev/learn"
    },
    "AWS": {
        "course": "AWS Skill Builder",
        "link": "https://skillbuilder.aws/"
    },
    "Git": {
        "course": "Git Tutorial",
        "link": "https://git-scm.com/docs/gittutorial"
    },
    "GitHub": {
        "course": "GitHub Skills",
        "link": "https://skills.github.com/"
    },
    "Power BI": {
        "course": "Microsoft Learn Power BI",
        "link": "https://learn.microsoft.com/training/"
    },
    "NLP": {
        "course": "Hugging Face NLP Course",
        "link": "https://huggingface.co/learn/nlp-course"
    },
    "TensorFlow": {
        "course": "TensorFlow Tutorials",
        "link": "https://www.tensorflow.org/tutorials"
    },
    "REST API": {
        "course": "REST API Tutorial",
        "link": "https://restfulapi.net/"
    },
    "FastAPI": {
        "course": "FastAPI Official Tutorial",
        "link": "https://fastapi.tiangolo.com/tutorial/"
    },
    "Node.js": {
        "course": "Node.js Official Learn",
        "link": "https://nodejs.org/en/learn"
    },
    "MongoDB": {
        "course": "MongoDB University",
        "link": "https://learn.mongodb.com/"
    },
}


def normalise(text):
    text = (text or "").lower()

    # Preserve important characters in technical skill names
    text = re.sub(r"[^a-z0-9+#./-]+", " ", text)

    return " " + re.sub(r"\s+", " ", text).strip() + " "


def extract_skills(text):
    normalised_text = normalise(text)
    found = set()

    for skill, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            alias_text = normalise(alias).strip()

            # Exact phrase matching avoids partial-word matches
            pattern = r"(?<![a-z0-9+#./-])" + re.escape(alias_text) + r"(?![a-z0-9+#./-])"

            if re.search(pattern, normalised_text):
                found.add(skill)
                break

    return sorted(found)


def analyze_resume_vs_jd(resume_text, jd_text):

    resume_skills = extract_skills(resume_text)
    required_skills = extract_skills(jd_text)

    resume_set = set(resume_skills)
    required_set = set(required_skills)

    matched = sorted(resume_set & required_set)
    missing = sorted(required_set - resume_set)
    additional = sorted(resume_set - required_set)

    if required_skills:
        score = round(
            (len(matched) / len(required_skills)) * 100,
            1
        )
    else:
        score = 0

    recommendations = []

    for skill in missing:
        course = COURSE_RECOMMENDATIONS.get(skill, {})

        recommendations.append({
            "skill": skill,
            "course": course.get(
                "course",
                f"Learn the fundamentals of {skill}"
            ),
            "link": course.get(
                "link",
                "https://www.coursera.org/"
            )
        })

    return {
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "additional_skills": additional,
        "match_percentage": score,
        "recommendations": recommendations
    }


def extract_text_from_file(uploaded_file):

    filename = uploaded_file.filename.lower()
    data = uploaded_file.read()

    if filename.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        import fitz

        with fitz.open(
            stream=data,
            filetype="pdf"
        ) as document:
            return "\n".join(
                page.get_text("text")
                for page in document
            )

    if filename.endswith(".docx"):
        from docx import Document

        document = Document(BytesIO(data))

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    raise ValueError("Upload PDF, DOCX or TXT resume.")


def create_pdf_report(result):

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer
    )
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    def safe_paragraph(value, style):
        return Paragraph(escape(str(value)), style)

    content = [
        Paragraph(
            "SkillMap - Resume Skill Gap Report",
            styles["Title"]
        ),
        Spacer(1, 20),

        safe_paragraph(
            f"Match Percentage: {result.get('match_percentage', 0)}%",
            styles["Heading2"]
        ),
        Spacer(1, 15),

        Paragraph("Matched Skills", styles["Heading3"]),
        safe_paragraph(
            ", ".join(result.get("matched_skills", [])) or "None",
            styles["BodyText"]
        ),
        Spacer(1, 15),

        Paragraph("Missing Skills", styles["Heading3"]),
        safe_paragraph(
            ", ".join(result.get("missing_skills", [])) or "None",
            styles["BodyText"]
        ),
        Spacer(1, 15),

        Paragraph("Additional Resume Skills", styles["Heading3"]),
        safe_paragraph(
            ", ".join(result.get("additional_skills", [])) or "None",
            styles["BodyText"]
        ),
        Spacer(1, 15),

        Paragraph("Course Recommendations", styles["Heading3"]),
        Spacer(1, 8)
    ]

    recommendations = result.get("recommendations", [])

    if recommendations:
        for item in recommendations:
            content.append(
                safe_paragraph(
                    f"{item.get('skill', '')}: {item.get('course', '')}",
                    styles["BodyText"]
                )
            )
            content.append(
                safe_paragraph(
                    item.get("link", ""),
                    styles["BodyText"]
                )
            )
            content.append(Spacer(1, 8))
    else:
        content.append(
            Paragraph(
                "No course recommendations available.",
                styles["BodyText"]
            )
        )

    document.build(content)

    return buffer.getvalue()


def analyze_skills(resume_text, job_description):
    return analyze_resume_vs_jd(
        resume_text,
        job_description
    )