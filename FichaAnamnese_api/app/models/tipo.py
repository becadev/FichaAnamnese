"""Tipo de pergunta (texto, radio, select...) — tabela de domínio."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.ficha import FichaPergunta


class Tipo(Base):
    __tablename__ = "tipo"

    # Quem aponta é `ficha_pergunta.tipo_id -> tipo.id`; a FK vive do outro lado.
    # A FK inversa que existia aqui referenciava `ficha_pergunta.tipo_id`, coluna
    # sem unicidade — o Postgres recusa: "there is no unique constraint matching
    # given keys".
    id = Column(BigInteger, primary_key=True)
    descricao = Column(String(255), nullable=False)

    ficha_perguntas: Mapped[list[FichaPergunta]] = relationship(
        "FichaPergunta", back_populates="tipo", foreign_keys="FichaPergunta.tipo_id"
    )
