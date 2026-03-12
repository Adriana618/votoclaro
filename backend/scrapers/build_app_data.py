#!/usr/bin/env python3
"""
Pipeline completo: JNE candidates + Congreso votes → app data.

Lee los datos crudos de jne_candidatos.json y congreso_votaciones.json,
cruza congresistas con candidatos 2026 (reelección), y genera el módulo
app/data/candidates.py listo para usar en la app.

Uso:
    python scrapers/build_app_data.py                     # Pipeline completo
    python scrapers/build_app_data.py --jne-only          # Solo JNE (sin cruce)
    python scrapers/build_app_data.py --stats              # Estadísticas
"""

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

# === PATHS ===
DATA_DIR = Path(__file__).resolve().parent / "data"
JNE_FILE = DATA_DIR / "jne_candidatos.json"
CONGRESO_FILE = DATA_DIR / "congreso_votaciones.json"
OUTPUT_JSON = DATA_DIR / "candidates_final.json"
APP_CANDIDATES_PY = Path(__file__).resolve().parent.parent / "app" / "data" / "candidates.py"

# === JNE PARTY → VotoClaro slug ===
# Maps partido_votoclaro from jne_scraper to our internal slug
JNE_PARTY_TO_SLUG = {
    "rp": "rp", "fp": "fp", "pm": "pm", "jpp": "jpp",
    "an": "an", "sc": "sc", "pl": "pl", "app": "app",
    "pod": "pod", "fep": "fep", "avp": "avp",
    "apra": "apra", "venc": "venc", "cp": "cp", "pte": "pte",
    "fyl": "fyl", "un": "un",
    # Partidos nuevos
    "ppt": "ppt", "pdup": "pdup", "id": "id", "ucd": "ucd",
    "pp": "pp", "lp": "lp", "pa": "pa", "pdv": "pdv",
    "frepap": "frepap", "prog": "prog", "pbg": "pbg",
    "prin": "prin", "obras": "obras", "plg": "plg",
    "pdf": "pdf", "salv": "salv", "ppp": "ppp", "fep2": "fep2",
    "pmod": "pmod", "sicreo": "sicreo", "cpp": "cpp",
}

# === JNE party name → slug (fallback when partido_votoclaro is empty) ===
JNE_NAME_TO_SLUG = {
    "RENOVACION POPULAR": "rp", "FUERZA POPULAR": "fp",
    "PARTIDO MORADO": "pm", "JUNTOS POR EL PERU": "jpp",
    "AHORA NACION - AN": "an", "PARTIDO DEMOCRATICO SOMOS PERU": "sc",
    "PARTIDO POLITICO NACIONAL PERU LIBRE": "pl",
    "ALIANZA PARA EL PROGRESO": "app", "PODEMOS PERU": "pod",
    "PARTIDO FRENTE DE LA ESPERANZA 2021": "fep",
    "AVANZA PAIS - PARTIDO DE INTEGRACION SOCIAL": "avp",
    "PARTIDO APRISTA PERUANO": "apra",
    "ALIANZA ELECTORAL VENCEREMOS": "venc",
    "PARTIDO POLITICO COOPERACION POPULAR": "cp",
    "PARTIDO DE LOS TRABAJADORES Y EMPRENDEDORES PTE - PERU": "pte",
    "FUERZA Y LIBERTAD": "fyl", "UNIDAD NACIONAL": "un",
    # 21 partidos nuevos
    "PARTIDO PAIS PARA TODOS": "ppt",
    "PARTIDO DEMOCRATA UNIDO PERU": "pdup",
    "PARTIDO POLITICO INTEGRIDAD DEMOCRATICA": "id",
    "UN CAMINO DIFERENTE": "ucd",
    "PARTIDO POLITICO PERU PRIMERO": "pp",
    "LIBERTAD POPULAR": "lp",
    "PARTIDO POLITICO PERU ACCION": "pa",
    "PARTIDO DEMOCRATA VERDE": "pdv",
    "FRENTE POPULAR AGRICOLA FIA DEL PERU": "frepap",
    "PROGRESEMOS": "prog",
    "PARTIDO DEL BUEN GOBIERNO": "pbg",
    "PARTIDO POLITICO PRIN": "prin",
    "PARTIDO CIVICO OBRAS": "obras",
    "PRIMERO LA GENTE - COMUNIDAD, ECOLOGIA, LIBERTAD Y PROGRESO": "plg",
    "PARTIDO DEMOCRATICO FEDERAL": "pdf",
    "SALVEMOS AL PERU": "salv",
    "PARTIDO PATRIOTICO DEL PERU": "ppp",
    "FE EN EL PERU": "fep2",
    "PERU MODERNO": "pmod",
    "PARTIDO SICREO": "sicreo",
    "PARTIDO CIUDADANOS POR EL PERU": "cpp",
}

