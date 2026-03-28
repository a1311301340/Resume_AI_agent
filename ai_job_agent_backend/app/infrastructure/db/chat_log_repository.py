from __future__ import annotations

from dataclasses import dataclass

import pymysql
from pymysql.cursors import DictCursor


@dataclass
class ChatMySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"


class ChatLogRepository:
    def __init__(self, config: ChatMySQLConfig) -> None:
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
                    CREATE TABLE IF NOT EXISTS interview_chat_message (
                      id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                      task_id CHAR(36) NULL,
                      role VARCHAR(20) NOT NULL,
                      content LONGTEXT NOT NULL,
                      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      KEY idx_chat_task_id (task_id),
                      KEY idx_chat_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )
        self._table_ready = True

    def save_message(self, task_id: str | None, role: str, content: str) -> tuple[bool, str | None]:
        try:
            self.ensure_table()
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO interview_chat_message (task_id, role, content)
                        VALUES (%s, %s, %s)
                        """,
                        (task_id, role, content),
                    )
            return True, None
        except Exception as exc:
            return False, str(exc)

    def list_messages(self, task_id: str, limit: int = 200) -> tuple[list[dict], str | None]:
        try:
            self.ensure_table()
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, task_id, role, content, created_at
                        FROM interview_chat_message
                        WHERE task_id = %s
                        ORDER BY id ASC
                        LIMIT %s
                        """,
                        (task_id, limit),
                    )
                    rows = cursor.fetchall() or []
            return rows, None
        except Exception as exc:
            return [], str(exc)
