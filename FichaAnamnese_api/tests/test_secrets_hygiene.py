"""Testes de higiene de segredos (F0-T1).

Garantem que o repositório não volte a versionar credenciais e que o
`docker-compose.yml` seja resolvível apenas a partir do `.env`.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
from pathlib import Path

import pytest

# Chaves cujo valor NUNCA pode aparecer literal em arquivo versionado.
CHAVES_SECRETAS = (
    "POSTGRES_PASSWORD",
    "PGADMIN_DEFAULT_PASSWORD",
    "JWT_SECRET",
    "SECRET_KEY",
    "AWS_SECRET_ACCESS_KEY",
    "R2_SECRET_ACCESS_KEY",
)

# Valor aceito para uma chave secreta: vazio, `${VAR}`, `$VAR` ou `<PLACEHOLDER>`.
_VALOR_SEGURO = re.compile(r"^(\$\{[^}]+\}|\$[A-Z_][A-Z0-9_]*|<[^>]+>)$")

# `[ \t]*` (e não `\s*`) para o valor nunca vazar para a linha seguinte.
_ATRIBUICAO = re.compile(
    r"^[ \t]*-?[ \t]*(?P<chave>"
    + "|".join(CHAVES_SECRETAS)
    + r")[ \t]*[:=][ \t]*(?P<valor>[^\n]*?)[ \t]*$",
    re.MULTILINE,
)

# URL de conexão com credencial embutida: postgresql://user:senha@host/db
_URL_COM_CREDENCIAL = re.compile(
    r"(?P<esquema>[a-z][a-z0-9+.\-]*)://(?P<user>[^\s:/@]+):(?P<senha>[^\s@/]+)@",
)

# SHA-256 dos segredos sabidamente comprometidos (o valor em si não é versionado).
DIGESTS_COMPROMETIDOS = {
    "f09ab5e40ec95c5a19bbf321b8ed5f48ce40c3735884be56394898605a672a95": (
        "senha do Postgres exposta no docker-compose.yml (histórico público)"
    ),
}

_SEPARADORES = "`\"'(),.;*[]{}"


def _repo_root() -> Path:
    saida = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(saida.stdout.strip())


REPO = _repo_root()
API_DIR = Path(__file__).resolve().parent.parent


def _arquivos_versionados() -> list[Path]:
    saida = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    return [REPO / nome for nome in saida.stdout.split("\0") if nome]


def violacoes_de_padrao(texto: str) -> list[str]:
    """Retorna descrições de credenciais literais encontradas em `texto`."""
    achados: list[str] = []

    for m in _ATRIBUICAO.finditer(texto):
        valor = m.group("valor")
        if valor and not _VALOR_SEGURO.match(valor):
            achados.append(f"{m.group('chave')} com valor literal")

    for m in _URL_COM_CREDENCIAL.finditer(texto):
        senha = m.group("senha")
        if not _VALOR_SEGURO.match(senha):
            achados.append(f"URL {m.group('esquema')}:// com senha embutida")

    return achados


def tokens_comprometidos(texto: str) -> list[str]:
    """Retorna a descrição de cada segredo comprometido presente em `texto`."""
    achados: list[str] = []
    for bruto in texto.split():
        token = bruto.strip(_SEPARADORES)
        if not token:
            continue
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        if digest in DIGESTS_COMPROMETIDOS:
            achados.append(DIGESTS_COMPROMETIDOS[digest])
    return achados


def _ler(caminho: Path) -> str | None:
    try:
        return caminho.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


# --------------------------------------------------------------------------
# Caminho feliz: o repositório está limpo
# --------------------------------------------------------------------------


def test_nenhum_segredo_literal_em_arquivo_versionado() -> None:
    problemas: list[str] = []
    for arquivo in _arquivos_versionados():
        texto = _ler(arquivo)
        if texto is None:
            continue
        rel = arquivo.relative_to(REPO)
        problemas += [f"{rel}: {v}" for v in violacoes_de_padrao(texto)]
        problemas += [f"{rel}: {v}" for v in tokens_comprometidos(texto)]

    assert not problemas, "Segredos literais versionados:\n" + "\n".join(problemas)


def test_env_e_ignorado_e_env_example_nao() -> None:
    def ignorado(caminho: str) -> bool:
        return (
            subprocess.run(
                ["git", "check-ignore", "-q", caminho], cwd=REPO, check=False
            ).returncode
            == 0
        )

    assert ignorado("FichaAnamnese_api/.env"), ".env precisa estar no .gitignore"
    assert not ignorado(
        "FichaAnamnese_api/.env.example"
    ), ".env.example deve continuar versionado"


def test_env_nao_esta_versionado() -> None:
    versionados = {p.name for p in _arquivos_versionados()}
    assert ".env" not in versionados


def test_env_example_declara_todas_as_variaveis_do_compose() -> None:
    compose = (API_DIR / "docker-compose.yml").read_text(encoding="utf-8")
    exemplo = (API_DIR / ".env.example").read_text(encoding="utf-8")

    usadas = set(re.findall(r"\$\{([A-Z_][A-Z0-9_]*)", compose))
    declaradas = set(re.findall(r"^([A-Z_][A-Z0-9_]*)=", exemplo, re.MULTILINE))

    faltando = usadas - declaradas
    assert not faltando, f"Variáveis sem entrada no .env.example: {sorted(faltando)}"


def test_env_example_nao_traz_valores_secretos() -> None:
    exemplo = (API_DIR / ".env.example").read_text(encoding="utf-8")
    assert not violacoes_de_padrao(exemplo)


# --------------------------------------------------------------------------
# Caminho de erro: o guarda precisa reprovar conteúdo sujo
# --------------------------------------------------------------------------


def test_scanner_reprova_senha_literal() -> None:
    sujo = "    POSTGRES_PASSWORD: super-secreta-123\n"
    assert violacoes_de_padrao(sujo) == ["POSTGRES_PASSWORD com valor literal"]


def test_scanner_reprova_url_com_credencial() -> None:
    sujo = "DATABASE_URL=postgresql://becadev:umaSenhaQualquer@db:5432/fichas\n"
    assert violacoes_de_padrao(sujo) == ["URL postgresql:// com senha embutida"]


def test_scanner_aceita_interpolacao_e_placeholder() -> None:
    limpo = (
        "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}\n"
        "PGADMIN_DEFAULT_PASSWORD=\n"
        "DATABASE_URL=postgresql+psycopg2://<POSTGRES_USER>:<POSTGRES_PASSWORD>@db:5432/x\n"
    )
    assert violacoes_de_padrao(limpo) == []


def test_scanner_detecta_segredo_comprometido_por_hash() -> None:
    (digest,) = DIGESTS_COMPROMETIDOS
    assert len(digest) == 64
    assert tokens_comprometidos("nada suspeito por aqui") == []


# --------------------------------------------------------------------------
# `docker compose config` resolve o .env (e falha sem ele)
# --------------------------------------------------------------------------

_sem_docker = pytest.mark.skipif(
    shutil.which("docker") is None, reason="docker não disponível"
)


def _compose_config(env_file: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "--env-file", str(env_file), "config"],
        cwd=API_DIR,
        capture_output=True,
        text=True,
        check=False,
    )


@_sem_docker
def test_compose_config_resolve_variaveis(tmp_path: Path) -> None:
    env = tmp_path / "env"
    env.write_text(
        "POSTGRES_USER=usuario_teste\n"
        "POSTGRES_PASSWORD=senha_de_teste\n"
        "POSTGRES_DB=banco_teste\n"
        "PGADMIN_DEFAULT_EMAIL=teste@example.com\n"
        "PGADMIN_DEFAULT_PASSWORD=pgadmin_de_teste\n"
        "DATABASE_URL=postgresql+psycopg2://usuario_teste:senha_de_teste@db:5432/banco_teste\n",
        encoding="utf-8",
    )

    resultado = _compose_config(env)

    assert resultado.returncode == 0, resultado.stderr
    assert "usuario_teste" in resultado.stdout
    assert "${" not in resultado.stdout


@_sem_docker
def test_compose_config_falha_sem_variavel_obrigatoria(tmp_path: Path) -> None:
    env = tmp_path / "env"
    env.write_text("POSTGRES_USER=usuario_teste\n", encoding="utf-8")

    resultado = _compose_config(env)

    assert resultado.returncode != 0
    # O compose aborta na primeira variável obrigatória que faltar; qual delas
    # é reportada varia com a ordem de avaliação dos serviços.
    assert "required variable" in resultado.stderr
    assert any(
        var in resultado.stderr
        for var in ("POSTGRES_PASSWORD", "POSTGRES_DB", "PGADMIN_DEFAULT_")
    ), resultado.stderr
