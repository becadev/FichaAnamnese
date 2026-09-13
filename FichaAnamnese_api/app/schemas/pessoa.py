"""Schemas de `Pessoa`."""

from pydantic import BaseModel, ConfigDict


class PessoaBase(BaseModel):
    nome: str
    # TODO(F0-T7): vira `str` junto com a coluna correspondente.
    sobrenome: int


class PessoaCreate(PessoaBase):
    pass


class PessoaRead(PessoaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
