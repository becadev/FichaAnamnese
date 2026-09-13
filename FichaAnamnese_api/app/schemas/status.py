"""Schemas de `Status`."""

from pydantic import BaseModel, ConfigDict


class StatusBase(BaseModel):
    descricao: str


class StatusCreate(StatusBase):
    pass


class StatusRead(StatusBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
