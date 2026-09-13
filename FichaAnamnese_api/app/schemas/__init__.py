"""Schemas Pydantic — separados dos models SQLAlchemy (F0-T2)."""

from app.schemas.ficha import (
    FichaBase,
    FichaCreate,
    FichaPerguntaBase,
    FichaPerguntaCreate,
    FichaPerguntaOpcaoBase,
    FichaPerguntaOpcaoCreate,
    FichaPerguntaOpcaoRead,
    FichaPerguntaRead,
    FichaRead,
)
from app.schemas.ficha_resposta import (
    FichaImagensBase,
    FichaImagensCreate,
    FichaImagensRead,
    FichaRespostaBase,
    FichaRespostaCreate,
    FichaRespostaRead,
    PerguntaRespostaBase,
    PerguntaRespostaCreate,
    PerguntaRespostaRead,
)
from app.schemas.pessoa import PessoaBase, PessoaCreate, PessoaRead
from app.schemas.status import StatusBase, StatusCreate, StatusRead
from app.schemas.tipo import TipoBase, TipoCreate, TipoRead
from app.schemas.usuario import UsuarioBase, UsuarioCreate, UsuarioRead

__all__ = [
    "FichaBase",
    "FichaCreate",
    "FichaImagensBase",
    "FichaImagensCreate",
    "FichaImagensRead",
    "FichaPerguntaBase",
    "FichaPerguntaCreate",
    "FichaPerguntaOpcaoBase",
    "FichaPerguntaOpcaoCreate",
    "FichaPerguntaOpcaoRead",
    "FichaPerguntaRead",
    "FichaRead",
    "FichaRespostaBase",
    "FichaRespostaCreate",
    "FichaRespostaRead",
    "PerguntaRespostaBase",
    "PerguntaRespostaCreate",
    "PerguntaRespostaRead",
    "PessoaBase",
    "PessoaCreate",
    "PessoaRead",
    "StatusBase",
    "StatusCreate",
    "StatusRead",
    "TipoBase",
    "TipoCreate",
    "TipoRead",
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioRead",
]
