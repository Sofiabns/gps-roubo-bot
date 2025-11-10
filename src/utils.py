import os
import pandas as pd
from datetime import datetime

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "LOGS")
HISTORY_PATH = os.path.join(LOGS_DIR, "history.csv")

def ensure_logs_dir():
    os.makedirs(LOGS_DIR, exist_ok=True)

def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def append_history(rows: list[dict]):
    ensure_logs_dir()
    df_new = pd.DataFrame(rows)
    if os.path.exists(HISTORY_PATH) and os.path.getsize(HISTORY_PATH) > 0:
        df_existing = pd.read_csv(HISTORY_PATH)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(HISTORY_PATH, index=False)
