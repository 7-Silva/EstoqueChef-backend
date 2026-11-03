from .conftest import criar_usuario

HOJE = "2026-11-02"


def novo_ingrediente(client, h, **extra):
    corpo = {"nome": "Farinha", "categoria": "Secos", "unidade": "kg", "minimo": 5, "quantidade": 3, **extra}
    r = client.post("/ingredientes/", json=corpo, headers=h)
    assert r.status_code == 201, r.text
    return r.json()


def saldo(client, h, ing_id):
    return next(i["quantidade"] for i in client.get("/ingredientes/", headers=h).json() if i["id"] == ing_id)


def entrada(client, h, ing_id, qtd=10, entrega=HOJE):
    return client.post(
        "/entradas/",
        json={"ingrediente_id": ing_id, "quantidade": qtd, "valor": 50, "data_compra": HOJE, "data_entrega": entrega},
        headers=h,
    )


def saida(client, h, ing_id, qtd):
    return client.post(
        "/saidas/", json={"ingrediente_id": ing_id, "quantidade": qtd, "data": HOJE, "motivo": "Uso na produção"}, headers=h
    )


def test_update_nao_altera_saldo(client, auth):
    ing = novo_ingrediente(client, auth)
    corpo = {"nome": "Farinha 00", "categoria": "Secos", "unidade": "kg", "minimo": 2, "quantidade": 999}
    r = client.put(f"/ingredientes/{ing['id']}", json=corpo, headers=auth)
    assert r.status_code == 200 and r.json()["nome"] == "Farinha 00"
    assert saldo(client, auth, ing["id"]) == 3  # "quantidade" enviada foi ignorada


def test_entrada_recebida_soma_ao_estoque(client, auth):
    ing = novo_ingrediente(client, auth)
    assert entrada(client, auth, ing["id"], 10).json()["recebido"] is True
    assert saldo(client, auth, ing["id"]) == 13


def test_entrada_pendente_nao_soma_ate_receber(client, auth):
    ing = novo_ingrediente(client, auth)
    e = entrada(client, auth, ing["id"], 10, entrega=None).json()
    assert e["recebido"] is False and saldo(client, auth, ing["id"]) == 3
    assert client.post(f"/entradas/{e['id']}/receber", headers=auth).json()["recebido"] is True
    assert saldo(client, auth, ing["id"]) == 13
    assert client.post(f"/entradas/{e['id']}/receber", headers=auth).status_code == 409  # não soma duas vezes


def test_saida_valida_saldo(client, auth):
    ing = novo_ingrediente(client, auth)
    r = saida(client, auth, ing["id"], 5)
    assert r.status_code == 409 and "Disponível" in r.json()["detail"]
    assert saida(client, auth, ing["id"], 2).status_code == 201
    assert saldo(client, auth, ing["id"]) == 1


def test_excluir_saida_devolve_ao_estoque(client, auth):
    ing = novo_ingrediente(client, auth)
    s = saida(client, auth, ing["id"], 2).json()
    assert client.delete(f"/saidas/{s['id']}", headers=auth).status_code == 204
    assert saldo(client, auth, ing["id"]) == 3


def test_excluir_entrada_recebida_desfaz_efeito(client, auth):
    ing = novo_ingrediente(client, auth)
    e = entrada(client, auth, ing["id"], 10).json()
    assert client.delete(f"/entradas/{e['id']}", headers=auth).status_code == 204
    assert saldo(client, auth, ing["id"]) == 3


def test_nao_exclui_entrada_ja_consumida(client, auth):
    ing = novo_ingrediente(client, auth, quantidade=0)
    e = entrada(client, auth, ing["id"], 10).json()
    saida(client, auth, ing["id"], 8)
    r = client.delete(f"/entradas/{e['id']}", headers=auth)
    assert r.status_code == 409
    assert saldo(client, auth, ing["id"]) == 2  # nada mudou


def test_soma_de_floats_nao_acumula_erro(client, auth):
    ing = novo_ingrediente(client, auth, quantidade=0)
    for _ in range(3):
        entrada(client, auth, ing["id"], 0.1)
    assert saldo(client, auth, ing["id"]) == 0.3


def test_excluir_ingrediente_apaga_historico(client, auth):
    ing = novo_ingrediente(client, auth)
    entrada(client, auth, ing["id"])
    saida(client, auth, ing["id"], 1)
    assert client.delete(f"/ingredientes/{ing['id']}", headers=auth).status_code == 204
    assert client.get("/entradas/", headers=auth).json() == []
    assert client.get("/saidas/", headers=auth).json() == []


def test_isolamento_entre_usuarios(client, auth):
    ing = novo_ingrediente(client, auth)
    outro = criar_usuario(client, "bia")
    assert client.get("/ingredientes/", headers=outro).json() == []
    assert entrada(client, outro, ing["id"]).status_code == 404
    assert saida(client, outro, ing["id"], 1).status_code == 404
    assert client.delete(f"/ingredientes/{ing['id']}", headers=outro).status_code == 404


def test_validacoes(client, auth):
    ing = novo_ingrediente(client, auth)
    assert saida(client, auth, ing["id"], 0).status_code == 422
    assert entrada(client, auth, ing["id"], -1).status_code == 422
