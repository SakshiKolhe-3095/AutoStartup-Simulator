"""Tests for ceo_agent"""
from unittest.mock import patch
from backend.agents.ceo_agent import (
    parse_idea,
    synthesize,
    defend_rebuttal,
    answer_investor_questions,
    call_llm
)


def test_parse_idea_strips_and_sets_running():
    state = {"idea": "  AI note-taking app  "}
    result = parse_idea(state)
    assert result["idea"] == "AI note-taking app"
    assert result["status"] == "running"


def test_parse_idea_empty_returns_failed():
    state = {"idea": "   "}
    result = parse_idea(state)
    assert result["status"] == "failed"
    assert "No idea provided" in result["errors"]


def test_parse_idea_appends_to_existing_errors():
    state = {"idea": "", "errors": ["prior error"]}
    result = parse_idea(state)
    assert result["errors"] == ["prior error", "No idea provided"]


def test_synthesize_combines_outputs(monkeypatch):
    monkeypatch.setattr(
        "backend.agents.ceo_agent.call_llm",
        lambda prompt, system=None: "Confident pitch narrative here.",
    )
    state = {
        "idea": "AI note-taking app",
        "cmo_output": {"market": "big"},
        "cto_output": {"stack": "python"},
        "cfo_output": {"funding_ask": {"amount": "$250k"}},
    }
    result = synthesize(state)
    assert result["ceo_narrative"] == "Confident pitch narrative here."


def test_synthesize_handles_llm_failure(monkeypatch):
    monkeypatch.setattr("backend.agents.ceo_agent.call_llm", lambda prompt, system=None: "")
    result = synthesize({"idea": "AI note-taking app"})
    assert "failed" in result["ceo_narrative"].lower()


def test_defend_rebuttal_returns_stripped_response(monkeypatch):
    monkeypatch.setattr(
        "backend.agents.ceo_agent.call_llm",
        lambda prompt, system=None: "  We have signed LOIs from 3 pilot customers.  ",
    )
    result = defend_rebuttal("What's your moat?", "We move fast.", "That's not a moat.", "narrative")
    assert result == "We have signed LOIs from 3 pilot customers."


def test_answer_investor_questions_basic_flow(monkeypatch):
    monkeypatch.setattr(
        "backend.agents.ceo_agent.call_llm",
        lambda prompt, system=None: "Solid answer.",
    )
    monkeypatch.setattr(
        "backend.agents.ceo_agent.generate_rebuttal",
        lambda q, a: "NO_REBUTTAL",
    )
    state = {
        "ceo_narrative": "narrative",
        "investor_questions": ["What's your CAC?", "Who's your competition?"],
    }
    result = answer_investor_questions(state)
    transcript = result["investor_transcript"]
    assert len(transcript) == 2
    assert all(entry["a"] == "Solid answer." for entry in transcript)
    assert all("rebuttal" not in entry for entry in transcript)


def test_answer_investor_questions_with_rebuttal(monkeypatch):
    monkeypatch.setattr(
        "backend.agents.ceo_agent.call_llm",
        lambda prompt, system=None: "Initial answer.",
    )
    monkeypatch.setattr(
        "backend.agents.ceo_agent.generate_rebuttal",
        lambda q, a: "But what about competitors?",
    )
    monkeypatch.setattr(
        "backend.agents.ceo_agent.defend_rebuttal",
        lambda q, a, r, n: "We're 6 months ahead.",
    )
    state = {
        "ceo_narrative": "narrative",
        "investor_questions": ["What's your CAC?"],
    }
    result = answer_investor_questions(state)
    entry = result["investor_transcript"][0]
    assert entry["rebuttal"] == "But what about competitors?"
    assert entry["defense"] == "We're 6 months ahead."


def test_answer_investor_questions_caps_rebuttals_at_two(monkeypatch):
    monkeypatch.setattr(
        "backend.agents.ceo_agent.call_llm",
        lambda prompt, system=None: "Answer.",
    )
    monkeypatch.setattr(
        "backend.agents.ceo_agent.generate_rebuttal",
        lambda q, a: "Pushback.",
    )
    monkeypatch.setattr(
        "backend.agents.ceo_agent.defend_rebuttal",
        lambda q, a, r, n: "Defense.",
    )
    state = {
        "ceo_narrative": "narrative",
        "investor_questions": [f"Q{i}" for i in range(5)],
    }
    result = answer_investor_questions(state)
    # global cap is now 4 total rounds (MAX_TOTAL_ROUNDS), not "2 questions with a rebuttal"
    total_rounds = sum(len(e.get("rounds", [])) for e in result["investor_transcript"])
    assert total_rounds == 4
    
@patch("backend.agents.ceo_agent.call_llm")
@patch("backend.agents.investor_agent.call_llm")
def test_answer_investor_questions_allows_two_rounds_per_question(mock_investor_llm, mock_ceo_llm):
    import itertools
    mock_ceo_llm.side_effect = itertools.cycle(["Weak answer.", "Better defense.", "Even better defense."])
    mock_investor_llm.return_value = "Still not convincing enough."

    from backend.agents.ceo_agent import answer_investor_questions
    state = {
        "investor_questions": ["Q1?"],
        "ceo_narrative": "Some narrative.",
    }
    result = answer_investor_questions(state)
    entry = result["investor_transcript"][0]

    assert len(entry["rounds"]) == 2  # hit the per-question cap
    assert entry["rebuttal"] == entry["rounds"][0]["rebuttal"]