class MatchService:
    def match(self, resume_info: dict, jd_info: dict) -> dict:
        resume_skills = set(resume_info.get("skills", []))
        jd_keywords = set(jd_info.get("keywords", []))

        matched = [item for item in jd_keywords if any(item.lower() in skill.lower() for skill in resume_skills)]
        missing = list(jd_keywords - set(matched))
        score = max(50, min(95, 60 + len(matched) * 8 - len(missing) * 3))

        summary = "匹配分析完成。"
        if not jd_keywords:
            summary = "未识别到 JD 关键词，请补充更完整的岗位描述。"
        elif not resume_skills:
            summary = "未识别到简历技能关键词，请检查简历文件内容是否可解析。"
        elif matched:
            summary = f"识别到 {len(jd_keywords)} 个 JD 关键词，匹配到 {len(matched)} 个。"
        else:
            summary = "已识别 JD 关键词，但当前未命中简历技能，可优化技能描述。"

        recommendations: list[str] = []
        if missing:
            recommendations.append(f"建议补充或强调这些关键词相关经历：{', '.join(missing[:8])}")
        if score < 70:
            recommendations.append("建议优先补充与目标岗位强相关的项目经历与技术栈。")
        if not recommendations:
            recommendations.append("匹配度较好，建议进一步量化项目成果（性能、效率、业务指标）。")

        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "score": score,
            "summary": summary,
            "jd_keywords": sorted(jd_keywords),
            "resume_skill_hits": sorted(resume_skills)[:20],
            "recommendations": recommendations,
        }