# === JNE DEPARTMENT → region slug ===
DEPT_TO_SLUG = {
    "AMAZONAS": "amazonas", "ANCASH": "ancash", "APURIMAC": "apurimac",
    "AREQUIPA": "arequipa", "AYACUCHO": "ayacucho", "CAJAMARCA": "cajamarca",
    "CALLAO": "callao", "CUSCO": "cusco", "HUANCAVELICA": "huancavelica",
    "HUANUCO": "huanuco", "ICA": "ica", "JUNIN": "junin",
    "LA LIBERTAD": "la-libertad", "LAMBAYEQUE": "lambayeque",
    "LIMA": "lima", "LIMA METROPOLITANA": "lima",
    "LIMA PROVINCIAS": "lima-provincias",
    "LORETO": "loreto", "MADRE DE DIOS": "madre-de-dios",
    "MOQUEGUA": "moquegua", "PASCO": "pasco", "PIURA": "piura",
    "PUNO": "puno", "SAN MARTIN": "san-martin",
    "TACNA": "tacna", "TUMBES": "tumbes", "UCAYALI": "ucayali",
    "PERUANOS RESIDENTES EN EL EXTRANJERO": "extranjero",
    "": "lima",  # Some Lima candidates have empty department
}

# === Controversy score weights (from app/services/controversy.py) ===
W_CRIMINAL = 30
W_PRO_CRIME = 20
W_INVESTIGATION = 15  # per investigation, max 3
W_PARTY_CHANGE = 10
W_REELECTION = 5


def normalize_name(name: str) -> str:
    """Normalize a name for fuzzy matching."""
    # Remove accents
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Uppercase, remove extra spaces
    return re.sub(r"\s+", " ", ascii_str.upper().strip())


