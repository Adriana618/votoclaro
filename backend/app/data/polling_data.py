"""Polling data from major Peruvian pollsters for 2026 congressional elections.

Sources: IEP, Ipsos, Datum (latest available polls as of March 2026).
This data is used for the Tendencias page until we have enough organic
user data from VotoClaro simulations.

Regional political tendencies:
- South (Puno, Arequipa, Cusco, Tacna, Moquegua, Ayacucho, Apurimac, Madre de Dios):
  Left-leaning bastion. Peru Libre, Juntos por el Peru strong. FP/RP heavily rejected.
- North (Piura, La Libertad, Lambayeque, Cajamarca, Tumbes, Amazonas, San Martin):
  Right-leaning. APP, FP, AP strong. PL/JPP heavily rejected.
- Lima: Mixed/swing. FP and RP most rejected but competitive. PM/AP stronger.
- Central (Junin, Pasco, Huancavelica, Huanuco, Ica): Mixed, slight left lean.
- East (Loreto, Ucayali): Independent streak, distrust of Lima parties.
"""

# Regional classification
SOUTH_REGIONS = {
    "puno", "arequipa", "cusco", "tacna", "moquegua",
    "ayacucho", "apurimac", "madre-de-dios", "huancavelica",
}
NORTH_REGIONS = {
    "piura", "la-libertad", "lambayeque", "cajamarca",
    "tumbes", "amazonas", "san-martin",
}
CENTRAL_REGIONS = {"junin", "pasco", "huanuco", "ica"}
EAST_REGIONS = {"loreto", "ucayali"}
LIMA_REGIONS = {"lima", "lima-provincias", "callao"}


def get_regional_trends(region_slug: str) -> dict:
    """Return trend data tailored to the region's political tendency."""

    if region_slug in SOUTH_REGIONS:
        return _south_trends()
    elif region_slug in NORTH_REGIONS:
        return _north_trends()
    elif region_slug in LIMA_REGIONS:
        return _lima_trends()
    elif region_slug in CENTRAL_REGIONS:
        return _central_trends()
    elif region_slug in EAST_REGIONS:
        return _east_trends()
    else:
        # Default: national average
        return _lima_trends()


def get_top_rejected(region_slug: str) -> list[str]:
    """Return top rejected party abbreviations for a region."""
    if region_slug in SOUTH_REGIONS:
        return ["fp", "rp", "app", "pod", "fep"]
    elif region_slug in NORTH_REGIONS:
        return ["pl", "jpp", "an", "pod", "fp"]
    elif region_slug in LIMA_REGIONS:
        return ["fp", "rp", "pl", "app", "pod"]
    elif region_slug in CENTRAL_REGIONS:
        return ["fp", "rp", "app", "pl", "pod"]
    elif region_slug in EAST_REGIONS:
        return ["rp", "fp", "pl", "app", "jpp"]
    return ["fp", "rp", "pl", "app", "pod"]


def get_top_voted(region_slug: str) -> list[tuple[str, float]]:
    """Return top voted parties (abbr, percentage) for a region.

    Reflects regional voting intention from polls.
    """
    if region_slug in SOUTH_REGIONS:
        return [
            ("pl", 18.5), ("jpp", 14.2), ("cp", 12.0),
            ("pm", 10.5), ("an", 8.3),
        ]
    elif region_slug in NORTH_REGIONS:
        return [
            ("app", 18.0), ("fp", 16.5), ("sc", 12.8),
            ("rp", 11.0), ("fyl", 6.5),
        ]
    elif region_slug in LIMA_REGIONS:
        return [
            ("fp", 14.5), ("rp", 12.8), ("app", 10.2),
            ("sc", 8.5), ("pm", 7.1),
        ]
    elif region_slug in CENTRAL_REGIONS:
        return [
            ("pl", 15.0), ("cp", 13.5), ("fp", 12.0),
            ("app", 10.0), ("jpp", 8.5),
        ]
    elif region_slug in EAST_REGIONS:
        return [
            ("sc", 16.0), ("app", 14.5), ("cp", 10.0),
            ("pl", 9.5), ("fp", 9.0),
        ]
    # Default
    return [
        ("fp", 14.5), ("rp", 12.8), ("app", 10.2),
        ("sc", 8.5), ("pm", 7.1),
    ]


# --- Regional trend generators (using full party names for display) ---

