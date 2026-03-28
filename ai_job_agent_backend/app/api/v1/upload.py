from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.deps import local_storage, resume_parse_service, resume_text_archive_repo, task_repo
from app.core.settings import settings
from app.schemas.response import BaseResponse, success_response

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("", response_model=BaseResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    ext = Path(file.filename or "").suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    content = await file.read()
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail=f"文件大小不能超过 {settings.MAX_FILE_SIZE_MB}MB")

    saved_path = local_storage.save_upload_file(file.filename, content)
    task = task_repo.create_task(filename=file.filename, file_path=str(saved_path))

    archive_saved = False
    archive_error: str | None = None
    resume_text = ""
    try:
        resume_text = resume_parse_service.parse_resume(str(saved_path))
        archive_saved, archive_error = resume_text_archive_repo.save_or_update_resume_text(
            task_id=task.task_id,
            filename=task.filename,
            file_path=task.file_path,
            resume_text=resume_text,
        )
    except Exception as exc:
        archive_error = str(exc)

    payload = task.to_dict()
    payload["resume_text_saved"] = archive_saved
    payload["resume_text_length"] = len(resume_text)
    if archive_error:
        payload["resume_text_error"] = archive_error
    return success_response(payload)
