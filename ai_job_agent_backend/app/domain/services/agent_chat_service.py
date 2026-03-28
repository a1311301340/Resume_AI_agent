from __future__ import annotations

from typing import Any

from app.infrastructure.db.chat_log_repository import ChatLogRepository
from app.infrastructure.db.resume_text_archive_repository import ResumeTextArchiveRepository
from app.integrations.llm.bailian_app_client import BailianAppClient


class AgentChatService:
    def __init__(
        self,
        bailian_client: BailianAppClient | None = None,
        resume_repo: ResumeTextArchiveRepository | None = None,
        chat_repo: ChatLogRepository | None = None,
    ) -> None:
        self.bailian_client = bailian_client
        self.resume_repo = resume_repo
        self.chat_repo = chat_repo

    def chat(
        self,
        message: str,
        history: list[dict[str, Any]] | None = None,
        task_id: str | None = None,
        jd_text: str | None = None,
        resume_text: str | None = None,
    ) -> str:
        if not resume_text and task_id and self.resume_repo:
            text, _ = self.resume_repo.get_resume_text(task_id)
            resume_text = text or ""

        prompt = self._build_business_prompt(
            message=message,
            resume_text=resume_text or "",
            jd_text=jd_text or "",
        )

        if self.bailian_client and self.bailian_client.enabled:
            try:
                reply = self.bailian_client.complete(prompt=prompt, history=history)
                self._save_chat(task_id=task_id, user_message=message, assistant_message=reply)
                return reply
            except Exception as exc:
                reply = f"模型调用失败：{exc}"
                self._save_chat(task_id=task_id, user_message=message, assistant_message=reply)
                return reply

        reply = (
            f"你刚刚输入的是：{message}\n"
            "当前系统已接收到简历信息与 JD 信息，但尚未配置百炼应用参数。"
        )
        self._save_chat(task_id=task_id, user_message=message, assistant_message=reply)
        return reply

    def _build_business_prompt(self, message: str, resume_text: str, jd_text: str) -> str:
        segments: list[str] = [
            "你是一位专业的面试官和简历顾问，请基于候选人简历进行模拟面试回答。",
        ]
        if jd_text.strip():
            segments.append(f"目标岗位JD：\n{jd_text.strip()}")
        if resume_text.strip():
            clipped = resume_text.strip()
            if len(clipped) > 5000:
                clipped = clipped[:5000] + "\n[简历内容过长，已截断]"
            segments.append(f"候选人简历：\n{clipped}")
        segments.append(f"用户当前问题：{message}")
        segments.append("请给出清晰、可执行、面试场景友好的回答。")
        return "\n\n".join(segments)

    def _save_chat(self, task_id: str | None, user_message: str, assistant_message: str) -> None:
        if not self.chat_repo:
            return
        self.chat_repo.save_message(task_id=task_id, role="user", content=user_message)
        self.chat_repo.save_message(task_id=task_id, role="assistant", content=assistant_message)
