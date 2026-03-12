#!/usr/bin/env python3
"""
Scraper de Voto Informado — JNE Perú 2026.

Descarga TODOS los candidatos (presidenciales, senadores, diputados)
desde la API pública de web.jne.gob.pe.

Uso:
    python scrapers/jne_scraper.py                    # Descarga todo
    python scrapers/jne_scraper.py --tipo senadores    # Solo senadores
    python scrapers/jne_scraper.py --tipo diputados    # Solo diputados
    python scrapers/jne_scraper.py --tipo presidencial # Solo presidenciales
    python scrapers/jne_scraper.py --stats             # Solo mostrar estadísticas
"""

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen, ProxyHandler, build_opener
from urllib.error import URLError

# === CONFIG ===
API_URL = "https://web.jne.gob.pe/serviciovotoinformado/api/votoinf/listarCanditatos"
FOTO_BASE = "https://mpesije.jne.gob.pe/apidocs"
PROCESO_ELECTORAL = 124  # Elecciones Generales 2026

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://votoinformado.jne.gob.pe",
    "Referer": "https://votoinformado.jne.gob.pe/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}

# Tipos de elección
TIPO_PRESIDENCIAL = 1
TIPO_DIPUTADOS = 15
TIPO_SENADORES = 20

# Códigos de departamento para diputados y senadores
DEPARTAMENTOS = {
    "010000": "AMAZONAS",
    "020000": "ANCASH",
    "030000": "APURIMAC",
    "040000": "AREQUIPA",
    "050000": "AYACUCHO",
    "060000": "CAJAMARCA",
    "240000": "CALLAO",
    "070000": "CUSCO",
    "080000": "HUANCAVELICA",
    "090000": "HUANUCO",
    "100000": "ICA",
    "110000": "JUNIN",
    "120000": "LA LIBERTAD",
    "130000": "LAMBAYEQUE",
    "140100": "LIMA METROPOLITANA",
    "140000": "LIMA PROVINCIAS",
    "150000": "LORETO",
    "160000": "MADRE DE DIOS",
    "170000": "MOQUEGUA",
    "180000": "PASCO",
    "140133": "PERUANOS RESIDENTES EN EL EXTRANJERO",
    "190000": "PIURA",
    "200000": "PUNO",
    "210000": "SAN MARTIN",
    "220000": "TACNA",
    "230000": "TUMBES",
    "250000": "UCAYALI",
}

