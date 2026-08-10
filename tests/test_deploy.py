"""Tests for the local landing page 'deploy' step."""
from backend.tools import deploy


def test_slugify_strips_special_characters():
    assert deploy._slugify("AI-powered plant disease detector!!") == "ai-powered-plant-disease-detector"


def test_slugify_empty_falls_back():
    assert deploy._slugify("!!!") == "landing-page"


def test_save_landing_page_writes_file(tmp_path, monkeypatch):
    monkeypatch.setattr(deploy, "OUTPUT_DIR", tmp_path / "landing_pages")
    path = deploy.save_landing_page("Test Idea", "<html></html>")
    assert path.endswith("test-idea.html")
    assert (tmp_path / "landing_pages" / "test-idea.html").read_text(encoding="utf-8") == "<html></html>"
