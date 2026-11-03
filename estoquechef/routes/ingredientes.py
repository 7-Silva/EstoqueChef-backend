from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_session
from ..deps import usuario_logado
from ..models import Ingrediente, Usuario
from ..schemas import IngredienteCreate, IngredienteOut, IngredienteUpdate
from ..services import buscar_ingrediente

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])


@router.get("/", response_model=list[IngredienteOut])
def listar(usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    return sessao.scalars(
        select(Ingrediente).where(Ingrediente.usuario_id == usuario.id).order_by(Ingrediente.nome)
    ).all()


@router.post("/", response_model=IngredienteOut, status_code=status.HTTP_201_CREATED)
def criar(dados: IngredienteCreate, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    ingrediente = Ingrediente(usuario_id=usuario.id, **dados.model_dump())
    sessao.add(ingrediente)
    sessao.commit()
    return ingrediente


@router.put("/{ingrediente_id}", response_model=IngredienteOut)
def atualizar(
    ingrediente_id: int,
    dados: IngredienteUpdate,
    usuario: Usuario = Depends(usuario_logado),
    sessao: Session = Depends(get_session),
):
    ingrediente = buscar_ingrediente(sessao, usuario, ingrediente_id)
    for campo, valor in dados.model_dump().items():
        setattr(ingrediente, campo, valor)
    sessao.commit()
    return ingrediente


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(ingrediente_id: int, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    """Apaga também o histórico de entradas/saídas do ingrediente (cascade)."""
    sessao.delete(buscar_ingrediente(sessao, usuario, ingrediente_id))
    sessao.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
