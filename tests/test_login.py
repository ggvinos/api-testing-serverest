import pytest
from jsonschema import validate

from tests import schemas


@pytest.mark.smoke
@pytest.mark.contract
def test_login_valido_devolve_token_bearer(api, user):
    res = api.post("/login", json={"email": user["email"], "password": user["password"]})
    assert res.status_code == 200
    validate(res.json(), schemas.LOGIN)


@pytest.mark.negative
@pytest.mark.parametrize(
    "campo, valor",
    [("password", "senha-errada"), ("email", "nao-cadastrado@teste.dev")],
)
def test_login_com_credencial_invalida_retorna_401(api, user, campo, valor):
    body = {"email": user["email"], "password": user["password"], campo: valor}
    res = api.post("/login", json=body)
    assert res.status_code == 401
    assert res.json()["message"] == "Email e/ou senha inválidos"


@pytest.mark.negative
@pytest.mark.parametrize("body", [{}, {"email": "a@b.com"}, {"password": "x"}])
def test_login_sem_campos_obrigatorios_retorna_400(api, body):
    res = api.post("/login", json=body)
    assert res.status_code == 400
