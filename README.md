# api-testing-serverest

Suíte de testes de API em Python (pytest, requests, jsonschema) contra a [Serverest](https://serverest.dev): CRUD de usuários e produtos, autenticação com token Bearer, fluxo de carrinho, validação de contrato com JSON Schema e casos negativos. Relatório HTML e CI no GitHub Actions.

Por padrão roda contra uma instância local (`npx serverest`), o que deixa os testes determinísticos e não sobrecarrega o serviço público.

## Cobertura

| Arquivo | O que verifica |
| --- | --- |
| `test_login.py` | Login válido, credencial inválida (401), campos ausentes (400) |
| `test_usuarios.py` | CRUD, filtro por e-mail, e-mail duplicado, erros de validação campo a campo |
| `test_produtos.py` | CRUD, filtro por nome, token ausente e inválido (401), não admin (403), nome duplicado, valores inválidos parametrizados, ids malformados e inexistentes |
| `test_carrinhos.py` | Compra baixa o estoque, cancelar devolve o estoque, segundo carrinho, estoque insuficiente, produto duplicado |

43 testes, divididos pelos marcadores `smoke`, `contract` e `negative`.

## Contrato

Os formatos de resposta ficam em `tests/schemas.py` como JSON Schema (usuário, produto, listagens, login e mensagens). Os testes `contract` validam cada resposta contra o schema, então um campo novo, removido ou com tipo diferente quebra o teste.

## Achado documentado

`GET /usuarios` devolve a senha em texto puro. O teste `test_listagem_nao_deveria_expor_senha` está marcado `xfail(strict=True)`: passa como "falha esperada" hoje e quebra a suíte quando a API for corrigida, avisando para remover a anotação.

## Como rodar

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
npx serverest &
pytest
pytest -m smoke
pytest -m "negative and not contract"
BASE_URL=https://serverest.dev pytest -m smoke
```

O relatório fica em `report/report.html`. Contra a Serverest pública use só o smoke.

## Estrutura

- `tests/conftest.py`: cliente HTTP, fixtures de usuário, token e produto, com limpeza ao final de cada teste.
- `tests/schemas.py`: contratos JSON Schema.
- `.github/workflows/api-tests.yml`: sobe a Serverest local, roda a suíte e anexa o relatório.
