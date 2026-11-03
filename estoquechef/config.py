"""Configuração lida de variáveis de ambiente (ou do arquivo .env)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./estoquechef.db"
    secret_key: str = "dev-inseguro-troque-em-producao"
    access_token_minutes: int = 30
    refresh_token_days: int = 7
    cors_origins: str = "http://localhost:5173"

    @property
    def origens_cors(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
