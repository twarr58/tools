#!/usr/bin/env python3
"""
Agregátor zpráv – webová aplikace.

Kategorie: česká/světová politika, sport, kultura, IT/AI.
Stahuje RSS feedy paralelně, cachuje výsledky a servíruje
přes Flask s moderním responzivním rozhraním.

Spuštění:
    pip install -r requirements.txt
    python news.py
    # → http://localhost:5000
"""

import hashlib
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import feedparser
from flask import Flask, jsonify, render_template

# ---------------------------------------------------------------------------
# Konfigurace RSS zdrojů
# ---------------------------------------------------------------------------

FEEDS = {
    "cz-politika": {
        "name": "Česká politika",
        "icon": "flag",
        "sources": [
            {
                "name": "iROZHLAS",
                "url": "https://www.irozhlas.cz/rss/irozhlas/section/zpravy-domov",
            },
            {
                "name": "Novinky.cz",
                "url": "https://www.novinky.cz/rss",
            },
            {
                "name": "ČT24",
                "url": "https://ct24.ceskatelevize.cz/rss/hlavni-zpravy",
            },
            {
                "name": "Aktuálně.cz",
                "url": "https://zpravy.aktualne.cz/domaci/rss/",
            },
            {
                "name": "ČTK",
                "url": "https://www.ceskenoviny.cz/sluzby/rss/cr/",
            },
            {
                "name": "Deník.cz",
                "url": "https://www.denik.cz/rss/zpravy_domov.html",
            },
        ],
    },
    "svet-politika": {
        "name": "Světová politika",
        "icon": "globe",
        "sources": [
            {
                "name": "iROZHLAS",
                "url": "https://www.irozhlas.cz/rss/irozhlas/section/zpravy-svet",
            },
            {
                "name": "BBC World",
                "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
            },
            {
                "name": "Al Jazeera",
                "url": "https://www.aljazeera.com/xml/rss/all.xml",
            },
            {
                "name": "Aktuálně.cz",
                "url": "https://zpravy.aktualne.cz/zahranici/rss/",
            },
        ],
    },
    "cz-sport": {
        "name": "Český sport",
        "icon": "trophy",
        "sources": [
            {
                "name": "iROZHLAS",
                "url": "https://www.irozhlas.cz/rss/irozhlas/section/sport",
            },
            {
                "name": "iSport.cz",
                "url": "https://isport.blesk.cz/rss",
            },
            {
                "name": "Aktuálně.cz",
                "url": "https://zpravy.aktualne.cz/sport/rss/",
            },
        ],
    },
    "svet-sport": {
        "name": "Světový sport",
        "icon": "globe-trophy",
        "sources": [
            {
                "name": "BBC Sport",
                "url": "https://feeds.bbci.co.uk/sport/rss.xml",
            },
            {
                "name": "ESPN",
                "url": "https://www.espn.com/espn/rss/news",
            },
        ],
    },
    "kultura": {
        "name": "Kultura",
        "icon": "palette",
        "sources": [
            {
                "name": "iROZHLAS",
                "url": "https://www.irozhlas.cz/rss/irozhlas/section/kultura",
            },
            {
                "name": "Aktuálně.cz",
                "url": "https://magazin.aktualne.cz/kultura/rss/",
            },
            {
                "name": "Guardian Film",
                "url": "https://www.theguardian.com/film/rss",
            },
            {
                "name": "Guardian Music",
                "url": "https://www.theguardian.com/music/rss",
            },
        ],
    },
    "ai": {
        "name": "IT & AI",
        "icon": "cpu",
        "sources": [
            {
                "name": "iROZHLAS",
                "url": "https://www.irozhlas.cz/rss/irozhlas/section/veda-technologie",
            },
            {
                "name": "Ars Technica",
                "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
            },
            {
                "name": "The Verge AI",
                "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            },
            {
                "name": "TechCrunch",
                "url": "https://techcrunch.com/feed/",
            },
            {
                "name": "MIT News AI",
                "url": "https://news.mit.edu/rss/topic/artificial-intelligence2",
            },
        ],
    },
}

# Aliasy pro kategorie
CATEGORY_GROUPS = {
    "politika": ["cz-politika", "svet-politika"],
    "sport": ["cz-sport", "svet-sport"],
    "kultura": ["kultura"],
    "ai": ["ai"],
}

# ---------------------------------------------------------------------------
# Cache a stahování
# ---------------------------------------------------------------------------

CACHE_TTL = 300  # 5 minut
_cache = {}
_cache_lock = threading.Lock()


def _parse_date(entry):
    """Extrahuje datetime z RSS entry."""
    for field in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, field, None)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                continue
    return None


