"""Integration test: CTO agent output format compat with deck builder."""
from backend.tools.deck_builder import DeckBuilder


def test_deck_builder_accepts_cto_output_without_error(tmp_path):
    """build_deck should not crash when cto_output is present in ceo_output."""
    cto_output = {
        "category": "saas",
        "mvp_features": [{"name": "Auth", "description": "user login", "priority": "must_have"}],
        "tech_stack": {"frontend": "React", "backend": "FastAPI", "database": "Postgres", "hosting": "Render"},
        "architecture_summary": "Lean React + FastAPI stack on free-tier hosting.",
        "landing_page_html": "<html></html>",
        "landing_page_path": "data/landing_pages/test.html",
        "landing_page_validation": {"valid": True},
        "code_repo": None,
    }
    ceo_output = {
        "idea": "AI note-taking app",
        "ceo_narrative": "We help professionals capture ideas instantly.",
        "cmo_output": {"market": {"tam": "$1B", "sam": "$100M", "som": "$5M"}},
        "cfo_output": {"funding_ask": {"amount": "$250k", "use_of_funds": "hiring"}},
        "cto_output": cto_output,
    }

    builder = DeckBuilder()
    output_path = str(tmp_path / "test_deck.pptx")
    path = builder.build_deck(ceo_output, output_path)

    assert path == output_path


def test_deck_builder_ignores_missing_cto_output_gracefully(tmp_path):
    """build_deck should still work if cto_output is absent (current gap)."""
    ceo_output = {
        "idea": "AI note-taking app",
        "ceo_narrative": "We help professionals capture ideas instantly.",
        "cmo_output": {},
        "cfo_output": {},
    }
    builder = DeckBuilder()
    output_path = str(tmp_path / "test_deck2.pptx")
    path = builder.build_deck(ceo_output, output_path)
    assert path == output_path