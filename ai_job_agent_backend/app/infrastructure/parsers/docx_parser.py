def parse_docx(file_path: str) -> str:
    try:
        from docx import Document  # type: ignore
    except ImportError:
        return ""

    try:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception:
        return ""

