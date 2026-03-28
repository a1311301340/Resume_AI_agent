from abc import ABC, abstractmethod

from app.domain.entities.task import Task


class TaskRepository(ABC):
    @abstractmethod
    def create_task(self, filename: str, file_path: str) -> Task:
        raise NotImplementedError

    @abstractmethod
    def get_task(self, task_id: str) -> Task | None:
        raise NotImplementedError

    @abstractmethod
    def update_task_status(self, task_id: str, status: str, progress: int, current_step: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_task_result(self, task_id: str, result: dict) -> None:
        raise NotImplementedError

