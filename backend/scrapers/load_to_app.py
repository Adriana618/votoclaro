#!/usr/bin/env python3
"""Carga los datos unificados de candidatos a la app.

Toma el archivo candidates_final.json generado por merge_data.py
y genera un modulo Python (backend/app/data/candidates.py) con todos
los candidatos como un diccionario Python importable por los endpoints.

Uso:
    python -m scrapers.load_to_app --input data/candidates_final.json
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from textwrap import dedent


# Ruta al modulo de datos de la app
APP_DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"
CANDIDATES_PY = APP_DATA_DIR / "candidates.py"


def _py_repr(value) -> str:
    """Convierte un valor a su representacion Python valida.

    json.dumps produce 'null' para None, que no es Python valido.
    Esta funcion usa repr() para valores Python nativos.
    """
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, str):
        return repr(value)
    return repr(value)


def _generar_modulo_python(candidatos: list[dict], stats: dict) -> str:
    """Genera el contenido del modulo candidates.py.

    Convierte la lista de candidatos a un diccionario Python indexado
    por un ID interno (basado en posicion).
    """
    lineas = [
        '"""Datos de candidatos importados desde fuentes externas.',
        "",
        f"Generado automaticamente por scrapers/load_to_app.py el {date.today()}.",
        f"Total de candidatos: {len(candidatos)}",
        '"""',
        "",
        "",
        "# Candidatos indexados por ID interno",
        "# Cada candidato tiene los campos del modelo Candidate mas datos adicionales",
        "CANDIDATES: dict[int, dict] = {",
    ]

    for i, candidato in enumerate(candidatos, start=1):
        # Construir el diccionario del candidato con formato limpio
        lineas.append(f"    {i}: {{")
        lineas.append(f'        "id": {i},')
        lineas.append(f'        "name": {_py_repr(candidato["name"])},')
        lineas.append(f'        "party_slug": {_py_repr(candidato.get("party_slug", ""))},')
        lineas.append(f'        "region_slug": {_py_repr(candidato.get("region_slug"))},')
        lineas.append(f'        "cargo": {_py_repr(candidato.get("cargo", "DIPUTADO"))},')
        lineas.append(f'        "position_number": {_py_repr(candidato.get("position_number"))},')
        lineas.append(f'        "has_criminal_record": {_py_repr(candidato.get("has_criminal_record", False))},')
        lineas.append(f'        "voted_pro_crime": {_py_repr(candidato.get("voted_pro_crime", False))},')
        lineas.append(f'        "is_reelection": {_py_repr(candidato.get("is_reelection", False))},')
        lineas.append(f'        "investigations": {candidato.get("investigations", 0)},')
        lineas.append(f'        "controversy_score": {candidato.get("controversy_score", 0.0)},')
        lineas.append(f'        "party_changed_from": {_py_repr(candidato.get("party_changed_from"))},')

        # Campos adicionales informativos
        lineas.append(f'        "jne_id": {_py_repr(candidato.get("jne_id", ""))},')
        lineas.append(f'        "foto_url": {_py_repr(candidato.get("foto_url"))},')
        lineas.append(f'        "hoja_vida_url": {_py_repr(candidato.get("hoja_vida_url", ""))},')
        lineas.append(f'        "educacion": {_py_repr(candidato.get("educacion", ""))},')
        lineas.append(f'        "experiencia_politica": {_py_repr(candidato.get("experiencia_politica", ""))},')
        lineas.append("    },")

    lineas.append("}")
    lineas.append("")
    lineas.append("")

    # Indices auxiliares para busquedas rapidas
    lineas.append("# Indice por partido: {partido_slug: [candidate_ids]}")
    lineas.append("CANDIDATES_BY_PARTY: dict[str, list[int]] = {}")
    lineas.append("for _id, _c in CANDIDATES.items():")
    lineas.append('    _party = _c["party_slug"]')
    lineas.append("    if _party not in CANDIDATES_BY_PARTY:")
    lineas.append("        CANDIDATES_BY_PARTY[_party] = []")
    lineas.append("    CANDIDATES_BY_PARTY[_party].append(_id)")
    lineas.append("")
    lineas.append("")

    lineas.append("# Indice por region: {region_slug: [candidate_ids]}")
    lineas.append("CANDIDATES_BY_REGION: dict[str, list[int]] = {}")
    lineas.append("for _id, _c in CANDIDATES.items():")
    lineas.append('    _region = _c["region_slug"]')
    lineas.append("    if _region:")
    lineas.append("        if _region not in CANDIDATES_BY_REGION:")
    lineas.append("            CANDIDATES_BY_REGION[_region] = []")
    lineas.append("        CANDIDATES_BY_REGION[_region].append(_id)")
    lineas.append("")
    lineas.append("")

    # Estadisticas de la importacion
    lineas.append("# Estadisticas de la ultima importacion")
    # Usar repr() en vez de json.dumps para generar Python valido (None vs null, True vs true)
    import pprint
    stats_str = pprint.pformat(stats, indent=4, width=100)
    lineas.append(f"IMPORT_STATS: dict = {stats_str}")
    lineas.append("")

    return "\n".join(lineas)


