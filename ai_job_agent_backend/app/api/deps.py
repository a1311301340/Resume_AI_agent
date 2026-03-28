from app.application.use_cases.process_task import ProcessTaskUseCase
from app.core.settings import settings
from app.domain.services.agent_chat_service import AgentChatService
from app.domain.services.export_service import ExportService
from app.domain.services.intro_service import IntroService
from app.domain.services.jd_analyze_service import JDAnalyzeService
from app.domain.services.match_service import MatchService
from app.domain.services.resume_extract_service import ResumeExtractService
from app.domain.services.resume_parse_service import ResumeParseService
from app.domain.services.rewrite_service import RewriteService
from app.integrations.llm.bailian_app_client import BailianAppClient
from app.infrastructure.db.chat_log_repository import ChatLogRepository, ChatMySQLConfig
from app.infrastructure.db.history_repository import HistoryMySQLConfig, HistoryRepository
from app.infrastructure.db.result_version_repository import ResultVersionMySQLConfig, ResultVersionRepository
from app.infrastructure.db.resume_text_archive_repository import MySQLConfig, ResumeTextArchiveRepository
from app.infrastructure.repositories.mysql_task_repository import MySQLTaskRepository
from app.infrastructure.storage.local_storage import LocalStorage


task_repo = MySQLTaskRepository(
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME,
    charset=settings.DB_CHARSET,
)
local_storage = LocalStorage(settings.UPLOAD_DIR)

resume_parse_service = ResumeParseService()
resume_extract_service = ResumeExtractService()
jd_analyze_service = JDAnalyzeService()
match_service = MatchService()
rewrite_service = RewriteService()
intro_service = IntroService()
export_service = ExportService(settings.OUTPUT_DIR)
bailian_client = BailianAppClient(
    api_key=settings.BAILIAN_API_KEY,
    app_id=settings.BAILIAN_APP_ID,
    completion_url=settings.bailian_completion_url,
    timeout_sec=settings.BAILIAN_TIMEOUT_SEC,
)
agent_chat_service = AgentChatService(bailian_client=bailian_client)
resume_text_archive_repo = ResumeTextArchiveRepository(
    MySQLConfig(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        charset=settings.DB_CHARSET,
    )
)
chat_log_repo = ChatLogRepository(
    ChatMySQLConfig(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        charset=settings.DB_CHARSET,
    )
)
history_repo = HistoryRepository(
    HistoryMySQLConfig(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        charset=settings.DB_CHARSET,
    )
)
result_version_repo = ResultVersionRepository(
    ResultVersionMySQLConfig(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        charset=settings.DB_CHARSET,
    )
)
agent_chat_service.resume_repo = resume_text_archive_repo
agent_chat_service.chat_repo = chat_log_repo

process_task_use_case = ProcessTaskUseCase(
    task_repo=task_repo,
    resume_parse_service=resume_parse_service,
    resume_extract_service=resume_extract_service,
    jd_analyze_service=jd_analyze_service,
    match_service=match_service,
    rewrite_service=rewrite_service,
    intro_service=intro_service,
)
