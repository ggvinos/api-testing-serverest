import os
import uuid

import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")


class Api:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"

    def request(self, method, path, token=None, **kwargs):
        headers = {"Authorization": token} if token else {}
        return self.session.request(
            method, f"{self.base_url}{path}", headers=headers, timeout=15, **kwargs
        )

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)

    def put(self, path, **kw):
        return self.request("PUT", path, **kw)

    def delete(self, path, **kw):
        return self.request("DELETE", path, **kw)


def unique(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


@pytest.fixture(scope="session")
def api():
    return Api(BASE_URL)


@pytest.fixture
def user_payload():
    return {
        "nome": "Usuário de teste",
        "email": f"{unique('qa')}@teste.dev",
        "password": "senha123",
        "administrador": "true",
    }


@pytest.fixture
def user(api, user_payload):
    res = api.post("/usuarios", json=user_payload)
    assert res.status_code == 201, res.text
    created = {**user_payload, "_id": res.json()["_id"]}
    yield created
    api.delete(f"/usuarios/{created['_id']}")


@pytest.fixture
def token(api, user):
    res = api.post("/login", json={"email": user["email"], "password": user["password"]})
    assert res.status_code == 200, res.text
    return res.json()["authorization"]


@pytest.fixture
def product_payload():
    return {"nome": unique("produto"), "preco": 100, "descricao": "item de teste", "quantidade": 10}


@pytest.fixture
def product(api, token, product_payload):
    res = api.post("/produtos", token=token, json=product_payload)
    assert res.status_code == 201, res.text
    created = {**product_payload, "_id": res.json()["_id"]}
    yield created
    api.delete(f"/produtos/{created['_id']}", token=token)