def cargar_a_app(input_path: str) -> None:
    """Carga candidatos del JSON unificado a la app como modulo Python.

    Args:
        input_path: Ruta al archivo JSON unificado (salida de merge_data).
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidatos = data.get("candidatos", [])
    stats = data.get("stats", {})

    if not candidatos:
        print("ERROR: No se encontraron candidatos en el archivo de entrada.")
        sys.exit(1)

    print(f"Cargando {len(candidatos)} candidatos a la app...")

    # Generar modulo Python
    contenido = _generar_modulo_python(candidatos, stats)

    # Asegurar que el directorio existe
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Escribir archivo
    with open(CANDIDATES_PY, "w", encoding="utf-8") as f:
        f.write(contenido)

    print(f"Modulo generado: {CANDIDATES_PY}")
    print(f"  Candidatos: {len(candidatos)}")
    print(f"  Partidos: {len(stats.get('por_partido', {}))}")
    print(f"  Regiones: {len(stats.get('por_region', {}))}")

    # Verificar que el modulo se puede importar
    print("\nVerificando importacion del modulo...")
    try:
        # Limpiar cache de importaciones
        import importlib
        if "app.data.candidates" in sys.modules:
            del sys.modules["app.data.candidates"]

        # Intentar importar
        sys.path.insert(0, str(APP_DATA_DIR.parent.parent))
        spec = importlib.util.spec_from_file_location("candidates", str(CANDIDATES_PY))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            print(f"  OK - CANDIDATES tiene {len(mod.CANDIDATES)} entradas")
            print(f"  OK - CANDIDATES_BY_PARTY tiene {len(mod.CANDIDATES_BY_PARTY)} partidos")
            print(f"  OK - CANDIDATES_BY_REGION tiene {len(mod.CANDIDATES_BY_REGION)} regiones")
        else:
            print("  ADVERTENCIA: No se pudo verificar la importacion")
    except Exception as e:
        print(f"  ERROR al verificar importacion: {e}")
        print("  El archivo fue generado pero puede tener errores de sintaxis")


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Carga datos de candidatos unificados a la app de VotoClaro. "
                    "Genera el modulo app/data/candidates.py con todos los "
                    "candidatos como un diccionario Python importable.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo:
  python -m scrapers.load_to_app --input data/candidates_final.json

Esto genera:
  app/data/candidates.py  - Modulo Python con CANDIDATES dict
                            CANDIDATES_BY_PARTY index
                            CANDIDATES_BY_REGION index
                            IMPORT_STATS metadata
        """,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Archivo JSON unificado (salida de merge_data.py)",
    )

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERROR: No se encontro el archivo: {args.input}")
        sys.exit(1)

    cargar_a_app(args.input)


if __name__ == "__main__":
    main()
