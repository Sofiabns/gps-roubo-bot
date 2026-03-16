"""
api_client.py — Leitura e normalização da planilha SSP-SP.

Suporta planilhas com coluna "Natureza" ou "NATUREZA" e detecta
automaticamente a coluna de totais, caindo para soma mensal se necessário.
"""

import logging
import os
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Palavras-chave que indicam ocorrências de interesse
CRIME_KEYWORDS = ["ROUBO", "FURTO"]

# Possíveis nomes da coluna principal de tipo de crime
NATUREZA_CANDIDATES = ["Natureza", "NATUREZA", "natureza", "Tipo", "TIPO"]

# Possíveis nomes da coluna de total anual já calculada
TOTAL_CANDIDATES = ["Total", "TOTAL", "total", "Ano", "ANO"]


def _find_column(columns: pd.Index, candidates: list[str]) -> Optional[str]:
    """Retorna o primeiro nome de candidato presente no Index, ou None."""
    for name in candidates:
        if name in columns:
            return name
    return None


def get_ssp_sp_data(local_xlsx_path: str) -> list[dict]:
    """
    Lê o arquivo .xlsx da SSP-SP e retorna as ocorrências de roubo/furto.

    Parâmetros
    ----------
    local_xlsx_path : str
        Caminho para o arquivo .xlsx da SSP-SP.

    Retorna
    -------
    list[dict]
        Lista de dicionários com as chaves:
          - ``natureza``  (str)  : tipo de crime
          - ``quantidade`` (int) : total de ocorrências
    """
    if not os.path.exists(local_xlsx_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {local_xlsx_path}")

    logger.debug("Lendo planilha: %s", local_xlsx_path)
    df = pd.read_excel(local_xlsx_path, sheet_name=0, dtype=str)

    # Normaliza nomes de colunas (remove espaços extras)
    df.columns = [str(c).strip() for c in df.columns]

    # Localiza coluna de natureza
    natureza_col = _find_column(df.columns, NATUREZA_CANDIDATES)
    if natureza_col is None:
        raise ValueError(
            f"Coluna de natureza não encontrada. Colunas disponíveis: {list(df.columns)}"
        )

    # Converte colunas numéricas (meses / totais)
    numeric_cols = [c for c in df.columns if c != natureza_col]
    for col in numeric_cols:
        df[col] = (
            pd.to_numeric(
                df[col]
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False),
                errors="coerce",
            ).fillna(0)
        )

    # Tenta usar coluna de total já existente; senão soma os meses
    total_col = _find_column(df.columns, TOTAL_CANDIDATES)
    if total_col:
        logger.debug("Usando coluna de total existente: '%s'", total_col)
        df["quantidade"] = df[total_col]
    else:
        # Exclui possíveis colunas de total/ano não mapeadas e soma o restante
        df["quantidade"] = df[numeric_cols].sum(axis=1)
        logger.debug("Coluna de total não encontrada; somando colunas: %s", numeric_cols)

    # Filtra apenas linhas com ROUBO ou FURTO
    mask = df[natureza_col].str.upper().str.contains("|".join(CRIME_KEYWORDS), na=False)
    filtered = df[mask].copy()

    if filtered.empty:
        logger.warning("Nenhum registro de roubo/furto encontrado na planilha.")

    result = [
        {"natureza": str(row[natureza_col]), "quantidade": int(row["quantidade"])}
        for _, row in filtered.iterrows()
    ]

    logger.info("Registros encontrados (roubo/furto): %d", len(result))
    return result
