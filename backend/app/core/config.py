"""Configurações da aplicação lidas de variáveis de ambiente.

Os valores podem vir do ambiente (ex.: Docker Compose / CI) ou de um
arquivo ``.env`` em ``backend/`` (veja ``backend/.env.example``).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variáveis de ambiente usadas pelo backend."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://c216:c216@localhost:5432/c216"
    # Origens liberadas no CORS, separadas por vírgula. Nunca usamos "*".
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_lista(self) -> list[str]:
        """``CORS_ORIGINS`` como lista, ignorando espaços e itens vazios."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Retorna as configurações (lidas uma única vez)."""
    return Settings()
