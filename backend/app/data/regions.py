"""Peru regions with seat counts for the 2026 bicameral congress.

Senado: 60 senators elected in a single national district.
Diputados: 130 representatives distributed by region based on population.
"""

# National senate configuration
SENATE_SEATS = 60

# Regions with seats for Camara de Diputados (130 total)
REGIONS: list[dict] = [
    {"name": "Amazonas", "slug": "amazonas", "seats_diputados": 2, "department_code": "AMA"},
    {"name": "Ancash", "slug": "ancash", "seats_diputados": 5, "department_code": "ANC"},
    {"name": "Apurimac", "slug": "apurimac", "seats_diputados": 2, "department_code": "APU"},
    {"name": "Arequipa", "slug": "arequipa", "seats_diputados": 6, "department_code": "ARE"},
    {"name": "Ayacucho", "slug": "ayacucho", "seats_diputados": 3, "department_code": "AYA"},
    {"name": "Cajamarca", "slug": "cajamarca", "seats_diputados": 6, "department_code": "CAJ"},
    {"name": "Callao", "slug": "callao", "seats_diputados": 4, "department_code": "CAL"},
    {"name": "Cusco", "slug": "cusco", "seats_diputados": 5, "department_code": "CUS"},
    {"name": "Huancavelica", "slug": "huancavelica", "seats_diputados": 2, "department_code": "HUV"},
    {"name": "Huanuco", "slug": "huanuco", "seats_diputados": 3, "department_code": "HUA"},
    {"name": "Ica", "slug": "ica", "seats_diputados": 4, "department_code": "ICA"},
    {"name": "Junin", "slug": "junin", "seats_diputados": 5, "department_code": "JUN"},
    {"name": "La Libertad", "slug": "la-libertad", "seats_diputados": 7, "department_code": "LAL"},
    {"name": "Lambayeque", "slug": "lambayeque", "seats_diputados": 5, "department_code": "LAM"},
    {"name": "Lima Provincias", "slug": "lima-provincias", "seats_diputados": 4, "department_code": "LPR"},
    {"name": "Lima Metropolitana", "slug": "lima", "seats_diputados": 36, "department_code": "LIM"},
    {"name": "Loreto", "slug": "loreto", "seats_diputados": 3, "department_code": "LOR"},
    {"name": "Madre de Dios", "slug": "madre-de-dios", "seats_diputados": 1, "department_code": "MDD"},
    {"name": "Moquegua", "slug": "moquegua", "seats_diputados": 2, "department_code": "MOQ"},
    {"name": "Pasco", "slug": "pasco", "seats_diputados": 2, "department_code": "PAS"},
    {"name": "Piura", "slug": "piura", "seats_diputados": 7, "department_code": "PIU"},
    {"name": "Puno", "slug": "puno", "seats_diputados": 5, "department_code": "PUN"},
    {"name": "San Martin", "slug": "san-martin", "seats_diputados": 3, "department_code": "SAM"},
    {"name": "Tacna", "slug": "tacna", "seats_diputados": 2, "department_code": "TAC"},
    {"name": "Tumbes", "slug": "tumbes", "seats_diputados": 2, "department_code": "TUM"},
    {"name": "Ucayali", "slug": "ucayali", "seats_diputados": 2, "department_code": "UCA"},
    {"name": "Peruanos en el Extranjero", "slug": "extranjero", "seats_diputados": 2, "department_code": "EXT"},
]

# Verify total seats
assert sum(r["seats_diputados"] for r in REGIONS) == 130, "Diputados seats must total 130"
