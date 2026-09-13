"""Schemas do template de ficha (ficha, perguntas e opções)."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.schemas.tipo import TipoRead


class FichaBase(BaseModel):
    servico: int
    dt_inclusao: date
    titulo: str


class FichaCreate(FichaBase):
    pass


class FichaRead(FichaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class FichaPerguntaBase(BaseModel):
    titulo: str
    tipo_id: int
    ficha_id: int
    ordem: int


class FichaPerguntaCreate(FichaPerguntaBase):
    pass


class FichaPerguntaRead(FichaPerguntaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoRead


class FichaPerguntaOpcaoBase(BaseModel):
    titulo: str
    ficha_pergunta_id: int


class FichaPerguntaOpcaoCreate(FichaPerguntaOpcaoBase):
    pass


class FichaPerguntaOpcaoRead(FichaPerguntaOpcaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