def fuzzy_match(name1: str, name2: str) -> float:
    """Calculate similarity between two names."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    return SequenceMatcher(None, n1, n2).ratio()


def load_jne_candidates() -> list[dict]:
    """Load and transform JNE candidates."""
    if not JNE_FILE.exists():
        print(f"✗ No existe {JNE_FILE}", file=sys.stderr)
        print("  Ejecuta primero: python scrapers/jne_scraper.py", file=sys.stderr)
        sys.exit(1)

    raw = json.loads(JNE_FILE.read_text(encoding="utf-8"))
    print(f"📥 Cargando {len(raw)} candidatos JNE...")

    candidates = []
    skipped = {"improcedente": 0, "exclusion": 0, "renuncia": 0, "otro": 0, "sin_partido": 0}

    for c in raw:
        # Solo candidatos INSCRITOS
        estado = c.get("estado", "").upper()
        if estado != "INSCRITO":
            if "IMPROCEDENTE" in estado:
                skipped["improcedente"] += 1
            elif "EXCLUSION" in estado:
                skipped["exclusion"] += 1
            elif "RENUNCIA" in estado:
                skipped["renuncia"] += 1
            else:
                skipped["otro"] += 1
            continue

        # Map party — try partido_votoclaro first, then fall back to partido_jne name
        party_vc = c.get("partido_votoclaro", "")
        party_slug = JNE_PARTY_TO_SLUG.get(party_vc, "")
        if not party_slug:
            # Fallback: map by JNE party name directly
            partido_jne = c.get("partido_jne", "")
            party_slug = JNE_NAME_TO_SLUG.get(partido_jne, "")
        if not party_slug:
            skipped["sin_partido"] += 1
            continue

        # Map region
        dept = c.get("departamento", "")
        cargo = c.get("cargo", "").upper()
        if cargo == "SENADOR" or "SENADOR" in c.get("tipo_eleccion", "").upper():
            region_slug = None  # Senators are national
        elif cargo in ("PRESIDENTE", "VICEPRESIDENTE"):
            region_slug = None  # Presidential candidates are national
        else:
            region_slug = DEPT_TO_SLUG.get(dept, None)

        # Determine cargo type
        if "PRESIDENTE" in cargo or "VICE" in cargo:
            cargo_type = "PRESIDENCIAL"
        elif "SENADOR" in c.get("tipo_eleccion", "").upper():
            cargo_type = "SENADOR"
        else:
            cargo_type = "DIPUTADO"

        candidates.append({
            "jne_id": c.get("jne_id", ""),
            "dni": c.get("dni", ""),
            "name": c.get("nombre_ordenado", c.get("nombre_completo", "")),
            "nombre_completo": c.get("nombre_completo", ""),
            "party_slug": party_slug,
            "partido_jne": c.get("partido_jne", ""),
            "region_slug": region_slug,
            "cargo": cargo_type,
            "position_number": c.get("posicion_lista"),
            "sexo": c.get("sexo", ""),
            "foto_url": c.get("foto_url"),
            # Fields to be filled by merge
            "has_criminal_record": False,
            "voted_pro_crime": False,
            "pro_crime_vote_count": 0,
            "is_reelection": False,
            "investigations": 0,
            "controversy_score": 0.0,
            "party_changed_from": None,
        })

    print(f"  ✓ {len(candidates)} candidatos inscritos")
    for reason, count in skipped.items():
        if count:
            print(f"  ⊘ {count} {reason}")

    return candidates


def load_congreso_votes() -> dict:
    """Load congress voting data and build per-congressperson summary."""
    if not CONGRESO_FILE.exists():
        print("⚠ No existe congreso_votaciones.json — saltando cruce de votos")
        return {}

    data = json.loads(CONGRESO_FILE.read_text(encoding="utf-8"))
    vote_summary = data.get("vote_summary", {})
    print(f"📥 Cargando votos del Congreso: {len(vote_summary)} congresistas")
    return vote_summary


def cross_reference(candidates: list[dict], congress_votes: dict) -> dict:
    """Cross-reference 2026 candidates with congress voting records.

    Identifies reelection candidates and their voting history.
    Returns stats about the merge.
    """
    if not congress_votes:
        return {"matches": 0, "reelection": 0, "pro_crime": 0}

    # Build normalized name index of congresspeople
    congress_normalized = {}
    for name, data in congress_votes.items():
        norm = normalize_name(name)
        congress_normalized[norm] = (name, data)

    matches = 0
    reelection = 0
    pro_crime_count = 0

    print(f"\n🔄 Cruzando {len(candidates)} candidatos con {len(congress_votes)} congresistas...")

    for candidate in candidates:
        cand_name = normalize_name(candidate["name"])

        # Try exact match first
        if cand_name in congress_normalized:
            original_name, congress_data = congress_normalized[cand_name]
            _apply_congress_data(candidate, congress_data)
            matches += 1
            if candidate["is_reelection"]:
                reelection += 1
            if candidate["voted_pro_crime"]:
                pro_crime_count += 1
            continue

        # Try fuzzy match
        best_match = None
        best_score = 0.0
        for norm_name, (original_name, congress_data) in congress_normalized.items():
            score = fuzzy_match(cand_name, norm_name)
            if score > best_score:
                best_score = score
                best_match = (original_name, congress_data)

        if best_score >= 0.85 and best_match:
            original_name, congress_data = best_match
            _apply_congress_data(candidate, congress_data)
            matches += 1
            if candidate["is_reelection"]:
                reelection += 1
            if candidate["voted_pro_crime"]:
                pro_crime_count += 1

    stats = {"matches": matches, "reelection": reelection, "pro_crime": pro_crime_count}
    print(f"  ✓ {matches} matches encontrados")
    print(f"  🔁 {reelection} buscando reelección")
    print(f"  ⚖️  {pro_crime_count} con votos pro-crimen")
    return stats


def _apply_congress_data(candidate: dict, congress_data: dict):
    """Apply congress voting data to a candidate."""
    candidate["is_reelection"] = True
    total_favor = congress_data.get("total_a_favor", 0)
    total_contra = congress_data.get("total_en_contra", 0)
    candidate["pro_crime_vote_count"] = total_favor
    # If they voted in favor more than against on controversial laws, flag as pro-crime
    if total_favor > 0:
        candidate["voted_pro_crime"] = True


def calculate_controversy_scores(candidates: list[dict]):
    """Calculate controversy scores for all candidates."""
    for c in candidates:
        score = 0.0
        if c.get("has_criminal_record"):
            score += W_CRIMINAL
        if c.get("voted_pro_crime"):
            score += W_PRO_CRIME
        investigations = min(c.get("investigations", 0), 3)
        score += investigations * W_INVESTIGATION
        if c.get("party_changed_from"):
            score += W_PARTY_CHANGE
        if c.get("is_reelection"):
            score += W_REELECTION
        c["controversy_score"] = min(score, 100.0)


def generate_candidates_py(candidates: list[dict], stats: dict) -> str:
    """Generate the app/data/candidates.py module."""
    lines = [
        '"""Datos de candidatos importados desde fuentes externas.',
        "",
        f"Generado automaticamente por scrapers/build_app_data.py el {date.today()}.",
        f"Total de candidatos: {len(candidates)}",
        '"""',
        "",
        "",
        "# Candidatos indexados por ID interno",
        "CANDIDATES: dict[int, dict] = {",
    ]

    for i, c in enumerate(candidates, start=1):
        lines.append(f"    {i}: {{")
        lines.append(f'        "id": {i},')
        lines.append(f'        "name": {repr(c["name"])},')
        lines.append(f'        "nombre_completo": {repr(c.get("nombre_completo", ""))},')
        lines.append(f'        "party_slug": {repr(c.get("party_slug", ""))},')
        lines.append(f'        "partido_jne": {repr(c.get("partido_jne", ""))},')
        lines.append(f'        "region_slug": {repr(c.get("region_slug"))},')
        lines.append(f'        "cargo": {repr(c.get("cargo", "DIPUTADO"))},')
        lines.append(f'        "position_number": {repr(c.get("position_number"))},')
        lines.append(f'        "sexo": {repr(c.get("sexo", ""))},')
        lines.append(f'        "has_criminal_record": {repr(c.get("has_criminal_record", False))},')
        lines.append(f'        "voted_pro_crime": {repr(c.get("voted_pro_crime", False))},')
        lines.append(f'        "pro_crime_vote_count": {c.get("pro_crime_vote_count", 0)},')
        lines.append(f'        "is_reelection": {repr(c.get("is_reelection", False))},')
        lines.append(f'        "investigations": {c.get("investigations", 0)},')
        lines.append(f'        "controversy_score": {c.get("controversy_score", 0.0)},')
        lines.append(f'        "party_changed_from": {repr(c.get("party_changed_from"))},')
        lines.append(f'        "jne_id": {repr(c.get("jne_id", ""))},')
        lines.append(f'        "dni": {repr(c.get("dni", ""))},')
        lines.append(f'        "foto_url": {repr(c.get("foto_url"))},')
        lines.append("    },")

    lines.append("}")
    lines.append("")
    lines.append("")

    # Party index
    lines.append("# Indice por partido: {partido_slug: [candidate_ids]}")
    lines.append("CANDIDATES_BY_PARTY: dict[str, list[int]] = {}")
    lines.append("for _id, _c in CANDIDATES.items():")
    lines.append('    _party = _c["party_slug"]')
    lines.append("    if _party not in CANDIDATES_BY_PARTY:")
    lines.append("        CANDIDATES_BY_PARTY[_party] = []")
    lines.append("    CANDIDATES_BY_PARTY[_party].append(_id)")
    lines.append("")
    lines.append("")

    # Region index
    lines.append("# Indice por region: {region_slug: [candidate_ids]}")
    lines.append("CANDIDATES_BY_REGION: dict[str, list[int]] = {}")
    lines.append("for _id, _c in CANDIDATES.items():")
    lines.append('    _region = _c["region_slug"]')
    lines.append("    if _region:")
    lines.append("        if _region not in CANDIDATES_BY_REGION:")
    lines.append("            CANDIDATES_BY_REGION[_region] = []")
    lines.append("        CANDIDATES_BY_REGION[_region].append(_id)")
    lines.append("")
    lines.append("")

    # Stats
    import pprint
    stats_str = pprint.pformat(stats, indent=4, width=100)
    lines.append("# Estadisticas de la ultima importacion")
    lines.append(f"IMPORT_STATS: dict = {stats_str}")
    lines.append("")

    return "\n".join(lines)


