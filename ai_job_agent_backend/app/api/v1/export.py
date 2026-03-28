from fastapi import APIRouter, HTTPException, Query

from app.api.deps import export_service, task_repo
from app.schemas.response import BaseResponse, success_response

router = APIRouter(prefix="/export", tags=["Export"])


def _export_by_task_id(task_id: str) -> dict:
    task = task_repo.get_task(task_id)
    if not task or not task.result:
        raise HTTPException(status_code=404, detail="结果不存在")
    content = str(task.result)
    path = export_service.export_txt(task_id, content)
    return {"export_path": path}


@router.get("/{task_id}", response_model=BaseResponse)
def export_result(task_id: str):
    return success_response(_export_by_task_id(task_id))


@router.get("/result/{task_id}", response_model=BaseResponse)
def export_result_alias(task_id: str):
    # Compatibility alias for /export/result/{task_id}
    return success_response(_export_by_task_id(task_id))


result_export_router = APIRouter(prefix="/result", tags=["Result"])


@result_export_router.get("/{task_id}/export", response_model=BaseResponse)
def export_result_under_result(task_id: str, format: str = Query(default="docx")):
    # Keep the same payload shape regardless of format in this version.
    data = _export_by_task_id(task_id)
    data["format"] = format
    return success_response(data)

