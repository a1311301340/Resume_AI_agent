from __future__ import annotations

from pathlib import Path

import pymysql
from fastapi import APIRouter
from pymysql.cursors import DictCursor

from app.core.settings import settings
from app.schemas.response import BaseResponse, success_response

router = APIRouter(prefix="/health", tags=["Health"])


def _check_db() -> dict:
    payload: dict = {
        "db_connected": False,
        "tables": {},
        "error": "",
    }
    try:
        with pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset=settings.DB_CHARSET,
            autocommit=True,
            cursorclass=DictCursor,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    """,
                    (settings.DB_NAME,),
                )
                rows = cursor.fetchall() or []
        names = {str(row.get("table_name", "")) for row in rows}
        payload["db_connected"] = True
        payload["tables"] = {
            "job_task": "job_task" in names,
            "task_result": "task_result" in names,
            "resume_text_archive": "resume_text_archive" in names,
            "interview_chat_message": "interview_chat_message" in names,
            "task_result_version": "task_result_version" in names,
        }
        return payload
    except Exception as exc:
        payload["error"] = str(exc)
        return payload


@router.get("/full", response_model=BaseResponse)
def health_full():
    upload_dir = Path(settings.UPLOAD_DIR)
    output_dir = Path(settings.OUTPUT_DIR)
    db_info = _check_db()
    data = {
        "api": "ok",
        "upload_dir_exists": upload_dir.exists(),
        "output_dir_exists": output_dir.exists(),
        "libreoffice_soffice": settings.LIBREOFFICE_SOFFICE,
        "db": db_info,
    }
    return success_response(data)
