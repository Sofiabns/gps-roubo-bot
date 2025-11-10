def filter_by_area(data, target_municipio, radius_km=None):
    """
    Fallback: se data apenas com municípios, filtra por município.
    Se houver lat/lon, pode usar raio.
    """
    filtered = []
    for item in data:
        municipio = item.get("municipio")
        if municipio and municipio.lower() == target_municipio.lower():
            filtered.append(item)
    return filtered
