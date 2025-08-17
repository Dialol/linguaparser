from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql://linguaparser:linguaparser_password@localhost:5432/linguaparser"

    app_name: str = "LinguaParser"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    translation_cache_size: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
