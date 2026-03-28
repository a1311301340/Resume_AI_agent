from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.intro_service import IntroService
from app.domain.services.jd_analyze_service import JDAnalyzeService
from app.domain.services.match_service import MatchService
from app.domain.services.resume_extract_service import ResumeExtractService
from app.domain.services.resume_parse_service import ResumeParseService
from app.domain.services.rewrite_service import RewriteService


class ProcessTaskUseCase:
    def __init__(
        self,
        task_repo: TaskRepository,
        resume_parse_service: ResumeParseService,
        resume_extract_service: ResumeExtractService,
        jd_analyze_service: JDAnalyzeService,
        match_service: MatchService,
        rewrite_service: RewriteService,
        intro_service: IntroService,
    ) -> None:
        self.task_repo = task_repo
        self.resume_parse_service = resume_parse_service
        self.resume_extract_service = resume_extract_service
        self.jd_analyze_service = jd_analyze_service
        self.match_service = match_service
        self.rewrite_service = rewrite_service
        self.intro_service = intro_service

    def execute(self, task_id: str, jd_text: str | None, mode: str) -> dict:
        task = self.task_repo.get_task(task_id)
        if not task:
            raise ValueError("任务不存在")

        self.task_repo.update_task_status(task_id, status="processing", progress=35, current_step="正在解析简历")

        resume_text = self.resume_parse_service.parse_resume(task.file_path)
        if not (resume_text or "").strip():
            self.task_repo.update_task_status(task_id, status="failed", progress=100, current_step="简历解析失败")
            raise ValueError("简历解析失败，请使用可解析的 PDF/DOCX，或确认本机已安装 Word/LibreOffice 以支持 DOC")

        resume_info = self.resume_extract_service.extract(resume_text)

        self.task_repo.update_task_status(task_id, status="processing", progress=65, current_step="正在分析 JD")
        jd_info = self.jd_analyze_service.analyze(jd_text or "")

        if mode == "resume_check":
            result = resume_info
        elif mode == "jd_match":
            if not (jd_text or "").strip():
                self.task_repo.update_task_status(task_id, status="failed", progress=100, current_step="缺少岗位 JD")
                raise ValueError("请先填写岗位 JD 再开始匹配")
            match_data = self.match_service.match(resume_info, jd_info)
            rewrite_data = self.rewrite_service.rewrite_project(resume_info, jd_info)
            result = {
                "mode": "jd_match",
                "match": match_data,
                "rewritten_projects": rewrite_data.get("rewritten_projects", []),
                "intro": self.intro_service.generate_intro(resume_info, jd_info),
                "resume_preview": {
                    "skills": resume_info.get("skills", [])[:10],
                    "projects": resume_info.get("projects", [])[:5],
                },
                "jd_preview": {
                    "keywords": jd_info.get("keywords", []),
                    "summary": jd_info.get("summary", ""),
                },
            }
        elif mode == "project_rewrite":
            result = self.rewrite_service.rewrite_project(resume_info, jd_info)
        else:
            result = {"intro": self.intro_service.generate_intro(resume_info, jd_info)}

        self.task_repo.save_task_result(task_id, result)
        return result
