from fastapi import APIRouter, HTTPException

from app.api.deps import process_task_use_case
from app.schemas.request import ProcessRequest
from app.schemas.response import BaseResponse, success_response

router = APIRouter(prefix="/process", tags=["Process"])


@router.post("", response_model=BaseResponse)
def process_task(req: ProcessRequest):
    try:
        result = process_task_use_case.execute(
            task_id=req.task_id,
            jd_text=req.jd_text,
            mode=req.mode,
        )
    except ValueError as exc:
        status_code = 404 if str(exc) == "任务不存在" else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return success_response(result)
