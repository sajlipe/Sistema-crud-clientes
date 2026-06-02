from __future__ import annotations

import logging
from pathlib import Path

from database import init_database
from interface import iniciar_interface
from config import data_dir


# Configurar logging básico
data_dir().mkdir(parents=True, exist_ok=True)
LOG_FILE = data_dir() / "app.log"
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logging.getLogger().addHandler(logging.StreamHandler())


def main() -> None:
    logging.info("Iniciando aplicação")
    init_database()
    iniciar_interface()
    logging.info("Aplicação encerrada")


if __name__ == "__main__":
    main()
