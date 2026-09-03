import logging

logger = logging.getLogger(__name__)


def parse_file(file_path: str) -> str:
    """Extract text from PDF, DOCX, or TXT file. Returns empty string on error."""
    try:
        lower = file_path.lower()
        if lower.endswith(".pdf"):
            return _parse_pdf(file_path)
        elif lower.endswith(".docx"):
            return _parse_docx(file_path)
        elif lower.endswith(".txt"):
            return _parse_txt(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_path}")
            return ""
    except Exception as e:
        logger.error(f"Error parsing file {file_path}: {e}")
        return ""


def _parse_pdf(file_path: str) -> str:
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts)
    except Exception as e:
        logger.error(f"PDF parse error: {e}")
        return ""


def _parse_docx(file_path: str) -> str:
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        logger.error(f"DOCX parse error: {e}")
        return ""


def _parse_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        logger.error(f"TXT parse error: {e}")
        return ""
