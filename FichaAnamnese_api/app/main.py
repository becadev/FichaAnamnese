from fastapi import FastAPI

app = FastAPI()

from app.database import Base, engine
from app.modules.usuario.models import *
from app.modules.fichas.models import *

Base.metadata.create_all(bind=engine)

@app.get("/")
def raiz():
    return {"mensagem": "API rodando!"}