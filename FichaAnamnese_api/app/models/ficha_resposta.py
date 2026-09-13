"""Ficha preenchida: respostas de uma pessoa e as imagens anexadas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.ficha import Ficha, FichaPerguntaOpcao
    from app.models.pessoa import Pessoa
    from app.models.status import Status


class FichaResposta(Base):
    __tablename__ = "ficha_resposta"

    id = Column(BigInteger, primary_key=True)
    ficha_id = Column(
        BigInteger,
        ForeignKey("ficha.id", name="ficha_resposta_ficha_id_foreign"),
        nullable=False,
    )
    pessoa_id = Column(
        BigInteger,
        ForeignKey("pessoa.id", name="ficha_resposta_pessoa_id_foreign"),
        nullable=False,
    )
    status_id = Column(
        BigInteger,
        ForeignKey("status.id", name="ficha_resposta_status_id_foreign"),
        nullable=False,
    )

    ficha: Mapped[Ficha] = relationship("Ficha", back_populates="ficha_respostas")
    pessoa: Mapped[Pessoa] = relationship("Pessoa", back_populates="ficha_respostas")
    status: Mapped[Status] = relationship("Status", back_populates="ficha_respostas")
    pergunta_respostas: Mapped[list[PerguntaResposta]] = relationship(
        "PerguntaResposta", back_populates="ficha_resposta"
    )
    imagens: Mapped[list[FichaImagens]] = relationship(
        "FichaImagens", back_populates="ficha_resposta"
    )


class PerguntaResposta(Base):
    __tablename__ = "pergunta_resposta"

    id = Column(BigInteger, primary_key=True)
    # TODO(F0-T7): renomear para `resposta_texto` e permitir nulo (CHECK entre
    # texto e opção). O nome está errado desde o DDL original.
    reposta_texto = Column(String(255), nullable=False)
    resposta_opcao_id = Column(
        BigInteger,
        ForeignKey(
            "ficha_pergunta_opcao.id",
            name="pergunta_resposta_resposta_opcao_id_foreign",
        ),
        nullable=False,
    )
    ficha_resposta_id = Column(
        BigInteger,
        ForeignKey(
            "ficha_resposta.id",
            name="pergunta_resposta_ficha_resposta_id_foreign",
        ),
        nullable=False,
    )

    resposta_opcao: Mapped[FichaPerguntaOpcao] = relationship(
        "FichaPerguntaOpcao", back_populates="pergunta_respostas"
    )
    ficha_resposta: Mapped[FichaResposta] = relationship(
        "FichaResposta", back_populates="pergunta_respostas"
    )


class FichaImagens(Base):
    __tablename__ = "ficha_imagens"

    id = Column(BigInteger, primary_key=True)
    arquivo = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=False)
    ficha_resposta_id = Column(
        BigInteger,
        ForeignKey("ficha_resposta.id", name="ficha_imagens_ficha_resposta_id_foreign"),
        nullable=False,
    )

    ficha_resposta: Mapped[FichaResposta] = relationship(
        "FichaResposta", back_populates="imagens"
    )
