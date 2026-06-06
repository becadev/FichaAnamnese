from ast import List
from app.models import Base
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    String,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.models import FichaResposta

class Usuario(Base):
    __tablename__ = "usuario"

    __table_args__ = (
        UniqueConstraint(
            "email",
            name="usuario_email_unique"
        ),
    )

    id = Column(BigInteger, primary_key=True)

    email = Column(
        String(255),
        nullable=False,
        unique=True
    )

    pessoa_id = Column(
        BigInteger,
        ForeignKey("pessoa.id"),
        nullable=False
    )

    pessoa = relationship(
        "Pessoa",
        back_populates="usuarios"
    )

class Pessoa(Base):
    __tablename__ = "pessoa"

    id = Column(BigInteger, primary_key=True)
    nome = Column(String(255), nullable=False)
    sobrenome = Column(BigInteger, nullable=False)  # mantido como no DDL original

    # Relacionamentos reversos
    usuarios: List["Usuario"] = relationship("Usuario", back_populates="pessoa")
    ficha_respostas: List["FichaResposta"] = relationship(
        "FichaResposta", back_populates="pessoa"
    )


# --- Pessoa ---
class PessoaBase(BaseModel):
    nome: str
    sobrenome: int  # mantido como BigInt conforme DDL

class PessoaCreate(PessoaBase):
    pass

class PessoaRead(PessoaBase):
    id: int
    model_config = {"from_attributes": True}


# --- Usuario ---
class UsuarioBase(BaseModel):
    email: EmailStr
    pessoa_id: int

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioRead(UsuarioBase):
    id: int
    pessoa: PessoaRead
    model_config = {"from_attributes": True}
