"""
Landing page codegen - LLM -> single-file HTML+Tailwind, with a generate -> validate ->
self-correct retry loop (max MAX_RETRIES attempts, falls back to a hardcoded template).
Owner: Lakshit
"""
import json
from typing import Any, Dict, List, Optional, Tuple

from backend.models.llm_client import call_llm
from backend.utils.logger import get_logger
from backend.tools.html_validator import validate_html, FALLBACK_TEMPLATE

logger = get_logger(__name__)

MAX_RETRIES = 3

SYSTEM_PROMPT = (
    "You are a frontend developer. Generate a SINGLE self-contained HTML file for a startup "
    "landing page using Tailwind CSS via the CDN script tag "
    '(<script src="https://cdn.tailwindcss.com"></script>). '
    "Include: a hero section with headline + subheadline, a features section listing the MVP "
    "features given, and a call-to-action section with an email signup form (no backend, just "
    "markup). Respond with ONLY the raw HTML, starting with <!DOCTYPE html> and nothing else — "
    "no markdown fences, no explanation."
)


def _strip_fences(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0]
    return raw.strip()


def _build_prompt(
    idea: str,
    mvp_features: List[Dict[str, Any]],
    tech_stack: Dict[str, Any],
    previous_errors: Optional[List[str]] = None,
) -> str:
    prompt = (
        f"Startup idea: {idea}\n"
        f"MVP features: {json.dumps(mvp_features)}\n"
        f"Tech stack (for tone only, do not display literally): {json.dumps(tech_stack)}"
    )
    if previous_errors:
        prompt += (
            "\n\nYour previous attempt was invalid for these reasons:\n"
            + "\n".join(f"- {e}" for e in previous_errors)
            + "\nFix these issues and regenerate the full HTML file."
        )
    return prompt


def generate_landing_page(
    idea: str, mvp_features: List[Dict[str, Any]], tech_stack: Dict[str, Any]
) -> Tuple[str, Dict[str, Any]]:
    """Generate -> validate -> self-correct loop, max MAX_RETRIES attempts.

    Falls back to a safe hardcoded template if every attempt fails validation.
    Returns (html, validation_dict) where validation_dict matches LandingPageValidation.
    """
    errors: List[str] = []
    for attempt in range(1, MAX_RETRIES + 1):
        prompt = _build_prompt(idea, mvp_features, tech_stack, previous_errors=errors)
        raw = call_llm(prompt=prompt, system=SYSTEM_PROMPT, temperature=0.4)
        html = _strip_fences(raw)
        is_valid, errors = validate_html(html)
        if is_valid:
            return html, {"valid": True, "attempts": attempt, "errors": [], "fallback": False}
        logger.warning(f"Landing page attempt {attempt} failed validation: {errors}")

    logger.error("Landing page generation failed after max retries — using fallback template.")
    return (
        FALLBACK_TEMPLATE.format(idea=idea),
        {"valid": False, "attempts": MAX_RETRIES, "errors": errors, "fallback": True},
    )
