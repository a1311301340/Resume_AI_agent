class RewriteService:
    def rewrite_project(self, resume_info: dict, jd_info: dict) -> dict:
        projects = resume_info.get("projects", [])
        keywords = jd_info.get("keywords", [])

        rewritten: list[str] = []
        for item in projects[:3]:
            rewritten.append(
                f"围绕岗位关注的 {', '.join(keywords) if keywords else '核心能力'}，"
                f"对原项目经历进行突出式表达：{item}"
            )

        return {"rewritten_projects": rewritten}

