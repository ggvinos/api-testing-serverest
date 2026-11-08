import pytest
from jsonschema import validate

from tests import schemas
from tests.conftest import unique


@pytest.mark.smoke
@pytest.mark.contract
def test_listar_produtos_segue_o_contrato(api):
    res = api.get("/produtos")
    assert res.status_code == 200
    body = res.json()
    validate(body, schemas.PRODUCT_LIST)
    assert body["quantidade"] == len(body["produtos"])


@pytest.mark.smoke
@pytest.mark.contract
def test_cadastrar_produto(api, token, product_payload):
    res = api.post("/produtos", token=token, json=product_payload)
    try:
        assert res.status_code == 201
        validate(res.json(), schemas.MESSAGE_WITH_ID)
    finally:
        if res.status_code == 201:
            api.delete(f"/produtos/{res.json()['_id']}", token=token)


@pytest.mark.contract
def test_consultar_produto_cadastrado(api, product):
    res = api.get(f"/produtos/{product['_id']}")
    assert res.status_code == 200
    validate(res.json(), schemas.PRODUCT)
    assert res.json()["nome"] == product["nome"]


def test_alterar_produto(api, token, product):
    novo = {**{k: product[k] for k in ("nome", "preco", "descricao", "quantidade")}, "preco": 250}
    res = api.put(f"/produtos/{product['_id']}", token=token, json=novo)
    assert res.status_code == 200
    assert api.get(f"/produtos/{product['_id']}").json()["preco"] == 250


def test_excluir_produto(api, token, product_payload):
    created = api.post("/produtos", token=token, json=product_payload).json()["_id"]
    res = api.delete(f"/produtos/{created}", token=token)
    assert res.status_code == 200
    assert api.get(f"/produtos/{created}").status_code == 400


def test_filtrar_por_nome(api, product):
    res = api.get("/produtos", params={"nome": product["nome"]})
    assert [p["_id"] for p in res.json()["produtos"]] == [product["_id"]]


@pytest.mark.negative
def test_cadastro_sem_token_retorna_401(api, product_payload):
    res = api.post("/produtos", json=product_payload)
    assert res.status_code == 401


@pytest.mark.negative
def test_cadastro_com_token_invalido_retorna_401(api, product_payload):
    res = api.post("/produtos", token="Bearer token.invalido.aqui", json=product_payload)
    assert res.status_code == 401


@pytest.mark.negative
def test_nome_duplicado_retorna_400(api, token, product):
    res = api.post("/produtos", token=token, json={k: product[k] for k in ("nome", "preco", "descricao", "quantidade")})
    assert res.status_code == 400
    assert res.json()["message"] == "Já existe produto com esse nome"


@pytest.mark.negative
def test_usuario_nao_admin_nao_cadastra_produto(api, user_payload, product_payload):
    user_payload["administrador"] = "false"
    created = api.post("/usuarios", json=user_payload).json()["_id"]
    try:
        tk = api.post("/login", json={"email": user_payload["email"], "password": user_payload["password"]}).json()["authorization"]
        res = api.post("/produtos", token=tk, json=product_payload)
        assert res.status_code == 403
    finally:
        api.delete(f"/usuarios/{created}")


@pytest.mark.negative
@pytest.mark.parametrize(
    "campo, valor",
    [
        ("preco", -1),
        ("preco", 0),
        ("preco", "dez"),
        ("quantidade", -5),
        ("nome", ""),
        ("descricao", ""),
    ],
)
def test_valores_invalidos_retornam_400(api, token, product_payload, campo, valor):
    product_payload[campo] = valor
    res = api.post("/produtos", token=token, json=product_payload)
    assert res.status_code == 400
    assert campo in res.json()


@pytest.mark.negative
def test_id_com_tamanho_invalido_retorna_400(api):
    res = api.get("/produtos/curto")
    assert res.status_code == 400
    assert "16 caracteres" in res.json()["id"]


@pytest.mark.negative
def test_id_inexistente_retorna_erro_de_negocio(api):
    res = api.get(f"/produtos/{'A' * 16}")
    assert res.status_code == 400
    assert res.json()["message"] == "Produto não encontrado"
