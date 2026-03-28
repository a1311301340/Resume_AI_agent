import threading
import uuid

from app.domain.entities.task import Task, now_text
from app.domain.repositories.task_repository import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._lock = threading.RLock()

    def create_task(self, filename: str, file_path: str) -> Task:
        with self._lock:
            task_id = str(uuid.uuid4())
            now = now_text()
            task = Task(
                task_id=task_id,
                filename=filename,
                file_path=file_path,
                status="uploaded",
                created_at=now,
                updated_at=now,
                progress=5,
                current_step="文件已上传，等待处理",
            )
            self._tasks[task_id] = task
            return task

    def get_task(self, task_id: str) -> Task | None:
        with self._lock:
            return self._tasks.get(task_id)

    def update_task_status(self, task_id: str, status: str, progress: int, current_step: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task.status = status
            task.progress = max(0, min(100, progress))
            task.current_step = current_step
            task.updated_at = now_text()

    def save_task_result(self, task_id: str, result: dict) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task.result = result
            task.status = "finished"
            task.progress = 100
            task.current_step = "处理完成"
            task.updated_at = now_text()

