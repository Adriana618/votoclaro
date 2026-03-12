#!/usr/bin/env python3
"""Importador de votaciones del Congreso.

Lee archivos JSON con votaciones extraidas de PDFs del Congreso,
identifica congresistas que votaron a favor de leyes pro-crimen,
y genera un mapeo nombre -> datos de voto pro-crimen.

Uso:
    python -m scrapers.import_votaciones --input data/votaciones/ --output data/votaciones_merged.json
    python -m scrapers.import_votaciones --input data/votacion_001.json --output data/votaciones_merged.json
"""

import argparse
import json
import sys
from pathlib import Path


# --- Las 6 leyes pro-crimen que rastreamos ---
LEYES_PRO_CRIMEN = [
    "Ley que modifica el codigo penal sobre crimen organizado",
    "Ley que limita la colaboracion eficaz",
    "Ley que reduce penas por lavado de activos",
    "Ley que debilita la extincion de dominio",
    "Ley que modifica la prision preventiva",
    "Ley que dificulta la persecucion de testaferros",
]


def _cargar_votaciones(input_path: str) -> list[dict]:
    """Carga votaciones desde un archivo JSON o un directorio de JSONs.

    Args:
        input_path: Ruta a un archivo JSON o directorio con archivos JSON.

    Returns:
        Lista combinada de todos los registros de votacion.
    """
    path = Path(input_path)
    todas_votaciones: list[dict] = []

    if path.is_file():
        archivos = [path]
    elif path.is_dir():
        archivos = sorted(path.glob("*.json"))
        if not archivos:
            print(f"ADVERTENCIA: No se encontraron archivos JSON en {input_path}")
            return []
    else:
        print(f"ERROR: Ruta no encontrada: {input_path}")
        sys.exit(1)

    for archivo in archivos:
        print(f"Leyendo: {archivo.name}")
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        votaciones = data.get("votaciones", [])
        todas_votaciones.extend(votaciones)
        print(f"  -> {len(votaciones)} registros de votacion")

    return todas_votaciones


def procesar_votaciones(input_path: str, output_path: str | None = None) -> dict:
    """Procesa votaciones y genera mapeo de congresistas con votos pro-crimen.

    Args:
        input_path: Ruta a archivo JSON o directorio con archivos JSON.
        output_path: Ruta al archivo de salida (opcional).

    Returns:
        Diccionario con el mapeo de congresistas y estadisticas.
    """
    votaciones = _cargar_votaciones(input_path)

    if not votaciones:
        print("No se encontraron votaciones para procesar.")
        return {"congresistas": {}, "stats": {}}

    print(f"\nTotal de registros de votacion cargados: {len(votaciones)}")

    # Construir perfil de voto por congresista
    congresistas: dict[str, dict] = {}

    for voto_registro in votaciones:
        nombre = voto_registro.get("congresista", "").strip()
        if not nombre:
            continue

        # Inicializar si es nuevo
        if nombre not in congresistas:
            congresistas[nombre] = {
                "nombre": nombre,
                "grupo_parlamentario": voto_registro.get("grupo_parlamentario", ""),
                "voted_pro_crime": False,
                "pro_crime_vote_count": 0,
                "pro_crime_votes_detail": [],
                "total_votes": 0,
                "is_reelection_candidate": False,  # Se determina en el merge
            }

        congresista = congresistas[nombre]
        congresista["total_votes"] += 1

        # Solo contamos votos A FAVOR en leyes pro-crimen
        es_pro_crimen = voto_registro.get("es_ley_procrimen", False)
        voto = voto_registro.get("voto", "").upper()

        if es_pro_crimen and voto == "A FAVOR":
            congresista["voted_pro_crime"] = True
            congresista["pro_crime_vote_count"] += 1
            congresista["pro_crime_votes_detail"].append({
                "proyecto_ley": voto_registro.get("proyecto_ley", ""),
                "titulo": voto_registro.get("titulo_ley", ""),
                "fecha": voto_registro.get("fecha", ""),
            })

    # Estadisticas
    total_congresistas = len(congresistas)
    con_votos_pro_crimen = sum(1 for c in congresistas.values() if c["voted_pro_crime"])
    max_votos_pro_crimen = max(
        (c["pro_crime_vote_count"] for c in congresistas.values()), default=0
    )

    stats = {
        "total_registros_votacion": len(votaciones),
        "total_congresistas": total_congresistas,
        "con_votos_pro_crimen": con_votos_pro_crimen,
        "sin_votos_pro_crimen": total_congresistas - con_votos_pro_crimen,
        "max_votos_pro_crimen_individual": max_votos_pro_crimen,
    }

    print(f"\n--- Resultados de votaciones ---")
    print(f"Total congresistas encontrados: {total_congresistas}")
    print(f"Con votos pro-crimen: {con_votos_pro_crimen}")
    print(f"Sin votos pro-crimen: {total_congresistas - con_votos_pro_crimen}")
    print(f"Max votos pro-crimen individual: {max_votos_pro_crimen}")

    # Mostrar los que mas votaron pro-crimen
    if con_votos_pro_crimen > 0:
        print(f"\n--- Top congresistas con votos pro-crimen ---")
        ranking = sorted(
            [c for c in congresistas.values() if c["voted_pro_crime"]],
            key=lambda x: x["pro_crime_vote_count"],
            reverse=True,
        )
        for c in ranking[:20]:
            print(f"  {c['nombre']} ({c['grupo_parlamentario']}): "
                  f"{c['pro_crime_vote_count']} votos pro-crimen")

    resultado = {
        "stats": stats,
        "congresistas": congresistas,
    }

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\nArchivo de salida guardado en: {output_path}")

    return resultado


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Procesa votaciones del Congreso e identifica votos pro-crimen. "
                    "Acepta un archivo JSON o un directorio con multiples JSONs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo:
  python -m scrapers.import_votaciones --input data/votaciones/ --output data/votaciones_merged.json
  python -m scrapers.import_votaciones --input data/votacion_001.json

Las 6 leyes pro-crimen rastreadas:
  1. Ley que modifica el codigo penal sobre crimen organizado
  2. Ley que limita la colaboracion eficaz
  3. Ley que reduce penas por lavado de activos
  4. Ley que debilita la extincion de dominio
  5. Ley que modifica la prision preventiva
  6. Ley que dificulta la persecucion de testaferros
        """,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Archivo JSON o directorio con archivos JSON de votaciones",
    )
    parser.add_argument(
        "--output", "-o",
        required=False,
        help="Archivo JSON de salida con mapeo de votos pro-crimen (opcional)",
    )

    args = parser.parse_args()
    procesar_votaciones(args.input, args.output)


if __name__ == "__main__":
    main()
