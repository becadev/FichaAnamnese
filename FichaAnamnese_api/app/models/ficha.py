"""Template de ficha: a ficha em si, suas perguntas e as opções de resposta."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.ficha_resposta import FichaResposta, PerguntaResposta
    from app.models.tipo import Tipo


class Ficha(Base):
    __tablename__ = "ficha"

    id = Column(BigInteger, primary_key=True)
    servico = Column(BigInteger, nullable=False)
    dt_inclusao = Column(Date, nullable=False)
    titulo = Column(String(255), nullable=False)

    ficha_perguntas: Mapped[list[FichaPergunta]] = relationship(
        "FichaPergunta", back_populates="ficha"
    )
    ficha_respostas: Mapped[list[FichaResposta]] = relationship(
        "FichaResposta", back_populates="ficha"
    )


class FichaPergunta(Base):
    __tablename__ = "ficha_pergunta"

    id = Column(BigInteger, primary_key=True)
    titulo = Column(String(255), nullable=False)
    tipo_id = Column(BigInteger, ForeignKey("tipo.id"), nullable=False)
    ficha_id = Column(BigInteger, ForeignKey("ficha.id"), nullable=False)
    ordem = Column(Integer, nullable=False)

    tipo: Mapped[Tipo] = relationship(
        "Tipo", back_populates="ficha_perguntas", foreign_keys=[tipo_id]
    )
    ficha: Mapped[Ficha] = relationship("Ficha", back_populates="ficha_perguntas")
    opcoes: Mapped[list[FichaPerguntaOpcao]] = relationship(
        "FichaPerguntaOpcao", back_populates="ficha_pergunta"
    )


class FichaPerguntaOpcao(Base):
    __tablename__ = "ficha_pergunta_opcao"

    id = Column(BigInteger, primary_key=True)
    titulo = Column(String(255), nullable=False)
    ficha_pergunta_id = Column(
        BigInteger,
        ForeignKey(
            "ficha_pergunta.id",
            name="ficha_pergunta_opcao_ficha_pergunta_id_foreign",
        ),
        nullable=False,
    )

    ficha_pergunta: Mapped[FichaPergunta] = relationship(
        "FichaPergunta", back_populates="opcoes"
    )
    pergunta_respostas: Mapped[list[PerguntaResposta]] = relationship(
        "PerguntaResposta", back_populates="resposta_opcao"
    )
