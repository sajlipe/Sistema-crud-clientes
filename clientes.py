from __future__ import annotations

from typing import Iterable

from database import DEFAULT_COMPANY_ID, agora, connect


class ValidationError(Exception):
    """Raised when a cliente operation receives invalid user data."""


def limpar_documento(documento: str | None) -> str:
    return "".join(filter(str.isdigit, documento or ""))


def limpar_telefone(telefone: str | None) -> str:
    return "".join(filter(str.isdigit, telefone or ""))


def validar_cpf_cnpj(documento: str | None) -> tuple[bool, str, str | None]:
    documento_limpo = limpar_documento(documento)
    if len(documento_limpo) == 11:
        return _validar_cpf(documento_limpo), documento_limpo, "CPF"
    if len(documento_limpo) == 14:
        return _validar_cnpj(documento_limpo), documento_limpo, "CNPJ"
    return False, documento_limpo, None


def _validar_cpf(cpf: str) -> bool:
    """Valida CPF pelo algoritmo dos dígitos verificadores."""
    if not cpf or len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False

    def _calc(digs: str) -> int:
        total = sum(int(digs[i]) * (len(digs) + 1 - i) for i in range(len(digs)))
        resto = total % 11
        return 0 if resto < 2 else 11 - resto

    primeiro = _calc(cpf[:9])
    segundo = _calc(cpf[:9] + str(primeiro))
    return cpf[9] == str(primeiro) and cpf[10] == str(segundo)


