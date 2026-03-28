from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def _normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join([line for line in lines if line])


def _resolve_soffice_path(configured_path: str | None = None) -> str:
    configured = (configured_path or "").strip()
    if configured and Path(configured).exists():
        return configured

    for name in ("soffice", "soffice.exe"):
        hit = shutil.which(name)
        if hit:
            return hit

    candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for item in candidates:
        if Path(item).exists():
            return item

    return ""


def _parse_with_win32com(file_path: str) -> str:
    try:
        import pythoncom  # type: ignore
        import win32com.client  # type: ignore
    except Exception:
        return ""

    word = None
    doc = None
    try:
        pythoncom.CoInitialize()
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(str(Path(file_path).resolve()), ReadOnly=True)
        raw = str(doc.Content.Text or "")
        return _normalize_text(raw)
    except Exception:
        return ""
    finally:
        if doc is not None:
            try:
                doc.Close(False)
            except Exception:
                pass
        if word is not None:
            try:
                word.Quit()
            except Exception:
                pass
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def _parse_with_soffice(file_path: str, configured_soffice: str | None = None) -> str:
    soffice = _resolve_soffice_path(configured_soffice)
    if not soffice:
        return ""

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            subprocess.run(
                [
                    soffice,
                    "--headless",
                    "--convert-to",
                    "txt:Text",
                    "--outdir",
                    tmp_dir,
                    file_path,
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            target = Path(tmp_dir) / f"{Path(file_path).stem}.txt"
            if not target.exists():
                candidates = list(Path(tmp_dir).glob("*.txt"))
                if not candidates:
                    return ""
                target = candidates[0]

            raw = target.read_text(encoding="utf-8", errors="ignore")
            return _normalize_text(raw)
    except Exception:
        return ""


def parse_doc(file_path: str, configured_soffice: str | None = None) -> str:
    text = _parse_with_win32com(file_path)
    if text:
        return text
    return _parse_with_soffice(file_path, configured_soffice)
