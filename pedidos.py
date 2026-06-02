from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from clientes import ValidationError
from database import DEFAULT_COMPANY_ID, agora, connect


def _nome_pasta_seguro(nome: str) -> str:
    nome = re.sub(r"[^\w\s.-]", "", nome, flags=re.UNICODE).strip()
    nome = re.sub(r"\s+", "_", nome)
    return nome or "cliente"


def _destino_disponivel(destino: Path) -> Path:
    if not destino.exists():
        return destino

    contador = 2
    while True:
        candidato = destino.with_name(f"{destino.stem}_{contador}{destino.suffix}")
        if not candidato.exists():
            return candidato
        contador += 1


def obter_pedido(pedido_id: int):
    with connect() as connection:
        return connection.execute(
            """
            SELECT pedidos.*, clientes.nome AS cliente_nome
            FROM pedidos
            LEFT JOIN clientes ON clientes.id = pedidos.cliente_id
            WHERE pedidos.id = ?
            """,
            (pedido_id,),
        ).fetchone()


def listar_pedidos_cliente(cliente_id: int):
    with connect() as connection:
        return connection.execute(
            """
            SELECT *
            FROM pedidos
            WHERE cliente_id = ?
            ORDER BY id DESC
            """,
            (cliente_id,),
        ).fetchall()


def buscar_pedidos(termo: str, limite: int = 300):
    termo = (termo or "").strip()
    parametros: list[str | int]

    if termo:
        filtro = """
            WHERE pedidos.numero_pedido LIKE ?
               OR LOWER(clientes.nome) LIKE ?
        """
        parametros = [f"%{termo}%", f"%{termo.lower()}%", limite]
    else:
        filtro = ""
        parametros = [limite]

    with connect() as connection:
        return connection.execute(
            f"""
            SELECT
                pedidos.id,
                pedidos.cliente_id,
                clientes.nome AS cliente_nome,
                pedidos.numero_pedido,
                pedidos.data_pedido,
                pedidos.caminho_pdf
            FROM pedidos
            LEFT JOIN clientes ON clientes.id = pedidos.cliente_id
            {filtro}
            ORDER BY pedidos.id DESC
            LIMIT ?
            """,
            parametros,
        ).fetchall()


def pedido_existe(numero_pedido: str) -> bool:
    with connect() as connection:
        return (
            connection.execute(
                "SELECT id FROM pedidos WHERE numero_pedido = ?",
                (numero_pedido.strip(),),
            ).fetchone()
            is not None
        )


def anexar_pdf(
    cliente_id: int,
    numero_pedido: str,
    arquivo_pdf: str | os.PathLike[str],
    pasta_pdfs: str | os.PathLike[str],
    empresa_id: int = DEFAULT_COMPANY_ID,
) -> tuple[int, Path]:
    numero_pedido = numero_pedido.strip()
    origem = Path(arquivo_pdf)
    pasta_base = Path(pasta_pdfs)

    if not numero_pedido:
        raise ValidationError("O numero do pedido e obrigatorio.")
    if pedido_existe(numero_pedido):
        raise ValidationError("Ja existe um pedido com esse numero.")
    if not origem.exists():
        raise ValidationError("Arquivo PDF nao encontrado.")
    if origem.suffix.lower() != ".pdf":
        raise ValidationError("Selecione um arquivo PDF.")

    with connect() as connection:
        cliente = connection.execute(
            "SELECT id, nome, empresa_id FROM clientes WHERE id = ?",
            (cliente_id,),
        ).fetchone()

        if not cliente:
            raise ValidationError("Cliente nao encontrado.")

        pasta_cliente = pasta_base / _nome_pasta_seguro(cliente["nome"])
        pasta_cliente.mkdir(parents=True, exist_ok=True)

        destino = _destino_disponivel(pasta_cliente / origem.name)
        shutil.copy2(origem, destino)

        cursor = connection.execute(
            """
            INSERT INTO pedidos
                (empresa_id, cliente_id, numero_pedido, caminho_pdf, data_pedido)
            VALUES
                (?, ?, ?, ?, ?)
            """,
            (
                cliente["empresa_id"] or empresa_id,
                cliente_id,
                numero_pedido,
                str(destino),
                agora(),
            ),
        )
        return int(cursor.lastrowid), destino


def pasta_do_cliente(cliente_nome: str, pasta_pdfs: str | os.PathLike[str]) -> Path:
    return Path(pasta_pdfs) / _nome_pasta_seguro(cliente_nome)
