"""Schemas da ficha preenchida (respostas e imagens)."""

from pydantic import BaseModel, ConfigDict

from app.schemas.ficha import FichaPerguntaOpcaoRead
from app.schemas.pessoa import PessoaRead
from app.schemas.status import StatusRead


class FichaRespostaBase(BaseModel):
    ficha_id: int
    pessoa_id: int
    status_id: int


class FichaRespostaCreate(FichaRespostaBase):
    pass


class FichaRespostaRead(FichaRespostaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusRead
    pessoa: PessoaRead


class PerguntaRespostaBase(BaseModel):
    # TODO(F0-T7): renomear para `resposta_texto` junto com a coluna.
    reposta_texto: str
    resposta_opcao_id: int
    ficha_resposta_id: int


class PerguntaRespostaCreate(PerguntaRespostaBase):
    pass


class PerguntaRespostaRead(PerguntaRespostaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resposta_opcao: FichaPerguntaOpcaoRead


class FichaImagensBase(BaseModel):
    arquivo: str
    descricao: str
    ficha_resposta_id: int


class FichaImagensCreate(FichaImagensBase):
    pass


class FichaImagensRead(FichaImagensBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
