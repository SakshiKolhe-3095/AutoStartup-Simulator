"""
Landing page "deployment" - writes the generated HTML to disk under data/landing_pages/.
Owner: Lakshit

Kept intentionally local/free per project scope (no paid hosting). Swapping in a real
free-tier host (Vercel/Netlify) later just means replacing save_landing_page's body —
callers only depend on it returning a path/URL string.
"""
import re
from pathlib import Path

OUTPUT_DIR = Path("data/landing_pages")


def _slugify(idea: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", idea.lower()).strip("-")
    return slug[:60] or "landing-page"


def save_landing_page(idea: str, html: str) -> str:
    """Write the generated HTML to disk and return its path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{_slugify(idea)}.html"
    path.write_text(html, encoding="utf-8")
    return str(path)
