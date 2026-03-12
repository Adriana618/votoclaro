#!/usr/bin/env python3
"""Script maestro de merge de todas las fuentes de datos.

Combina datos de candidatos (Voto Informado), votaciones del Congreso
e investigaciones periodisticas (Convoca) en un unico archivo JSON
unificado listo para la app.

Usa fuzzy matching con difflib para emparejar nombres entre fuentes.

Uso:
    python -m scrapers.merge_data \
      --candidates data/candidatos_validados.json \
      --votaciones data/votaciones_merged.json \
      --investigaciones data/convoca_output.json \
      --output data/candidates_final.json
"""

import argparse
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

# Agregar el directorio padre al path para importar modulos de la app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.controversy import calculate_controversy_score


# --- Configuracion de fuzzy matching ---
# Umbral minimo de similitud para considerar que dos nombres son la misma persona
SIMILARITY_THRESHOLD = 0.80


def _normalizar_nombre(nombre: str) -> str:
    """Normaliza un nombre para mejorar el matching.

    Convierte a mayusculas, elimina tildes y caracteres especiales,
    y ordena apellidos/nombres de forma consistente.
    """
    import unicodedata

    if not nombre:
        return ""

    # Convertir a mayusculas
    nombre = nombre.upper().strip()

    # Remover tildes/acentos
    nombre = "".join(
        c for c in unicodedata.normalize("NFKD", nombre)
        if not unicodedata.combining(c)
    )

    # Remover caracteres especiales excepto espacios y comas
    nombre = "".join(c for c in nombre if c.isalpha() or c in " ,")

    # Normalizar espacios multiples
    nombre = " ".join(nombre.split())

    return nombre


def _calcular_similitud(nombre1: str, nombre2: str) -> float:
    """Calcula la similitud entre dos nombres normalizados.

    Usa SequenceMatcher de difflib que funciona bien para nombres
    con diferentes ordenes de apellido/nombre.
    """
    n1 = _normalizar_nombre(nombre1)
    n2 = _normalizar_nombre(nombre2)

    if not n1 or not n2:
        return 0.0

    # Similitud directa
    ratio_directo = SequenceMatcher(None, n1, n2).ratio()

    # Tambien intentar con las partes del nombre reordenadas
    # (A veces el JNE tiene "APELLIDO, NOMBRE" y el Congreso "NOMBRE APELLIDO")
    partes1 = sorted(n1.replace(",", " ").split())
    partes2 = sorted(n2.replace(",", " ").split())
    ratio_ordenado = SequenceMatcher(None, " ".join(partes1), " ".join(partes2)).ratio()

    return max(ratio_directo, ratio_ordenado)


def _encontrar_mejor_match(nombre: str, candidatos: list[dict]) -> tuple[dict | None, float]:
    """Encuentra el candidato con el nombre mas similar.

    Args:
        nombre: Nombre a buscar.
        candidatos: Lista de candidatos validados.

    Returns:
        Tupla (candidato_match, score_similitud) o (None, 0.0) si no hay match.
    """
    mejor_match = None
    mejor_score = 0.0

    for candidato in candidatos:
        score = _calcular_similitud(nombre, candidato["name"])
        if score > mejor_score:
            mejor_score = score
            mejor_match = candidato

    if mejor_score >= SIMILARITY_THRESHOLD:
        return mejor_match, mejor_score

    return None, 0.0


