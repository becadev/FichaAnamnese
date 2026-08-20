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
`PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD` e monte a `DATABASE_URL` com
os mesmos valores. Se a senha tiver caracteres especiais, faça URL-encode dela:

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

## Testes

```bash
python3 -m venv .venv && .venv/bin/pip install pytest
.venv/bin/pytest FichaAnamnese_api/tests
```
