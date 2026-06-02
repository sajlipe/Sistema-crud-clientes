from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from config import database_path


DEFAULT_COMPANY_ID = 1


def agora() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def db_path() -> Path:
    return database_path()


def connect() -> sqlite3.Connection:
    db_path().parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _columns(connection: sqlite3.Connection, table: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def _ensure_column(
    connection: sqlite3.Connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    if column not in _columns(connection, table):
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_database() -> None:
    db_path().parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path()) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf_cnpj TEXT,
                telefone TEXT,
                endereco TEXT,
                data_cadastro TEXT
            )
            """
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO empresas
                (id, nome, data_cadastro)
            VALUES
                (?, ?, ?)
            """,
            (DEFAULT_COMPANY_ID, "Empresa Principal", agora()),
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL DEFAULT 1,
                nome TEXT NOT NULL,
                email TEXT,
                perfil TEXT DEFAULT 'admin',
                ativo INTEGER DEFAULT 1,
                data_cadastro TEXT,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL DEFAULT 1,
                nome TEXT NOT NULL,
                telefone TEXT,
                endereco TEXT,
                cpf_cnpj TEXT UNIQUE,
                data_cadastro TEXT,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL DEFAULT 1,
                cliente_id INTEGER,
                numero_pedido TEXT UNIQUE,
                caminho_pdf TEXT,
                data_pedido TEXT,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
            """
        )

        _ensure_column(connection, "clientes", "empresa_id", "INTEGER DEFAULT 1")
        _ensure_column(connection, "pedidos", "empresa_id", "INTEGER DEFAULT 1")

        connection.execute(
            "UPDATE clientes SET empresa_id = ? WHERE empresa_id IS NULL",
            (DEFAULT_COMPANY_ID,),
        )
        connection.execute(
            """
            UPDATE pedidos
            SET empresa_id = COALESCE(
                (SELECT clientes.empresa_id FROM clientes WHERE clientes.id = pedidos.cliente_id),
                ?
            )
            WHERE empresa_id IS NULL
            """,
            (DEFAULT_COMPANY_ID,),
        )

        connection.execute("CREATE INDEX IF NOT EXISTS idx_cliente_nome ON clientes(nome)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_cliente_cpf ON clientes(cpf_cnpj)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_cliente_tel ON clientes(telefone)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_cliente_empresa ON clientes(empresa_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_pedido_numero ON pedidos(numero_pedido)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_pedido_cliente ON pedidos(cliente_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_pedido_empresa ON pedidos(empresa_id)")
        # Normalizar valores vazios de CPF/CNPJ para NULL para evitar conflito de UNIQUE em strings vazias
        connection.execute("UPDATE clientes SET cpf_cnpj = NULL WHERE cpf_cnpj = ''")


def dashboard_data() -> dict[str, Any]:
    with connect() as connection:
        clientes = connection.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        pedidos = connection.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        ultimo_cliente = connection.execute(
            """
            SELECT nome, data_cadastro
            FROM clientes
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
        ultimo_pedido = connection.execute(
            """
            SELECT pedidos.numero_pedido, pedidos.data_pedido, clientes.nome AS cliente_nome
            FROM pedidos
            LEFT JOIN clientes ON clientes.id = pedidos.cliente_id
            ORDER BY pedidos.id DESC
            LIMIT 1
            """
        ).fetchone()

    return {
        "clientes": clientes,
        "pedidos": pedidos,
        "ultimo_cliente": dict(ultimo_cliente) if ultimo_cliente else None,
        "ultimo_pedido": dict(ultimo_pedido) if ultimo_pedido else None,
    }


def atualizar_empresa_padrao(dados: dict[str, str]) -> None:
    with connect() as connection:
        connection.execute(
            """
            UPDATE empresas
            SET nome = ?, cpf_cnpj = ?, telefone = ?, endereco = ?
            WHERE id = ?
            """,
            (
                dados.get("company_name") or "Empresa Principal",
                dados.get("company_document") or "",
                dados.get("company_phone") or "",
                dados.get("company_address") or "",
                DEFAULT_COMPANY_ID,
            ),
        )