# Mapping de partidos JNE → abreviatura VotoClaro
PARTY_MAPPING = {
    "RENOVACION POPULAR": "rp",
    "FUERZA POPULAR": "fp",
    "PARTIDO MORADO": "pm",
    "JUNTOS POR EL PERU": "jpp",
    # AP no participa directamente en 2026 — hay "AHORA NACION" (alianza)
    "AHORA NACION - AN": "an",
    "PARTIDO DEMOCRATICO SOMOS PERU": "sc",
    "PARTIDO POLITICO NACIONAL PERU LIBRE": "pl",
    "ALIANZA PARA EL PROGRESO": "app",
    "PODEMOS PERU": "pod",
    "PARTIDO FRENTE DE LA ESPERANZA 2021": "fep",
    "AVANZA PAIS - PARTIDO DE INTEGRACION SOCIAL": "avp",
    # Partidos adicionales que podemos agregar
    "PARTIDO APRISTA PERUANO": "apra",
    "ALIANZA ELECTORAL VENCEREMOS": "venc",
    "PARTIDO POLITICO COOPERACION POPULAR": "cp",
    "PARTIDO DE LOS TRABAJADORES Y EMPRENDEDORES PTE - PERU": "pte",
    "FUERZA Y LIBERTAD": "fyl",
    "UNIDAD NACIONAL": "un",
    # Partidos adicionales descubiertos en scraping
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


_opener = None


def _get_opener(proxy: str | None = None):
    """Build a URL opener, optionally with proxy support."""
    global _opener
    if _opener is not None:
        return _opener
    if proxy:
        # Format: host:port:user:pass → http://user:pass@host:port
        parts = proxy.split(":")
        if len(parts) == 4:
            host, port, user, passwd = parts
            proxy_url = f"http://{user}:{passwd}@{host}:{port}"
        elif len(parts) == 2:
            proxy_url = f"http://{parts[0]}:{parts[1]}"
        else:
            proxy_url = proxy
        handler = ProxyHandler({"https": proxy_url, "http": proxy_url})
        _opener = build_opener(handler)
        print(f"🔒 Usando proxy: {host}:{port}" if len(parts) >= 2 else f"🔒 Proxy: {proxy_url}")
    else:
        _opener = build_opener()
    return _opener


def fetch_candidates(tipo_eleccion: int, departamento: str = "") -> list[dict]:
    """Llama a la API de JNE y devuelve la lista de candidatos."""
    payload = json.dumps({
        "idProcesoElectoral": PROCESO_ELECTORAL,
        "strUbiDepartamento": departamento,
        "idTipoEleccion": tipo_eleccion,
    }).encode("utf-8")

    req = Request(API_URL, data=payload, headers=HEADERS, method="POST")
    opener = _get_opener()

    try:
        with opener.open(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("data", [])
    except URLError as e:
        print(f"  ✗ Error: {e}", file=sys.stderr)
        return []


def normalize_candidate(raw: dict) -> dict:
    """Normaliza un candidato del formato JNE al formato VotoClaro."""
    nombre = f"{raw['strApellidoPaterno']} {raw['strApellidoMaterno']}, {raw['strNombres']}"
    nombre_completo = f"{raw['strNombres']} {raw['strApellidoPaterno']} {raw['strApellidoMaterno']}"

    foto_guid = raw.get("strGuidFoto", "")
    foto_url = f"{FOTO_BASE}/{foto_guid}.jpg" if foto_guid else None

    partido_jne = raw.get("strOrganizacionPolitica", "")
    partido_vc = PARTY_MAPPING.get(partido_jne, "")

    return {
        # Identificación
        "jne_id": raw.get("strCodExpedienteExt", ""),
        "dni": raw.get("strDocumentoIdentidad", ""),
        "nombre_completo": nombre_completo.strip(),
        "nombre_ordenado": nombre.strip(),
        "apellido_paterno": raw.get("strApellidoPaterno", ""),
        "apellido_materno": raw.get("strApellidoMaterno", ""),
        "nombres": raw.get("strNombres", ""),
        "sexo": raw.get("strSexo", ""),
        "fecha_nacimiento": raw.get("strFechaNacimiento", ""),

        # Partido
        "partido_jne": partido_jne,
        "partido_id_jne": raw.get("idOrganizacionPolitica"),
        "partido_votoclaro": partido_vc,

        # Cargo
        "tipo_eleccion": raw.get("strTipoEleccion", ""),
        "cargo": raw.get("strCargo", ""),
        "posicion_lista": raw.get("intPosicion"),
        "ubigeo": raw.get("strUbigeo", ""),
        "departamento": raw.get("strDepartamento", ""),
        "provincia": raw.get("strProvincia", ""),

        # Estado
        "estado": raw.get("strEstadoCandidato", ""),
        "es_nativo": raw.get("strEsNativo", ""),

        # Foto
        "foto_guid": foto_guid,
        "foto_url": foto_url,

        # Estos campos se llenan después con el merge de otras fuentes
        "antecedentes_penales": None,
        "sentencias": None,
        "voted_pro_crime": None,
        "pro_crime_vote_count": None,
        "is_reelection": None,
        "party_changed_from": None,
        "investigations": None,
        "controversy_score": None,
    }


def scrape_presidenciales() -> list[dict]:
    """Descarga candidatos presidenciales."""
    print("📥 Descargando candidatos presidenciales...")
    raw = fetch_candidates(TIPO_PRESIDENCIAL)
    candidates = [normalize_candidate(c) for c in raw]
    print(f"  ✓ {len(candidates)} candidatos presidenciales")
    return candidates


def scrape_senadores() -> list[dict]:
    """Descarga senadores (distrito único nacional, pero iteramos por depto)."""
    print("📥 Descargando senadores...")
    # Senadores son distrito único, pero la API acepta sin departamento
    raw = fetch_candidates(TIPO_SENADORES, "")
    candidates = [normalize_candidate(c) for c in raw]
    print(f"  ✓ {len(candidates)} senadores")
    return candidates


def scrape_diputados() -> list[dict]:
    """Descarga diputados por cada departamento."""
    print("📥 Descargando diputados por departamento...")
    all_candidates = []

    for codigo, nombre in sorted(DEPARTAMENTOS.items(), key=lambda x: x[1]):
        raw = fetch_candidates(TIPO_DIPUTADOS, codigo)
        candidates = [normalize_candidate(c) for c in raw]
        all_candidates.extend(candidates)
        print(f"  ✓ {nombre}: {len(candidates)} diputados")
        time.sleep(0.5)  # Ser amables con el servidor

    print(f"  Total diputados: {len(all_candidates)}")
    return all_candidates


def print_stats(candidates: list[dict]):
    """Imprime estadísticas de los candidatos descargados."""
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS")
    print("=" * 60)

    # Por tipo
    tipos = {}
    for c in candidates:
        t = c["tipo_eleccion"]
        tipos[t] = tipos.get(t, 0) + 1
    print(f"\nTotal candidatos: {len(candidates)}")
    for t, n in sorted(tipos.items()):
        print(f"  {t}: {n}")

    # Por partido
    print(f"\nPor partido:")
    partidos = {}
    for c in candidates:
        p = c["partido_jne"]
        partidos[p] = partidos.get(p, 0) + 1
    for p, n in sorted(partidos.items(), key=lambda x: -x[1]):
        mapped = PARTY_MAPPING.get(p, "❌ SIN MAPEAR")
        print(f"  {p}: {n} → [{mapped}]")

    # Partidos sin mapear
    sin_mapear = [p for p in partidos if p not in PARTY_MAPPING]
    if sin_mapear:
        print(f"\n⚠️  {len(sin_mapear)} partidos SIN MAPEAR a VotoClaro:")
        for p in sorted(sin_mapear):
            print(f"  - {p} ({partidos[p]} candidatos)")

    # Por departamento (diputados)
    diputados = [c for c in candidates if c["cargo"] == "DIPUTADO"]
    if diputados:
        print(f"\nDiputados por departamento:")
        deptos = {}
        for c in diputados:
            d = c["departamento"]
            deptos[d] = deptos.get(d, 0) + 1
        for d, n in sorted(deptos.items()):
            print(f"  {d}: {n}")

    # Por estado
    print(f"\nPor estado de candidatura:")
    estados = {}
    for c in candidates:
        e = c["estado"]
        estados[e] = estados.get(e, 0) + 1
    for e, n in sorted(estados.items(), key=lambda x: -x[1]):
        print(f"  {e}: {n}")

    # Sexo
    print(f"\nPor sexo:")
    sexos = {}
    for c in candidates:
        s = c["sexo"]
        sexos[s] = sexos.get(s, 0) + 1
    for s, n in sorted(sexos.items()):
        pct = n / len(candidates) * 100
        print(f"  {s}: {n} ({pct:.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="Scraper de candidatos JNE — Elecciones Generales 2026"
    )
    parser.add_argument(
        "--tipo",
        choices=["presidencial", "senadores", "diputados", "todo"],
        default="todo",
        help="Tipo de candidatos a descargar (default: todo)",
    )
    parser.add_argument(
        "-o", "--output",
        default="scrapers/data/jne_candidatos.json",
        help="Archivo de salida (default: scrapers/data/jne_candidatos.json)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Solo mostrar estadísticas de un archivo existente",
    )
    parser.add_argument(
        "--proxy",
        default=None,
        help="Proxy en formato host:port:user:pass (ej: proxy.com:8080:user:pass)",
    )
    args = parser.parse_args()

    # Inicializar proxy si se proporcionó
    if args.proxy:
        _get_opener(args.proxy)

    output_path = Path(args.output)

    if args.stats:
        if not output_path.exists():
            print(f"✗ No existe {output_path}", file=sys.stderr)
            sys.exit(1)
        candidates = json.loads(output_path.read_text())
        print_stats(candidates)
        return

    # Descargar
    candidates = []

    if args.tipo in ("presidencial", "todo"):
        candidates.extend(scrape_presidenciales())

    if args.tipo in ("senadores", "todo"):
        candidates.extend(scrape_senadores())

    if args.tipo in ("diputados", "todo"):
        candidates.extend(scrape_diputados())

    # Estadísticas
    print_stats(candidates)

    # Guardar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(candidates, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n✅ Guardado en {output_path}")
    print(f"   {len(candidates)} candidatos, {output_path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
