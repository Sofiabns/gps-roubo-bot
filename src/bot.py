"""
bot.py — Ponto de entrada principal do furto-roubo-bot.

Executa o pipeline completo:
  1. Lê e processa dados da SSP-SP
  2. Filtra por município (config.json)
  3. Persiste histórico em CSV
  4. Dispara alerta por e-mail se o limiar for atingido
  5. (Opcional) roda em loop periódico via `schedule`
"""

import json
import logging
import os
import sys

import schedule
import time

from api_client import get_ssp_sp_data
from email_alert import send_alert
from scraper import filter_by_area
from utils import append_history, now_iso, setup_logging

# ---------------------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------------------
setup_logging()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Carga de configuração
# ---------------------------------------------------------------------------
CFG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def load_config(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.critical("Arquivo config.json não encontrado em: %s", path)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        logger.critical("config.json inválido: %s", exc)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
def run_pipeline(cfg: dict) -> None:
    xlsx_path = cfg.get("ssp_xlsx_path")
    if not xlsx_path:
        logger.error("config.json deve conter a chave 'ssp_xlsx_path'.")
        return

    alert_threshold: int = cfg.get("alert_threshold", 1)
    municipio: str = cfg.get("area", {}).get("municipio", "")
    email_cfg: dict = cfg.get("email", {})

    logger.info("Iniciando coleta de dados — %s", now_iso())

    # 1. Lê dados da planilha SSP-SP
    try:
        data = get_ssp_sp_data(local_xlsx_path=xlsx_path)
    except FileNotFoundError as exc:
        logger.error("Planilha não encontrada: %s", exc)
        return
    except Exception as exc:  # noqa: BLE001
        logger.error("Erro ao processar planilha: %s", exc)
        return

    # 2. Filtra por município, se configurado
    if municipio:
        data = filter_by_area(data, municipio)
        logger.info("Filtro aplicado → município: %s | registros: %d", municipio, len(data))

    total: int = sum(r["quantidade"] for r in data)
    logger.info("Total de ocorrências (roubo/furto): %d", total)

    # 3. Salva histórico
    append_history([{"timestamp": now_iso(), "municipio": municipio or "TODOS", "quantidade": total}])
    logger.info("Histórico atualizado em LOGS/history.csv")

    # 4. Alerta por e-mail
    if email_cfg.get("enabled", False):
        if total >= alert_threshold:
            subject = f"[Alerta SSP-SP] {total} ocorrências de roubo/furto"
            body = (
                f"Monitoramento SSP-SP — {now_iso()}\n\n"
                f"Município : {municipio or 'Todos'}\n"
                f"Ocorrências: {total}\n"
                f"Limiar     : {alert_threshold}\n\n"
                "Acesse o arquivo LOGS/history.csv para o histórico completo."
            )
            receiver = email_cfg.get("receiver", "")
            if receiver:
                try:
                    send_alert(receiver, subject, body)
                    logger.info("Alerta enviado para: %s", receiver)
                except Exception as exc:  # noqa: BLE001
                    logger.error("Falha ao enviar e-mail: %s", exc)
            else:
                logger.warning("E-mail habilitado mas 'receiver' não configurado.")
        else:
            logger.info(
                "Total (%d) abaixo do limiar (%d). Nenhum alerta enviado.",
                total,
                alert_threshold,
            )

    logger.info("Execução concluída — %s", now_iso())


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
def main() -> None:
    cfg = load_config(CFG_PATH)
    schedule_cfg = cfg.get("schedule", {})

    if schedule_cfg.get("enabled", False):
        interval_hours: int = schedule_cfg.get("interval_hours", 24)
        logger.info("Modo agendado ativo — intervalo: %d hora(s)", interval_hours)
        schedule.every(interval_hours).hours.do(run_pipeline, cfg=cfg)
        run_pipeline(cfg)  # executa imediatamente na primeira vez
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_pipeline(cfg)


if __name__ == "__main__":
    main()
