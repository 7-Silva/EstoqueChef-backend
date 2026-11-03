import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from estoquechef.app import app
from estoquechef.db import Base, get_session


@pytest.fixture()
def client():
    # SQLite em memória, isolado por teste.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Sessao = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def _sessao():
        with Sessao() as s:
            yield s

    app.dependency_overrides[get_session] = _sessao
    with TestClient(app) as c:  # o lifespan roda create_all no engine real; sem efeito nos testes
        yield c
    app.dependency_overrides.clear()


def criar_usuario(client, username="ana", senha="123456"):
    r = client.post("/user/", json={"username": username, "email": f"{username}@x.com", "password": senha})
    assert r.status_code == 201, r.text
    r = client.post("/token", data={"username": username, "password": senha})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def auth(client):
    return criar_usuario(client)
