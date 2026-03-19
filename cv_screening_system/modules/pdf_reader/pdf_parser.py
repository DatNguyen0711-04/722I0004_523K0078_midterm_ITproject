import re

import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    raw_text = "\n".join(text_parts)
    # Fix hyphenated line breaks and collapse excessive blank lines
    raw_text = re.sub(r"(?<=[a-z])-\n(?=[a-z])", "", raw_text)
    raw_text = re.sub(r"\n{3,}", "\n\n", raw_text)
    return raw_text
