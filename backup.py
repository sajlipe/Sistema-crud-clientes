from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from database import db_path, init_database


def caminho_backup_do_dia(pasta_backup: str | Path) -> Path:
    data = datetime.now().strftime("%Y_%m_%d")
    return Path(pasta_backup) / f"backup_{data}.db"


def criar_backup(pasta_backup: str | Path, substituir: bool = False) -> Path:
    init_database()
    origem = db_path()
    destino = caminho_backup_do_dia(pasta_backup)
    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.exists() and not substituir:
        raise FileExistsError(destino)

    shutil.copy2(origem, destino)
    return destino


def restaurar_backup(arquivo_backup: str | Path) -> Path:
    origem = Path(arquivo_backup)
    destino = db_path()

    if not origem.exists():
        raise FileNotFoundError(origem)
    if origem.suffix.lower() != ".db":
        raise ValueError("Selecione um arquivo .db valido.")

    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.exists():
        antes = destino.with_name(
            f"{destino.stem}_antes_restauracao_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.db"
        )
        shutil.copy2(destino, antes)

    shutil.copy2(origem, destino)
    init_database()
    return destino
