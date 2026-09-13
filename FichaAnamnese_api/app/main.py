"""Ponto de entrada da API."""

from fastapi import FastAPI

# Importar o pacote registra todos os models no metadata da Base. O schema em si
# passa a ser criado pelo Alembic (F0-T7) — `create_all` sai de cena.
from app import models  # noqa: F401

app = FastAPI(title="Ficha Anamnese API")


@app.get("/")
def raiz() -> dict[str, str]:
    return {"mensagem": "API rodando!"}
