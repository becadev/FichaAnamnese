from fastapi import FastAPI

app = FastAPI()

from app.database import Base, engine
# Todo módulo de modelo precisa ser importado antes do create_all: é o import que
# registra a classe no metadata. app.models traz Status e Tipo, que antes só
# chegavam de carona nos imports cruzados entre os módulos.
from app.models import *
from app.modules.usuario.models import *
from app.modules.fichas.models import *

Base.metadata.create_all(bind=engine)

@app.get("/")
def raiz():
    return {"mensagem": "API rodando!"}