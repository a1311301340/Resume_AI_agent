from __future__ import annotations

from dataclasses import dataclass

import pymysql
from pymysql.cursors import DictCursor


@dataclass
class MySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"


class ResumeTextArchiveRepository:
    def __init__(self, config: MySQLConfig) -> None:
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

    def ensure_table(self) -> None:
        if self._table_ready:
            return
        with self._connect() as conn:
            with conn.cursor() as cursor:
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

    def save_or_update_resume_text(
        self,
        *,
        task_id: str,
        filename: str,
        file_path: str,
        resume_text: str,
    ) -> tuple[bool, str | None]:
        try:
            self.ensure_table()
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO resume_text_archive (task_id, filename, file_path, resume_text, text_length)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                          filename = VALUES(filename),
                          file_path = VALUES(file_path),
                          resume_text = VALUES(resume_text),
                          text_length = VALUES(text_length),
                          updated_at = CURRENT_TIMESTAMP
                        """,
                        (task_id, filename, file_path, resume_text, len(resume_text)),
                    )
            return True, None
        except Exception as exc:
            return False, str(exc)

    def get_resume_text(self, task_id: str) -> tuple[str | None, str | None]:
        try:
            self.ensure_table()
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT resume_text
                        FROM resume_text_archive
                        WHERE task_id = %s
                        LIMIT 1
                        """,
                        (task_id,),
                    )
                    row = cursor.fetchone()
            if not row:
                return None, None
            text = row.get("resume_text")
            return (str(text) if text is not None else ""), None
        except Exception as exc:
            return None, str(exc)
