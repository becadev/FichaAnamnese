"""Camada de configuração da API (F0-T4).

Todo valor de ambiente entra por aqui — nenhum módulo lê `os.environ` direto.
As chaves vêm do `.env` (ignorado pelo git) ou do ambiente do processo, que tem
precedência sobre o arquivo (é assim que o docker-compose/CI injetam valores).
"""

from __future__ import annotations

from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Esquemas aceitos na DATABASE_URL. `postgresql+psycopg` é o driver v3, o
# recomendado pelo Neon e o que está no requirements.
_ESQUEMAS_VALIDOS = ("postgresql", "postgresql+psycopg", "postgresql+psycopg2")


class Settings(BaseSettings):
    """Configuração da aplicação, validada na primeira leitura."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Banco ----
    database_url: str

    # ---- Autenticação (usado a partir da F1-T1) ----
    jwt_secret: str
    jwt_expire_min: int = 60

    # ---- CORS ----
    # Lida como texto e separada por vírgula de propósito: o pydantic-settings
    # tenta fazer JSON de campos `list[...]` vindos do ambiente e quebraria com
    # `CORS_ORIGINS=http://a,http://b`. A lista pronta sai em `cors_origins_list`.
    cors_origins: str = ""

    # ---- Storage de imagens (S3/R2, usado a partir da F4) ----
    storage_endpoint_url: str | None = None
    storage_bucket: str | None = None
    storage_access_key_id: str | None = None
    storage_secret_access_key: str | None = None
    storage_region: str = "auto"
    storage_public_base_url: str | None = None

    @field_validator("database_url")
    @classmethod
    def _valida_database_url(cls, valor: str) -> str:
        """Recusa cedo uma URL que o engine só rejeitaria na 1ª conexão.

        Senha com caractere especial precisa vir **URL-encoded** (`@` → `%40`,
        `#` → `%23`): cru, o `@` confunde o host e o `#` corta o resto da URL
        como fragmento.
        """
        try:
            url = urlsplit(valor)
            host = url.hostname
        except ValueError as erro:  # porta inválida, colchetes soltos, etc.
            raise ValueError(f"DATABASE_URL malformada: {erro}") from erro

        if url.scheme not in _ESQUEMAS_VALIDOS:
            raise ValueError(
                "DATABASE_URL precisa usar um destes esquemas: "
                + ", ".join(_ESQUEMAS_VALIDOS)
            )
        if not host:
            raise ValueError("DATABASE_URL sem host (senha com `@`/`#` cru?)")
        if not url.path.lstrip("/"):
            raise ValueError("DATABASE_URL sem nome de banco")
        if url.fragment:
            raise ValueError(
                "DATABASE_URL com `#` cru — faça URL-encode da senha (`#` → %23)"
            )
        return valor

    @field_validator("jwt_secret")
    @classmethod
    def _valida_jwt_secret(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("JWT_SECRET não pode ser vazia")
        return valor

    @property
    def cors_origins_list(self) -> list[str]:
        """Origens permitidas, já separadas e sem espaços em volta."""
        return [
            origem.strip() for origem in self.cors_origins.split(",") if origem.strip()
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Instância única de `Settings` (o `.env` é lido uma vez por processo)."""
    return Settings()
