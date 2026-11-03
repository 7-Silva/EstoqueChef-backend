from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(100))
    avatar: Mapped[str | None] = mapped_column(String(255), default=None)
    bio: Mapped[str | None] = mapped_column(String(255), default=None)


class Ingrediente(Base):
    """Estoque atual. `quantidade` só muda por entrada recebida ou saída."""

    __tablename__ = "ingredientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    nome: Mapped[str] = mapped_column(String(120))
    categoria: Mapped[str] = mapped_column(String(50))
    quantidade: Mapped[float] = mapped_column(Float, default=0)
    unidade: Mapped[str] = mapped_column(String(20))
    minimo: Mapped[float] = mapped_column(Float, default=0)
    validade: Mapped[date | None] = mapped_column(Date, default=None)
    fornecedor: Mapped[str] = mapped_column(String(120), default="")

    entradas: Mapped[list["Entrada"]] = relationship(cascade="all, delete-orphan")
    saidas: Mapped[list["Saida"]] = relationship(cascade="all, delete-orphan")


class Entrada(Base):
    """Compra. Pendente (recebido=False) não altera o estoque."""

    __tablename__ = "entradas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingredientes.id"), index=True)
    quantidade: Mapped[float] = mapped_column(Float)
    valor: Mapped[float] = mapped_column(Float)
    data_compra: Mapped[date] = mapped_column(Date)
    data_entrega: Mapped[date | None] = mapped_column(Date, default=None)
    fornecedor: Mapped[str] = mapped_column(String(120), default="")
    recebido: Mapped[bool] = mapped_column(Boolean, default=False)

    ingrediente: Mapped[Ingrediente] = relationship(back_populates="entradas")


class Saida(Base):
    __tablename__ = "saidas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingredientes.id"), index=True)
    quantidade: Mapped[float] = mapped_column(Float)
    data: Mapped[date] = mapped_column(Date)
    motivo: Mapped[str] = mapped_column(String(50))
    observacao: Mapped[str] = mapped_column(String(255), default="")

    ingrediente: Mapped[Ingrediente] = relationship(back_populates="saidas")
