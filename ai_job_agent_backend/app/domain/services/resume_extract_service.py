class ResumeExtractService:
    def extract(self, text: str) -> dict:
        return {
            "raw_text": text,
            "education": self._simple_extract(text, ["大学", "硕士", "本科", "研究生"]),
            "skills": self._simple_extract(text, ["Python", "Java", "SQL", "Vue", "Spring Boot", "FastAPI"]),
            "projects": self._simple_extract(text, ["项目", "系统", "平台", "开发", "优化"]),
        }

    def _simple_extract(self, text: str, keywords: list[str]) -> list[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        result: list[str] = []
        for line in lines:
            if any(keyword.lower() in line.lower() for keyword in keywords):
                result.append(line)
        return result[:20]