def print_stats(candidates: list[dict]):
    """Print statistics."""
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS — CANDIDATOS FINALES")
    print("=" * 60)

    print(f"\nTotal: {len(candidates)}")

    # By cargo
    cargos = {}
    for c in candidates:
        t = c["cargo"]
        cargos[t] = cargos.get(t, 0) + 1
    for t, n in sorted(cargos.items()):
        print(f"  {t}: {n}")

    # By party (top 15)
    parties = {}
    for c in candidates:
        p = c["party_slug"]
        parties[p] = parties.get(p, 0) + 1
    print(f"\nTop 15 partidos:")
    for p, n in sorted(parties.items(), key=lambda x: -x[1])[:15]:
        print(f"  {p:8s}: {n}")

    # Gender
    sexos = {}
    for c in candidates:
        s = c.get("sexo", "?")
        sexos[s] = sexos.get(s, 0) + 1
    print(f"\nPor sexo:")
    for s, n in sorted(sexos.items()):
        pct = n / len(candidates) * 100
        print(f"  {s}: {n} ({pct:.1f}%)")

    # Controversy
    with_controversy = [c for c in candidates if c["controversy_score"] > 0]
    print(f"\nCon score controversia > 0: {len(with_controversy)}")
    reelection = [c for c in candidates if c["is_reelection"]]
    print(f"Buscando reelección: {len(reelection)}")
    pro_crime = [c for c in candidates if c["voted_pro_crime"]]
    print(f"Con votos pro-crimen: {len(pro_crime)}")


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline completo: JNE + Congreso → app/data/candidates.py"
    )
    parser.add_argument("--jne-only", action="store_true", help="Solo importar JNE, sin cruce con Congreso")
    parser.add_argument("--stats", action="store_true", help="Solo mostrar estadísticas")
    parser.add_argument("--no-generate", action="store_true", help="No generar candidates.py")
    args = parser.parse_args()

    if args.stats:
        if OUTPUT_JSON.exists():
            data = json.loads(OUTPUT_JSON.read_text())
            print_stats(data["candidatos"])
        else:
            print(f"✗ No existe {OUTPUT_JSON}")
        return

    # Step 1: Load JNE candidates
    candidates = load_jne_candidates()

    # Step 2: Load congress votes and cross-reference
    merge_stats = {}
    if not args.jne_only:
        congress_votes = load_congreso_votes()
        merge_stats = cross_reference(candidates, congress_votes)

    # Step 3: Calculate controversy scores
    calculate_controversy_scores(candidates)

    # Print stats
    print_stats(candidates)

    # Step 4: Save intermediate JSON
    output_data = {
        "fecha": str(date.today()),
        "stats": {
            "total_candidatos": len(candidates),
            "por_cargo": {},
            "por_partido": {},
            "merge": merge_stats,
        },
        "candidatos": candidates,
    }
    # Populate stats
    for c in candidates:
        cargo = c["cargo"]
        output_data["stats"]["por_cargo"][cargo] = output_data["stats"]["por_cargo"].get(cargo, 0) + 1
        party = c["party_slug"]
        output_data["stats"]["por_partido"][party] = output_data["stats"]["por_partido"].get(party, 0) + 1

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n💾 JSON guardado en {OUTPUT_JSON}")

    # Step 5: Generate candidates.py
    if not args.no_generate:
        print(f"\n🔧 Generando {APP_CANDIDATES_PY}...")
        module_content = generate_candidates_py(candidates, output_data["stats"])
        APP_CANDIDATES_PY.write_text(module_content, encoding="utf-8")
        print(f"  ✓ {len(candidates)} candidatos escritos")

        # Verify import
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("candidates", str(APP_CANDIDATES_PY))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                print(f"  ✓ Import OK: {len(mod.CANDIDATES)} candidatos")
                print(f"  ✓ {len(mod.CANDIDATES_BY_PARTY)} partidos")
                print(f"  ✓ {len(mod.CANDIDATES_BY_REGION)} regiones")
        except Exception as e:
            print(f"  ✗ Error al verificar: {e}", file=sys.stderr)

    print("\n✅ Pipeline completado!")


if __name__ == "__main__":
    main()
