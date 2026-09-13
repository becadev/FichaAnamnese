"""Usuário que acessa a área de gestão."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.pessoa import Pessoa


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (UniqueConstraint("email", name="usuario_email_unique"),)

    id = Column(BigInteger, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    pessoa_id = Column(BigInteger, ForeignKey("pessoa.id"), nullable=False)

    pessoa: Mapped[Pessoa] = relationship("Pessoa", back_populates="usuarios")
