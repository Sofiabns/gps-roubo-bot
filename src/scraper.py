"""
scraper.py — Filtragem geográfica de ocorrências.

Fornece funções para filtrar registros por município e, opcionalmente,
por raio geográfico usando coordenadas lat/lon (requer geopy).
"""

import logging
import math
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers de distância
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula a distância em km entre dois pontos (fórmula de Haversine)."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# Filtros públicos
# ---------------------------------------------------------------------------

def filter_by_area(
    data: list[dict],
    target_municipio: str,
    radius_km: Optional[float] = None,
    center_lat: Optional[float] = None,
    center_lon: Optional[float] = None,
) -> list[dict]:
    """
    Filtra ocorrências por município e, opcionalmente, por raio geográfico.

    Parâmetros
    ----------
    data : list[dict]
        Lista de ocorrências retornada por ``get_ssp_sp_data``.
    target_municipio : str
        Nome do município de interesse (comparação case-insensitive).
    radius_km : float, opcional
        Raio em quilômetros. Requer ``center_lat`` e ``center_lon`` e que
        cada item de ``data`` possua as chaves ``lat`` e ``lon``.
    center_lat : float, opcional
        Latitude do ponto central para o filtro por raio.
    center_lon : float, opcional
        Longitude do ponto central para o filtro por raio.

    Retorna
    -------
    list[dict]
        Subconjunto de ``data`` que satisfaz os critérios.
    """
    if not target_municipio:
        logger.debug("Nenhum município configurado; retornando todos os registros.")
        return data

    target_lower = target_municipio.strip().lower()
    filtered = [
        item for item in data
        if str(item.get("municipio", "")).strip().lower() == target_lower
    ]
    logger.debug(
        "filter_by_area: %d/%d registros para município '%s'",
        len(filtered), len(data), target_municipio,
    )

    # Filtro adicional por raio, se todos os parâmetros estiverem presentes
    if radius_km and center_lat is not None and center_lon is not None:
        geo_filtered = []
        for item in filtered:
            lat = item.get("lat")
            lon = item.get("lon")
            if lat is None or lon is None:
                continue
            dist = _haversine_km(center_lat, center_lon, float(lat), float(lon))
            if dist <= radius_km:
                geo_filtered.append({**item, "_distancia_km": round(dist, 2)})
        logger.debug(
            "Filtro por raio (%.1f km): %d registros", radius_km, len(geo_filtered)
        )
        return geo_filtered

    return filtered
