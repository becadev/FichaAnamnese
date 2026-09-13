"""Pessoa: identidade comum a usuários e a quem responde uma ficha."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.ficha_resposta import FichaResposta
    from app.models.usuario import Usuario


class Pessoa(Base):
    __tablename__ = "pessoa"

    id = Column(BigInteger, primary_key=True)
    nome = Column(String(255), nullable=False)
    # TODO(F0-T7): virar String — está BigInteger só porque o DDL original está.
    sobrenome = Column(BigInteger, nullable=False)

    usuarios: Mapped[list[Usuario]] = relationship("Usuario", back_populates="pessoa")
    ficha_respostas: Mapped[list[FichaResposta]] = relationship(
        "FichaResposta", back_populates="pessoa"
    )
