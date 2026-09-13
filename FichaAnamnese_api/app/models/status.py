"""Status do ciclo de vida de uma ficha respondida."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base

# Import só para o type checker: em runtime o SQLAlchemy acha a outra ponta do
# relacionamento pelo nome da classe no registry da Base. Importar de verdade
# fecharia um ciclo com app.models.ficha_resposta, que já aponta para cá.
if TYPE_CHECKING:
    from app.models.ficha_resposta import FichaResposta


class Status(Base):
    __tablename__ = "status"

    id = Column(BigInteger, primary_key=True)
    descricao = Column(String(255), nullable=False)

    ficha_respostas: Mapped[list[FichaResposta]] = relationship(
        "FichaResposta", back_populates="status"
    )
