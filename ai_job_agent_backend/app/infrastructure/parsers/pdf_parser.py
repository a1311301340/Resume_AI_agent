def parse_pdf(file_path: str) -> str:
    try:
        import pdfplumber  # type: ignore
    except ImportError:
        return ""

    texts: list[str] = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                texts.append(page.extract_text() or "")
    except Exception:
        return ""
    return "\n".join(texts)

