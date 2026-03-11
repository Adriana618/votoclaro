"""15 quiz questions for ideological affinity calculation.

Each question maps to one or more ideological dimensions.
Answers use a 1-5 Likert scale:
  1 = Totalmente en desacuerdo
  2 = En desacuerdo
  3 = Neutral
  4 = De acuerdo
  5 = Totalmente de acuerdo

The mapping indicates how a high answer (agree) maps to each dimension:
  positive value = agreeing pushes toward right/conservative/authoritarian
  negative value = agreeing pushes toward left/progressive/libertarian
"""

QUIZ_QUESTIONS: list[dict] = [
    {
        "id": "q1",
        "text": "El Estado deberia controlar los precios de los productos basicos.",
        "category": "economy",
        "mapping": {"economy": -1},
    },
    {
        "id": "q2",
        "text": "Las empresas privadas son mas eficientes que las estatales.",
        "category": "economy",
        "mapping": {"economy": 1},
    },
    {
        "id": "q3",
        "text": "El matrimonio igualitario deberia ser legal en Peru.",
        "category": "social",
        "mapping": {"social": -1},
    },
    {
        "id": "q4",
        "text": "La educacion sexual integral debe ensenarse en los colegios.",
        "category": "social",
        "mapping": {"social": -1},
    },
    {
        "id": "q5",
        "text": "Se necesita mano dura contra la delincuencia, incluyendo pena de muerte.",
        "category": "authority",
        "mapping": {"authority": 1},
    },
    {
        "id": "q6",
        "text": "Las Fuerzas Armadas deberian tener mas poder para combatir el crimen.",
        "category": "authority",
        "mapping": {"authority": 1},
    },
    {
        "id": "q7",
        "text": "La mineria es mas importante que la proteccion del medio ambiente.",
        "category": "environment",
        "mapping": {"environment": 1},
    },
    {
        "id": "q8",
        "text": "Los politicos investigados por corrupcion no deberian poder postular.",
        "category": "corruption",
        "mapping": {"corruption": -1},
    },
    {
        "id": "q9",
        "text": "El Peru necesita mas inversion extranjera, aunque sea en recursos naturales.",
        "category": "economy",
        "mapping": {"economy": 1, "environment": 1},
    },
    {
        "id": "q10",
        "text": "Las comunidades campesinas deben tener derecho a veto sobre proyectos mineros en su territorio.",
        "category": "environment",
        "mapping": {"environment": -1, "authority": -1},
    },
    {
        "id": "q11",
        "text": "La descentralizacion ha fracasado y Lima debe retomar el control.",
        "category": "authority",
        "mapping": {"authority": 1},
    },
    {
        "id": "q12",
        "text": "El aborto deberia ser legal en mas circunstancias de las actuales.",
        "category": "social",
        "mapping": {"social": -1},
    },
    {
        "id": "q13",
        "text": "Los programas sociales como Pension 65 o Juntos deben ampliarse.",
        "category": "economy",
        "mapping": {"economy": -1},
    },
    {
        "id": "q14",
        "text": "La Constitucion de 1993 debe ser reemplazada por una nueva.",
        "category": "authority",
        "mapping": {"authority": -1, "economy": -1},
    },
    {
        "id": "q15",
        "text": "Es mas importante generar empleo que proteger los derechos laborales.",
        "category": "economy",
        "mapping": {"economy": 1, "social": 1},
    },
]
