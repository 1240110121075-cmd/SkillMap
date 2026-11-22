from flask import Flask, render_template, request, jsonify, send_file
from analyzer import analyze_skills, create_pdf_report
from io import BytesIO

app = Flask(__name__)


def read_resume(file):
    filename = file.filename.lower()
    content = file.read()

    if filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    elif filename.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(content))
        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif filename.endswith(".docx"):
        from docx import Document
        document = Document(BytesIO(content))
        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    raise ValueError("Please upload a PDF, DOCX or TXT resume.")


def get_analysis():
    resume = request.files.get("resume")
    job_description = request.form.get("jobDescription", "")

    if not resume or not resume.filename:
        raise ValueError("Please upload your resume.")

    if not job_description.strip():
        raise ValueError("Please enter the job description.")

    resume_text = read_resume(resume)

    if not resume_text.strip():
        raise ValueError("Could not read the resume. Please check the file.")

    return analyze_skills(resume_text, job_description)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        result = get_analysis()
        return jsonify(result)

    except Exception as error:
        return jsonify({"error": str(error)}), 400


@app.route("/download-report", methods=["POST"])
def download_report():
    try:
        result = get_analysis()
        pdf_data = create_pdf_report(result)

        return send_file(
            BytesIO(pdf_data),
            mimetype="application/pdf",
            as_attachment=True,
            download_name="SkillMap_Report.pdf"
        )

    except Exception as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True)