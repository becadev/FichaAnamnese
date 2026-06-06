from datetime import date
from pydantic import BaseModel
from FichaAnamnese_api.app.models import StatusRead, TipoRead
from FichaAnamnese_api.app.modules.usuario.models import PessoaRead


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