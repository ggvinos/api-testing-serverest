USER = {
    "type": "object",
    "required": ["nome", "email", "password", "administrador", "_id"],
    "properties": {
        "nome": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string"},
        "administrador": {"enum": ["true", "false"]},
        "_id": {"type": "string", "pattern": "^[A-Za-z0-9]{16}$"},
    },
    "additionalProperties": False,
}

USER_LIST = {
    "type": "object",
    "required": ["quantidade", "usuarios"],
    "properties": {
        "quantidade": {"type": "integer", "minimum": 0},
        "usuarios": {"type": "array", "items": USER},
    },
}

PRODUCT = {
    "type": "object",
    "required": ["nome", "preco", "descricao", "quantidade", "_id"],
    "properties": {
        "nome": {"type": "string", "minLength": 1},
        "preco": {"type": "integer", "minimum": 1},
        "descricao": {"type": "string"},
        "quantidade": {"type": "integer", "minimum": 0},
        "_id": {"type": "string", "pattern": "^[A-Za-z0-9]{16}$"},
    },
    "additionalProperties": False,
}

PRODUCT_LIST = {
    "type": "object",
    "required": ["quantidade", "produtos"],
    "properties": {
        "quantidade": {"type": "integer", "minimum": 0},
        "produtos": {"type": "array", "items": PRODUCT},
    },
}

LOGIN = {
    "type": "object",
    "required": ["message", "authorization"],
    "properties": {
        "message": {"type": "string"},
        "authorization": {"type": "string", "pattern": r"^Bearer\s\S+$"},
    },
}

MESSAGE_WITH_ID = {
    "type": "object",
    "required": ["message", "_id"],
    "properties": {"message": {"type": "string"}, "_id": {"type": "string"}},
}

MESSAGE = {
    "type": "object",
    "required": ["message"],
    "properties": {"message": {"type": "string"}},
}
