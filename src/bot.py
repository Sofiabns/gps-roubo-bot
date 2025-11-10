import json
import os
from api_client import get_ssp_sp_data
from utils import append_history, now_iso
from email_alert import send_alert

# Carrega config
cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
with open(cfg_path, "r", encoding="utf‑8") as f:
    cfg = json.load(f)

alert_threshold = cfg.get("alert_threshold", 1)
email_cfg = cfg.get("email", {})
xlsx_path = cfg.get("ssp_xlsx_path")
if not xlsx_path:
    print("⚠️ config.json deve conter 'ssp_xlsx_path':'caminho/do/arquivo.xlsx'")
    exit(1)

# Lê dados de roubo/furto
data = get_ssp_sp_data(local_xlsx_path=xlsx_path)
total = sum(r["quantidade"] for r in data)

print(f"[{now_iso()}] Total de ocorrências de roubo/furto → {total}")

# Salva histórico
rows = [{"timestamp": now_iso(), "quantidade": total}]
append_history(rows)

# Alerta
if email_cfg.get("enabled", False) and total >= alert_threshold:
    subject = f"Alerta: {total} ocorrências de roubo/furto"
    body = f"No arquivo SSP‑SP foram registradas {total} ocorrências de roubo/furto.\nVerifique o histórico."
    send_alert(email_cfg.get("receiver"), subject, body)
    print(f"📧 Alerta enviado para {email_cfg.get('receiver')}")

print("✅ Execução concluída.")
