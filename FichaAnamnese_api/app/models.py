from typing import List
from sqlalchemy import (
    BigInteger, Column, ForeignKey, String,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from app.modules.fichas.models import FichaResposta, FichaPergunta

class Base(DeclarativeBase):
    pass

class Status(Base):
    __tablename__ = "status"

    id = Column(BigInteger, primary_key=True)
    descricao = Column(String(255), nullable=False)

    # Relacionamentos reversos
    ficha_respostas: List["FichaResposta"] = relationship(
        "FichaResposta", back_populates="status"
    )


class Tipo(Base):
    __tablename__ = "tipo"

    id = Column(
        BigInteger,
        ForeignKey("ficha_pergunta.tipo_id"),
        primary_key=True,
    )
    descricao = Column(String(255), nullable=False)

    # Relacionamentos reversos
    ficha_perguntas: List["FichaPergunta"] = relationship(
        "FichaPergunta", back_populates="tipo", foreign_keys="FichaPergunta.tipo_id"
    )
