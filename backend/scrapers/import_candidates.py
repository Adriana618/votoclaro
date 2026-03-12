#!/usr/bin/env python3
"""Importador de candidatos desde datos de Voto Informado (JNE).

Lee un archivo JSON con la salida del spider de Voto Informado,
valida los datos, mapea partidos y regiones a los slugs internos,
calcula el controversy_score inicial, y genera un JSON validado
listo para la app.

Uso:
    python -m scrapers.import_candidates --input datos_jne.json --output candidatos_validados.json
"""

import argparse
import json
import sys
from pathlib import Path

# --- Mapeo de siglas JNE a slugs internos de la app ---
# Las siglas que aparecen en Voto Informado pueden diferir de nuestros slugs
PARTY_SIGLA_TO_SLUG: dict[str, str] = {
    "FP": "fp",
    "RP": "rp",
    "PM": "pm",
    "JPP": "jpp",
    "AP": "ap",
    "SP": "sc",       # Somos Peru usa 'sc' internamente
    "PL": "pl",
    "AN": "an",
    "APP": "app",
    "PP": "pod",       # Podemos Peru usa 'pod' internamente
    "FE": "fep",       # Frente Esperanza usa 'fep'
    "AVP": "avp",
}

# --- Mapeo de nombres de region (MAYUSCULAS del JNE) a slugs internos ---
REGION_NAME_TO_SLUG: dict[str, str] = {
    "AMAZONAS": "amazonas",
    "ANCASH": "ancash",
    "APURIMAC": "apurimac",
    "AREQUIPA": "arequipa",
    "AYACUCHO": "ayacucho",
    "CAJAMARCA": "cajamarca",
    "CALLAO": "callao",
    "CUSCO": "cusco",
    "HUANCAVELICA": "huancavelica",
    "HUANUCO": "huanuco",
    "ICA": "ica",
    "JUNIN": "junin",
    "LA LIBERTAD": "la-libertad",
    "LAMBAYEQUE": "lambayeque",
    "LIMA PROVINCIAS": "lima-provincias",
    "LIMA": "lima",
    "LIMA METROPOLITANA": "lima",
    "LORETO": "loreto",
    "MADRE DE DIOS": "madre-de-dios",
    "MOQUEGUA": "moquegua",
    "PASCO": "pasco",
    "PIURA": "piura",
    "PUNO": "puno",
    "SAN MARTIN": "san-martin",
    "TACNA": "tacna",
    "TUMBES": "tumbes",
    "UCAYALI": "ucayali",
    "PERUANOS EN EL EXTRANJERO": "extranjero",
    "EXTRANJERO": "extranjero",
    # Senadores postulan a nivel nacional, no tienen region especifica
    "NACIONAL": None,
}

# --- Pesos para el calculo inicial de controversy_score ---
# (Coincide con app/services/controversy.py)
WEIGHT_CRIMINAL_RECORD = 30
WEIGHT_SENTENCIAS = 20  # Usamos el peso de voted_pro_crime temporalmente


def _calcular_score_inicial(candidato: dict) -> float:
    """Calcula un score de controversia inicial basado solo en datos de JNE.

    Solo usa antecedentes_penales y sentencias. Los votos pro-crimen
    e investigaciones se agregan despues en el merge.
    """
    score = 0.0
    if candidato.get("antecedentes_penales"):
        score += WEIGHT_CRIMINAL_RECORD
    if candidato.get("sentencias"):
        score += WEIGHT_SENTENCIAS
    return min(score, 100.0)


def _validar_candidato(candidato: dict, index: int) -> list[str]:
    """Valida un candidato individual. Retorna lista de errores."""
    errores = []

    # Campos requeridos
    for campo in ["jne_id", "nombre_completo", "dni", "partido_sigla", "region", "cargo"]:
        if not candidato.get(campo):
            errores.append(f"Candidato #{index}: falta campo requerido '{campo}'")

    # Validar DNI (8 digitos)
    dni = candidato.get("dni", "")
    if dni and (len(dni) != 8 or not dni.isdigit()):
        errores.append(f"Candidato #{index} ({candidato.get('nombre_completo', '?')}): "
                       f"DNI invalido '{dni}' (debe ser 8 digitos)")

    # Validar partido
    sigla = candidato.get("partido_sigla", "")
    if sigla and sigla.upper() not in PARTY_SIGLA_TO_SLUG:
        errores.append(f"Candidato #{index} ({candidato.get('nombre_completo', '?')}): "
                       f"sigla de partido desconocida '{sigla}'. "
                       f"Siglas validas: {list(PARTY_SIGLA_TO_SLUG.keys())}")

    # Validar region
    region = candidato.get("region", "")
    if region and region.upper() not in REGION_NAME_TO_SLUG:
        errores.append(f"Candidato #{index} ({candidato.get('nombre_completo', '?')}): "
                       f"region desconocida '{region}'")

    # Validar cargo
    cargo = candidato.get("cargo", "")
    if cargo and cargo.upper() not in ("SENADOR", "DIPUTADO"):
        errores.append(f"Candidato #{index} ({candidato.get('nombre_completo', '?')}): "
                       f"cargo invalido '{cargo}' (debe ser SENADOR o DIPUTADO)")

    return errores


