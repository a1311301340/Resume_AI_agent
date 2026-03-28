from dataclasses import dataclass
from datetime import datetime


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Task:
    task_id: str
    filename: str
    file_path: str
    status: str = "uploaded"
    created_at: str = ""
    updated_at: str = ""
    result: dict | None = None
    progress: int = 0
    current_step: str = "等待任务启动"

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "taskId": self.task_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "filePath": self.file_path,
            "status": self.status,
            "created_at": self.created_at,
            "createdAt": self.created_at,
            "updated_at": self.updated_at,
            "updatedAt": self.updated_at,
            "result": self.result,
            "progress": self.progress,
            "current_step": self.current_step,
            "currentStep": self.current_step,
        }

    def to_task_status(self) -> dict:
        status_map = {
            "uploaded": "pending",
            "processing": "running",
            "finished": "success",
            "failed": "failed",
        }
        return {
            "taskId": self.task_id,
            "status": status_map.get(self.status, "pending"),
            "progress": self.progress,
            "currentStep": self.current_step,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }
