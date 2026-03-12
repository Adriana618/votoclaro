#!/usr/bin/env python3
"""
Scraper del Congreso de la República del Perú.

Descarga proyectos de ley, extrae PDFs de votación del pleno,
y parsea los votos individuales de cada congresista.

Uso:
    python scrapers/congreso_scraper.py                          # Descarga leyes controversiales
    python scrapers/congreso_scraper.py --keyword "penal"        # Buscar por palabra clave
    python scrapers/congreso_scraper.py --pley 13349             # Un proyecto específico
    python scrapers/congreso_scraper.py --all-approved           # Todas las aprobadas
    python scrapers/congreso_scraper.py --stats                  # Estadísticas de datos existentes
"""

import argparse
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener, urlopen

# pdfplumber for PDF parsing
try:
    import pdfplumber
except ImportError:
    print("✗ pdfplumber requerido: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)

# pycryptodome for Congreso API encryption
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
except ImportError:
    print("✗ pycryptodome requerido: pip install pycryptodome", file=sys.stderr)
    sys.exit(1)

import base64

# === CONFIG ===
API_BASE = "https://api.congreso.gob.pe/spley-portal-service"
ENCRYPTION_KEY = b"ProdALg5ZrAsxBMD"  # AES-128 ECB, from portal JS
PROCESO_PARLAMENTARIO = 2021  # Periodo 2021-2026

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://wb2server.congreso.gob.pe",
    "Referer": "https://wb2server.congreso.gob.pe/spley-portal/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    ),
}

# Bancadas del Congreso 2021-2026
BANCADAS = [
    "FP", "APP", "PP", "PL", "RP", "JPP-VP", "SP", "AP",
    "AP-PIS", "BS", "HYD", "BDP", "NA",
]

# Mapping de bancada congreso → partido VotoClaro
BANCADA_TO_PARTY = {
    "FP": "fp",         # Fuerza Popular
    "APP": "app",        # Alianza Para el Progreso
    "PP": "pod",         # Podemos Perú
    "PL": "pl",          # Perú Libre
    "RP": "rp",          # Renovación Popular
    "JPP-VP": "jpp",     # Juntos por el Perú - Voces del Pueblo
    "SP": "sc",          # Somos Perú
    "AP": "an",          # Acción Popular (ahora parte de Ahora Nación)
    "AP-PIS": "avp",     # Avanza País
    "BS": "bs",          # Bancada Socialista
    "HYD": "hyd",        # Honor y Democracia
    "BDP": "bdp",        # Bloque Democrático Popular
    "NA": "",            # No Agrupados
}

# Leyes controversiales que queremos trackear para VotoClaro
# Categoría "pro-crimen" y otras controversiales
CONTROVERSIAL_KEYWORDS = [
    # Pro-crimen
    "prescripción", "extinción de dominio", "crimen organizado",
    "prisión preventiva", "colaboración eficaz", "lavado de activos",
    "enriquecimiento ilícito", "inhabilitación", "inmunidad",
    "detención preliminar", "flagrancia",
    # Anti-institucional
    "defensoría", "contraloría", "junta nacional de justicia",
    "tribunal constitucional", "sunedu",
    # Anti-derechos
    "género", "aborto", "eutanasia", "unión civil",
    # Anti-medio ambiente
    "minería ilegal", "deforestación", "áreas protegidas",
]

# Proyecto de ley numbers conocidos como controversiales
KNOWN_CONTROVERSIAL_PLEYS = [
    # Pro-crimen / debilitan justicia
    6951,   # Ley que modifica la prisión preventiva
    1867,   # Ley que modifica el Código Penal sobre crimen organizado
    2474,   # Ley sobre prescripción de delitos
    6611,   # Ley de extinción de dominio
    # Anti-institucional
    2917,   # Ley que limita funciones de la Defensoría del Pueblo
    3042,   # Ley que modifica la Ley Orgánica del Tribunal Constitucional
    4877,   # Ley que modifica composición de la JNJ
    # Otros controversiales
    904,    # Ley sobre el retorno a la bicameralidad
]

_opener = None


def _get_opener(proxy: str | None = None):
    """Build URL opener with optional proxy."""
    global _opener
    if _opener is not None:
        return _opener
    if proxy:
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
        print(f"🔒 Usando proxy")
    else:
        _opener = build_opener()
    return _opener


def _encrypt_param(value) -> str:
    """Encrypt a parameter for the Congreso API using AES-128 ECB."""
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    padded = pad(str(value).encode("utf-8"), AES.block_size)
    encrypted = cipher.encrypt(padded)
    b64 = base64.b64encode(encrypted).decode()
    return b64.replace("+", "-").replace("/", "_").replace("=", "")


def _api_get(path: str) -> dict:
    """GET request to Congreso API."""
    url = f"{API_BASE}/{path}"
    req = Request(url, headers=HEADERS)
    opener = _get_opener()
    with opener.open(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _api_post(path: str, payload: dict) -> dict:
    """POST request to Congreso API."""
    url = f"{API_BASE}/{path}"
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=HEADERS, method="POST")
    opener = _get_opener()
    with opener.open(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_projects(
    keywords: str | None = None,
    estado_id: int | None = None,
    page_size: int = 50,
    row_start: int = 0,
) -> dict:
    """Search for projects using the Congreso API."""
    payload = {
        "perParId": PROCESO_PARLAMENTARIO,
        "perLegId": None,
        "comisionId": None,
        "estadoId": estado_id,
        "congresistaId": None,
        "grupoParlamentarioId": None,
        "proponenteId": None,
        "legislaturaId": None,
        "fecPresentacionDesde": None,
        "fecPresentacionHasta": None,
        "pleyNum": None,
        "palabras": keywords,
        "tipoFirmanteId": None,
        "pageSize": page_size,
        "rowStart": row_start,
    }
    return _api_post("proyecto-ley/lista-con-filtro", payload)


def get_expediente(pley_num: int) -> dict | None:
    """Get full project detail including seguimiento and voting PDFs."""
    enc_periodo = _encrypt_param(PROCESO_PARLAMENTARIO)
    enc_pley = _encrypt_param(pley_num)
    try:
        result = _api_get(f"expediente/{enc_periodo}/{enc_pley}")
        return result.get("data")
    except URLError as e:
        print(f"  ✗ Error fetching expediente {pley_num}: {e}", file=sys.stderr)
        return None


def _archivo_url(archivo_id: int) -> str:
    """Build a PDF download URL from a proyectoArchivoId."""
    b64 = base64.b64encode(str(archivo_id).encode()).decode()
    return f"{API_BASE}/archivo/{b64}/pdf"


def extract_voting_pdfs(expediente: dict) -> list[dict]:
    """Extract voting PDF URLs from expediente seguimiento."""
    pdfs = []
    seen_keys = set()

    for seg in expediente.get("seguimientos", []):
        detalle = seg.get("detalle", "").upper()
        # Get entries with VOTACIÓN or ASISTENCIA Y VOTACIÓN
        if "VOTACI" not in detalle and "ASISTENCIA" not in detalle:
            continue

        archivos = seg.get("archivos") or []
        for archivo in archivos:
            # Use enlace if available, otherwise build URL from archivo ID
            url = archivo.get("enlace")
            archivo_id = archivo.get("proyectoArchivoId")

            if not url and archivo_id:
                url = _archivo_url(archivo_id)

            if not url:
                continue

            # Deduplicate by URL or archivo ID
            key = url or str(archivo_id)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            pdfs.append({
                "url": url,
                "fecha": seg.get("fecha", ""),
                "detalle": seg.get("detalle", ""),
                "descripcion": archivo.get("descripcion", ""),
                "archivo_id": archivo_id,
            })

    return pdfs


def download_pdf(url: str) -> str | None:
    """Download a PDF to a temp file and return the path."""
    try:
        opener = _get_opener()
        req = Request(url, headers={
            "User-Agent": HEADERS["User-Agent"],
            "Referer": "https://www2.congreso.gob.pe/",
        })
        with opener.open(req, timeout=60) as resp:
            content = resp.read()
            fd, path = tempfile.mkstemp(suffix=".pdf")
            with os.fdopen(fd, "wb") as f:
                f.write(content)
            return path
    except URLError as e:
        print(f"  ✗ Error downloading PDF: {e}", file=sys.stderr)
        return None


def parse_voting_page(text: str) -> dict | None:
    """Parse a single VOTACIÓN page from extracted text."""
    lines = text.split("\n")

    # Check this is a VOTACIÓN page
    is_votacion = any("VOTACIÓN:" in line for line in lines[:5])
    if not is_votacion:
        return None

    # Extract header info
    asunto_lines = []
    collecting_asunto = False
    for line in lines:
        if line.startswith("Asunto:"):
            collecting_asunto = True
            rest = line[len("Asunto:"):].strip()
            if rest:
                asunto_lines.append(rest)
            continue
        if collecting_asunto:
            # Asunto ends when we hit a bancada code line
            if any(line.startswith(b + " ") for b in BANCADAS):
                break
            asunto_lines.append(line.strip())

    asunto = " ".join(asunto_lines).strip()

    # Extract date/time
    fecha_match = re.search(r"Fecha:\s*(\S+)\s+Hora:\s*(.+)", text)
    fecha = fecha_match.group(1) if fecha_match else ""
    hora = fecha_match.group(2).strip() if fecha_match else ""

    # Build regex for vote parsing
    bancada_pattern = "|".join(re.escape(b) for b in BANCADAS)
    vote_re = re.compile(
        rf"({bancada_pattern})\s+"
        rf"([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?,\s+[A-ZÁÉÍÓÚÑA-Z\s\.]+?)\s+"
        rf"(SI \+\+\+|NO---|Abst\.|SínRes|aus|LO|LP|LE|L25A)"
    )

    votes = []
    for line in lines:
        for match in vote_re.finditer(line):
            bancada, nombre, voto = match.groups()
            votes.append({
                "bancada": bancada.strip(),
                "nombre": nombre.strip(),
                "voto": voto.strip(),
            })

    # Extract summary
    summary = {}
    summary_re = re.compile(r"^(SI\+\+\+|NO---|Abst\.|SínRes)\s+(\d+)", re.MULTILINE)
    for m in summary_re.finditer(text):
        summary[m.group(1)] = int(m.group(2))

    # Also try alternate format from "Resultados de VOTACIÓN"
    if not summary:
        alt_re = re.compile(r"SI\+\+\+\s+(\d+)")
        m = alt_re.search(text)
        if m:
            summary["SI+++"] = int(m.group(1))

    return {
        "fecha": fecha,
        "hora": hora,
        "asunto": asunto,
        "votos": votes,
        "resumen": summary,
        "total_votos": len([v for v in votes if v["voto"] in ("SI +++", "NO---", "Abst.", "SínRes")]),
    }


def parse_voting_pdf(pdf_path: str) -> list[dict]:
    """Parse all voting pages from a PDF file."""
    votaciones = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            result = parse_voting_page(text)
            if result and result["votos"]:
                votaciones.append(result)
    return votaciones


def classify_vote(voto: str) -> str:
    """Classify a vote into a standard category."""
    if voto == "SI +++":
        return "a_favor"
    elif voto == "NO---":
        return "en_contra"
    elif voto == "Abst.":
        return "abstencion"
    elif voto == "SínRes":
        return "sin_respuesta"
    else:
        return "ausente"


def process_project(pley_num: int) -> dict | None:
    """Process a single project: fetch detail, download PDFs, parse votes."""
    print(f"  📋 Proyecto {pley_num}...")

    expediente = get_expediente(pley_num)
    if not expediente:
        return None

    general = expediente.get("general", {})
    title = general.get("titulo", "").strip()
    estado = general.get("desEstado", "")

    print(f"     {title[:80]}...")
    print(f"     Estado: {estado}")

    # Get voting PDFs
    voting_pdfs = extract_voting_pdfs(expediente)
    if not voting_pdfs:
        print(f"     ⚠ Sin PDFs de votación")
        return {
            "pley_num": pley_num,
            "proyecto_ley": general.get("proyectoLey", ""),
            "titulo": title,
            "estado": estado,
            "autores": expediente.get("autores", []),
            "bancada": general.get("desGpar", ""),
            "fecha_presentacion": general.get("fecPresentacion", ""),
            "votaciones": [],
        }

    # Download and parse each voting PDF
    all_votaciones = []
    seen_pdf_urls = set()

    for pdf_info in voting_pdfs:
        url = pdf_info["url"]
        if url in seen_pdf_urls:
            continue
        seen_pdf_urls.add(url)

        print(f"     📥 Descargando PDF: {pdf_info['descripcion'][:60]}...")
        pdf_path = download_pdf(url)
        if not pdf_path:
            continue

        try:
            votaciones = parse_voting_pdf(pdf_path)
            for v in votaciones:
                v["pdf_url"] = url
                v["pdf_detalle"] = pdf_info["detalle"]
            all_votaciones.extend(votaciones)
            print(f"     ✓ {len(votaciones)} votaciones extraídas")
        finally:
            os.unlink(pdf_path)

    return {
        "pley_num": pley_num,
        "proyecto_ley": general.get("proyectoLey", ""),
        "titulo": title,
        "estado": estado,
        "autores": [
            {"nombre": a.get("desCongresista", ""), "bancada": a.get("desGrupoPar", "")}
            for a in expediente.get("autores", [])
        ],
        "bancada": general.get("desGpar", ""),
        "fecha_presentacion": general.get("fecPresentacion", ""),
        "votaciones": all_votaciones,
    }


def search_controversial_projects() -> list[int]:
    """Search for controversial projects by keywords."""
    pley_nums = set(KNOWN_CONTROVERSIAL_PLEYS)

    for keyword in CONTROVERSIAL_KEYWORDS:
        print(f"  🔍 Buscando: {keyword}...")
        try:
            result = search_projects(keywords=keyword, page_size=50)
            projects = result.get("data", {}).get("proyectos", [])
            for p in projects:
                pley_nums.add(p["pleyNum"])
            if projects:
                print(f"     {len(projects)} proyectos encontrados")
            time.sleep(0.3)
        except URLError as e:
            print(f"     ✗ Error: {e}", file=sys.stderr)

    return sorted(pley_nums)


def search_approved_projects() -> list[int]:
    """Get all approved projects (estado: APROBADO, AUTÓGRAFA)."""
    pley_nums = []

    for estado_id in [10, 9, 72]:  # APROBADO, AUTÓGRAFA, APROBADO 1ERA VOTACIÓN
        row_start = 0
        while True:
            result = search_projects(estado_id=estado_id, page_size=50, row_start=row_start)
            projects = result.get("data", {}).get("proyectos", [])
            total = result.get("data", {}).get("rowsTotal", 0)

            for p in projects:
                pley_nums.append(p["pleyNum"])

            if not projects or row_start + len(projects) >= total:
                break
            row_start += len(projects)
            time.sleep(0.3)

    return sorted(set(pley_nums))


def build_vote_summary(projects: list[dict]) -> dict:
    """Build a summary of votes per congressperson across all projects."""
    congresspeople = {}

    for project in projects:
        for votacion in project.get("votaciones", []):
            asunto = votacion.get("asunto", "")
            for voto_data in votacion.get("votos", []):
                nombre = voto_data["nombre"]
                bancada = voto_data["bancada"]
                voto = classify_vote(voto_data["voto"])

                if nombre not in congresspeople:
                    congresspeople[nombre] = {
                        "nombre": nombre,
                        "bancada": bancada,
                        "partido_votoclaro": BANCADA_TO_PARTY.get(bancada, ""),
                        "votos": [],
                        "total_a_favor": 0,
                        "total_en_contra": 0,
                        "total_abstencion": 0,
                        "total_ausente": 0,
                    }

                cp = congresspeople[nombre]
                cp["votos"].append({
                    "pley_num": project["pley_num"],
                    "asunto": asunto[:200],
                    "voto": voto,
                })

                if voto == "a_favor":
                    cp["total_a_favor"] += 1
                elif voto == "en_contra":
                    cp["total_en_contra"] += 1
                elif voto == "abstencion":
                    cp["total_abstencion"] += 1
                elif voto in ("ausente", "sin_respuesta"):
                    cp["total_ausente"] += 1

    return congresspeople


def print_stats(data: dict):
    """Print statistics from scraped data."""
    projects = data.get("projects", [])
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS — CONGRESO")
    print("=" * 60)

    print(f"\nTotal proyectos: {len(projects)}")
    with_votes = [p for p in projects if p.get("votaciones")]
    print(f"Con votaciones: {len(with_votes)}")

    total_votaciones = sum(len(p.get("votaciones", [])) for p in projects)
    print(f"Total votaciones parseadas: {total_votaciones}")

    # Vote summary
    summary = data.get("vote_summary", {})
    if summary:
        print(f"\nCongresistas con votos registrados: {len(summary)}")

        # Top voters a_favor
        by_favor = sorted(summary.values(), key=lambda x: -x["total_a_favor"])
        print(f"\nTop 10 congresistas que más votaron A FAVOR:")
        for cp in by_favor[:10]:
            print(f"  {cp['bancada']:8s} {cp['nombre']:40s} {cp['total_a_favor']} a favor")

        # By bancada
        print(f"\nVotos por bancada:")
        bancada_stats = {}
        for cp in summary.values():
            b = cp["bancada"]
            if b not in bancada_stats:
                bancada_stats[b] = {"a_favor": 0, "en_contra": 0, "abstencion": 0, "ausente": 0}
            bancada_stats[b]["a_favor"] += cp["total_a_favor"]
            bancada_stats[b]["en_contra"] += cp["total_en_contra"]
            bancada_stats[b]["abstencion"] += cp["total_abstencion"]
            bancada_stats[b]["ausente"] += cp["total_ausente"]

        for b, stats in sorted(bancada_stats.items()):
            total = stats["a_favor"] + stats["en_contra"] + stats["abstencion"]
            if total > 0:
                pct_favor = stats["a_favor"] / total * 100
                print(
                    f"  {b:8s}: {stats['a_favor']:3d} favor, "
                    f"{stats['en_contra']:3d} contra, "
                    f"{stats['abstencion']:3d} abst. "
                    f"({pct_favor:.0f}% a favor)"
                )


def main():
    parser = argparse.ArgumentParser(
        description="Scraper del Congreso — Proyectos de Ley y Votaciones 2021-2026"
    )
    parser.add_argument(
        "--keyword", default=None,
        help="Buscar proyectos por palabra clave",
    )
    parser.add_argument(
        "--pley", type=int, default=None,
        help="Número de proyecto de ley específico",
    )
    parser.add_argument(
        "--all-approved", action="store_true",
        help="Descargar todos los proyectos aprobados",
    )
    parser.add_argument(
        "--controversial", action="store_true",
        help="Buscar proyectos controversiales (default)",
    )
    parser.add_argument(
        "-o", "--output",
        default="scrapers/data/congreso_votaciones.json",
        help="Archivo de salida",
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="Solo mostrar estadísticas de datos existentes",
    )
    parser.add_argument(
        "--proxy", default=None,
        help="Proxy en formato host:port:user:pass",
    )
    args = parser.parse_args()

    output_path = Path(args.output)

    if args.proxy:
        _get_opener(args.proxy)

    if args.stats:
        if not output_path.exists():
            print(f"✗ No existe {output_path}", file=sys.stderr)
            sys.exit(1)
        data = json.loads(output_path.read_text())
        print_stats(data)
        return

    # Determine which projects to process
    pley_nums = []

    if args.pley:
        pley_nums = [args.pley]
    elif args.keyword:
        print(f"🔍 Buscando proyectos con: {args.keyword}")
        result = search_projects(keywords=args.keyword, page_size=50)
        projects = result.get("data", {}).get("proyectos", [])
        pley_nums = [p["pleyNum"] for p in projects]
        print(f"  {len(pley_nums)} proyectos encontrados")
    elif args.all_approved:
        print("📥 Buscando todos los proyectos aprobados...")
        pley_nums = search_approved_projects()
        print(f"  {len(pley_nums)} proyectos aprobados")
    else:
        # Default: controversial
        print("📥 Buscando proyectos controversiales...")
        pley_nums = search_controversial_projects()
        print(f"  {len(pley_nums)} proyectos a procesar")

    if not pley_nums:
        print("⚠ No se encontraron proyectos")
        return

    # Process each project
    print(f"\n📋 Procesando {len(pley_nums)} proyectos...")
    projects = []
    for i, pley_num in enumerate(pley_nums):
        print(f"\n[{i + 1}/{len(pley_nums)}]")
        try:
            result = process_project(pley_num)
            if result:
                projects.append(result)
        except Exception as e:
            print(f"  ✗ Error en proyecto {pley_num}: {e}", file=sys.stderr)
        time.sleep(0.5)  # Be nice to the server

    # Build vote summary
    vote_summary = build_vote_summary(projects)

    # Compile output
    output_data = {
        "periodo": "2021-2026",
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "projects": projects,
        "vote_summary": vote_summary,
    }

    # Stats
    print_stats(output_data)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n✅ Guardado en {output_path}")
    print(f"   {len(projects)} proyectos, {len(vote_summary)} congresistas")


if __name__ == "__main__":
    main()
