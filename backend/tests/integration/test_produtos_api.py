"""Testes dos endpoints de produtos com o PostgreSQL de teste."""

PRODUTO = {"nome": "Caneta azul", "preco": "2.50", "estoque_minimo": 5}


def _criar(client, **campos) -> dict:
    resposta = client.post("/produtos", json={**PRODUTO, **campos})
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def _movimentar(client, produto_id, tipo, quantidade):
    return client.post(
        f"/produtos/{produto_id}/movimentacoes",
        json={"tipo": tipo, "quantidade": quantidade},
    )


def test_raiz(client):
    assert client.get("/").json()["status"] == "ok"


def test_crud_completo(client):
    produto = _criar(client)
    assert produto["quantidade"] == 0
    assert produto["abaixo_do_minimo"] is True

    assert client.get(f"/produtos/{produto['id']}").json()["nome"] == "Caneta azul"

    editado = client.put(
        f"/produtos/{produto['id']}", json={**PRODUTO, "preco": "3.10"}
    )
    assert editado.status_code == 200
    assert editado.json()["preco"] == "3.10"

    assert client.delete(f"/produtos/{produto['id']}").status_code == 204
    assert client.get(f"/produtos/{produto['id']}").status_code == 404


def test_nome_duplicado_responde_409(client):
    _criar(client)
    resposta = client.post("/produtos", json={**PRODUTO, "nome": "CANETA AZUL"})
    assert resposta.status_code == 409


def test_dados_invalidos_respondem_422(client):
    assert (
        client.post("/produtos", json={"nome": "X", "preco": "-1"}).status_code == 422
    )


def test_busca_e_filtro_abaixo_do_minimo(client):
    caneta = _criar(client)
    _criar(client, nome="Caderno", estoque_minimo=0)
    _movimentar(client, caneta["id"], "entrada", 2)

    nomes = [p["nome"] for p in client.get("/produtos").json()]
    assert nomes == ["Caderno", "Caneta azul"]  # ordem alfabética
    busca = client.get("/produtos", params={"busca": "cad"}).json()
    assert [p["nome"] for p in busca] == ["Caderno"]
    baixos = client.get("/produtos", params={"abaixo_do_minimo": True}).json()
    assert [p["nome"] for p in baixos] == ["Caneta azul"]


def test_movimentacoes_atualizam_saldo_e_historico(client):
    produto = _criar(client)
    assert _movimentar(client, produto["id"], "entrada", 10).status_code == 201
    assert _movimentar(client, produto["id"], "saida", 3).status_code == 201

    assert client.get(f"/produtos/{produto['id']}").json()["quantidade"] == 7
    historico = client.get(f"/produtos/{produto['id']}/movimentacoes").json()
    assert [m["tipo"] for m in historico] == ["saida", "entrada"]  # recentes antes


def test_saida_sem_saldo_responde_409_e_nao_grava(client):
    produto = _criar(client)
    _movimentar(client, produto["id"], "entrada", 2)
    resposta = _movimentar(client, produto["id"], "saida", 5)
    assert resposta.status_code == 409
    assert "insuficiente" in resposta.json()["detail"]
    assert client.get(f"/produtos/{produto['id']}").json()["quantidade"] == 2
    assert len(client.get(f"/produtos/{produto['id']}/movimentacoes").json()) == 1


def test_movimentar_produto_inexistente_responde_404(client):
    assert _movimentar(client, 999, "entrada", 1).status_code == 404


def test_remover_produto_apaga_o_historico(client, session):
    from sqlalchemy import func, select

    from app.models.produto import MovimentacaoModel

    produto = _criar(client)
    _movimentar(client, produto["id"], "entrada", 1)
    client.delete(f"/produtos/{produto['id']}")
    assert session.scalar(select(func.count(MovimentacaoModel.id))) == 0


def test_resumo(client):
    vazio = client.get("/produtos/resumo").json()
    assert vazio == {
        "total_produtos": 0,
        "total_unidades": 0,
        "valor_total": "0",
        "abaixo_do_minimo": 0,
    }
    caneta = _criar(client)  # mínimo 5
    caderno = _criar(client, nome="Caderno", preco="10.00", estoque_minimo=0)
    _movimentar(client, caneta["id"], "entrada", 4)
    _movimentar(client, caderno["id"], "entrada", 3)

    resumo = client.get("/produtos/resumo").json()
    assert resumo["total_produtos"] == 2
    assert resumo["total_unidades"] == 7
    assert float(resumo["valor_total"]) == 40.0  # 4*2.50 + 3*10.00
    assert resumo["abaixo_do_minimo"] == 1


def test_cors_libera_a_origem_do_frontend(client):
    resposta = client.options(
        "/produtos",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "DELETE",
        },
    )
    assert resposta.headers["access-control-allow-origin"] == "http://localhost:5173"
