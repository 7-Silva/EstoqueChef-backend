"""Regras de negócio do estoque.

O saldo de um ingrediente é sempre consequência de movimentações:
  + entrada recebida      - saída
Nenhuma rota altera `Ingrediente.quantidade` por conta própria; tudo passa por aqui.
"""
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Entrada, Ingrediente, Saida, Usuario


def _arredondar(valor: float) -> float:
    return round(valor, 3)  # evita 0.30000000000000004 em somas de float


def buscar_ingrediente(sessao: Session, usuario: Usuario, ingrediente_id: int, travar: bool = False) -> Ingrediente:
    """Ingrediente do usuário logado, ou 404 (nunca vaza dados de outro usuário).

    travar=True usa SELECT ... FOR UPDATE (Postgres) para duas requisições simultâneas
    não lerem o mesmo saldo e sobrescreverem uma a outra. No SQLite é ignorado.
    """
    consulta = select(Ingrediente).where(Ingrediente.id == ingrediente_id, Ingrediente.usuario_id == usuario.id)
    if travar:
        consulta = consulta.with_for_update()
    ingrediente = sessao.scalar(consulta)
    if not ingrediente:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ingrediente não encontrado.")
    return ingrediente


def _sem_saldo(ingrediente: Ingrediente) -> HTTPException:
    return HTTPException(
        status.HTTP_409_CONFLICT,
        f"Estoque insuficiente. Disponível: {ingrediente.quantidade:g} {ingrediente.unidade}.",
    )


def registrar_entrada(sessao: Session, usuario: Usuario, dados) -> Entrada:
    ingrediente = buscar_ingrediente(sessao, usuario, dados.ingrediente_id, travar=True)
    recebido = dados.data_entrega is not None
    entrada = Entrada(
        usuario_id=usuario.id,
        ingrediente_id=ingrediente.id,
        quantidade=dados.quantidade,
        valor=dados.valor,
        data_compra=dados.data_compra,
        data_entrega=dados.data_entrega,
        fornecedor=dados.fornecedor.strip() or ingrediente.fornecedor,
        recebido=recebido,
    )
    if recebido:
        ingrediente.quantidade = _arredondar(ingrediente.quantidade + dados.quantidade)
    sessao.add(entrada)
    sessao.commit()
    return entrada


def receber_entrada(sessao: Session, usuario: Usuario, entrada_id: int) -> Entrada:
    entrada = buscar_entrada(sessao, usuario, entrada_id)
    if entrada.recebido:
        raise HTTPException(status.HTTP_409_CONFLICT, "Esta entrada já foi recebida.")
    ingrediente = buscar_ingrediente(sessao, usuario, entrada.ingrediente_id, travar=True)
    entrada.recebido = True
    entrada.data_entrega = date.today()
    ingrediente.quantidade = _arredondar(ingrediente.quantidade + entrada.quantidade)
    sessao.commit()
    return entrada


def excluir_entrada(sessao: Session, usuario: Usuario, entrada_id: int) -> None:
    entrada = buscar_entrada(sessao, usuario, entrada_id)
    if entrada.recebido:
        ingrediente = buscar_ingrediente(sessao, usuario, entrada.ingrediente_id, travar=True)
        if ingrediente.quantidade < entrada.quantidade:
            # Parte do que entrou já foi consumido: desfazer deixaria o saldo negativo.
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Não dá para excluir: parte desta entrada já foi usada em saídas. Ajuste as saídas antes.",
            )
        ingrediente.quantidade = _arredondar(ingrediente.quantidade - entrada.quantidade)
    sessao.delete(entrada)
    sessao.commit()


def registrar_saida(sessao: Session, usuario: Usuario, dados) -> Saida:
    ingrediente = buscar_ingrediente(sessao, usuario, dados.ingrediente_id, travar=True)
    if dados.quantidade > ingrediente.quantidade:
        raise _sem_saldo(ingrediente)
    saida = Saida(
        usuario_id=usuario.id,
        ingrediente_id=ingrediente.id,
        quantidade=dados.quantidade,
        data=dados.data,
        motivo=dados.motivo,
        observacao=dados.observacao.strip(),
    )
    ingrediente.quantidade = _arredondar(ingrediente.quantidade - dados.quantidade)
    sessao.add(saida)
    sessao.commit()
    return saida


def excluir_saida(sessao: Session, usuario: Usuario, saida_id: int) -> None:
    saida = buscar_saida(sessao, usuario, saida_id)
    ingrediente = buscar_ingrediente(sessao, usuario, saida.ingrediente_id, travar=True)
    ingrediente.quantidade = _arredondar(ingrediente.quantidade + saida.quantidade)
    sessao.delete(saida)
    sessao.commit()


def buscar_entrada(sessao: Session, usuario: Usuario, entrada_id: int) -> Entrada:
    entrada = sessao.scalar(select(Entrada).where(Entrada.id == entrada_id, Entrada.usuario_id == usuario.id))
    if not entrada:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entrada não encontrada.")
    return entrada


def buscar_saida(sessao: Session, usuario: Usuario, saida_id: int) -> Saida:
    saida = sessao.scalar(select(Saida).where(Saida.id == saida_id, Saida.usuario_id == usuario.id))
    if not saida:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Saída não encontrada.")
    return saida
