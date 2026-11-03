from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import services
from ..db import get_session
from ..deps import usuario_logado
from ..models import Entrada, Usuario
from ..schemas import EntradaCreate, EntradaOut

router = APIRouter(prefix="/entradas", tags=["entradas"])


def serializar(e: Entrada) -> EntradaOut:
    return EntradaOut(
        id=e.id,
        ingrediente_id=e.ingrediente_id,
        ingrediente_nome=e.ingrediente.nome,
        unidade=e.ingrediente.unidade,
        quantidade=e.quantidade,
        valor=e.valor,
        data_compra=e.data_compra,
        data_entrega=e.data_entrega,
        fornecedor=e.fornecedor,
        recebido=e.recebido,
    )


@router.get("/", response_model=list[EntradaOut])
def listar(usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    entradas = sessao.scalars(
        select(Entrada).where(Entrada.usuario_id == usuario.id).order_by(Entrada.data_compra.desc(), Entrada.id.desc())
    ).all()
    return [serializar(e) for e in entradas]


@router.post("/", response_model=EntradaOut, status_code=status.HTTP_201_CREATED)
def criar(dados: EntradaCreate, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    return serializar(services.registrar_entrada(sessao, usuario, dados))


@router.post("/{entrada_id}/receber", response_model=EntradaOut)
def receber(entrada_id: int, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    return serializar(services.receber_entrada(sessao, usuario, entrada_id))


@router.delete("/{entrada_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(entrada_id: int, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    services.excluir_entrada(sessao, usuario, entrada_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
