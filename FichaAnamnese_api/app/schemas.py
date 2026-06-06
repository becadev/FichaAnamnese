from pydantic import BaseModel

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
