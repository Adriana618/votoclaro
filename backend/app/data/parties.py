"""All party data with ideological positions.

Each party has positions on a -2 to +2 scale for each dimension:
  -2 = strongly left/progressive/libertarian
  +2 = strongly right/conservative/authoritarian
  0  = centrist / no clear position

Dimensions:
  economy: left(-2) to right(+2)
  social: progressive(-2) to conservative(+2)
  authority: libertarian(-2) to authoritarian(+2)
  corruption: clean(-2) to questionable(+2)
  environment: green(-2) to extractivist(+2)
"""

PARTIES: dict[str, dict] = {
    "rp": {
        "abbreviation": "rp",
        "name": "Renovacion Popular",
        "leader": "Rafael Lopez Aliaga",
        "color": "#1B3A6B",
        "positions": {
            "economy": 2,
            "social": 2,
            "authority": 1,
            "corruption": 0,
            "environment": 1,
        },
        "notable_figures": [
            {"name": "Rafael Lopez Aliaga", "nickname": "Porky", "role": "Alcalde de Lima, lider del partido"},
        ],
    },
    "fp": {
        "abbreviation": "fp",
        "name": "Fuerza Popular",
        "leader": "Keiko Fujimori",
        "color": "#FF6B00",
        "positions": {
            "economy": 1,
            "social": 1,
            "authority": 2,
            "corruption": 2,
            "environment": 1,
        },
        "notable_figures": [
            {"name": "Keiko Fujimori", "nickname": "Keiko", "role": "Lider del partido, 3 veces candidata presidencial"},
            {"name": "Alberto Fujimori", "nickname": "El Chino", "role": "Expresidente (1990-2000), fallecido"},
        ],
    },
    "pm": {
        "abbreviation": "pm",
        "name": "Partido Morado",
        "leader": "Julio Guzman",
        "color": "#7B2D8E",
        "positions": {
            "economy": 0,
            "social": -1,
            "authority": -1,
            "corruption": -2,
            "environment": -1,
        },
        "notable_figures": [
            {"name": "Julio Guzman", "nickname": None, "role": "Fundador, excandidato presidencial"},
        ],
    },
    "jpp": {
        "abbreviation": "jpp",
        "name": "Juntos por el Peru",
        "leader": "Roberto Sanchez",
        "color": "#D32F2F",
        "positions": {
            "economy": -2,
            "social": -1,
            "authority": 0,
            "corruption": 0,
            "environment": -1,
        },
        "notable_figures": [
            {"name": "Roberto Sanchez", "nickname": None, "role": "Excanciller del gobierno de Castillo"},
            {"name": "Veronika Mendoza", "nickname": "Vero", "role": "Excongresista, lider historica de la izquierda"},
        ],
    },
    "ap": {
        "abbreviation": "ap",
        "name": "Accion Popular",
        "leader": "Varios",
        "color": "#4CAF50",
        "positions": {
            "economy": 0,
            "social": 0,
            "authority": 0,
            "corruption": 1,
            "environment": 0,
        },
        "notable_figures": [
            {"name": "Edmundo del Aguila", "nickname": None, "role": "Exsecretario general"},
        ],
    },
    "sc": {
        "abbreviation": "sc",
        "name": "Somos Peru",
        "leader": "Varios",
        "color": "#00BCD4",
        "positions": {
            "economy": 0,
            "social": 0,
            "authority": 0,
            "corruption": 1,
            "environment": 0,
        },
        "notable_figures": [],
    },
    "pl": {
        "abbreviation": "pl",
        "name": "Peru Libre",
        "leader": "Vladimir Cerron",
        "color": "#B71C1C",
        "positions": {
            "economy": -2,
            "social": 1,
            "authority": 2,
            "corruption": 2,
            "environment": 0,
        },
        "notable_figures": [
            {"name": "Vladimir Cerron", "nickname": None, "role": "Fundador, profugo de la justicia"},
            {"name": "Pedro Castillo", "nickname": "El Profe", "role": "Expresidente (2021-2022), preso por golpe de estado"},
        ],
    },
    "an": {
        "abbreviation": "an",
        "name": "Alianza Nacional",
        "leader": "Varios",
        "color": "#3F51B5",
        "positions": {
            "economy": 1,
            "social": 1,
            "authority": 1,
            "corruption": 0,
            "environment": 1,
        },
        "notable_figures": [],
    },
    "app": {
        "abbreviation": "app",
        "name": "Alianza Para el Progreso",
        "leader": "Cesar Acuna",
        "color": "#009688",
        "positions": {
            "economy": 1,
            "social": 0,
            "authority": 1,
            "corruption": 2,
            "environment": 1,
        },
        "notable_figures": [
            {"name": "Cesar Acuna", "nickname": "Plata como cancha", "role": "Gobernador de La Libertad, fundador UCV"},
        ],
    },
    "pod": {
        "abbreviation": "pod",
        "name": "Podemos Peru",
        "leader": "Jose Luna",
        "color": "#E91E63",
        "positions": {
            "economy": 0,
            "social": 0,
            "authority": 1,
            "corruption": 2,
            "environment": 0,
        },
        "notable_figures": [
            {"name": "Jose Luna Galvez", "nickname": None, "role": "Fundador de Telesup, investigado por corrupcion"},
            {"name": "Daniel Urresti", "nickname": None, "role": "Ex candidato a Lima, general retirado"},
        ],
    },
    "fep": {
        "abbreviation": "fep",
        "name": "Frente Esperanza",
        "leader": "Fernando Olivera",
        "color": "#795548",
        "positions": {
            "economy": 1,
            "social": 2,
            "authority": 1,
            "corruption": 1,
            "environment": 0,
        },
        "notable_figures": [
            {"name": "Fernando Olivera", "nickname": None, "role": "Excongresista, lider historico del FIM"},
        ],
    },
    "avp": {
        "abbreviation": "avp",
        "name": "Avanza Pais",
        "leader": "Aldo Borrero",
        "color": "#FF9800",
        "positions": {
            "economy": 2,
            "social": 1,
            "authority": 0,
            "corruption": 0,
            "environment": 1,
        },
        "notable_figures": [
            {"name": "Hernando de Soto", "nickname": None, "role": "Economista, excandidato presidencial 2021"},
        ],
    },
    # === Partidos adicionales (elecciones 2026) ===
    "apra": {
        "abbreviation": "apra",
        "name": "Partido Aprista Peruano",
        "leader": "Varios",
        "color": "#C62828",
        "positions": {"economy": 0, "social": 0, "authority": 1, "corruption": 1, "environment": 0},
        "notable_figures": [
            {"name": "Alan Garcia", "nickname": "El Caballo Loco", "role": "Expresidente (1985-1990, 2006-2011), fallecido"},
        ],
    },
    "venc": {
        "abbreviation": "venc",
        "name": "Alianza Electoral Venceremos",
        "leader": "Varios",
        "color": "#6A1B9A",
        "positions": {"economy": -1, "social": -1, "authority": 0, "corruption": 0, "environment": -1},
    },
    "cp": {
        "abbreviation": "cp",
        "name": "Cooperacion Popular",
        "leader": "Varios",
        "color": "#1565C0",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "pte": {
        "abbreviation": "pte",
        "name": "PTE Peru",
        "leader": "Varios",
        "color": "#2E7D32",
        "positions": {"economy": -1, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "fyl": {
        "abbreviation": "fyl",
        "name": "Fuerza y Libertad",
        "leader": "Varios",
        "color": "#0D47A1",
        "positions": {"economy": 2, "social": 1, "authority": 0, "corruption": -1, "environment": 1},
    },
    "un": {
        "abbreviation": "un",
        "name": "Unidad Nacional",
        "leader": "Varios",
        "color": "#004D40",
        "positions": {"economy": 1, "social": 1, "authority": 0, "corruption": -1, "environment": 0},
    },
    "ppt": {
        "abbreviation": "ppt",
        "name": "Pais Para Todos",
        "leader": "Varios",
        "color": "#F57F17",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "pdup": {
        "abbreviation": "pdup",
        "name": "Democrata Unido Peru",
        "leader": "Varios",
        "color": "#5D4037",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "id": {
        "abbreviation": "id",
        "name": "Integridad Democratica",
        "leader": "Varios",
        "color": "#37474F",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": -1, "environment": 0},
    },
    "ucd": {
        "abbreviation": "ucd",
        "name": "Un Camino Diferente",
        "leader": "Varios",
        "color": "#00838F",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "pp": {
        "abbreviation": "pp",
        "name": "Peru Primero",
        "leader": "Varios",
        "color": "#AD1457",
        "positions": {"economy": 1, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "lp": {
        "abbreviation": "lp",
        "name": "Libertad Popular",
        "leader": "Varios",
        "color": "#EF6C00",
        "positions": {"economy": 1, "social": 0, "authority": -1, "corruption": 0, "environment": 0},
    },
    "pa": {
        "abbreviation": "pa",
        "name": "Peru Accion",
        "leader": "Varios",
        "color": "#558B2F",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "pdv": {
        "abbreviation": "pdv",
        "name": "Democrata Verde",
        "leader": "Varios",
        "color": "#2E7D32",
        "positions": {"economy": 0, "social": -1, "authority": -1, "corruption": -1, "environment": -2},
    },
    "frepap": {
        "abbreviation": "frepap",
        "name": "FREPAP",
        "leader": "Varios",
        "color": "#4E342E",
        "positions": {"economy": -1, "social": 2, "authority": 1, "corruption": 0, "environment": 0},
    },
    "prog": {
        "abbreviation": "prog",
        "name": "Progresemos",
        "leader": "Varios",
        "color": "#00695C",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "pbg": {
        "abbreviation": "pbg",
        "name": "Partido del Buen Gobierno",
        "leader": "Varios",
        "color": "#33691E",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": -1, "environment": 0},
    },
    "prin": {
        "abbreviation": "prin",
        "name": "PRIN",
        "leader": "Varios",
        "color": "#827717",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "obras": {
        "abbreviation": "obras",
        "name": "Civico Obras",
        "leader": "Varios",
        "color": "#FF8F00",
        "positions": {"economy": 1, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "plg": {
        "abbreviation": "plg",
        "name": "Primero la Gente",
        "leader": "Varios",
        "color": "#00BFA5",
        "positions": {"economy": 0, "social": -1, "authority": -1, "corruption": -1, "environment": -1},
    },
    "pdf": {
        "abbreviation": "pdf",
        "name": "Democratico Federal",
        "leader": "Varios",
        "color": "#283593",
        "positions": {"economy": 0, "social": 0, "authority": -1, "corruption": 0, "environment": 0},
    },
    "salv": {
        "abbreviation": "salv",
        "name": "Salvemos al Peru",
        "leader": "Varios",
        "color": "#D84315",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": -1, "environment": 0},
    },
    "ppp": {
        "abbreviation": "ppp",
        "name": "Partido Patriotico del Peru",
        "leader": "Varios",
        "color": "#BF360C",
        "positions": {"economy": 0, "social": 1, "authority": 1, "corruption": 0, "environment": 0},
    },
    "fep2": {
        "abbreviation": "fep2",
        "name": "Fe en el Peru",
        "leader": "Varios",
        "color": "#4527A0",
        "positions": {"economy": 0, "social": 1, "authority": 0, "corruption": 0, "environment": 0},
    },
    "pmod": {
        "abbreviation": "pmod",
        "name": "Peru Moderno",
        "leader": "Varios",
        "color": "#0277BD",
        "positions": {"economy": 1, "social": -1, "authority": -1, "corruption": -1, "environment": -1},
    },
    "sicreo": {
        "abbreviation": "sicreo",
        "name": "Sicreo",
        "leader": "Varios",
        "color": "#6D4C41",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
    "cpp": {
        "abbreviation": "cpp",
        "name": "Ciudadanos por el Peru",
        "leader": "Varios",
        "color": "#546E7A",
        "positions": {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0},
    },
}

# Mapping from abbreviation to full name for quick lookup
PARTY_NAMES: dict[str, str] = {k: v["name"] for k, v in PARTIES.items()}

# General ideological positions (for internal reference, not quiz matching)
# Quiz matching uses PARTY_POSITIONS from quiz_questions.py instead
PARTY_IDEOLOGICAL_POSITIONS: dict[str, dict[str, int]] = {
    k: v["positions"] for k, v in PARTIES.items()
}
