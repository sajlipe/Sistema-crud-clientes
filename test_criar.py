from __future__ import annotations

import os
import tempfile
from pathlib import Path


tmp = Path(tempfile.mkdtemp(prefix="sistema_clientes_test_"))
os.environ["SISTEMA_CLIENTES_DATA_DIR"] = str(tmp)
os.environ["SISTEMA_CLIENTES_DB"] = str(tmp / "clientes.db")

from database import connect, init_database  # noqa: E402
import clientes  # noqa: E402


init_database()

with connect() as connection:
    connection.execute("DELETE FROM clientes WHERE nome LIKE 'Teste Unit %'")

try:
    id1 = clientes.criar_cliente(
        "Teste Unit SemDoc",
        "",
        "11999999999",
        "Rua Teste",
        permitir_sem_documento=True,
    )
    print("criado sem doc id=", id1)
except Exception as exc:
    print("erro sem doc", exc)

try:
    id2 = clientes.criar_cliente(
        "Teste Unit Val",
        "123",
        "11999999999",
        "Rua Teste",
        permitir_sem_documento=False,
    )
    print("criado com doc id=", id2)
except Exception as exc:
    print("erro com doc invalido (esperado):", exc)

try:
    id3 = clientes.criar_cliente(
        "Teste Unit CPF",
        "11144477735",
        "11988887777",
        "Rua Teste",
        permitir_sem_documento=False,
    )
    print("criado com cpf id=", id3)
except Exception as exc:
    print("erro criar com cpf:", exc)

print("banco temporario:", tmp / "clientes.db")
