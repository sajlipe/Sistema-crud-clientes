from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


APP_ID = "SistemaCRUD"
APP_TITLE = "Sistema de Gerenciamento de Clientes e Pedidos"
APP_VERSION = "2.0"
CONFIG_FILE = "config.json"
DEFAULT_THEME = "flatly"


def app_dir() -> Path:
    """Return the folder where the application is installed."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def user_data_dir() -> Path:
    override = os.environ.get("SISTEMA_CLIENTES_DATA_DIR")
    if override:
        return Path(override).resolve()

    if getattr(sys, "frozen", False):
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            local_app_data = str(Path.home() / "AppData" / "Local")
        return Path(local_app_data) / APP_ID

    return app_dir()


def migrate_old_data() -> None:
    """Migrate database and config from old install folder to user data directory."""
    if not getattr(sys, "frozen", False):
        return

    new_dir = user_data_dir()
    old_dir = app_dir()
    if new_dir == old_dir:
        return

    new_dir.mkdir(parents=True, exist_ok=True)

    for filename in ["clientes.db", CONFIG_FILE]:
        old_file = old_dir / filename
        new_file = new_dir / filename
        if old_file.exists() and not new_file.exists():
            shutil.copy2(old_file, new_file)


def data_dir() -> Path:
    directory = user_data_dir()
    directory.mkdir(parents=True, exist_ok=True)
    migrate_old_data()
    return directory


def database_path() -> Path:
    override = os.environ.get("SISTEMA_CLIENTES_DB")
    if override:
        return Path(override).resolve()
    return data_dir() / "clientes.db"


def config_path() -> Path:
    override = os.environ.get("SISTEMA_CLIENTES_CONFIG")
    if override:
        return Path(override).resolve()
    return data_dir() / CONFIG_FILE


def assets_dir() -> Path:
    bundled_root = Path(getattr(sys, "_MEIPASS", app_dir()))
    bundled_assets = bundled_root / "assets"
    local_assets = app_dir() / "assets"

    if bundled_assets.exists():
        return bundled_assets
    if local_assets.exists():
        return local_assets
    return app_dir()


def asset_path(filename: str) -> Path:
    candidate = assets_dir() / filename
    if candidate.exists():
        return candidate
    return app_dir() / filename


def default_config() -> dict[str, Any]:
    base = data_dir()
    return {
        "pdf_folder": "",
        "backup_folder": str(base / "backups"),
        "theme": DEFAULT_THEME,
        "company_name": "Sua empresa",
        "company_document": "",
        "company_phone": "",
        "company_address": "",
    }


def load_config() -> dict[str, Any]:
    values = default_config()
    path = config_path()

    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as file:
                stored = json.load(file)
            if isinstance(stored, dict):
                values.update(stored)
        except (OSError, json.JSONDecodeError):
            pass

    return values


def save_config(values: dict[str, Any]) -> dict[str, Any]:
    config = default_config()
    config.update(values)

    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)

    return config
