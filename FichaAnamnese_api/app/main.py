from fastapi import FastAPI

app = FastAPI()

from app.database import Base, engine

Base.metadata.create_all(bind=engine)

@app.get("/")
def raiz():
    return {"mensagem": "API rodando!"}