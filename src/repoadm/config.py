from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    database_url: str = Field(default="sqlite:///./repomgr.db", description="Путь до базы данных")

    repository_path: str = Field(default="./repository/", description="Путь до файлов исходных репозиториев")

    source_config_root: str = Field(default="./mirror/", description="Путь, куда будут выкачиваться репозитории")

    repofile_path: str = Field(default="./repofile/", description="Путь, куда будут выкладываться файлы на локальный bundle-file репозитория")

    repository_url: str = Field(default="http://repo.example.com", description="Адрес репозитория")

    job_log_root: str = Field(default="./logs/", description="Директория в которой будут храниться логи")

    app_timezone: str = Field(default="UTC", description="Используемая TZ")

    max_parallel_jobs: int = Field(default=1, description="Количество потоков по обработке задач")

    poll_interval: int = Field(default=3600, description="Интервал между опросами репозиториев на наличие обновлений")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()

settings = get_settings()