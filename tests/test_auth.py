from .conftest import criar_usuario


def test_cadastro_login_e_perfil(client):
    h = criar_usuario(client)
    r = client.get("/user/ana/", headers=h)
    assert r.status_code == 200 and r.json()["username"] == "ana"


def test_cadastro_duplicado_409(client):
    criar_usuario(client)
    r = client.post("/user/", json={"username": "ana", "email": "outro@x.com", "password": "123456"})
    assert r.status_code == 409


def test_login_senha_errada_401(client):
    criar_usuario(client)
    assert client.post("/token", data={"username": "ana", "password": "errada"}).status_code == 401


def test_rotas_exigem_token(client):
    assert client.get("/ingredientes/").status_code == 401


def test_nao_ve_perfil_de_outro_usuario(client):
    h = criar_usuario(client, "ana")
    criar_usuario(client, "bia")
    assert client.get("/user/bia/", headers=h).status_code == 403


def test_refresh_token(client):
    criar_usuario(client)
    tokens = client.post("/token", data={"username": "ana", "password": "123456"}).json()
    r = client.post("/refresh_token", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    # access token não pode ser usado como refresh
    assert client.post("/refresh_token", json={"refresh_token": tokens["access_token"]}).status_code == 401
