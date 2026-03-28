from __future__ import annotations

from dataclasses import dataclass

import pymysql
from pymysql.cursors import DictCursor


@dataclass
class HistoryMySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"


class HistoryRepository:
    def __init__(self, config: HistoryMySQLConfig) -> None:
        self.config = config
        self._table_ready = False

    def _connect(self):
        return pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
            charset=self.config.charset,
            autocommit=True,
            cursorclass=DictCursor,
        )

    def ensure_tables(self) -> None:
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
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS resume_text_archive (
                      id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                      task_id CHAR(36) NOT NULL,
                      filename VARCHAR(255) NOT NULL,
                      file_path VARCHAR(500) NOT NULL,
                      resume_text LONGTEXT NULL,
                      text_length INT UNSIGNED NOT NULL DEFAULT 0,
                      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                      UNIQUE KEY uk_resume_text_task_id (task_id),
                      KEY idx_resume_text_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )
        self._table_ready = True

    def list_tasks(self, limit: int = 30) -> tuple[list[dict], str | None]:
        try:
            self.ensure_tables()
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
                          IFNULL(rta.text_length, 0) AS resume_text_length,
                          IFNULL(LEFT(rta.resume_text, 300), '') AS resume_text_preview
                        FROM job_task t
                        LEFT JOIN resume_text_archive rta ON t.task_id = rta.task_id
                        ORDER BY t.id DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    rows = cursor.fetchall() or []
            return rows, None
        except Exception as exc:
            return [], str(exc)

    def get_task_detail(self, task_id: str) -> tuple[dict | None, str | None]:
        try:
            self.ensure_tables()
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
                          IFNULL(rta.resume_text, '') AS resume_text,
                          IFNULL(rta.text_length, 0) AS resume_text_length,
                          tr.result_json
                        FROM job_task t
                        LEFT JOIN resume_text_archive rta ON t.task_id = rta.task_id
                        LEFT JOIN task_result tr ON tr.task_id = t.id
                        WHERE t.task_id = %s
                        LIMIT 1
                        """,
                        (task_id,),
                    )
                    row = cursor.fetchone()
            return row, None
        except Exception as exc:
            return None, str(exc)
