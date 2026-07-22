"""
Extracts raw text from uploaded resume files (PDF, DOCX, TXT).
"""
from pathlib import Path

import pdfplumber
import docx


class UnsupportedFileType(Exception):
    pass


def extract_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)
    elif suffix == ".docx":
        return _extract_docx(path)
    elif suffix == ".txt":
        return path.read_text(errors="ignore")
    else:
        raise UnsupportedFileType(
            f"Unsupported file type '{suffix}'. Please upload PDF, DOCX, or TXT."
        )


def _extract_pdf(path: Path) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_docx(path: Path) -> str:
    document = docx.Document(str(path))
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())