def _entry_id(entry):
    """Vytvoří unikátní ID pro článek."""
    raw = entry.get("link", "") or entry.get("title", "") or ""
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]


def fetch_single(source):
    """Stáhne jeden RSS feed. Vrací (source_name, articles, error?)."""
    try:
        feed = feedparser.parse(source["url"])
        if feed.bozo and not feed.entries:
            return source["name"], [], f"Parse error: {feed.bozo_exception}"

        articles = []
        for entry in feed.entries:
            pub = _parse_date(entry)
            # Vyčistit summary od HTML tagů (zjednodušeně)
            summary = entry.get("summary", "")
            articles.append(
                {
                    "id": _entry_id(entry),
                    "title": (entry.get("title") or "(bez titulku)").strip(),
                    "link": entry.get("link", ""),
                    "published": pub.isoformat() if pub else None,
                    "published_ts": pub.timestamp() if pub else 0,
                    "summary": summary,
                    "source": source["name"],
                }
            )
        return source["name"], articles, None
    except Exception as exc:  # pylint: disable=broad-except
        return source["name"], [], str(exc)


def fetch_category(cat_key):
    """Stáhne všechny zdroje jedné kategorie. Používá cache."""
    now = time.time()
    with _cache_lock:
        if cat_key in _cache:
            cached_time, cached_data = _cache[cat_key]
            if now - cached_time < CACHE_TTL:
                return cached_data

    cat = FEEDS[cat_key]
    all_articles = []
    errors = []

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(fetch_single, src): src for src in cat["sources"]
        }
        for future in as_completed(futures):
            name, articles, err = future.result()
            all_articles.extend(articles)
            if err:
                errors.append({"source": name, "error": err})

    # Seřadit podle data (nejnovější první)
    all_articles.sort(key=lambda a: a["published_ts"], reverse=True)

    result = {
        "key": cat_key,
        "name": cat["name"],
        "icon": cat["icon"],
        "articles": all_articles,
        "errors": errors,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    with _cache_lock:
        _cache[cat_key] = (now, result)

    return result


def fetch_all():
    """Stáhne všechny kategorie paralelně."""
    results = {}
    with ThreadPoolExecutor(max_workers=len(FEEDS)) as pool:
        futures = {
            pool.submit(fetch_category, key): key for key in FEEDS
        }
        for future in as_completed(futures):
            key = futures[future]
            results[key] = future.result()
    return results


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/")
def index():
    """Hlavní stránka."""
    categories = [
        {"key": k, "name": v["name"], "icon": v["icon"]}
        for k, v in FEEDS.items()
    ]
    groups = CATEGORY_GROUPS
    return render_template("index.html", categories=categories, groups=groups)


@app.route("/api/feeds")
def api_all_feeds():
    """API – všechny kategorie."""
    data = fetch_all()
    return jsonify(data)


@app.route("/api/feeds/<cat_key>")
def api_feed(cat_key):
    """API – jedna kategorie."""
    if cat_key in FEEDS:
        return jsonify(fetch_category(cat_key))
    if cat_key in CATEGORY_GROUPS:
        results = {}
        for sub_key in CATEGORY_GROUPS[cat_key]:
            results[sub_key] = fetch_category(sub_key)
        return jsonify(results)
    return jsonify({"error": f"Neznámá kategorie: {cat_key}"}), 404


if __name__ == "__main__":
    print("Zpravodajský agregátor – http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
