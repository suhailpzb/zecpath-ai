import pdfplumber
import docx
import re

def extract_pdf_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_docx_text(file_path):
    doc = docx.Document(file_path)
    text = []
    
    for para in doc.paragraphs:
        text.append(para.text)

    return "\n".join(text)



def clean_resume_text(text):

    text = text.lower()

    text = re.sub(r'\n+', '\n', text)

    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    text = text.strip()

    return text