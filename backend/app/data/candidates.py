"""Datos de candidatos importados desde fuentes externas.

Generado automaticamente por scrapers/load_to_app.py el 2026-03-12.
Total de candidatos: 3
"""


# Candidatos indexados por ID interno
# Cada candidato tiene los campos del modelo Candidate mas datos adicionales
CANDIDATES: dict[int, dict] = {
    1: {
        "id": 1,
        "name": 'GARCIA LOPEZ, MARIA ELENA',
        "party_slug": 'fp',
        "region_slug": 'lima',
        "cargo": 'DIPUTADO',
        "position_number": 3,
        "has_criminal_record": False,
        "voted_pro_crime": False,
        "is_reelection": False,
        "investigations": 0,
        "controversy_score": 0.0,
        "party_changed_from": None,
        "jne_id": 'JNE-2026-001234',
        "foto_url": 'https://example.com/foto1.jpg',
        "hoja_vida_url": 'https://example.com/hv/001234',
        "educacion": 'Abogada - UNMSM',
        "experiencia_politica": 'Regidora 2019-2022',
    },
    2: {
        "id": 2,
        "name": 'QUISPE HUAMANI, PEDRO ROBERTO',
        "party_slug": 'rp',
        "region_slug": 'arequipa',
        "cargo": 'DIPUTADO',
        "position_number": 1,
        "has_criminal_record": True,
        "voted_pro_crime": False,
        "is_reelection": False,
        "investigations": 0,
        "controversy_score": 30.0,
        "party_changed_from": None,
        "jne_id": 'JNE-2026-005678',
        "foto_url": 'https://example.com/foto2.jpg',
        "hoja_vida_url": 'https://example.com/hv/005678',
        "educacion": 'Ingeniero Civil - UNSA',
        "experiencia_politica": 'Congresista 2021-2026',
    },
    3: {
        "id": 3,
        "name": 'TORRES MENDOZA, ANA LUCIA',
        "party_slug": 'pm',
        "region_slug": None,
        "cargo": 'SENADOR',
        "position_number": 5,
        "has_criminal_record": False,
        "voted_pro_crime": False,
        "is_reelection": False,
        "investigations": 0,
        "controversy_score": 0.0,
        "party_changed_from": None,
        "jne_id": 'JNE-2026-009012',
        "foto_url": None,
        "hoja_vida_url": 'https://example.com/hv/009012',
        "educacion": 'Economista - PUCP',
        "experiencia_politica": 'Directora SUNAT 2016-2018',
    },
}


# Indice por partido: {partido_slug: [candidate_ids]}
CANDIDATES_BY_PARTY: dict[str, list[int]] = {}
for _id, _c in CANDIDATES.items():
    _party = _c["party_slug"]
    if _party not in CANDIDATES_BY_PARTY:
        CANDIDATES_BY_PARTY[_party] = []
    CANDIDATES_BY_PARTY[_party].append(_id)


# Indice por region: {region_slug: [candidate_ids]}
CANDIDATES_BY_REGION: dict[str, list[int]] = {}
for _id, _c in CANDIDATES.items():
    _region = _c["region_slug"]
    if _region:
        if _region not in CANDIDATES_BY_REGION:
            CANDIDATES_BY_REGION[_region] = []
        CANDIDATES_BY_REGION[_region].append(_id)


# Estadisticas de la ultima importacion
IMPORT_STATS: dict = {   'buscando_reeleccion': 0,
    'con_antecedentes': 1,
    'con_investigaciones': 0,
    'con_sentencias': 1,
    'con_votos_pro_crimen': 0,
    'congresistas_sin_match': [],
    'investigaciones_sin_match': [],
    'matches_investigaciones': 0,
    'matches_votaciones': 0,
    'por_cargo': {'DIPUTADO': 2, 'SENADOR': 1},
    'por_partido': {'fp': 1, 'pm': 1, 'rp': 1},
    'por_region': {'arequipa': 1, 'lima': 1, 'nacional': 1},
    'score_max': 30.0,
    'score_promedio': 10.0,
    'total_candidatos': 3}
