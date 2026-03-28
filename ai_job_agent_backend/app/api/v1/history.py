import json

from fastapi import APIRouter, HTTPException

from app.api.deps import chat_log_repo, history_repo, result_version_repo
from app.schemas.request import SaveResultVersionRequest
from app.schemas.response import BaseResponse, success_response

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/tasks", response_model=BaseResponse)
def list_tasks():
    rows, err = history_repo.list_tasks(limit=50)
    if err:
        raise HTTPException(status_code=500, detail=f"failed to list history tasks: {err}")
    return success_response(rows)


@router.get("/tasks/{task_id}", response_model=BaseResponse)
def get_task_detail(task_id: str):
    row, err = history_repo.get_task_detail(task_id)
    if err:
        raise HTTPException(status_code=500, detail=f"failed to fetch task detail: {err}")
    if not row:
        raise HTTPException(status_code=404, detail="task not found")

    result_payload = None
    raw = row.get("result_json")
    if isinstance(raw, str) and raw.strip():
        try:
            result_payload = json.loads(raw)
        except Exception:
            result_payload = {"raw": raw}

    payload = {
        "task_id": row.get("task_id"),
        "filename": row.get("filename"),
        "file_path": row.get("file_path"),
        "status": row.get("status"),
        "progress": row.get("progress"),
        "current_step": row.get("current_step"),
        "created_at": str(row.get("created_at") or ""),
        "updated_at": str(row.get("updated_at") or ""),
        "resume_text": row.get("resume_text") or "",
        "resume_text_length": int(row.get("resume_text_length") or 0),
        "result": result_payload,
    }
    return success_response(payload)


@router.get("/tasks/{task_id}/chats", response_model=BaseResponse)
def get_task_chats(task_id: str):
    rows, err = chat_log_repo.list_messages(task_id=task_id, limit=300)
    if err:
        raise HTTPException(status_code=500, detail=f"failed to fetch chat history: {err}")
    return success_response(rows)


@router.post("/tasks/{task_id}/versions", response_model=BaseResponse)
def save_task_result_version(task_id: str, req: SaveResultVersionRequest):
    payload, err = result_version_repo.save_version(
        task_id=task_id,
        result=req.result,
        note=req.note,
        apply_as_current=req.apply_as_current,
    )
    if err:
        raise HTTPException(status_code=500, detail=f"failed to save result version: {err}")
    return success_response(payload)


@router.get("/tasks/{task_id}/versions", response_model=BaseResponse)
def list_task_result_versions(task_id: str):
    rows, err = result_version_repo.list_versions(task_id=task_id, limit=100)
    if err:
        raise HTTPException(status_code=500, detail=f"failed to list result versions: {err}")
    return success_response(rows)


@router.get("/tasks/{task_id}/versions/{version_id}", response_model=BaseResponse)
def get_task_result_version(task_id: str, version_id: int):
    row, err = result_version_repo.get_version_detail(task_id=task_id, version_id=version_id)
    if err:
        raise HTTPException(status_code=500, detail=f"failed to fetch version detail: {err}")
    if not row:
        raise HTTPException(status_code=404, detail="version not found")
    return success_response(row)
