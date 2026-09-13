"""Testes da estrutura de pacotes e dos imports (F0-T2)."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy.orm import configure_mappers

from app.core.database import Base

API_DIR = Path(__file__).resolve().parent.parent
APP_DIR = API_DIR / "app"

TABELAS_ESPERADAS = {
    "ficha",
    "ficha_imagens",
    "ficha_pergunta",
    "ficha_pergunta_opcao",
    "ficha_resposta",
    "pergunta_resposta",
    "pessoa",
    "status",
    "tipo",
    "usuario",
}


def _modulos_do_app() -> list[Path]:
    return sorted(APP_DIR.rglob("*.py"))


def _imports(arquivo: Path) -> list[str]:
    """Nomes de módulo importados por `arquivo` (absolutos e relativos)."""
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"), filename=str(arquivo))
    nomes: list[str] = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes += [alias.name for alias in no.names]
        elif isinstance(no, ast.ImportFrom):
            nomes.append("." * no.level + (no.module or ""))
    return nomes


# --------------------------------------------------------------------------
# Caminho feliz
# --------------------------------------------------------------------------


def test_importa_app_main_sem_banco_configurado() -> None:
    """`import app.main` não pode exigir DATABASE_URL nem conexão."""
    resultado = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        cwd=API_DIR,
        capture_output=True,
        text=True,
        # Ambiente enxuto: sem DATABASE_URL/JWT_SECRET herdados do shell.
        env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(API_DIR)},
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr


def test_todos_os_models_usam_a_mesma_base() -> None:
    import app.models as models

    configure_mappers()  # resolve todo relacionamento; explode se faltar classe

    assert set(Base.metadata.tables) == TABELAS_ESPERADAS
    assert {getattr(models, nome).registry for nome in models.__all__} == {
        Base.registry
    }


def test_pacotes_esperados_existem() -> None:
    for pacote in ("core", "models", "schemas", "routers", "services"):
        assert (APP_DIR / pacote / "__init__.py").is_file(), f"falta app/{pacote}"


# --------------------------------------------------------------------------
# Fronteira entre models (SQLAlchemy) e schemas (Pydantic)
# --------------------------------------------------------------------------


def test_models_nao_declaram_schemas_pydantic() -> None:
    suspeitos = [
        arquivo.relative_to(API_DIR)
        for arquivo in (APP_DIR / "models").rglob("*.py")
        if "pydantic" in arquivo.read_text(encoding="utf-8")
    ]

    assert not suspeitos, f"Pydantic dentro de app/models: {suspeitos}"


def test_schemas_nao_importam_sqlalchemy() -> None:
    suspeitos = [
        arquivo.relative_to(API_DIR)
        for arquivo in (APP_DIR / "schemas").rglob("*.py")
        if any(nome.startswith("sqlalchemy") for nome in _imports(arquivo))
    ]

    assert not suspeitos, f"SQLAlchemy dentro de app/schemas: {suspeitos}"


# --------------------------------------------------------------------------
# Caminho de erro: os imports quebrados não podem voltar
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "quebrado",
    [
        "ast",  # `from ast import List` — era o typing.List
        "FichaAnamnese_api.app.models",  # import pela raiz do repositório
        "FichaAnamnese_api.app.modules.usuario.models",
    ],
)
def test_imports_quebrados_nao_reaparecem(quebrado: str) -> None:
    culpados = [
        arquivo.relative_to(API_DIR)
        for arquivo in _modulos_do_app()
        if quebrado in _imports(arquivo)
    ]

    assert not culpados, f"import `{quebrado}` de volta em: {culpados}"


def test_nenhum_modulo_do_app_importa_fora_do_pacote() -> None:
    """Todo import interno é absoluto a partir de `app.` (nada de `..app`)."""
    culpados: list[str] = []
    for arquivo in _modulos_do_app():
        for nome in _imports(arquivo):
            if nome.startswith(".."):
                culpados.append(f"{arquivo.relative_to(API_DIR)}: {nome}")

    assert not culpados, "imports relativos para fora do módulo:\n" + "\n".join(
        culpados
    )
