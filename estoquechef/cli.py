"""Comando `estoquechef`: run (sobe a API) e seed (cria dados de exemplo)."""
import argparse
from datetime import date, timedelta

from sqlalchemy import select


def _rodar(args):
    import uvicorn

    uvicorn.run("estoquechef.app:app", host=args.host, port=args.port, reload=args.reload)


def _seed(args):
    from .db import Base, SessionLocal, engine
    from .models import Entrada, Ingrediente, Saida, Usuario
    from .security import gerar_hash

    Base.metadata.create_all(engine)
    hoje = date.today()
    d = lambda n: hoje + timedelta(days=n)  # noqa: E731

    with SessionLocal() as s:
        if s.scalar(select(Usuario).where(Usuario.username == args.username)):
            print(f"Usuário '{args.username}' já existe — nada a fazer.")
            return
        u = Usuario(username=args.username, email=f"{args.username}@exemplo.com", senha_hash=gerar_hash(args.password))
        s.add(u)
        s.flush()

        dados = [  # nome, categoria, qtd, unidade, mínimo, validade, fornecedor
            ("Farinha de trigo", "Secos", 3.5, "kg", 5, d(40), "Moinho Bela Vista"),
            ("Manteiga sem sal", "Laticínios", 2, "kg", 3, d(5), "Laticínios Serra Azul"),
            ("Ovos", "Ovos", 1, "dúzia", 2, d(2), "Granja Boa Safra"),
            ("Chocolate meio amargo 70%", "Confeitaria", 8, "kg", 2, d(120), "Cacau do Vale"),
            ("Leite integral", "Laticínios", 4, "litro", 6, d(1), "Laticínios Serra Azul"),
            ("Morango", "Frutas e legumes", 1.2, "kg", 1, d(-1), "Hortifruti Central"),
            ("Caixas para bolo P", "Embalagens", 15, "unidade", 20, None, "Embalatudo"),
        ]
        ings = [
            Ingrediente(usuario_id=u.id, nome=n, categoria=c, quantidade=q, unidade=un, minimo=m, validade=v, fornecedor=f)
            for n, c, q, un, m, v, f in dados
        ]
        s.add_all(ings)
        s.flush()
        farinha, manteiga = ings[0], ings[1]
        s.add_all([
            Entrada(usuario_id=u.id, ingrediente_id=farinha.id, quantidade=3.5, valor=24.9, data_compra=d(-5),
                    data_entrega=d(-3), fornecedor=farinha.fornecedor, recebido=True),
            Entrada(usuario_id=u.id, ingrediente_id=manteiga.id, quantidade=2, valor=38.5, data_compra=d(-2),
                    data_entrega=d(-1), fornecedor=manteiga.fornecedor, recebido=True),
            Entrada(usuario_id=u.id, ingrediente_id=farinha.id, quantidade=10, valor=68.0, data_compra=d(0),
                    data_entrega=None, fornecedor=farinha.fornecedor, recebido=False),
            Saida(usuario_id=u.id, ingrediente_id=ings[2].id, quantidade=1, data=d(-1), motivo="Uso na produção",
                  observacao="Bolos de aniversário"),
        ])
        s.commit()
    print(f"Pronto! Login de exemplo: {args.username} / {args.password}")


def main():
    parser = argparse.ArgumentParser(prog="estoquechef", description="EstoqueChef — API de controle de estoque")
    sub = parser.add_subparsers(dest="comando", required=True)

    run = sub.add_parser("run", help="sobe a API")
    run.add_argument("--host", default="127.0.0.1")
    run.add_argument("--port", type=int, default=8000)
    run.add_argument("--reload", action="store_true", help="recarrega ao salvar (dev)")
    run.set_defaults(func=_rodar)

    seed = sub.add_parser("seed", help="cria usuário e dados de exemplo")
    seed.add_argument("--username", default="demo")
    seed.add_argument("--password", default="demo123")
    seed.set_defaults(func=_seed)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
