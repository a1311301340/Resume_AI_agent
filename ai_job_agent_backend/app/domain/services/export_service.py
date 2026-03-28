from pathlib import Path


class ExportService:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_txt(self, task_id: str, content: str) -> str:
        file_path = self.output_dir / f"{task_id}.txt"
        file_path.write_text(content, encoding="utf-8")
        return str(file_path)

