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
    },
}

# Mapping from abbreviation to full name for quick lookup
PARTY_NAMES: dict[str, str] = {k: v["name"] for k, v in PARTIES.items()}

# General ideological positions (for internal reference, not quiz matching)
# Quiz matching uses PARTY_POSITIONS from quiz_questions.py instead
PARTY_IDEOLOGICAL_POSITIONS: dict[str, dict[str, int]] = {
    k: v["positions"] for k, v in PARTIES.items()
}
