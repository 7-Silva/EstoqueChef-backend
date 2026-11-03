from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)  # 72 = limite do bcrypt


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    avatar: str | None = None
    bio: str | None = None


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


# ----------------------------- Ingredientes -----------------------------

class IngredienteBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    categoria: str = Field(min_length=1, max_length=50)
    unidade: str = Field(min_length=1, max_length=20)
    minimo: float = Field(ge=0)
    validade: date | None = None
    fornecedor: str = Field(default="", max_length=120)


class IngredienteCreate(IngredienteBase):
    # Saldo inicial, informado só na criação. Depois disso, só entradas/saídas mexem nele.
    quantidade: float = Field(default=0, ge=0)


class IngredienteUpdate(IngredienteBase):
    """Sem `quantidade` de propósito: o saldo não é editável diretamente."""


class IngredienteOut(IngredienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    quantidade: float


# ------------------------------- Entradas -------------------------------

class EntradaCreate(BaseModel):
    ingrediente_id: int
    quantidade: float = Field(gt=0)
    valor: float = Field(ge=0)
    data_compra: date
    data_entrega: date | None = None  # None = pedido pendente (ainda não chegou)
    fornecedor: str = Field(default="", max_length=120)


class EntradaOut(BaseModel):
    id: int
    ingrediente_id: int
    ingrediente_nome: str
    unidade: str
    quantidade: float
    valor: float
    data_compra: date
    data_entrega: date | None
    fornecedor: str
    recebido: bool


# -------------------------------- Saídas --------------------------------

class SaidaCreate(BaseModel):
    ingrediente_id: int
    quantidade: float = Field(gt=0)
    data: date
    motivo: str = Field(min_length=1, max_length=50)
    observacao: str = Field(default="", max_length=255)


class SaidaOut(BaseModel):
    id: int
    ingrediente_id: int
    ingrediente_nome: str
    unidade: str
    quantidade: float
    data: date
    motivo: str
    observacao: str
