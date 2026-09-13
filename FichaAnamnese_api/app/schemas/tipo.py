"""Schemas de `Tipo`."""

from pydantic import BaseModel, ConfigDict


class TipoBase(BaseModel):
    descricao: str


class TipoCreate(TipoBase):
    pass


class TipoRead(TipoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
