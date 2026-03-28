from fastapi import APIRouter, HTTPException

from app.api.deps import task_repo
from app.schemas.response import BaseResponse, success_response

router = APIRouter(prefix="/result", tags=["Result"])


@router.get("/{task_id}", response_model=BaseResponse)
def get_result(task_id: str):
    task = task_repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(task.to_dict())

