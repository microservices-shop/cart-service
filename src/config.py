from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """Загрузка переменных окружения"""

    model_config = SettingsConfigDict(
        env_file=str(env_path), case_sensitive=True, extra="ignore"
    )

    # Режим отладки приложения (ВАЖНО для безопасности!)
    # Если True - пользователи ВИДЯТ полные traceback ошибок в HTTP-ответах (DevTools, на экране)
    # Если False - пользователи видят только request_id, traceback остается ТОЛЬКО в логах на сервере
    # Также контролирует: формат логов (цветной текст vs JSON)
    # Dev: True, Production: False (ОБЯЗАТЕЛЬНО!)
    DEBUG: bool = False

    LOG_LEVEL: str = "INFO"

    # Вывод SQL-запросов SQLAlchemy в консоль (независим от DEBUG)
    # Если True - все SQL-запросы выводятся в консоль
    DB_ECHO: bool = False

    DB_HOST: str = ""
    DB_PORT: str = "5432"
    DB_USER: str = ""
    DB_PASS: str = ""
    DB_NAME: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
