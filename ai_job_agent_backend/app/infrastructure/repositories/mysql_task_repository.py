from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime

import pymysql
from pymysql.cursors import DictCursor

from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository


class MySQLTaskRepository(TaskRepository):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        charset: str = "utf8mb4",
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self._table_ready = False
        self._lock = threading.RLock()

    def _connect(self):
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            autocommit=True,
            cursorclass=DictCursor,
        )

    def _ensure_tables(self) -> None:
        if self._table_ready:
            return
        with self._lock:
            if self._table_ready:
                return
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS job_task (
                          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                          task_id CHAR(36) NOT NULL,
                          filename VARCHAR(255) NOT NULL,
                          file_path VARCHAR(500) NOT NULL,
                          status VARCHAR(30) NOT NULL DEFAULT 'uploaded',
                          progress TINYINT UNSIGNED NOT NULL DEFAULT 0,
                          current_step VARCHAR(255) NULL,
                          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                          UNIQUE KEY uk_job_task_task_id (task_id),
                          KEY idx_job_task_status (status),
                          KEY idx_job_task_created_at (created_at)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS task_result (
                          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                          task_id BIGINT UNSIGNED NOT NULL,
                          result_json LONGTEXT NOT NULL,
                          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                          UNIQUE KEY uk_task_result_task_id (task_id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                        """
                    )
            self._table_ready = True

    def create_task(self, filename: str, file_path: str) -> Task:
        self._ensure_tables()
        task_id = str(uuid.uuid4())
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO job_task (task_id, filename, file_path, status, progress, current_step)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (task_id, filename, file_path, "uploaded", 5, "文件已上传，等待处理"),
                )
        task = self.get_task(task_id)
        if not task:
            raise RuntimeError("创建任务失败")
        return task

    def get_task(self, task_id: str) -> Task | None:
        self._ensure_tables()
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                      t.task_id,
                      t.filename,
                      t.file_path,
                      t.status,
                      t.progress,
                      t.current_step,
                      t.created_at,
                      t.updated_at,
                      r.result_json
                    FROM job_task t
                    LEFT JOIN task_result r ON t.id = r.task_id
                    WHERE t.task_id = %s
                    LIMIT 1
                    """,
                    (task_id,),
                )
                row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_task(row)

    def update_task_status(self, task_id: str, status: str, progress: int, current_step: str) -> None:
        self._ensure_tables()
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE job_task
                    SET status = %s, progress = %s, current_step = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = %s
                    """,
                    (status, max(0, min(100, progress)), current_step, task_id),
                )

    def save_task_result(self, task_id: str, result: dict) -> None:
        self._ensure_tables()
        result_json = json.dumps(result, ensure_ascii=False)
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id FROM job_task WHERE task_id = %s LIMIT 1
                    """,
                    (task_id,),
                )
                row = cursor.fetchone()
                if not row:
                    raise RuntimeError(f"任务不存在: {task_id}")
                task_row_id = int(row["id"])

                cursor.execute(
                    """
                    INSERT INTO task_result (task_id, result_json)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE
                      result_json = VALUES(result_json),
                      updated_at = CURRENT_TIMESTAMP
                    """,
                    (task_row_id, result_json),
                )
                cursor.execute(
                    """
                    UPDATE job_task
                    SET status = 'finished', progress = 100, current_step = '处理完成', updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = %s
                    """,
                    (task_id,),
                )

    def _row_to_task(self, row: dict) -> Task:
        created_at = self._fmt_dt(row.get("created_at"))
        updated_at = self._fmt_dt(row.get("updated_at"))
        result_json = row.get("result_json")
        result: dict | None = None
        if isinstance(result_json, str) and result_json.strip():
            try:
                parsed = json.loads(result_json)
                if isinstance(parsed, dict):
                    result = parsed
                else:
                    result = {"value": parsed}
            except Exception:
                result = {"raw": result_json}
        return Task(
            task_id=str(row.get("task_id", "")),
            filename=str(row.get("filename", "")),
            file_path=str(row.get("file_path", "")),
            status=str(row.get("status", "uploaded")),
            created_at=created_at,
            updated_at=updated_at,
            result=result,
            progress=int(row.get("progress", 0) or 0),
            current_step=str(row.get("current_step", "等待任务启动")),
        )

    def _fmt_dt(self, value) -> str:
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if value is None:
            return ""
        return str(value)