def merge_datos(
    candidates_path: str,
    votaciones_path: str | None = None,
    investigaciones_path: str | None = None,
    output_path: str | None = None,
    threshold: float = SIMILARITY_THRESHOLD,
) -> dict:
    """Combina las 3 fuentes de datos en un archivo unificado.

    Args:
        candidates_path: JSON con candidatos validados (de import_candidates).
        votaciones_path: JSON con votaciones procesadas (de import_votaciones).
        investigaciones_path: JSON con investigaciones de Convoca.
        output_path: Ruta de salida para el JSON final.
        threshold: Umbral de similitud para fuzzy matching.

    Returns:
        Diccionario con candidatos unificados y estadisticas.
    """
    global SIMILARITY_THRESHOLD
    SIMILARITY_THRESHOLD = threshold

    # --- 1. Cargar candidatos base ---
    with open(candidates_path, "r", encoding="utf-8") as f:
        data_candidatos = json.load(f)

    candidatos = data_candidatos.get("candidatos", [])
    print(f"Candidatos cargados: {len(candidatos)}")

    # --- 2. Merge con votaciones del Congreso ---
    matches_votaciones = 0
    congresistas_no_match = []

    if votaciones_path and Path(votaciones_path).exists():
        with open(votaciones_path, "r", encoding="utf-8") as f:
            data_votaciones = json.load(f)

        congresistas = data_votaciones.get("congresistas", {})
        print(f"Congresistas con votaciones: {len(congresistas)}")

        for nombre_congresista, datos_voto in congresistas.items():
            match, score = _encontrar_mejor_match(nombre_congresista, candidatos)

            if match:
                matches_votaciones += 1
                # El congresista busca reeleccion
                match["is_reelection"] = True
                match["voted_pro_crime"] = datos_voto.get("voted_pro_crime", False)
                match["pro_crime_vote_count"] = datos_voto.get("pro_crime_vote_count", 0)
                match["pro_crime_votes_detail"] = datos_voto.get("pro_crime_votes_detail", [])
            else:
                congresistas_no_match.append(nombre_congresista)

        print(f"  Matches encontrados: {matches_votaciones}")
        if congresistas_no_match:
            print(f"  Congresistas sin match ({len(congresistas_no_match)}):")
            for nombre in congresistas_no_match[:10]:
                print(f"    - {nombre}")
            if len(congresistas_no_match) > 10:
                print(f"    ... y {len(congresistas_no_match) - 10} mas")
    else:
        print("Sin datos de votaciones (archivo no proporcionado o no encontrado)")

    # --- 3. Merge con investigaciones de Convoca ---
    matches_investigaciones = 0
    investigaciones_no_match = []

    if investigaciones_path and Path(investigaciones_path).exists():
        with open(investigaciones_path, "r", encoding="utf-8") as f:
            data_investigaciones = json.load(f)

        investigaciones = data_investigaciones.get("investigaciones", [])
        print(f"Investigaciones de Convoca: {len(investigaciones)}")

        # Agrupar investigaciones por candidato
        inv_por_candidato: dict[str, list[dict]] = {}
        for inv in investigaciones:
            nombre = inv.get("nombre_candidato", "")
            if nombre not in inv_por_candidato:
                inv_por_candidato[nombre] = []
            inv_por_candidato[nombre].append(inv)

        for nombre_inv, lista_inv in inv_por_candidato.items():
            match, score = _encontrar_mejor_match(nombre_inv, candidatos)

            if match:
                matches_investigaciones += 1
                match["investigations"] = match.get("investigations", 0) + len(lista_inv)
                # Guardar detalle de investigaciones
                if "investigations_detail" not in match:
                    match["investigations_detail"] = []
                match["investigations_detail"].extend([
                    {
                        "tipo": inv.get("tipo_investigacion", ""),
                        "detalle": inv.get("detalle", ""),
                        "fuente_url": inv.get("fuente_url", ""),
                        "fecha": inv.get("fecha_publicacion", ""),
                    }
                    for inv in lista_inv
                ])
            else:
                investigaciones_no_match.append(nombre_inv)

        print(f"  Matches encontrados: {matches_investigaciones}")
        if investigaciones_no_match:
            print(f"  Nombres sin match ({len(investigaciones_no_match)}):")
            for nombre in investigaciones_no_match[:10]:
                print(f"    - {nombre}")
    else:
        print("Sin datos de Convoca (archivo no proporcionado o no encontrado)")

    # --- 4. Recalcular controversy_score con todos los datos ---
    print("\nRecalculando controversy scores...")
    for candidato in candidatos:
        candidato["controversy_score"] = calculate_controversy_score(
            has_criminal_record=candidato.get("has_criminal_record", False),
            voted_pro_crime=candidato.get("voted_pro_crime", False),
            is_reelection=candidato.get("is_reelection", False),
            investigations=candidato.get("investigations", 0),
            party_changed_from=candidato.get("party_changed_from"),
        )

    # --- 5. Estadisticas finales ---
    stats = {
        "total_candidatos": len(candidatos),
        "por_partido": {},
        "por_region": {},
        "por_cargo": {"SENADOR": 0, "DIPUTADO": 0},
        "con_antecedentes": 0,
        "con_sentencias": 0,
        "con_votos_pro_crimen": 0,
        "buscando_reeleccion": 0,
        "con_investigaciones": 0,
        "score_promedio": 0.0,
        "score_max": 0.0,
        "matches_votaciones": matches_votaciones,
        "matches_investigaciones": matches_investigaciones,
        "congresistas_sin_match": congresistas_no_match,
        "investigaciones_sin_match": investigaciones_no_match,
    }

    for c in candidatos:
        partido = c.get("party_slug", "desconocido")
        region = c.get("region_slug") or "nacional"
        stats["por_partido"][partido] = stats["por_partido"].get(partido, 0) + 1
        stats["por_region"][region] = stats["por_region"].get(region, 0) + 1
        stats["por_cargo"][c.get("cargo", "DIPUTADO")] += 1
        if c.get("has_criminal_record"):
            stats["con_antecedentes"] += 1
        if c.get("has_sentencias"):
            stats["con_sentencias"] += 1
        if c.get("voted_pro_crime"):
            stats["con_votos_pro_crimen"] += 1
        if c.get("is_reelection"):
            stats["buscando_reeleccion"] += 1
        if c.get("investigations", 0) > 0:
            stats["con_investigaciones"] += 1

    scores = [c["controversy_score"] for c in candidatos]
    if scores:
        stats["score_promedio"] = round(sum(scores) / len(scores), 2)
        stats["score_max"] = max(scores)

    # Imprimir resumen
    print(f"\n{'='*50}")
    print(f"RESUMEN FINAL DEL MERGE")
    print(f"{'='*50}")
    print(f"Total candidatos: {stats['total_candidatos']}")
    print(f"  Senadores: {stats['por_cargo']['SENADOR']}")
    print(f"  Diputados: {stats['por_cargo']['DIPUTADO']}")
    print(f"Con antecedentes penales: {stats['con_antecedentes']}")
    print(f"Con sentencias: {stats['con_sentencias']}")
    print(f"Con votos pro-crimen: {stats['con_votos_pro_crimen']}")
    print(f"Buscando reeleccion: {stats['buscando_reeleccion']}")
    print(f"Con investigaciones Convoca: {stats['con_investigaciones']}")
    print(f"Score controversia promedio: {stats['score_promedio']}")
    print(f"Score controversia maximo: {stats['score_max']}")
    print(f"\nPor partido:")
    for partido, count in sorted(stats["por_partido"].items(), key=lambda x: -x[1]):
        print(f"  {partido}: {count}")

    resultado = {
        "fecha_merge": str(__import__("datetime").date.today()),
        "stats": stats,
        "candidatos": candidatos,
    }

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\nArchivo unificado guardado en: {output_path}")

    return resultado


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Merge maestro de todas las fuentes de datos de VotoClaro. "
                    "Combina candidatos, votaciones del Congreso e investigaciones "
                    "de Convoca en un unico archivo JSON unificado.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo:
  python -m scrapers.merge_data \\
    --candidates data/candidatos_validados.json \\
    --votaciones data/votaciones_merged.json \\
    --investigaciones data/convoca_output.json \\
    --output data/candidates_final.json \\
    --threshold 0.85

