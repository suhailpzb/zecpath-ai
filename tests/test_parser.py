from parsers.resume_parser import extract_pdf_text

def test_pdf_reader():
    
    text = extract_pdf_text("data/sample_resumes/resume1.pdf")

    assert len(text) > 0