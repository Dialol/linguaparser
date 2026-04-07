from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql://linguaparser:linguaparser_password@localhost:5432/linguaparser"

    app_name: str = "LinguaParser"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    translation_cache_size: int = 1000
    
    postgres_db: str = "linguaparser"
    postgres_user: str = "linguaparser"
    postgres_password: str="linguaparser_password"

    keycloak_url: str = "http://localhost:7001"
    keycloak_realm: str = "demo"
    keycloak_client_id: str = "linguaparser-client"
    keycloak_issuer: str | None = None
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
