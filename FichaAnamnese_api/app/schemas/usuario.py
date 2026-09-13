"""Schemas de `Usuario`."""

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.pessoa import PessoaRead


class UsuarioBase(BaseModel):
    email: EmailStr
    pessoa_id: int


class UsuarioCreate(UsuarioBase):
    pass


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pessoa: PessoaRead
