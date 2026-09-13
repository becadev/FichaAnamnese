# FichaAnamnese

Aplicação para criar fichas de Anamnese para estética.

- [Frontend](https://github.com/becadev/FichaAnamnese-Frontend)

## Configuração de ambiente

Nenhum segredo é versionado. Toda credencial vive no `.env` (ignorado pelo git);
o `.env.example` documenta as chaves esperadas, sem valores.

```bash
cd FichaAnamnese_api
cp .env.example .env
chmod 600 .env
```

Gere senhas fortes e **URL-safe** (evita quebrar a `DATABASE_URL`, onde `@` e `#`
são delimitadores):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

Preencha `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`,
`PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD`, `JWT_SECRET` (mesmo gerador
de segredo) e monte a `DATABASE_URL` com os mesmos valores. O driver é o
`psycopg` v3 — a URL começa com `postgresql+psycopg://`. Se a senha tiver
caracteres especiais, faça URL-encode dela:

```bash
python3 -c "from urllib.parse import quote; print(quote(input(), safe=''))"
```

Confira que tudo foi resolvido antes de subir:

```bash
docker compose config
```

## Como rodar

```bash
cd FichaAnamnese_api
docker compose up -d --build
docker compose ps   # db, api e pgadmin
```

- API: <http://localhost:8000>
- pgAdmin: <http://localhost:5050>
- Postgres: `localhost:5433`

## Rotação de credenciais

As credenciais anteriores foram expostas em commits públicos e estão
**comprometidas**. Ao trocar `POSTGRES_USER`/`POSTGRES_PASSWORD`, o volume
existente ainda guarda a senha antiga — recrie-o:

```bash
docker compose down -v   # apaga o volume postgres_data
docker compose up -d --build
```

> O histórico do git ainda contém os valores antigos. Reescrever o histórico
> (`git filter-repo`) é opcional; o essencial é que as senhas antigas não sejam
> mais válidas em lugar nenhum.

## Estrutura da API

```
FichaAnamnese_api/
  app/
    core/      config.py (settings do .env), database.py (Base + engine/sessão)
    models/    models SQLAlchemy, um arquivo por agregado
    schemas/   schemas Pydantic (separados dos models)
    routers/   endpoints FastAPI
    services/  regras de negócio
    main.py    cria o app e registra os routers
  tests/
```

A `Base` declarativa é única e vive em `app/core/database.py`; todo import
interno é absoluto a partir de `app.` (`from app.models.status import Status`).
O schema do banco passa a ser criado pelo Alembic (F0-T7) — não há mais
`create_all` no start da aplicação.

## Desenvolvimento e testes

```bash
python3 -m venv .venv
.venv/bin/pip install -r FichaAnamnese_api/requirements.txt \
                      -r FichaAnamnese_api/requirements-dev.txt
```

Rode tudo a partir de `FichaAnamnese_api/` (é onde estão o `pyproject.toml` e as
configurações de `ruff`, `black` e `pytest`):

```bash
cd FichaAnamnese_api
../.venv/bin/ruff check .
../.venv/bin/black --check .
../.venv/bin/pytest -q
```
