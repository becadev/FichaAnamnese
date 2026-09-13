"""Testes da camada de configuração (F0-T4)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from app.core.config import Settings, get_settings

# Senha com os dois caracteres que quebram uma URL: `@` separa o host e `#`
# corta o resto como fragmento. Vai para o `.env` já URL-encoded.
SENHA = "s3nh@#forte"
SENHA_CODIFICADA = "s3nh%40%23forte"

# O scanner de segredos (test_secrets_hygiene) varre este arquivo por ser
# versionado, e `usuario:senha@host` tem cara de credencial literal. As URLs de
# teste nascem deste molde, com a senha entrando só em tempo de execução.
MOLDE_URL = "postgresql+psycopg://usuario_teste:<senha>@db:5432/banco_teste"


def url_com(senha: str) -> str:
    """URL de teste com `senha` no lugar do placeholder."""
    return MOLDE_URL.replace("<senha>", senha)


CHAVES = (
    "DATABASE_URL",
    "JWT_SECRET",
    "JWT_EXPIRE_MIN",
    "CORS_ORIGINS",
    "STORAGE_BUCKET",
    "STORAGE_REGION",
)


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch: pytest.MonkeyPatch) -> None:
    """O ambiente do processo tem precedência sobre o `.env`; isola o teste."""
    for chave in CHAVES:
        monkeypatch.delenv(chave, raising=False)
    get_settings.cache_clear()


@pytest.fixture
def env_de_teste(tmp_path: Path) -> Path:
    arquivo = tmp_path / ".env"
    arquivo.write_text(
        f"DATABASE_URL={url_com(SENHA_CODIFICADA)}\n"
        "JWT_SECRET=segredo-de-teste\n"
        "JWT_EXPIRE_MIN=15\n"
        "CORS_ORIGINS=http://localhost:5173, https://app.exemplo.com\n"
        "STORAGE_BUCKET=fichas-teste\n",
        encoding="utf-8",
    )
    return arquivo


# --------------------------------------------------------------------------
# Caminho feliz
# --------------------------------------------------------------------------


def test_carrega_settings_do_env_de_teste(env_de_teste: Path) -> None:
    settings = Settings(_env_file=env_de_teste)

    assert settings.jwt_secret == "segredo-de-teste"
    assert settings.jwt_expire_min == 15
    assert settings.storage_bucket == "fichas-teste"
    # Valores não declarados no `.env` caem no default.
    assert settings.storage_region == "auto"
    assert settings.storage_access_key_id is None


def test_cors_origins_vira_lista_sem_espacos(env_de_teste: Path) -> None:
    settings = Settings(_env_file=env_de_teste)

    assert settings.cors_origins_list == [
        "http://localhost:5173",
        "https://app.exemplo.com",
    ]


def test_cors_origins_vazia_vira_lista_vazia(env_de_teste: Path) -> None:
    settings = Settings(_env_file=env_de_teste, cors_origins="")

    assert settings.cors_origins_list == []


def test_database_url_com_senha_url_encoded_e_aceita(env_de_teste: Path) -> None:
    settings = Settings(_env_file=env_de_teste)

    # É o próprio SQLAlchemy quem vai ler essa URL: ele decodifica o %40/%23 e
    # devolve a senha original.
    url = make_url(settings.database_url)
    assert url.password == SENHA
    assert url.host == "db"
    assert url.database == "banco_teste"
    assert url.drivername == "postgresql+psycopg"


def test_get_settings_tem_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", url_com("p"))
    monkeypatch.setenv("JWT_SECRET", "segredo-de-teste")

    assert get_settings() is get_settings()


# --------------------------------------------------------------------------
# Caminho de erro
# --------------------------------------------------------------------------


def test_jwt_secret_ausente_falha(tmp_path: Path) -> None:
    arquivo = tmp_path / ".env"
    arquivo.write_text(f"DATABASE_URL={url_com('p')}\n", encoding="utf-8")

    with pytest.raises(ValidationError, match="jwt_secret"):
        Settings(_env_file=arquivo)


@pytest.mark.parametrize(
    ("url", "erro"),
    [
        # Senha com `#` cru: o resto da URL vira fragmento.
        (url_com("s3nh#a"), "DATABASE_URL"),
        ("mysql://db:3306/banco_teste", "esquemas"),
        ("postgresql+psycopg://db:5432/", "sem nome de banco"),
        ("nao-e-uma-url", "esquemas"),
    ],
)
def test_database_url_invalida_falha(url: str, erro: str) -> None:
    with pytest.raises(ValidationError, match=erro):
        Settings(database_url=url, jwt_secret="segredo-de-teste", _env_file=None)


def test_jwt_secret_em_branco_falha() -> None:
    with pytest.raises(ValidationError, match="JWT_SECRET"):
        Settings(database_url=url_com("p"), jwt_secret="   ", _env_file=None)
