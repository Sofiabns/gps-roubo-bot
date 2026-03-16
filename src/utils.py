"""
utils.py — Utilitários compartilhados do furto-roubo-bot.

Inclui:
  - Configuração centralizada de logging (arquivo + console)
  - Geração de timestamp ISO-8601
  - Persistência de histórico em CSV (thread-safe via arquivo temporário)
"""

import csv
import logging
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT_DIR / "LOGS"
HISTORY_PATH = LOGS_DIR / "history.csv"
LOG_FILE_PATH = LOGS_DIR / "bot.log"

HISTORY_FIELDNAMES = ["timestamp", "municipio", "quantidade"]


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(level: int = logging.INFO) -> None:
    """
    Configura handlers de logging para console e arquivo rotativo.
    Deve ser chamada uma única vez no início da aplicação.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    fmt = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        ],
    )


# ---------------------------------------------------------------------------
# Timestamp
# ---------------------------------------------------------------------------

def now_iso() -> str:
    """Retorna o timestamp atual no formato 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Histórico CSV
# ---------------------------------------------------------------------------

def append_history(rows: list[dict]) -> None:
    """
    Acrescenta ``rows`` ao CSV de histórico de forma atômica.

    Cria o arquivo com cabeçalho se não existir. A escrita é feita
    num arquivo temporário e depois movida para evitar corrupção.

    Parâmetros
    ----------
    rows : list[dict]
        Cada dicionário deve conter as chaves definidas em
        ``HISTORY_FIELDNAMES``.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    file_exists = HISTORY_PATH.exists() and HISTORY_PATH.stat().st_size > 0

    # Escreve num arquivo temporário no mesmo diretório (garante rename atômico)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=LOGS_DIR, suffix=".csv.tmp")
    try:
        with os.fdopen(tmp_fd, "w", newline="", encoding="utf-8") as tmp_file:
            # Copia conteúdo existente
            if file_exists:
                with open(HISTORY_PATH, "r", encoding="utf-8", newline="") as src:
                    shutil.copyfileobj(src, tmp_file)

            writer = csv.DictWriter(
                tmp_file,
                fieldnames=HISTORY_FIELDNAMES,
                extrasaction="ignore",
            )
            if not file_exists:
                writer.writeheader()
            for row in rows:
                writer.writerow(row)

        shutil.move(tmp_path, HISTORY_PATH)
    except Exception:
        os.unlink(tmp_path)
        raise


def read_history() -> list[dict]:
    """
    Lê o histórico completo e retorna uma lista de dicionários.

    Retorna lista vazia se o arquivo não existir.
    """
    if not HISTORY_PATH.exists():
        return []
    with open(HISTORY_PATH, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
