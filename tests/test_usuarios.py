import pytest
from jsonschema import validate

from tests import schemas


@pytest.mark.smoke
@pytest.mark.contract
def test_cadastrar_usuario(api, user_payload):
    res = api.post("/usuarios", json=user_payload)
    try:
        assert res.status_code == 201
        validate(res.json(), schemas.MESSAGE_WITH_ID)
        assert res.json()["message"] == "Cadastro realizado com sucesso"
    finally:
        if res.status_code == 201:
            api.delete(f"/usuarios/{res.json()['_id']}")


@pytest.mark.contract
def test_consultar_usuario_por_id(api, user):
    res = api.get(f"/usuarios/{user['_id']}")
    assert res.status_code == 200
    validate(res.json(), schemas.USER)
    assert res.json()["email"] == user["email"]


@pytest.mark.contract
def test_listagem_segue_o_contrato(api, user):
    res = api.get("/usuarios")
    assert res.status_code == 200
    body = res.json()
    validate(body, schemas.USER_LIST)
    assert body["quantidade"] == len(body["usuarios"])
    assert user["_id"] in {u["_id"] for u in body["usuarios"]}


def test_filtrar_listagem_por_email(api, user):
    res = api.get("/usuarios", params={"email": user["email"]})
    assert res.status_code == 200
    assert [u["_id"] for u in res.json()["usuarios"]] == [user["_id"]]


def test_alterar_usuario(api, user):
    novo = {**{k: user[k] for k in ("nome", "email", "password", "administrador")}, "nome": "Nome alterado"}
    res = api.put(f"/usuarios/{user['_id']}", json=novo)
    assert res.status_code == 200
    assert api.get(f"/usuarios/{user['_id']}").json()["nome"] == "Nome alterado"


def test_excluir_usuario(api, user_payload):
    created = api.post("/usuarios", json=user_payload).json()["_id"]
    res = api.delete(f"/usuarios/{created}")
    assert res.status_code == 200
    assert api.get(f"/usuarios/{created}").status_code == 400


@pytest.mark.negative
def test_email_duplicado_retorna_400(api, user):
    res = api.post("/usuarios", json={k: user[k] for k in ("nome", "email", "password", "administrador")})
    assert res.status_code == 400
    assert res.json()["message"] == "Este email já está sendo usado"


@pytest.mark.negative
def test_campos_invalidos_listam_cada_erro(api):
    res = api.post(
        "/usuarios",
        json={"nome": "", "email": "nao-e-email", "password": "", "administrador": "talvez"},
    )
    assert res.status_code == 400
    assert set(res.json()) == {"nome", "email", "password", "administrador"}


@pytest.mark.negative
@pytest.mark.parametrize("campo", ["nome", "email", "password", "administrador"])
def test_campo_ausente_retorna_400(api, user_payload, campo):
    user_payload.pop(campo)
    res = api.post("/usuarios", json=user_payload)
    assert res.status_code == 400
    assert campo in res.json()


@pytest.mark.negative
@pytest.mark.xfail(
    strict=True,
    reason="Achado de segurança: a listagem devolve a senha em texto puro (comportamento da Serverest)",
)
def test_listagem_nao_deveria_expor_senha(api, user):
    body = api.get("/usuarios", params={"_id": user["_id"]}).json()
    assert all("password" not in u for u in body["usuarios"])
