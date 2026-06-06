from datetime import date
from typing import Optional, List

from sqlalchemy import (
    BigInteger, Column, Date, ForeignKey, Integer,
    String, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from pydantic import BaseModel, EmailStr


# ---------------------------------------------------------------------------
# SQLAlchemy – Base e Models (ORM)
# ---------------------------------------------------------------------------

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


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (UniqueConstraint("email", name="usuario_email_unique"),)

    id = Column(BigInteger, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    pessoa_id = Column(BigInteger, ForeignKey("pessoa.id"), nullable=False)

    pessoa: "Pessoa" = relationship("Pessoa", back_populates="usuarios")


class Ficha(Base):
    __tablename__ = "ficha"

    id = Column(BigInteger, primary_key=True)
    servico = Column(BigInteger, nullable=False)
    dt_inclusao = Column(Date, nullable=False)
    titulo = Column(String(255), nullable=False)

    # Relacionamentos reversos
    ficha_perguntas: List["FichaPergunta"] = relationship(
        "FichaPergunta", back_populates="ficha"
    )
    ficha_respostas: List["FichaResposta"] = relationship(
        "FichaResposta", back_populates="ficha"
    )


class FichaPergunta(Base):
    __tablename__ = "ficha_pergunta"

    id = Column(BigInteger, primary_key=True)
    titulo = Column(String(255), nullable=False)
    tipo_id = Column(BigInteger, ForeignKey("tipo.id"), nullable=False)
    ficha_id = Column(BigInteger, ForeignKey("ficha.id"), nullable=False)
    ordem = Column(Integer, nullable=False)

    tipo: "Tipo" = relationship(
        "Tipo", back_populates="ficha_perguntas", foreign_keys=[tipo_id]
    )
    ficha: "Ficha" = relationship("Ficha", back_populates="ficha_perguntas")
    opcoes: List["FichaPerguntaOpcao"] = relationship(
        "FichaPerguntaOpcao", back_populates="ficha_pergunta"
    )


class FichaPerguntaOpcao(Base):
    __tablename__ = "ficha_pergunta_opcao"

    id = Column(BigInteger, primary_key=True)
    titulo = Column(String(255), nullable=False)
    ficha_pergunta_id = Column(
        BigInteger,
        ForeignKey("ficha_pergunta.id",
                   name="ficha_pergunta_opcao_ficha_pergunta_id_foreign"),
        nullable=False,
    )

    ficha_pergunta: "FichaPergunta" = relationship(
        "FichaPergunta", back_populates="opcoes"
    )
    pergunta_respostas: List["PerguntaResposta"] = relationship(
        "PerguntaResposta", back_populates="resposta_opcao"
    )


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

    ficha: "Ficha" = relationship("Ficha", back_populates="ficha_respostas")
    pessoa: "Pessoa" = relationship("Pessoa", back_populates="ficha_respostas")
    status: "Status" = relationship("Status", back_populates="ficha_respostas")
    pergunta_respostas: List["PerguntaResposta"] = relationship(
        "PerguntaResposta", back_populates="ficha_resposta"
    )
    imagens: List["FichaImagens"] = relationship(
        "FichaImagens", back_populates="ficha_resposta"
    )


class PerguntaResposta(Base):
    __tablename__ = "pergunta_resposta"

    id = Column(BigInteger, primary_key=True)
    reposta_texto = Column(String(255), nullable=False)  # mantido como no DDL original
    resposta_opcao_id = Column(
        BigInteger,
        ForeignKey("ficha_pergunta_opcao.id",
                   name="pergunta_resposta_resposta_opcao_id_foreign"),
        nullable=False,
    )
    ficha_resposta_id = Column(
        BigInteger,
        ForeignKey("ficha_resposta.id",
                   name="pergunta_resposta_ficha_resposta_id_foreign"),
        nullable=False,
    )

    resposta_opcao: "FichaPerguntaOpcao" = relationship(
        "FichaPerguntaOpcao", back_populates="pergunta_respostas"
    )
    ficha_resposta: "FichaResposta" = relationship(
        "FichaResposta", back_populates="pergunta_respostas"
    )


class FichaImagens(Base):
    __tablename__ = "ficha_imagens"

    id = Column(BigInteger, primary_key=True)
    arquivo = Column(String(255), nullable=False)
    descricao = Column(String(255), nullable=False)
    ficha_resposta_id = Column(
        BigInteger,
        ForeignKey("ficha_resposta.id",
                   name="ficha_imagens_ficha_resposta_id_foreign"),
        nullable=False,
    )

    ficha_resposta: "FichaResposta" = relationship(
        "FichaResposta", back_populates="imagens"
    )


# ---------------------------------------------------------------------------
# Pydantic – Schemas (validação / serialização)
# ---------------------------------------------------------------------------

# --- Status ---
class StatusBase(BaseModel):
    descricao: str

class StatusCreate(StatusBase):
    pass

class StatusRead(StatusBase):
    id: int
    model_config = {"from_attributes": True}


# --- Tipo ---
class TipoBase(BaseModel):
    descricao: str

class TipoCreate(TipoBase):
    pass

class TipoRead(TipoBase):
    id: int
    model_config = {"from_attributes": True}


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


# --- Ficha ---
class FichaBase(BaseModel):
    servico: int
    dt_inclusao: date
    titulo: str

class FichaCreate(FichaBase):
    pass

class FichaRead(FichaBase):
    id: int
    model_config = {"from_attributes": True}


# --- FichaPergunta ---
class FichaPerguntaBase(BaseModel):
    titulo: str
    tipo_id: int
    ficha_id: int
    ordem: int

class FichaPerguntaCreate(FichaPerguntaBase):
    pass

class FichaPerguntaRead(FichaPerguntaBase):
    id: int
    tipo: TipoRead
    model_config = {"from_attributes": True}


# --- FichaPerguntaOpcao ---
class FichaPerguntaOpcaoBase(BaseModel):
    titulo: str
    ficha_pergunta_id: int

class FichaPerguntaOpcaoCreate(FichaPerguntaOpcaoBase):
    pass

class FichaPerguntaOpcaoRead(FichaPerguntaOpcaoBase):
    id: int
    model_config = {"from_attributes": True}


# --- FichaResposta ---
class FichaRespostaBase(BaseModel):
    ficha_id: int
    pessoa_id: int
    status_id: int

class FichaRespostaCreate(FichaRespostaBase):
    pass

class FichaRespostaRead(FichaRespostaBase):
    id: int
    status: StatusRead
    pessoa: PessoaRead
    model_config = {"from_attributes": True}


# --- PerguntaResposta ---
class PerguntaRespostaBase(BaseModel):
    reposta_texto: str  # mantido como no DDL original
    resposta_opcao_id: int
    ficha_resposta_id: int

class PerguntaRespostaCreate(PerguntaRespostaBase):
    pass

class PerguntaRespostaRead(PerguntaRespostaBase):
    id: int
    resposta_opcao: FichaPerguntaOpcaoRead
    model_config = {"from_attributes": True}


# --- FichaImagens ---
class FichaImagensBase(BaseModel):
    arquivo: str
    descricao: str
    ficha_resposta_id: int

class FichaImagensCreate(FichaImagensBase):
    pass

class FichaImagensRead(FichaImagensBase):
    id: int
    model_config = {"from_attributes": True}