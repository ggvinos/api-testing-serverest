import pytest
from jsonschema import validate

from tests import schemas


def _cart(product_id, qtd=1):
    return {"produtos": [{"idProduto": product_id, "quantidade": qtd}]}


@pytest.mark.smoke
def test_fluxo_de_compra_baixa_o_estoque(api, token, product):
    created = api.post("/carrinhos", token=token, json=_cart(product["_id"], 3))
    assert created.status_code == 201
    validate(created.json(), schemas.MESSAGE_WITH_ID)
    assert api.get(f"/produtos/{product['_id']}").json()["quantidade"] == product["quantidade"] - 3

    done = api.delete("/carrinhos/concluir-compra", token=token)
    assert done.status_code == 200
    assert done.json()["message"] == "Registro excluído com sucesso"


def test_cancelar_compra_devolve_o_estoque(api, token, product):
    api.post("/carrinhos", token=token, json=_cart(product["_id"], 4))
    res = api.delete("/carrinhos/cancelar-compra", token=token)
    assert res.status_code == 200
    assert api.get(f"/produtos/{product['_id']}").json()["quantidade"] == product["quantidade"]


@pytest.mark.negative
def test_segundo_carrinho_do_mesmo_usuario_retorna_400(api, token, product):
    api.post("/carrinhos", token=token, json=_cart(product["_id"]))
    res = api.post("/carrinhos", token=token, json=_cart(product["_id"]))
    try:
        assert res.status_code == 400
        assert res.json()["message"] == "Não é permitido ter mais de 1 carrinho"
    finally:
        api.delete("/carrinhos/cancelar-compra", token=token)


@pytest.mark.negative
def test_quantidade_acima_do_estoque_retorna_400(api, token, product):
    res = api.post("/carrinhos", token=token, json=_cart(product["_id"], product["quantidade"] + 1))
    assert res.status_code == 400
    assert res.json()["message"] == "Produto não possui quantidade suficiente"


@pytest.mark.negative
def test_carrinho_sem_token_retorna_401(api, product):
    res = api.post("/carrinhos", json=_cart(product["_id"]))
    assert res.status_code == 401


@pytest.mark.negative
def test_produto_repetido_no_carrinho_retorna_400(api, token, product):
    body = {"produtos": [{"idProduto": product["_id"], "quantidade": 1}] * 2}
    res = api.post("/carrinhos", token=token, json=body)
    assert res.status_code == 400
    assert res.json()["message"] == "Não é permitido possuir produto duplicado"
