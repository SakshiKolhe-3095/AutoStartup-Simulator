"""Tests for landing page codegen retry/self-correct loop and HTML validator."""
from backend.tools import codegen
from backend.tools.html_validator import validate_html

VALID_HTML = (
    "<!DOCTYPE html><html><head>"
    '<script src="https://cdn.tailwindcss.com"></script>'
    "</head><body><h1>Hi</h1></body></html>"
)
INVALID_HTML = "<div>not a full page</div>"


def test_validate_html_accepts_well_formed_page():
    is_valid, errors = validate_html(VALID_HTML)
    assert is_valid is True
    assert errors == []


def test_validate_html_rejects_missing_tags():
    is_valid, errors = validate_html(INVALID_HTML)
    assert is_valid is False
    assert any("html" in e for e in errors)
    assert any("tailwind" in e.lower() for e in errors)


def test_validate_html_rejects_empty_string():
    is_valid, errors = validate_html("")
    assert is_valid is False
    assert errors == ["empty response"]


def test_generate_landing_page_returns_valid_html_first_try(monkeypatch):
    monkeypatch.setattr(codegen, "call_llm", lambda prompt, system, temperature=0.4: VALID_HTML)
    html, validation = codegen.generate_landing_page("idea", [], {})
    assert validation["valid"] is True
    assert validation["attempts"] == 1
    assert html == VALID_HTML


def test_generate_landing_page_retries_then_succeeds(monkeypatch):
    responses = iter([INVALID_HTML, INVALID_HTML, VALID_HTML])
    monkeypatch.setattr(
        codegen, "call_llm", lambda prompt, system, temperature=0.4: next(responses)
    )
    html, validation = codegen.generate_landing_page("idea", [], {})
    assert validation["valid"] is True
    assert validation["attempts"] == 3
    assert html == VALID_HTML


def test_generate_landing_page_falls_back_after_max_retries(monkeypatch):
    monkeypatch.setattr(codegen, "call_llm", lambda prompt, system, temperature=0.4: INVALID_HTML)
    html, validation = codegen.generate_landing_page("idea", [], {})
    assert validation["valid"] is False
    assert validation["fallback"] is True
    assert validation["attempts"] == codegen.MAX_RETRIES
    assert "cdn.tailwindcss.com" in html
    assert "idea" in html