El umbral de similitud (--threshold) controla que tan estricto es el
fuzzy matching de nombres. Valores recomendados:
  0.75 - Permisivo (puede generar falsos positivos)
  0.80 - Balance (default)
  0.90 - Estricto (puede perder matches validos)
        """,
    )
    parser.add_argument(
        "--candidates", "-c",
        required=True,
        help="JSON con candidatos validados (salida de import_candidates)",
    )
    parser.add_argument(
        "--votaciones", "-v",
        required=False,
        help="JSON con votaciones procesadas (salida de import_votaciones)",
    )
    parser.add_argument(
        "--investigaciones", "-g",
        required=False,
        help="JSON con investigaciones de Convoca",
    )
    parser.add_argument(
        "--output", "-o",
        required=False,
        help="Archivo JSON de salida unificado",
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=SIMILARITY_THRESHOLD,
        help=f"Umbral de similitud para fuzzy matching (default: {SIMILARITY_THRESHOLD})",
    )

    args = parser.parse_args()

    if not Path(args.candidates).exists():
        print(f"ERROR: No se encontro el archivo de candidatos: {args.candidates}")
        sys.exit(1)

    merge_datos(
        candidates_path=args.candidates,
        votaciones_path=args.votaciones,
        investigaciones_path=args.investigaciones,
        output_path=args.output,
        threshold=args.threshold,
    )


if __name__ == "__main__":
    main()
