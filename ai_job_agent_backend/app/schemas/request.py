from typing import Any, Literal

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    task_id: str
    jd_text: str | None = None
    mode: Literal["resume_check", "jd_match", "project_rewrite", "intro_generate"]


class ChatRequest(BaseModel):
    message: str
    task_id: str | None = None
    resume_text: str | None = None
    jd_text: str | None = None
    history: list[dict[str, Any]] = Field(default_factory=list)


class TaskCreateRequest(BaseModel):
    jd_text: str | None = Field(default=None, alias="jdText")
    mode: Literal["resume_parse", "jd_match", "full_process"] = "full_process"
    file_path: str | None = Field(default=None, alias="filePath")

    model_config = {"populate_by_name": True}


class SaveResultVersionRequest(BaseModel):
    result: dict[str, Any]
    note: str | None = None
    apply_as_current: bool = True