def importar_candidatos(input_path: str, output_path: str | None = None) -> dict:
    """Importa y valida candidatos desde un archivo JSON de Voto Informado.

    Args:
        input_path: Ruta al archivo JSON de entrada.
        output_path: Ruta al archivo JSON de salida (opcional).

    Returns:
        Diccionario con candidatos validados y estadisticas.
    """
    # Leer archivo de entrada
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidatos_raw = data.get("candidatos", [])
    if not candidatos_raw:
        print("ERROR: No se encontraron candidatos en el archivo de entrada.")
        sys.exit(1)

    print(f"Procesando {len(candidatos_raw)} candidatos...")

    # Validar todos los candidatos
    todos_errores: list[str] = []
    candidatos_validos: list[dict] = []
    candidatos_con_errores = 0

    # Estadisticas
    stats = {
        "total_procesados": len(candidatos_raw),
        "validos": 0,
        "con_errores": 0,
        "por_partido": {},
        "por_region": {},
        "por_cargo": {"SENADOR": 0, "DIPUTADO": 0},
        "con_antecedentes": 0,
        "con_sentencias": 0,
        "score_promedio": 0.0,
    }

    for i, candidato in enumerate(candidatos_raw):
        errores = _validar_candidato(candidato, i)
        if errores:
            todos_errores.extend(errores)
            candidatos_con_errores += 1
            continue

        # Mapear a formato interno
        sigla = candidato["partido_sigla"].upper()
        region_raw = candidato["region"].upper()
        partido_slug = PARTY_SIGLA_TO_SLUG[sigla]
        region_slug = REGION_NAME_TO_SLUG[region_raw]
        cargo = candidato["cargo"].upper()

        # Calcular score inicial
        score = _calcular_score_inicial(candidato)

        # Construir candidato validado en formato interno
        candidato_validado = {
            "jne_id": candidato["jne_id"],
            "name": candidato["nombre_completo"],
            "dni": candidato["dni"],
            "party_slug": partido_slug,
            "region_slug": region_slug,
            "cargo": cargo,
            "position_number": candidato.get("posicion_lista"),
            "has_criminal_record": bool(candidato.get("antecedentes_penales", False)),
            "criminal_record_detail": candidato.get("antecedentes_detalle"),
            "has_sentencias": bool(candidato.get("sentencias", False)),
            "sentencias_detail": candidato.get("sentencias_detalle"),
            "voted_pro_crime": False,  # Se llena en el merge con votaciones
            "is_reelection": False,    # Se llena en el merge con votaciones
            "investigations": 0,       # Se llena en el merge con Convoca
            "party_changed_from": None,
            "controversy_score": score,
            # Datos informativos adicionales
            "educacion": candidato.get("educacion", ""),
            "experiencia_politica": candidato.get("experiencia_politica", ""),
            "bienes_muebles": candidato.get("bienes_muebles", 0),
            "bienes_inmuebles": candidato.get("bienes_inmuebles", 0),
            "ingresos_anuales": candidato.get("ingresos_anuales", 0),
            "foto_url": candidato.get("foto_url"),
            "hoja_vida_url": candidato.get("hoja_vida_url", ""),
        }

        candidatos_validos.append(candidato_validado)

        # Actualizar estadisticas
        stats["por_partido"][partido_slug] = stats["por_partido"].get(partido_slug, 0) + 1
        if region_slug:
            stats["por_region"][region_slug] = stats["por_region"].get(region_slug, 0) + 1
        stats["por_cargo"][cargo] += 1
        if candidato_validado["has_criminal_record"]:
            stats["con_antecedentes"] += 1
        if candidato_validado["has_sentencias"]:
            stats["con_sentencias"] += 1

    stats["validos"] = len(candidatos_validos)
    stats["con_errores"] = candidatos_con_errores
    if candidatos_validos:
        stats["score_promedio"] = round(
            sum(c["controversy_score"] for c in candidatos_validos) / len(candidatos_validos), 2
        )

    # Mostrar resultados
    print(f"\n--- Resultados de importacion ---")
    print(f"Total procesados: {stats['total_procesados']}")
    print(f"Validos: {stats['validos']}")
    print(f"Con errores: {stats['con_errores']}")
    print(f"Con antecedentes penales: {stats['con_antecedentes']}")
    print(f"Con sentencias: {stats['con_sentencias']}")
    print(f"Score controversia promedio: {stats['score_promedio']}")
    print(f"\nPor partido:")
    for partido, count in sorted(stats["por_partido"].items()):
        print(f"  {partido}: {count}")
    print(f"\nPor cargo:")
    for cargo, count in stats["por_cargo"].items():
        print(f"  {cargo}: {count}")

    if todos_errores:
        print(f"\n--- Errores ({len(todos_errores)}) ---")
        for error in todos_errores:
            print(f"  ! {error}")

    # Construir resultado final
    resultado = {
        "fecha_importacion": data.get("fecha_extraccion", ""),
        "stats": stats,
        "candidatos": candidatos_validos,
    }

    # Guardar si se especifico archivo de salida
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\nArchivo de salida guardado en: {output_path}")

    return resultado


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Importa candidatos desde datos de Voto Informado (JNE). "
                    "Valida, mapea partidos/regiones, calcula score inicial.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo:
  python -m scrapers.import_candidates --input data/voto_informado.json --output data/candidatos.json

Siglas de partido soportadas:
  FP, RP, PM, JPP, AP, SP, PL, AN, APP, PP, FE, AVP
        """,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Archivo JSON de entrada con datos de Voto Informado",
    )
    parser.add_argument(
        "--output", "-o",
        required=False,
        help="Archivo JSON de salida con candidatos validados (opcional)",
    )

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERROR: No se encontro el archivo de entrada: {args.input}")
        sys.exit(1)

    importar_candidatos(args.input, args.output)


if __name__ == "__main__":
    main()
