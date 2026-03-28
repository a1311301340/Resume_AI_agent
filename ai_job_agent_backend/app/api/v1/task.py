from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.deps import process_task_use_case, task_repo
from app.schemas.request import TaskCreateRequest
from app.schemas.response import BaseResponse, success_response

router = APIRouter(prefix="/task", tags=["Task"])


@router.post("/create", response_model=BaseResponse)
def create_task(req: TaskCreateRequest):
    file_path = req.file_path or ""
    filename = Path(file_path).name if file_path else "manual_task.docx"

    if not file_path:
        task = task_repo.create_task(filename=filename, file_path="")
        task_repo.update_task_status(task.task_id, status="failed", progress=100, current_step="请先上传简历文件")
        return success_response(task.to_task_status())

    task = task_repo.create_task(filename=filename, file_path=file_path)
    task_repo.update_task_status(task.task_id, status="processing", progress=30, current_step="任务已创建")

    try:
        mode_map = {
            "resume_parse": "resume_check",
            "jd_match": "jd_match",
            "full_process": "project_rewrite",
        }
        process_task_use_case.execute(
            task_id=task.task_id,
            jd_text=req.jd_text,
            mode=mode_map.get(req.mode, "project_rewrite"),
        )
    except Exception as exc:
        detail = str(exc).strip() or "处理失败"
        task_repo.update_task_status(task.task_id, status="failed", progress=100, current_step=detail[:200])

    latest = task_repo.get_task(task.task_id)
    return success_response(latest.to_task_status() if latest else task.to_task_status())


@router.get("/{task_id}", response_model=BaseResponse)
def get_task_status(task_id: str):
    task = task_repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(task.to_task_status())
