import pandas as pd
import os

def get_ssp_sp_data(local_xlsx_path: str):
    """
    Lê arquivo .xlsx da SSP‑SP e retorna total de ocorrências de roubo/furto por linha.
    Retorna lista de dict: {'natureza': str, 'quantidade': int}
    """
    if not os.path.exists(local_xlsx_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {local_xlsx_path}")

    # Lê planilha principal
    df = pd.read_excel(local_xlsx_path, sheet_name=0, dtype=str)

    # Limpa nomes de coluna
    df.columns = [c.strip() for c in df.columns]

    # Substitui valores ausentes por 0 e converte para inteiro
    for col in df.columns[1:]:  # ignora coluna "Natureza"
        df[col] = pd.to_numeric(df[col].str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce").fillna(0)

    # Cria coluna total somando todos os meses (caso Total não esteja confiável)
    df["quantidade"] = df[df.columns[1:-1]].sum(axis=1)

    # Filtra apenas linhas com "ROUBO" ou "FURTO"
    filtered = df[df["Natureza"].str.upper().str.contains("ROUBO|FURTO")]

    result = []
    for _, row in filtered.iterrows():
        result.append({
            "natureza": row["Natureza"],
            "quantidade": int(row["quantidade"])
        })

    return result
