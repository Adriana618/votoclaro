#!/usr/bin/env python3
"""
Spider para buscar investigaciones de candidatos en Convoca.pe via DuckDuckGo.

Busca cada candidato en Convoca.pe y extrae artículos relevantes sobre
investigaciones, denuncias, y antecedentes.

Uso:
    # Buscar solo candidatos de reelección (rápido)
    python scrapers/convoca_spider.py --reelection-only

    # Buscar todos los candidatos (lento, ~5500 queries)
    python scrapers/convoca_spider.py --all

    # Buscar candidatos específicos por nombre
    python scrapers/convoca_spider.py --query "Keiko Fujimori"

    # Usar proxy
    python scrapers/convoca_spider.py --reelection-only --proxy host:port:user:pass
"""

import argparse
import html as html_mod
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent / "data"
CANDIDATES_FINAL = DATA_DIR / "candidates_final.json"
OUTPUT_FILE = DATA_DIR / "convoca_investigations.json"

# Keywords that indicate relevant investigative articles
RELEVANCE_KEYWORDS = [
    "investigación", "investigado", "investigacion",
    "denuncia", "denunciado",
    "sentencia", "sentenciado", "condenado", "condena",
    "procesado", "proceso penal", "proceso judicial",
    "lavado de activos", "corrupción", "corrupcion", "peculado",
    "colusión", "cohecho", "malversación", "enriquecimiento ilícito",
    "organización criminal", "crimen organizado",
    "narcotráfico", "tráfico de influencias",
    "soborno", "fraude", "estafa",
    "fiscalía", "fiscal", "poder judicial",
    "prisión", "detenido", "arrestado", "prófugo",
    "antecedentes", "prontuario",
    "congresista", "parlamentario", "legislador",
    "acusado", "acusación", "acusacion",
    "ilícito", "ilicito", "irregular",
]

# Rate limiting
REQUEST_DELAY = 2.0  # seconds between requests (DDG is more sensitive)


def _get_session(proxy: str | None = None) -> requests.Session:
    """Build requests session, optionally with proxy."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    })

    if proxy:
        parts = proxy.split(":")
        if len(parts) == 4:
            host, port, user, passwd = parts
            proxy_url = f"http://{user}:{passwd}@{host}:{port}"
        elif len(parts) == 2:
            proxy_url = f"http://{parts[0]}:{parts[1]}"
        else:
            proxy_url = f"http://{proxy}"
        session.proxies = {"http": proxy_url, "https": proxy_url}

    return session


def search_ddg(query: str, session: requests.Session, retries: int = 3) -> list[dict]:
    """Search DuckDuckGo HTML and return results."""
    for attempt in range(retries):
        try:
            resp = session.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                timeout=20,
            )
            resp.raise_for_status()
            break
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 403 and attempt < retries - 1:
                wait = (attempt + 1) * 10  # 10s, 20s, 30s
                print(f"\n  ⏳ Rate limited, esperando {wait}s...", end=" ", flush=True)
                time.sleep(wait)
                continue
            print(f"  ✗ Error: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"  ✗ Error: {e}", file=sys.stderr)
            return []

    html = resp.text
    results = []

    # Extract result links and titles
    links = re.findall(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        html, re.DOTALL,
    )
    snippets = re.findall(
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
        html, re.DOTALL,
    )

    for i, (raw_url, raw_title) in enumerate(links):
        title = html_mod.unescape(re.sub(r'<[^>]+>', '', raw_title).strip())

        # DDG wraps URLs through redirect
        actual = re.search(r'uddg=([^&]+)', raw_url)
        url = urllib.parse.unquote(actual.group(1)) if actual else raw_url

        snippet = ""
        if i < len(snippets):
            snippet = html_mod.unescape(re.sub(r'<[^>]+>', '', snippets[i]).strip())

        # Only keep convoca.pe results
        if "convoca.pe" not in url:
            continue

        results.append({
            "title": title,
            "url": url,
            "snippet": snippet,
        })

    return results


def is_relevant(result: dict, candidate_name: str) -> bool:
    """Check if a search result is relevant to candidate investigations."""
    text = f"{result['title']} {result['snippet']}".lower()
    name_parts = candidate_name.lower().split(",")[0].split()  # Use surname

    # At least one surname should appear (skip short parts like "DE", "LA")
    has_name = any(part in text for part in name_parts if len(part) > 3)
    if not has_name:
        return False

    # Check for investigation-related keywords
    has_keyword = any(kw in text for kw in RELEVANCE_KEYWORDS)
    return has_keyword


def _format_name_for_search(name: str) -> str:
    """Convert 'APELLIDO1 APELLIDO2, NOMBRE1 NOMBRE2' to 'Nombre1 Apellido1 Apellido2'."""
    parts = name.split(",")
    if len(parts) >= 2:
        surnames = parts[0].strip().title()
        firstnames = parts[1].strip().title()
        # Use first name + all surnames
        first = firstnames.split()[0] if firstnames else ""
        return f"{first} {surnames}".strip()
    return name.title()


def search_candidate(name: str, session: requests.Session,
                     extra_terms: str = "") -> list[dict]:
    """Search for a specific candidate on Convoca.pe and return relevant articles."""
    search_name = _format_name_for_search(name)

    query = f"site:convoca.pe \"{search_name}\""
    if extra_terms:
        query = f"site:convoca.pe \"{search_name}\" {extra_terms}"

    results = search_ddg(query, session)

    # If no results with quotes, try without quotes
    if not results:
        query2 = f"site:convoca.pe {search_name}"
        results = search_ddg(query2, session)
        time.sleep(1)  # Extra delay for double request

    # Filter for relevance
    relevant = [r for r in results if is_relevant(r, name)]

    # If no relevant results, include any convoca results mentioning surname
    if not relevant and results:
        surname_parts = name.split(",")[0].lower().split()
        for r in results:
            text = f"{r['title']} {r['snippet']}".lower()
            if any(p in text for p in surname_parts if len(p) > 3):
                relevant.append(r)

    return relevant


def load_candidates_to_search(args) -> list[dict]:
    """Load the list of candidates to search based on args."""
    if args.query:
        return [{"name": args.query, "party_slug": "", "region_slug": None}]

    if not CANDIDATES_FINAL.exists():
        print(f"✗ No existe {CANDIDATES_FINAL}", file=sys.stderr)
        print("  Ejecuta primero: python scrapers/build_app_data.py", file=sys.stderr)
        sys.exit(1)

    data = json.loads(CANDIDATES_FINAL.read_text(encoding="utf-8"))
    candidates = data.get("candidatos", [])

    if args.reelection_only:
        candidates = [c for c in candidates if c.get("is_reelection")]
        print(f"🔍 Buscando solo candidatos de reelección: {len(candidates)}")
    elif args.controversial_only:
        candidates = [c for c in candidates if c.get("controversy_score", 0) > 0]
        print(f"🔍 Buscando solo candidatos con controversia: {len(candidates)}")
    elif args.all:
        print(f"🔍 Buscando TODOS los candidatos: {len(candidates)}")
    else:
        candidates = [
            c for c in candidates
            if c.get("is_reelection") or c.get("controversy_score", 0) > 0
        ]
        print(f"🔍 Buscando candidatos relevantes: {len(candidates)}")

    return candidates


def main():
    parser = argparse.ArgumentParser(description="Spider de Convoca.pe via DuckDuckGo")
    parser.add_argument("--query", type=str, help="Buscar un nombre específico")
    parser.add_argument("--reelection-only", action="store_true",
                        help="Solo candidatos de reelección")
    parser.add_argument("--controversial-only", action="store_true",
                        help="Solo candidatos con controversia > 0")
    parser.add_argument("--all", action="store_true",
                        help="Buscar TODOS los candidatos (lento)")
    parser.add_argument("--proxy", type=str,
                        help="Proxy en formato host:port:user:pass")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY,
                        help="Delay entre requests (default 2.0s)")
    parser.add_argument("--extra-terms", type=str, default="",
                        help="Términos extra para la búsqueda")
    args = parser.parse_args()

    session = _get_session(args.proxy)
    candidates = load_candidates_to_search(args)

    if not candidates:
        print("No hay candidatos para buscar.")
        return

    # Load existing results if any
    existing = {}
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
            print(f"📄 Cargando {len(existing)} resultados previos")
        except json.JSONDecodeError:
            pass

    total = len(candidates)
    found = 0
    searched = 0
    errors = 0

    print(f"\n🕷️  Iniciando búsqueda en Convoca.pe ({total} candidatos)...")
    print(f"   Delay: {args.delay}s | Proxy: {'Sí' if args.proxy else 'No'}")
    print()

    for i, candidate in enumerate(candidates, 1):
        name = candidate["name"]
        party = candidate.get("party_slug", "")

        # Skip if already searched (use name as key)
        if name in existing and not args.query:
            if existing[name].get("articles"):
                found += 1
            continue

        searched += 1
        print(f"[{i}/{total}] {name} ({party})...", end=" ", flush=True)

        try:
            articles = search_candidate(name, session, args.extra_terms)

            existing[name] = {
                "name": name,
                "party_slug": party,
                "region_slug": candidate.get("region_slug"),
                "articles": articles,
                "article_count": len(articles),
                "searched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            if articles:
                found += 1
                print(f"✓ {len(articles)} artículos")
                for a in articles[:3]:
                    print(f"    → {a['title'][:80]}")
            else:
                print("∅")

        except Exception as e:
            errors += 1
            print(f"✗ {e}")

        # Save periodically (every 10 candidates)
        if searched % 10 == 0:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            OUTPUT_FILE.write_text(
                json.dumps(existing, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        # Rate limit
        if i < total:
            time.sleep(args.delay)

    # Final save
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\n{'=' * 60}")
    print(f"📊 RESULTADOS")
    print(f"{'=' * 60}")
    print(f"  Total candidatos: {total}")
    print(f"  Buscados (nuevos): {searched}")
    print(f"  Con artículos: {found}")
    print(f"  Errores: {errors}")
    print(f"  Guardado en: {OUTPUT_FILE}")

    # Show top findings
    top = sorted(
        [v for v in existing.values() if v.get("article_count", 0) > 0],
        key=lambda x: -x["article_count"],
    )
    if top:
        print(f"\n🔝 Top candidatos con más artículos:")
        for entry in top[:15]:
            print(f"  {entry['name']} ({entry['party_slug']}): "
                  f"{entry['article_count']} artículos")


if __name__ == "__main__":
    main()