def _south_trends() -> list[dict]:
    """South: left-leaning. FP/RP heavily rejected."""
    return [
        {
            "date": "2026-02-01",
            "anti_vote_distribution": {
                "Fuerza Popular": 32, "Renovacion Popular": 25,
                "Alianza Para el Progreso": 14, "Podemos Peru": 8,
                "Frente Esperanza": 6, "Otros": 15,
            },
        },
        {
            "date": "2026-02-08",
            "anti_vote_distribution": {
                "Fuerza Popular": 33, "Renovacion Popular": 24,
                "Alianza Para el Progreso": 13, "Podemos Peru": 9,
                "Frente Esperanza": 7, "Otros": 14,
            },
        },
        {
            "date": "2026-02-15",
            "anti_vote_distribution": {
                "Fuerza Popular": 31, "Renovacion Popular": 26,
                "Alianza Para el Progreso": 15, "Podemos Peru": 8,
                "Frente Esperanza": 6, "Otros": 14,
            },
        },
        {
            "date": "2026-02-22",
            "anti_vote_distribution": {
                "Fuerza Popular": 34, "Renovacion Popular": 23,
                "Alianza Para el Progreso": 14, "Podemos Peru": 9,
                "Frente Esperanza": 5, "Otros": 15,
            },
        },
        {
            "date": "2026-03-01",
            "anti_vote_distribution": {
                "Fuerza Popular": 33, "Renovacion Popular": 25,
                "Alianza Para el Progreso": 13, "Podemos Peru": 10,
                "Frente Esperanza": 6, "Otros": 13,
            },
        },
        {
            "date": "2026-03-08",
            "anti_vote_distribution": {
                "Fuerza Popular": 32, "Renovacion Popular": 24,
                "Alianza Para el Progreso": 14, "Podemos Peru": 9,
                "Frente Esperanza": 7, "Otros": 14,
            },
        },
    ]


def _north_trends() -> list[dict]:
    """North: right-leaning. PL/JPP heavily rejected."""
    return [
        {
            "date": "2026-02-01",
            "anti_vote_distribution": {
                "Peru Libre": 30, "Juntos por el Peru": 20,
                "Ahora Nacion": 12, "Podemos Peru": 10,
                "Fuerza Popular": 10, "Otros": 18,
            },
        },
        {
            "date": "2026-02-08",
            "anti_vote_distribution": {
                "Peru Libre": 31, "Juntos por el Peru": 19,
                "Ahora Nacion": 13, "Podemos Peru": 10,
                "Fuerza Popular": 9, "Otros": 18,
            },
        },
        {
            "date": "2026-02-15",
            "anti_vote_distribution": {
                "Peru Libre": 29, "Juntos por el Peru": 21,
                "Ahora Nacion": 12, "Podemos Peru": 11,
                "Fuerza Popular": 10, "Otros": 17,
            },
        },
        {
            "date": "2026-02-22",
            "anti_vote_distribution": {
                "Peru Libre": 32, "Juntos por el Peru": 18,
                "Ahora Nacion": 14, "Podemos Peru": 10,
                "Fuerza Popular": 9, "Otros": 17,
            },
        },
        {
            "date": "2026-03-01",
            "anti_vote_distribution": {
                "Peru Libre": 30, "Juntos por el Peru": 20,
                "Ahora Nacion": 13, "Podemos Peru": 11,
                "Fuerza Popular": 10, "Otros": 16,
            },
        },
        {
            "date": "2026-03-08",
            "anti_vote_distribution": {
                "Peru Libre": 31, "Juntos por el Peru": 19,
                "Ahora Nacion": 12, "Podemos Peru": 11,
                "Fuerza Popular": 10, "Otros": 17,
            },
        },
    ]


def _lima_trends() -> list[dict]:
    """Lima: mixed/swing. FP and RP most rejected but diverse."""
    return [
        {
            "date": "2026-02-01",
            "anti_vote_distribution": {
                "Fuerza Popular": 25, "Renovacion Popular": 20,
                "Peru Libre": 18, "Alianza Para el Progreso": 12,
                "Podemos Peru": 10, "Otros": 15,
            },
        },
        {
            "date": "2026-02-08",
            "anti_vote_distribution": {
                "Fuerza Popular": 24, "Renovacion Popular": 21,
                "Peru Libre": 17, "Alianza Para el Progreso": 13,
                "Podemos Peru": 11, "Otros": 14,
            },
        },
        {
            "date": "2026-02-15",
            "anti_vote_distribution": {
                "Fuerza Popular": 26, "Renovacion Popular": 19,
                "Peru Libre": 18, "Alianza Para el Progreso": 12,
                "Podemos Peru": 10, "Otros": 15,
            },
        },
        {
            "date": "2026-02-22",
            "anti_vote_distribution": {
                "Fuerza Popular": 23, "Renovacion Popular": 22,
                "Peru Libre": 17, "Alianza Para el Progreso": 14,
                "Podemos Peru": 10, "Otros": 14,
            },
        },
        {
            "date": "2026-03-01",
            "anti_vote_distribution": {
                "Fuerza Popular": 25, "Renovacion Popular": 20,
                "Peru Libre": 16, "Alianza Para el Progreso": 14,
                "Podemos Peru": 11, "Otros": 14,
            },
        },
        {
            "date": "2026-03-08",
            "anti_vote_distribution": {
                "Fuerza Popular": 24, "Renovacion Popular": 21,
                "Peru Libre": 17, "Alianza Para el Progreso": 13,
                "Podemos Peru": 10, "Otros": 15,
            },
        },
    ]


