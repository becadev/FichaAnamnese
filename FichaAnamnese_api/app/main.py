from fastapi import FastAPI

# Todo módulo de modelo precisa ser importado antes do create_all: é o import que
# registra a classe no metadata. app.models traz Status e Tipo, que antes só
# chegavam de carona nos imports cruzados entre os módulos.
from app import models  # noqa: F401
from app.database import Base, engine
from app.modules.fichas import models as fichas_models  # noqa: F401
from app.modules.usuario import models as usuario_models  # noqa: F401

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def raiz():
    return {"mensagem": "API rodando!"}