def _validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ pelo algoritmo dos dígitos verificadores."""
    if not cnpj or len(cnpj) != 14:
        return False
    if cnpj == cnpj[0] * 14:
        return False

    def _calc(digs: str, pesos: list[int]) -> int:
        total = sum(int(digs[i]) * pesos[i] for i in range(len(digs)))
        resto = total % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    primeiro = _calc(cnpj[:12], pesos1)
    segundo = _calc(cnpj[:12] + str(primeiro), pesos2)
    return cnpj[12] == str(primeiro) and cnpj[13] == str(segundo)


def formatar_documento(documento: str | None) -> str:
    documento_limpo = limpar_documento(documento)
    if len(documento_limpo) == 11:
        return (
            f"{documento_limpo[:3]}."
            f"{documento_limpo[3:6]}."
            f"{documento_limpo[6:9]}-"
            f"{documento_limpo[9:]}"
        )
    if len(documento_limpo) == 14:
        return (
            f"{documento_limpo[:2]}."
            f"{documento_limpo[2:5]}."
            f"{documento_limpo[5:8]}/"
            f"{documento_limpo[8:12]}-"
            f"{documento_limpo[12:]}"
        )
    return documento or ""


def formatar_documento_parcial(documento: str | None) -> str:
    digitos = limpar_documento(documento)[:14]

    if len(digitos) <= 11:
        partes = []
        if len(digitos) <= 3:
            return digitos
        partes.append(digitos[:3])
        if len(digitos) <= 6:
            partes.append(digitos[3:])
            return ".".join(filter(None, partes))
        partes.append(digitos[3:6])
        if len(digitos) <= 9:
            partes.append(digitos[6:])
            return ".".join(filter(None, partes))
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"

    if len(digitos) <= 2:
        return digitos
    if len(digitos) <= 5:
        return f"{digitos[:2]}.{digitos[2:]}"
    if len(digitos) <= 8:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:]}"
    if len(digitos) <= 12:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:]}"
    return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"


def formatar_telefone(telefone: str | None) -> str:
    digitos = limpar_telefone(telefone)
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    return telefone or ""


def formatar_telefone_parcial(telefone: str | None) -> str:
    digitos = limpar_telefone(telefone)[:11]
    if len(digitos) <= 2:
        return digitos
    if len(digitos) <= 6:
        return f"({digitos[:2]}) {digitos[2:]}"
    if len(digitos) <= 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"


def obter_cliente(cliente_id: int):
    with connect() as connection:
        return connection.execute(
            "SELECT * FROM clientes WHERE id = ?",
            (cliente_id,),
        ).fetchone()


def listar_clientes(limite: int = 300):
    with connect() as connection:
        return connection.execute(
            """
            SELECT *
            FROM clientes
            ORDER BY nome COLLATE NOCASE
            LIMIT ?
            """,
            (limite,),
        ).fetchall()


def buscar_cliente_inteligente(termo: str, limite: int = 300):
    termo = (termo or "").strip()
    if not termo:
        return listar_clientes(limite)

    termo_lower = termo.lower()
    termo_doc = limpar_documento(termo)
    termo_tel = limpar_telefone(termo)

    filtros = [
        "LOWER(nome) LIKE ?",
        "LOWER(COALESCE(endereco, '')) LIKE ?",
    ]
    parametros: list[str | int] = [f"%{termo_lower}%", f"%{termo_lower}%"]

    if termo_doc:
        filtros.append("cpf_cnpj LIKE ?")
        parametros.append(f"%{termo_doc}%")

    if termo_tel:
        filtros.append("telefone LIKE ?")
        parametros.append(f"%{termo_tel}%")

    parametros.append(limite)

    with connect() as connection:
        return connection.execute(
            f"""
            SELECT *
            FROM clientes
            WHERE {" OR ".join(filtros)}
            ORDER BY nome COLLATE NOCASE
            LIMIT ?
            """,
            parametros,
        ).fetchall()


def existe_nome(nome: str, excluir_id: int | None = None) -> bool:
    query = "SELECT id FROM clientes WHERE LOWER(nome) = LOWER(?)"
    parametros: list[str | int] = [nome]
    if excluir_id is not None:
        query += " AND id != ?"
        parametros.append(excluir_id)

    with connect() as connection:
        return connection.execute(query, parametros).fetchone() is not None


def existe_documento(documento: str, excluir_id: int | None = None) -> bool:
    documento_limpo = limpar_documento(documento)
    query = "SELECT id FROM clientes WHERE cpf_cnpj = ?"
    parametros: list[str | int] = [documento_limpo]
    if excluir_id is not None:
        query += " AND id != ?"
        parametros.append(excluir_id)

    with connect() as connection:
        return connection.execute(query, parametros).fetchone() is not None


def criar_cliente(
    nome: str,
    cpf_cnpj: str,
    telefone: str,
    endereco: str,
    empresa_id: int = DEFAULT_COMPANY_ID,
    permitir_sem_documento: bool = False,
) -> int:
    nome = nome.strip()
    endereco = endereco.strip()
    valido, documento_limpo, tipo = validar_cpf_cnpj(cpf_cnpj)

    if not nome:
        raise ValidationError("O nome é obrigatório.")

    if not documento_limpo:
        # Sem documento informado
        if not permitir_sem_documento:
            raise ValidationError("CPF/CNPJ inválido. Use 11 dígitos para CPF ou 14 para CNPJ.")
    else:
        if not valido:
            raise ValidationError("CPF/CNPJ inválido. Use 11 dígitos para CPF ou 14 para CNPJ.")
        if existe_documento(documento_limpo):
            raise ValidationError(f"Esse {tipo} já existe no sistema.")

    if existe_nome(nome):
        raise ValidationError("Já existe um cliente com esse nome completo.")

    with connect() as connection:
        documento_valor = documento_limpo or None
        cursor = connection.execute(
            """
            INSERT INTO clientes
                (empresa_id, nome, telefone, endereco, cpf_cnpj, data_cadastro)
            VALUES
                (?, ?, ?, ?, ?, ?)
            """,
            (
                empresa_id,
                nome,
                limpar_telefone(telefone),
                endereco,
                documento_valor,
                agora(),
            ),
        )
        return int(cursor.lastrowid)


def atualizar_cliente(
    cliente_id: int,
    nome: str,
    cpf_cnpj: str,
    telefone: str,
    endereco: str,
    permitir_nome_duplicado: bool = False,
    permitir_sem_documento: bool = False,
) -> None:
    nome = nome.strip()
    endereco = endereco.strip()
    valido, documento_limpo, tipo = validar_cpf_cnpj(cpf_cnpj)

    if not nome:
        raise ValidationError("O nome é obrigatório.")

    if not documento_limpo:
        if not permitir_sem_documento:
            raise ValidationError("CPF/CNPJ inválido. Use 11 dígitos para CPF ou 14 para CNPJ.")
    else:
        if not valido:
            raise ValidationError("CPF/CNPJ inválido. Use 11 dígitos para CPF ou 14 para CNPJ.")
        if existe_documento(documento_limpo, cliente_id):
            raise ValidationError(f"Esse {tipo} já existe no sistema para outro cliente.")

    if not permitir_nome_duplicado and existe_nome(nome, cliente_id):
        raise ValidationError("Já existe outro cliente com esse nome completo.")

    with connect() as connection:
        connection.execute(
            """
            UPDATE clientes
            SET nome = ?, telefone = ?, endereco = ?, cpf_cnpj = ?
            WHERE id = ?
            """,
            (
                nome,
                limpar_telefone(telefone),
                endereco,
                documento_limpo or None,
                cliente_id,
            ),
        )


def excluir_cliente(cliente_id: int) -> None:
    with connect() as connection:
        connection.execute("DELETE FROM pedidos WHERE cliente_id = ?", (cliente_id,))
        connection.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))


def total_pedidos_cliente(cliente_id: int) -> int:
    with connect() as connection:
        return int(
            connection.execute(
                "SELECT COUNT(*) FROM pedidos WHERE cliente_id = ?",
                (cliente_id,),
            ).fetchone()[0]
        )


def linhas_para_exibicao(clientes: Iterable) -> list[tuple[str, str, str, str]]:
    return [
        (
            cliente["nome"],
            formatar_documento(cliente["cpf_cnpj"]),
            formatar_telefone(cliente["telefone"]),
            cliente["endereco"] or "",
        )
        for cliente in clientes
    ]
