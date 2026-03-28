class JDAnalyzeService:
    def analyze(self, jd_text: str) -> dict:
        keywords: list[str] = []
        for token in ["Python", "Java", "Vue", "SQL", "AI", "大模型", "Agent", "后端", "前端"]:
            if token.lower() in jd_text.lower():
                keywords.append(token)

        return {
            "jd_text": jd_text,
            "keywords": keywords,
            "summary": f"岗位重点关键词包括：{', '.join(keywords) if keywords else '暂无明确技术关键词'}",
        }

