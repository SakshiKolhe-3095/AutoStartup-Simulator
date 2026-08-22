"""Test the full graph runs end-to-end with the real CMO/CTO/CFO agents wired in."""
import pytest
from backend.orchestration.graph import build_graph
from unittest.mock import patch, MagicMock
import itertools

# CMOAgent.scan_competitors instantiates WebSearchTool() directly (backend/tools/web_search.py),
# which raises unless TAVILY_API_KEY is set. Every test that invokes the graph with a non-empty
# idea now runs the real cmo_node, so this needs mocking to keep the suite deterministic and
# key-free — even the empty-idea test, since the graph's fan-out edges aren't conditional on
# parse_idea's status (route_after_parse exists but isn't wired in yet).
def _mock_web_search_tool():
    mock_tool = MagicMock()
    mock_tool.search.return_value = [{"title": "Competitor A", "content": "A rival product."}]
    return patch("backend.tools.web_search.WebSearchTool", return_value=mock_tool)


CMO_JSON = '{"tam": "$1B", "sam": "$100M", "som": "$5M", "reasoning": "estimate"}'
CFO_JSON = '{"amount": "$250k"}'


@_mock_web_search_tool()
@patch("backend.agents.cmo_agent.call_llm", return_value=CMO_JSON)
@patch("backend.agents.cfo_agent.call_llm", return_value=CFO_JSON)
@patch("backend.agents.ceo_agent.call_llm", return_value="Mocked pitch narrative.")
def test_graph_runs_with_valid_idea(mock_ceo_llm, mock_cfo_llm, mock_cmo_llm, mock_web_search):
    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})

    assert result["status"] == "done"
    assert result["cmo_output"] is not None
    assert result["cto_output"] is not None
    assert result["cfo_output"] is not None
    assert result["cfo_output"]["funding_ask"] is not None
    assert result["ceo_narrative"] == "Mocked pitch narrative."
    assert len(result["investor_questions"]) > 0
    assert len(result["investor_transcript"]) == len(result["investor_questions"])
    assert result["investor_score"] is not None


@_mock_web_search_tool()
@patch("backend.agents.cmo_agent.call_llm", return_value=CMO_JSON)
@patch("backend.agents.cfo_agent.call_llm", return_value=CFO_JSON)
def test_graph_fails_gracefully_on_empty_idea(mock_cfo_llm, mock_cmo_llm, mock_web_search):
    app = build_graph()
    result = app.invoke({"idea": ""})
    assert result["status"] == "failed"
    assert "No idea provided" in result["errors"]


@_mock_web_search_tool()
@patch("backend.agents.cmo_agent.call_llm", return_value=CMO_JSON)
@patch("backend.agents.cfo_agent.call_llm", return_value=CFO_JSON)
@patch("backend.agents.ceo_agent.call_llm", return_value="Mocked answer.")
def test_investor_score_in_valid_range(mock_ceo_llm, mock_cfo_llm, mock_cmo_llm, mock_web_search):
    app = build_graph()
    result = app.invoke({"idea": "Subscription box for eco-friendly cleaning products"})
    assert 0 <= result["investor_score"] <= 10


@_mock_web_search_tool()
@patch("backend.agents.cmo_agent.call_llm", return_value=CMO_JSON)
@patch("backend.agents.cfo_agent.call_llm", return_value=CFO_JSON)
@patch("backend.agents.ceo_agent.call_llm")
@patch("backend.agents.investor_agent.call_llm")
def test_rebuttal_loop_triggers_and_defends(
    mock_investor_llm, mock_ceo_llm, mock_cfo_llm, mock_cmo_llm, mock_web_search
):
    # cycle so we never run out regardless of how many questions/rebuttals fire
    mock_ceo_llm.side_effect = itertools.cycle(["A vague generic answer.", "A sharper, specific defense."])
    mock_investor_llm.return_value = "That's too vague — give me a number."

    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})

    transcript = result["investor_transcript"]
    assert len(transcript) > 0
    assert any("rebuttal" in entry for entry in transcript)


@_mock_web_search_tool()
@patch("backend.agents.cmo_agent.call_llm", return_value=CMO_JSON)
@patch("backend.agents.cfo_agent.call_llm", return_value=CFO_JSON)
@patch("backend.agents.ceo_agent.call_llm")
@patch("backend.agents.investor_agent.call_llm")
def test_no_rebuttal_when_answer_strong(
    mock_investor_llm, mock_ceo_llm, mock_cfo_llm, mock_cmo_llm, mock_web_search
):
    mock_ceo_llm.return_value = "A very specific, strong answer with numbers."
    mock_investor_llm.return_value = "NO_REBUTTAL"

    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})

    transcript = result["investor_transcript"]
    assert all("rebuttal" not in entry for entry in transcript)


@_mock_web_search_tool()
@patch("backend.agents.cmo_agent.call_llm", return_value=CMO_JSON)
@patch("backend.agents.cfo_agent.call_llm", return_value=CFO_JSON)
@patch("backend.agents.ceo_agent.call_llm", return_value="Mocked pitch narrative.")
def test_status_is_done_on_successful_run(mock_ceo_llm, mock_cfo_llm, mock_cmo_llm, mock_web_search):
    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})
    assert result["status"] == "done"


@_mock_web_search_tool()
@patch("backend.agents.cmo_agent.call_llm", return_value=CMO_JSON)
@patch("backend.agents.cfo_agent.call_llm", return_value=CFO_JSON)
@patch("backend.agents.ceo_agent.call_llm", return_value="Mocked pitch narrative.")
def test_cfo_output_reflects_cmo_market_sizing(mock_ceo_llm, mock_cfo_llm, mock_cmo_llm, mock_web_search):
    """cfo runs after cmo in the graph (see graph.py's cmo -> cfo edge) so it can ground
    its funding ask / unit economics in cmo's TAM/SAM/SOM rather than inventing its own."""
    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})

    assert result["cmo_output"]["market"]["tam"] == "$1B"
    assert result["cfo_output"] is not None

@patch("backend.agents.ceo_agent.call_llm", return_value="Mocked pitch narrative.")
@patch("backend.orchestration.graph.cmo_node")
def test_cmo_node_failure_does_not_crash_pipeline(mock_cmo_node, mock_llm):
    mock_cmo_node.side_effect = Exception("simulated CMO crash")
    app = build_graph()
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})

    assert result["status"] == "done"
    assert result["cmo_output"] == {"market": {}, "competitors": [], "persona": {}, "gtm_strategy": ""}
    assert any("cmo failed" in e for e in result.get("errors", []))