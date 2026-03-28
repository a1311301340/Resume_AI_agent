from fastapi import APIRouter

from app.api.deps import agent_chat_service
from app.schemas.request import ChatRequest
from app.schemas.response import BaseResponse, success_response

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/chat", response_model=BaseResponse)
def chat(req: ChatRequest):
    reply = agent_chat_service.chat(
        message=req.message,
        history=req.history,
        task_id=req.task_id,
        jd_text=req.jd_text,
        resume_text=req.resume_text,
    )
    return success_response({"reply": reply})
