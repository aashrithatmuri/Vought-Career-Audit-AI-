import fitz


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from uploaded PDF file
    """

    text = ""

    pdf_document = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    for page in pdf_document:
        text += page.get_text()

    return text