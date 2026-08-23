from typing import TYPE_CHECKING, List
from sqlalchemy import (
    BigInteger, Column, String,
)
from sqlalchemy.orm import relationship

# A Base é uma só, a de app.database: com duas, Status e Tipo cairiam num
# registry separado e os relacionamentos com FichaResposta/FichaPergunta nunca
# se resolveriam — nem as tabelas entrariam no create_all.
from app.database import Base

# Só para os type checkers. Em runtime o SQLAlchemy resolve o outro lado do
# relacionamento pelo nome da classe no registry, então importar de verdade aqui
# só serviria para fechar um ciclo com app.modules.fichas.models, que por sua vez
# precisa do Tipo e do Status daqui.
if TYPE_CHECKING:
    from app.modules.fichas.models import FichaPergunta, FichaResposta


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

    # `tipo` é tabela de referência: quem aponta é ficha_pergunta.tipo_id -> tipo.id,
    # e essa FK já existe do outro lado. A FK inversa que estava aqui referenciava
    # ficha_pergunta.tipo_id, coluna sem unicidade — o Postgres recusa:
    # "there is no unique constraint matching given keys".
    id = Column(BigInteger, primary_key=True)
    descricao = Column(String(255), nullable=False)

    # Relacionamentos reversos
    ficha_perguntas: List["FichaPergunta"] = relationship(
        "FichaPergunta", back_populates="tipo", foreign_keys="FichaPergunta.tipo_id"
    )
