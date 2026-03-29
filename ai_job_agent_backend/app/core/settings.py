from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "AI Job Agent"
    APP_ENV: str = "dev"
    API_PREFIX: str = ""

    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"

    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = ".pdf,.doc,.docx"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    MODEL_NAME: str = "gpt-4o-mini"
    DASHSCOPE_API_KEY: str = ""
    BAILIAN_API_KEY: str = ""
    BAILIAN_APP_ID: str = ""
    BAILIAN_BASE_URL: str = "https://dashscope.aliyuncs.com"
    BAILIAN_COMPAT_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    BAILIAN_CHAT_MODEL: str = "qwen3.5-plus"
    BAILIAN_ENABLE_THINKING: bool = True
    BAILIAN_TIMEOUT_SEC: int = 60
    LIBREOFFICE_SOFFICE: str = ""

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "ai_job_agent"
    DB_CHARSET: str = "utf8mb4"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def allowed_extensions(self) -> list[str]:
        return [item.strip().lower() for item in self.ALLOWED_EXTENSIONS.split(",") if item.strip()]

    @property
    def mysql_dsn(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset={self.DB_CHARSET}"
        )

    @property
    def bailian_completion_url(self) -> str:
        base = self.BAILIAN_BASE_URL.rstrip("/")
        return f"{base}/api/v1/apps/{self.BAILIAN_APP_ID}/completion"

    @property
    def dashscope_api_key(self) -> str:
        # Backward compatible: prefer DASHSCOPE_API_KEY, fallback to BAILIAN_API_KEY.
        return (self.DASHSCOPE_API_KEY or self.BAILIAN_API_KEY or "").strip()


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