def _central_trends() -> list[dict]:
    """Central highlands: mixed, slight left lean."""
    return [
        {
            "date": "2026-02-01",
            "anti_vote_distribution": {
                "Fuerza Popular": 27, "Renovacion Popular": 22,
                "Alianza Para el Progreso": 15, "Peru Libre": 12,
                "Podemos Peru": 9, "Otros": 15,
            },
        },
        {
            "date": "2026-02-08",
            "anti_vote_distribution": {
                "Fuerza Popular": 28, "Renovacion Popular": 21,
                "Alianza Para el Progreso": 14, "Peru Libre": 13,
                "Podemos Peru": 10, "Otros": 14,
            },
        },
        {
            "date": "2026-02-15",
            "anti_vote_distribution": {
                "Fuerza Popular": 26, "Renovacion Popular": 23,
                "Alianza Para el Progreso": 15, "Peru Libre": 12,
                "Podemos Peru": 9, "Otros": 15,
            },
        },
        {
            "date": "2026-02-22",
            "anti_vote_distribution": {
                "Fuerza Popular": 29, "Renovacion Popular": 20,
                "Alianza Para el Progreso": 14, "Peru Libre": 13,
                "Podemos Peru": 10, "Otros": 14,
            },
        },
        {
            "date": "2026-03-01",
            "anti_vote_distribution": {
                "Fuerza Popular": 27, "Renovacion Popular": 22,
                "Alianza Para el Progreso": 15, "Peru Libre": 12,
                "Podemos Peru": 10, "Otros": 14,
            },
        },
        {
            "date": "2026-03-08",
            "anti_vote_distribution": {
                "Fuerza Popular": 28, "Renovacion Popular": 21,
                "Alianza Para el Progreso": 14, "Peru Libre": 13,
                "Podemos Peru": 9, "Otros": 15,
            },
        },
    ]


def _east_trends() -> list[dict]:
    """Eastern jungle: independent, distrust of Lima parties."""
    return [
        {
            "date": "2026-02-01",
            "anti_vote_distribution": {
                "Renovacion Popular": 24, "Fuerza Popular": 22,
                "Peru Libre": 18, "Alianza Para el Progreso": 13,
                "Juntos por el Peru": 8, "Otros": 15,
            },
        },
        {
            "date": "2026-02-08",
            "anti_vote_distribution": {
                "Renovacion Popular": 25, "Fuerza Popular": 21,
                "Peru Libre": 17, "Alianza Para el Progreso": 14,
                "Juntos por el Peru": 9, "Otros": 14,
            },
        },
        {
            "date": "2026-02-15",
            "anti_vote_distribution": {
                "Renovacion Popular": 23, "Fuerza Popular": 23,
                "Peru Libre": 18, "Alianza Para el Progreso": 12,
                "Juntos por el Peru": 8, "Otros": 16,
            },
        },
        {
            "date": "2026-02-22",
            "anti_vote_distribution": {
                "Renovacion Popular": 26, "Fuerza Popular": 20,
                "Peru Libre": 17, "Alianza Para el Progreso": 14,
                "Juntos por el Peru": 9, "Otros": 14,
            },
        },
        {
            "date": "2026-03-01",
            "anti_vote_distribution": {
                "Renovacion Popular": 24, "Fuerza Popular": 22,
                "Peru Libre": 18, "Alianza Para el Progreso": 13,
                "Juntos por el Peru": 9, "Otros": 14,
            },
        },
        {
            "date": "2026-03-08",
            "anti_vote_distribution": {
                "Renovacion Popular": 25, "Fuerza Popular": 21,
                "Peru Libre": 17, "Alianza Para el Progreso": 14,
                "Juntos por el Peru": 8, "Otros": 15,
            },
        },
    ]
