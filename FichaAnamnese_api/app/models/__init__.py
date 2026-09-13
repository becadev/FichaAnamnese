"""Models SQLAlchemy.

Importar este pacote registra **todas** as classes no metadata da `Base` — é
disso que o Alembic (F0-T7) precisa para enxergar o schema inteiro.
"""

from app.models.ficha import Ficha, FichaPergunta, FichaPerguntaOpcao
from app.models.ficha_resposta import FichaImagens, FichaResposta, PerguntaResposta
from app.models.pessoa import Pessoa
from app.models.status import Status
from app.models.tipo import Tipo
from app.models.usuario import Usuario

__all__ = [
    "Ficha",
    "FichaImagens",
    "FichaPergunta",
    "FichaPerguntaOpcao",
    "FichaResposta",
    "PerguntaResposta",
    "Pessoa",
    "Status",
    "Tipo",
    "Usuario",
]
