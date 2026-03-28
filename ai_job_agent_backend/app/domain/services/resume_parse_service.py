from pathlib import Path

from app.core.settings import settings
from app.infrastructure.parsers.doc_parser import parse_doc
from app.infrastructure.parsers.docx_parser import parse_docx
from app.infrastructure.parsers.pdf_parser import parse_pdf


class ResumeParseService:
    def parse_resume(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            return parse_pdf(file_path)
        if ext == ".doc":
            return parse_doc(file_path, settings.LIBREOFFICE_SOFFICE)
        if ext == ".docx":
            return parse_docx(file_path)
        return ""
