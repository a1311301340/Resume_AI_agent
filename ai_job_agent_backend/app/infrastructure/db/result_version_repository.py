from __future__ import annotations

import json
from dataclasses import dataclass

import pymysql
from pymysql.cursors import DictCursor


@dataclass
class ResultVersionMySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str = "utf8mb4"


class ResultVersionRepository:
    def __init__(self, config: ResultVersionMySQLConfig) -> None:
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
                    CREATE TABLE IF NOT EXISTS task_result_version (
                      id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                      task_row_id BIGINT UNSIGNED NOT NULL,
                      version_no INT UNSIGNED NOT NULL,
                      note VARCHAR(255) NULL,
                      result_json LONGTEXT NOT NULL,
                      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      UNIQUE KEY uk_task_result_version (task_row_id, version_no),
                      KEY idx_task_result_version_task (task_row_id),
                      KEY idx_task_result_version_created (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )
        self._table_ready = True

    def _get_task_row_id(self, cursor, task_id: str) -> int | None:
        cursor.execute(
            "SELECT id FROM job_task WHERE task_id = %s LIMIT 1",
            (task_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return int(row["id"])

    def save_version(
        self,
        *,
        task_id: str,
        result: dict,
        note: str | None = None,
        apply_as_current: bool = True,
    ) -> tuple[dict | None, str | None]:
        try:
            self.ensure_table()
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    task_row_id = self._get_task_row_id(cursor, task_id)
                    if task_row_id is None:
                        return None, "task not found"

                    cursor.execute(
                        """
                        SELECT IFNULL(MAX(version_no), 0) AS max_ver
                        FROM task_result_version
                        WHERE task_row_id = %s
                        """,
                        (task_row_id,),
                    )
                    max_row = cursor.fetchone() or {"max_ver": 0}
                    version_no = int(max_row.get("max_ver") or 0) + 1

                    result_json = json.dumps(result, ensure_ascii=False)
                    cursor.execute(
                        """
                        INSERT INTO task_result_version (task_row_id, version_no, note, result_json)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (task_row_id, version_no, note, result_json),
                    )

                    if apply_as_current:
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

            payload = {
                "task_id": task_id,
                "version_no": version_no,
                "note": note or "",
                "apply_as_current": apply_as_current,
            }
            return payload, None
        except Exception as exc:
            return None, str(exc)

    def list_versions(self, task_id: str, limit: int = 50) -> tuple[list[dict], str | None]:
        try:
            self.ensure_table()
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    task_row_id = self._get_task_row_id(cursor, task_id)
                    if task_row_id is None:
                        return [], None
                    cursor.execute(
                        """
                        SELECT id, version_no, note, created_at
                        FROM task_result_version
                        WHERE task_row_id = %s
                        ORDER BY version_no DESC
                        LIMIT %s
                        """,
                        (task_row_id, limit),
                    )
                    rows = cursor.fetchall() or []
            return rows, None
        except Exception as exc:
            return [], str(exc)

    def get_version_detail(self, task_id: str, version_id: int) -> tuple[dict | None, str | None]:
        try:
            self.ensure_table()
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    task_row_id = self._get_task_row_id(cursor, task_id)
                    if task_row_id is None:
                        return None, None
                    cursor.execute(
                        """
                        SELECT id, version_no, note, result_json, created_at
                        FROM task_result_version
                        WHERE task_row_id = %s AND id = %s
                        LIMIT 1
                        """,
                        (task_row_id, version_id),
                    )
                    row = cursor.fetchone()
            if not row:
                return None, None
            result_json = row.get("result_json")
            result = None
            if isinstance(result_json, str) and result_json.strip():
                try:
                    result = json.loads(result_json)
                except Exception:
                    result = {"raw": result_json}
            payload = {
                "id": row.get("id"),
                "version_no": row.get("version_no"),
                "note": row.get("note") or "",
                "created_at": str(row.get("created_at") or ""),
                "result": result,
            }
            return payload, None
        except Exception as exc:
            return None, str(exc)
