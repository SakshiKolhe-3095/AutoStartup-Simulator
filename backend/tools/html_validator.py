"""
Landing page HTML validator - basic structural checks that drive the codegen retry loop.
Owner: Lakshit
"""
from typing import List, Tuple

from bs4 import BeautifulSoup

REQUIRED_TAGS = ["html", "head", "body"]

FALLBACK_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{idea}</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white text-gray-900">
<section class="min-h-screen flex flex-col items-center justify-center text-center px-6">
<h1 class="text-4xl font-bold mb-4">{idea}</h1>
<p class="text-lg text-gray-600 mb-8">A better way to get started. Sign up for early access.</p>
<form class="flex gap-2">
<input type="email" placeholder="you@example.com" class="border rounded px-4 py-2 w-64">
<button type="submit" class="bg-black text-white px-6 py-2 rounded">Get Early Access</button>
</form>
</section>
</body>
</html>"""


def validate_html(html: str) -> Tuple[bool, List[str]]:
    """Basic structural checks. Returns (is_valid, list_of_error_strings)."""
    if not html or not html.strip():
        return False, ["empty response"]

    errors: List[str] = []

    if "<!DOCTYPE" not in html.upper():
        errors.append("missing <!DOCTYPE html> declaration")

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        return False, [f"HTML failed to parse: {e}"]

    for tag in REQUIRED_TAGS:
        if not soup.find(tag):
            errors.append(f"missing required <{tag}> tag")

    if "cdn.tailwindcss.com" not in html:
        errors.append("missing Tailwind CDN script tag")

    return (len(errors) == 0), errors
