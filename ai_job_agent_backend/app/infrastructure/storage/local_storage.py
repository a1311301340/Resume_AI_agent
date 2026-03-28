from pathlib import Path
from uuid import uuid4


class LocalStorage:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_upload_file(self, filename: str, content: bytes) -> Path:
        safe_name = f"{uuid4().hex[:8]}_{Path(filename).name}"
        save_path = self.base_dir / safe_name
        save_path.write_bytes(content)
        return save_path

