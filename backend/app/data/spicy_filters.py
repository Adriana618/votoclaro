"""Spicy filter definitions for party/candidate listing.

Each filter lets users slice candidates and parties by controversial topics.
Designed for virality and engagement. Matches spec section 5.1 exactly.
"""

SPICY_FILTERS: list[dict] = [
    # --- SEGURIDAD ---
    {
        "id": "pro_crimen",
        "label": "🚔 Votaron leyes pro-crimen",
        "category": "seguridad",
        "description": "Congresistas que votaron 6+ veces a favor de leyes que debilitan la persecución del crimen",
        "source": "Convoca.pe / Ojo Público",
        "type": "candidates",
        "data_field": "voted_pro_crime",
    },
    {
        "id": "mano_dura",
        "label": "👊 Mano dura: militares en las calles",
        "category": "seguridad",
        "description": "Partidos que proponen estado de emergencia y militarización",
        "type": "parties",
        "parties": ["rp", "fp"],
    },
    # --- CORRUPCIÓN ---
    {
        "id": "antecedentes_penales",
        "label": "🚨 Con antecedentes penales",
        "category": "corrupcion",
        "description": "292 candidatos al Senado y Diputados declararon antecedentes penales",
        "source": "RPP Noticias",
        "type": "candidates",
        "data_field": "has_criminal_record",
    },
    {
        "id": "congresistas_reelectos",
        "label": "🔄 Congresistas buscando reelección",
        "category": "corrupcion",
        "description": "88 congresistas actuales buscan reelegirse, 35 en partido diferente",
        "source": "Wikipedia / RPP",
        "type": "candidates",
        "data_field": "is_reelection",
    },
    # --- TEMAS SOCIALES ---
    {
        "id": "pro_aborto",
        "label": "🩺 A favor de despenalizar el aborto",
        "category": "social",
        "description": "Partidos cuyo plan de gobierno incluye despenalización del aborto",
        "type": "parties",
        "parties": ["pm", "jpp"],
    },
    {
        "id": "anti_aborto",
        "label": "🚫 En contra total del aborto",
        "category": "social",
        "description": "Partidos con postura pro-vida y contra la despenalización",
        "type": "parties",
        "parties": ["rp", "fp"],
    },
    {
        "id": "pro_matrimonio_igualitario",
        "label": "🏳️‍🌈 A favor matrimonio igualitario",
        "category": "social",
        "description": "Partidos que apoyan el matrimonio igualitario o unión civil",
        "type": "parties",
        "parties": ["pm"],
    },
    {
        "id": "anti_genero",
        "label": "🚫 Contra 'ideología de género' en escuelas",
        "category": "social",
        "description": "Partidos que buscan eliminar la ESI (Educación Sexual Integral)",
        "type": "parties",
        "parties": ["rp", "fp", "fep"],
    },
    # --- ECONOMÍA ---
    {
        "id": "privatizar_petroperu",
        "label": "⛽ Privatizar Petroperú",
        "category": "economia",
        "description": "Partidos que proponen privatizar Petroperú total o parcialmente",
        "type": "parties",
        "parties": ["avp", "sc"],
    },
    {
        "id": "defender_petroperu",
        "label": "⛽ Defender Petroperú estatal",
        "category": "economia",
        "description": "Partidos que quieren mantener Petroperú como empresa estatal",
        "type": "parties",
        "parties": ["jpp", "pl", "an"],
    },
    # --- POLÍTICA ---
    {
        "id": "nueva_constitucion",
        "label": "📜 Quieren nueva Constitución",
        "category": "politica",
        "description": "Partidos que proponen Asamblea Constituyente o nueva Constitución",
        "source": "Perú21",
        "type": "parties",
        "parties": ["jpp", "pl", "an", "venc", "cp", "pod", "pte"],
    },
]
