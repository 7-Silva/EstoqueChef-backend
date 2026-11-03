from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import services
from ..db import get_session
from ..deps import usuario_logado
from ..models import Saida, Usuario
from ..schemas import SaidaCreate, SaidaOut

router = APIRouter(prefix="/saidas", tags=["saidas"])


def serializar(s: Saida) -> SaidaOut:
    return SaidaOut(
        id=s.id,
        ingrediente_id=s.ingrediente_id,
        ingrediente_nome=s.ingrediente.nome,
        unidade=s.ingrediente.unidade,
        quantidade=s.quantidade,
        data=s.data,
        motivo=s.motivo,
        observacao=s.observacao,
    )


@router.get("/", response_model=list[SaidaOut])
def listar(usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    saidas = sessao.scalars(
        select(Saida).where(Saida.usuario_id == usuario.id).order_by(Saida.data.desc(), Saida.id.desc())
    ).all()
    return [serializar(s) for s in saidas]


@router.post("/", response_model=SaidaOut, status_code=status.HTTP_201_CREATED)
def criar(dados: SaidaCreate, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    return serializar(services.registrar_saida(sessao, usuario, dados))


@router.delete("/{saida_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(saida_id: int, usuario: Usuario = Depends(usuario_logado), sessao: Session = Depends(get_session)):
    services.excluir_saida(sessao, usuario, saida_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
