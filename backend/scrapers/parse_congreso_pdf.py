#!/usr/bin/env python3
"""Parser de PDFs de votacion del Congreso de la Republica.

Extrae tablas de votacion de los PDFs publicados en congreso.gob.pe.
Los PDFs tipicamente contienen tablas con columnas:
  Congresista | Grupo Parlamentario | Voto

Usa pdfplumber para extraer las tablas y genera JSON en el formato
del schema congreso_votaciones.json.

Uso:
    python -m scrapers.parse_congreso_pdf --input votacion.pdf --output votacion.json
    python -m scrapers.parse_congreso_pdf --input votacion.pdf --proyecto "PL-01234" --titulo "Ley X" --fecha 2025-06-15
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber no esta instalado. Ejecutar:")
    print("  pip install pdfplumber")
    sys.exit(1)


# Patrones comunes en PDFs del Congreso para identificar el tipo de voto
VOTO_PATTERNS = {
    "A FAVOR": re.compile(r"(?:a\s+favor|si|sí|afirmativo)", re.IGNORECASE),
    "EN CONTRA": re.compile(r"(?:en\s+contra|no|negativo)", re.IGNORECASE),
    "ABSTENCION": re.compile(r"(?:abstenci[oó]n|abstenci[oó]n|se\s+abstiene)", re.IGNORECASE),
    "AUSENTE": re.compile(r"(?:ausente|no\s+present[eo]|sin\s+registro)", re.IGNORECASE),
}

# Patrones para limpiar nombres de congresistas
PREFIJOS_IGNORAR = re.compile(
    r"^(?:Sr\.|Sra\.|Cong\.|Congresista|Hon\.)\s*", re.IGNORECASE
)


def _limpiar_nombre(nombre: str) -> str:
    """Limpia el nombre de un congresista removiendo prefijos y espacios extra."""
    if not nombre:
        return ""
    nombre = PREFIJOS_IGNORAR.sub("", nombre).strip()
    # Normalizar espacios multiples
    nombre = re.sub(r"\s+", " ", nombre)
    return nombre.upper()


def _normalizar_voto(texto_voto: str) -> str:
    """Normaliza el texto del voto a uno de los 4 valores validos."""
    if not texto_voto:
        return "AUSENTE"

    texto = texto_voto.strip()
    for voto_normalizado, patron in VOTO_PATTERNS.items():
        if patron.search(texto):
            return voto_normalizado

    # Si no coincide con ningun patron, intentar match directo
    texto_upper = texto.upper().strip()
    if texto_upper in ("A FAVOR", "EN CONTRA", "ABSTENCION", "AUSENTE"):
        return texto_upper

    print(f"  ADVERTENCIA: voto no reconocido '{texto_voto}', marcando como AUSENTE")
    return "AUSENTE"


def _detectar_columnas(tabla: list[list[str]]) -> dict[str, int]:
    """Detecta la posicion de las columnas en la tabla.

    Los PDFs del Congreso varian en formato, asi que intentamos detectar
    las columnas por sus encabezados.

    Returns:
        Diccionario con indices: congresista, grupo, voto
    """
    # Buscar en las primeras filas un encabezado
    for i, fila in enumerate(tabla[:5]):
        if not fila:
            continue

        fila_texto = [str(c).lower().strip() if c else "" for c in fila]

        # Buscar columna de congresista
        col_congresista = None
        col_grupo = None
        col_voto = None

        for j, texto in enumerate(fila_texto):
            if any(kw in texto for kw in ["congresista", "parlamentario", "nombre", "apellido"]):
                col_congresista = j
            elif any(kw in texto for kw in ["grupo", "bancada", "partido"]):
                col_grupo = j
            elif any(kw in texto for kw in ["voto", "votacion", "sentido"]):
                col_voto = j

        if col_congresista is not None and col_voto is not None:
            return {
                "congresista": col_congresista,
                "grupo": col_grupo if col_grupo is not None else -1,
                "voto": col_voto,
                "header_row": i,
            }

    # Si no se detectan encabezados, asumir formato comun:
    # Columna 0 = Numero, 1 = Congresista, 2 = Grupo, 3 = Voto
    # o: 0 = Congresista, 1 = Grupo, 2 = Voto
    if tabla and len(tabla[0]) >= 3:
        num_cols = len(tabla[0])
        if num_cols >= 4:
            return {"congresista": 1, "grupo": 2, "voto": 3, "header_row": 0}
        else:
            return {"congresista": 0, "grupo": 1, "voto": 2, "header_row": 0}

    return {"congresista": 0, "grupo": -1, "voto": 1, "header_row": 0}


def _es_fila_datos(fila: list[str], col_map: dict[str, int]) -> bool:
    """Determina si una fila contiene datos de un congresista (no encabezado/pie)."""
    if not fila:
        return False

    # Verificar que la celda del congresista tiene contenido
    idx_congresista = col_map["congresista"]
    if idx_congresista >= len(fila):
        return False

    nombre = str(fila[idx_congresista]).strip() if fila[idx_congresista] else ""
    if not nombre or len(nombre) < 3:
        return False

    # Filtrar filas que son encabezados, totales o pies de pagina
    nombre_lower = nombre.lower()
    palabras_excluir = [
        "total", "resultado", "votacion", "congresista", "nombre",
        "aprobado", "rechazado", "pagina", "fecha", "sesion",
    ]
    if any(palabra in nombre_lower for palabra in palabras_excluir):
        return False

    return True


def parsear_pdf(
    input_path: str,
    proyecto_ley: str = "",
    titulo_ley: str = "",
    fecha: str = "",
    es_ley_procrimen: bool = False,
    output_path: str | None = None,
) -> dict:
    """Extrae datos de votacion de un PDF del Congreso.

    Args:
        input_path: Ruta al archivo PDF.
        proyecto_ley: Numero del proyecto de ley.
        titulo_ley: Titulo de la ley votada.
        fecha: Fecha de la votacion (YYYY-MM-DD).
        es_ley_procrimen: Si esta votacion es de una ley pro-crimen.
        output_path: Ruta de salida para el JSON (opcional).

    Returns:
        Diccionario con las votaciones extraidas.
    """
    path = Path(input_path)
    if not path.exists():
        print(f"ERROR: No se encontro el archivo: {input_path}")
        sys.exit(1)

    print(f"Parseando PDF: {path.name}")

    votaciones: list[dict] = []
    paginas_procesadas = 0
    tablas_encontradas = 0

    with pdfplumber.open(str(path)) as pdf:
        print(f"  Paginas: {len(pdf.pages)}")

        for page_num, page in enumerate(pdf.pages, 1):
            # Intentar extraer tablas de la pagina
            tablas = page.extract_tables()

            if not tablas:
                # Si no hay tablas, intentar con configuraciones alternativas
                tablas = page.extract_tables(
                    table_settings={
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                        "min_words_vertical": 2,
                        "min_words_horizontal": 1,
                    }
                )

            paginas_procesadas += 1

            for tabla in tablas:
                if not tabla or len(tabla) < 2:
                    continue

                tablas_encontradas += 1
                col_map = _detectar_columnas(tabla)

                # Procesar filas de datos (saltar encabezado)
                start_row = col_map.get("header_row", 0) + 1
                for fila in tabla[start_row:]:
                    if not _es_fila_datos(fila, col_map):
                        continue

                    # Extraer datos de la fila
                    idx_c = col_map["congresista"]
                    idx_g = col_map["grupo"]
                    idx_v = col_map["voto"]

                    nombre = _limpiar_nombre(
                        str(fila[idx_c]) if idx_c < len(fila) and fila[idx_c] else ""
                    )
                    grupo = (
                        str(fila[idx_g]).strip()
                        if idx_g >= 0 and idx_g < len(fila) and fila[idx_g]
                        else ""
                    )
                    voto_raw = (
                        str(fila[idx_v]).strip()
                        if idx_v < len(fila) and fila[idx_v]
                        else ""
                    )

                    if not nombre:
                        continue

                    voto = _normalizar_voto(voto_raw)

                    votaciones.append({
                        "congresista": nombre,
                        "grupo_parlamentario": grupo.upper(),
                        "proyecto_ley": proyecto_ley,
                        "titulo_ley": titulo_ley,
                        "es_ley_procrimen": es_ley_procrimen,
                        "voto": voto,
                        "fecha": fecha or str(date.today()),
                    })

    print(f"  Paginas procesadas: {paginas_procesadas}")
    print(f"  Tablas encontradas: {tablas_encontradas}")
    print(f"  Votaciones extraidas: {len(votaciones)}")

    # Resumen de votos
    if votaciones:
        resumen = {}
        for v in votaciones:
            resumen[v["voto"]] = resumen.get(v["voto"], 0) + 1
        print(f"  Resumen: {resumen}")

    resultado = {
        "fecha_extraccion": str(date.today()),
        "archivo_fuente": path.name,
        "total_registros": len(votaciones),
        "votaciones": votaciones,
    }

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\nArchivo de salida guardado en: {output_path}")

    return resultado


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Extrae datos de votacion de PDFs del Congreso de la Republica. "
                    "Usa pdfplumber para parsear tablas con formato: "
                    "Congresista | Grupo Parlamentario | Voto.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Parsear un PDF simple
  python -m scrapers.parse_congreso_pdf --input votacion.pdf --output votacion.json

  # Parsear con metadatos de la ley
  python -m scrapers.parse_congreso_pdf \\
    --input votacion_crimen_organizado.pdf \\
    --proyecto "PL-01234/2024-CR" \\
    --titulo "Ley que modifica el codigo penal sobre crimen organizado" \\
    --fecha 2025-06-15 \\
    --procrimen \\
    --output votacion_crimen_organizado.json

Notas:
  - Los PDFs del Congreso varian en formato. El parser intenta detectar
    las columnas automaticamente.
  - Si el parser no detecta correctamente las columnas, revisar la salida
    y reportar el formato del PDF para mejorar la deteccion.
  - Usar --procrimen para marcar votaciones de las 6 leyes pro-crimen.
        """,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Archivo PDF de votacion del Congreso",
    )
    parser.add_argument(
        "--output", "-o",
        required=False,
        help="Archivo JSON de salida (opcional, si no se especifica se imprime a stdout)",
    )
    parser.add_argument(
        "--proyecto",
        default="",
        help="Numero del proyecto de ley (e.g. 'PL-01234/2024-CR')",
    )
    parser.add_argument(
        "--titulo",
        default="",
        help="Titulo o descripcion de la ley votada",
    )
    parser.add_argument(
        "--fecha",
        default="",
        help="Fecha de la votacion en formato YYYY-MM-DD",
    )
    parser.add_argument(
        "--procrimen",
        action="store_true",
        default=False,
        help="Marcar esta votacion como ley pro-crimen",
    )

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERROR: No se encontro el archivo: {args.input}")
        sys.exit(1)

    resultado = parsear_pdf(
        input_path=args.input,
        proyecto_ley=args.proyecto,
        titulo_ley=args.titulo,
        fecha=args.fecha,
        es_ley_procrimen=args.procrimen,
        output_path=args.output,
    )

    # Si no hay archivo de salida, imprimir JSON a stdout
    if not args.output:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
