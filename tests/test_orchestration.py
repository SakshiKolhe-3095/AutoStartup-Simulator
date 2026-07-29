"""Test the full graph runs end-to-end with stub agents."""
import pytest
from backend.orchestration.graph import build_graph
from unittest.mock import patch
import itertools


@patch("backend.agents.ceo_agent.call_llm", return_value="Mocked pitch narrative.")
def test_graph_runs_with_valid_idea(mock_llm):
    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})

    assert result["status"] == "done"
    assert result["cmo_output"] is not None
    assert result["cto_output"] is not None
    assert result["cfo_output"] is not None
    assert result["ceo_narrative"] == "Mocked pitch narrative."
    assert len(result["investor_questions"]) > 0
    assert len(result["investor_transcript"]) == len(result["investor_questions"])
    assert result["investor_score"] is not None


def test_graph_fails_gracefully_on_empty_idea():
    app = build_graph()
    result = app.invoke({"idea": ""})
    assert result["status"] == "failed"
    assert "No idea provided" in result["errors"]


@patch("backend.agents.ceo_agent.call_llm", return_value="Mocked answer.")
def test_investor_score_in_valid_range(mock_llm):
    app = build_graph()
    result = app.invoke({"idea": "Subscription box for eco-friendly cleaning products"})
    assert 0 <= result["investor_score"] <= 10


@patch("backend.agents.ceo_agent.call_llm")
@patch("backend.agents.investor_agent.call_llm")
def test_rebuttal_loop_triggers_and_defends(mock_investor_llm, mock_ceo_llm):
    # cycle so we never run out regardless of how many questions/rebuttals fire
    mock_ceo_llm.side_effect = itertools.cycle(["A vague generic answer.", "A sharper, specific defense."])
    mock_investor_llm.return_value = "That's too vague — give me a number."

    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})

    transcript = result["investor_transcript"]
    assert len(transcript) > 0
    assert any("rebuttal" in entry for entry in transcript)

@patch("backend.agents.ceo_agent.call_llm")
@patch("backend.agents.investor_agent.call_llm")
def test_no_rebuttal_when_answer_strong(mock_investor_llm, mock_ceo_llm):
    mock_ceo_llm.return_value = "A very specific, strong answer with numbers."
    mock_investor_llm.return_value = "NO_REBUTTAL"

    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})

    transcript = result["investor_transcript"]
    assert all("rebuttal" not in entry for entry in transcript)

@patch("backend.agents.ceo_agent.call_llm", return_value="Mocked pitch narrative.")
def test_status_is_done_on_successful_run(mock_llm):
    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})
    assert result["status"] == "done"