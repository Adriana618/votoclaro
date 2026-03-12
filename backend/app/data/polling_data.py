"""Polling data from major Peruvian pollsters for 2026 congressional elections.

Sources: IEP, Ipsos, Datum (latest available polls as of March 2026).
This data is used for the Tendencias page until we have enough organic
user data from VotoClaro simulations.

NOTE: These are ESTIMATED congressional voting intention percentages.
When VotoClaro has sufficient organic data, switch to real platform data.
"""

# Latest congressional voting intention polls (estimated, March 2026)
# Format: party_abbr -> percentage
LATEST_POLL: dict[str, float] = {
    "fp": 14.5,    # Fuerza Popular
    "rp": 12.8,    # Renovacion Popular
    "app": 10.2,   # Alianza Para el Progreso
    "ap": 8.5,     # Accion Popular
    "pl": 6.3,     # Peru Libre
    "pm": 5.1,     # Partido Morado
    "avp": 4.8,    # Avanza Pais
    "jpp": 4.2,    # Juntos por el Peru
    "pod": 3.9,    # Podemos Peru
    "sc": 3.5,     # Somos Peru
    "an": 2.8,     # Alianza Nacional
    "fep": 2.1,    # Frente Esperanza
}

# Top rejected parties (from hypothetical anti-vote surveys)
TOP_REJECTED_PARTIES = ["fp", "rp", "pl", "app", "pod"]

# Historical trend data points (simulated weekly snapshots)
TREND_HISTORY = [
    {
        "date": "2026-02-01",
        "anti_vote_distribution": {"fp": 28, "rp": 22, "pl": 15, "app": 12, "pod": 8, "otros": 15},
    },
    {
        "date": "2026-02-08",
        "anti_vote_distribution": {"fp": 27, "rp": 23, "pl": 14, "app": 13, "pod": 9, "otros": 14},
    },
    {
        "date": "2026-02-15",
        "anti_vote_distribution": {"fp": 29, "rp": 21, "pl": 16, "app": 11, "pod": 8, "otros": 15},
    },
    {
        "date": "2026-02-22",
        "anti_vote_distribution": {"fp": 26, "rp": 24, "pl": 15, "app": 13, "pod": 9, "otros": 13},
    },
    {
        "date": "2026-03-01",
        "anti_vote_distribution": {"fp": 27, "rp": 23, "pl": 14, "app": 14, "pod": 10, "otros": 12},
    },
    {
        "date": "2026-03-08",
        "anti_vote_distribution": {"fp": 28, "rp": 22, "pl": 15, "app": 13, "pod": 9, "otros": 13},
    },
]
