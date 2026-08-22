"""Tests for CMOAgent"""
import pytest
from backend.agents.cmo_agent import CMOAgent


def test_clean_json_strips_fences():
    agent = CMOAgent()
    raw = '```json\n{"key": "value"}\n```'
    result = agent._clean_json(raw)
    assert result == '{"key": "value"}'


def test_clean_json_passthrough_plain():
    agent = CMOAgent()
    raw = '{"key": "value"}'
    result = agent._clean_json(raw)
    assert result == '{"key": "value"}'


def test_analyze_market_returns_dict_keys():
    agent = CMOAgent()
    result = agent.analyze_market("AI-powered note-taking app")
    assert set(["tam", "sam", "som", "reasoning"]).issubset(result.keys())


def test_scan_competitors_returns_list():
    agent = CMOAgent()
    result = agent.scan_competitors("AI-powered note-taking app")
    assert isinstance(result, list)
    assert len(result) > 0


def test_generate_persona_returns_dict_keys():
    agent = CMOAgent()
    result = agent.generate_persona("AI-powered note-taking app")
    assert set(["name", "age_range", "occupation"]).issubset(result.keys())

def test_generate_gtm_strategy_returns_string(monkeypatch):
    agent = CMOAgent()
    monkeypatch.setattr(
        "backend.agents.cmo_agent.call_llm",
        lambda prompt, system, temperature=0.6, model=None: "Launch via community-led growth, freemium pricing.",
    )
    result = agent.generate_gtm_strategy("AI note-taking app", {"tam": "$1B"})
    assert isinstance(result, str)
    assert "growth" in result.lower()


def test_run_produces_full_output(monkeypatch):
    agent = CMOAgent()
    monkeypatch.setattr(agent, "analyze_market", lambda idea: {"tam": "$1B", "sam": "$100M", "som": "$5M", "reasoning": "r"})
    monkeypatch.setattr(agent, "scan_competitors", lambda idea: [{"name": "CompA", "summary": "s"}])
    monkeypatch.setattr(agent, "generate_persona", lambda idea: {"name": "Alex", "age_range": "25-34", "occupation": "PM"})
    monkeypatch.setattr(agent, "generate_gtm_strategy", lambda idea, market: "GTM plan text")

    result = agent.run("AI note-taking app")
    assert result["market"]["tam"] == "$1B"
    assert result["competitors"][0]["name"] == "CompA"
    assert result["persona"]["name"] == "Alex"
    assert result["gtm_strategy"] == "GTM plan text"


def test_analyze_market_handles_bad_json(monkeypatch):
    agent = CMOAgent()
    monkeypatch.setattr(
        "backend.agents.cmo_agent.call_llm",
        lambda prompt, system, temperature=0.3, model=None: "not json",
    )
    result = agent.analyze_market("AI note-taking app")
    assert result["reasoning"] == "not json"


def test_generate_persona_falls_back_to_groq_when_local_llm_empty(monkeypatch):
    agent = CMOAgent()
    monkeypatch.setattr(agent, "_call_local_llm", lambda prompt, system: "")
    monkeypatch.setattr(
        "backend.agents.cmo_agent.call_llm",
        lambda prompt, system, temperature=0.5, model=None: (
            '{"name": "Alex", "age_range": "25-34", "occupation": "PM", '
            '"pain_points": [], "motivations": []}'
        ),
    )
    result = agent.generate_persona("AI note-taking app")
    assert result["name"] == "Alex"