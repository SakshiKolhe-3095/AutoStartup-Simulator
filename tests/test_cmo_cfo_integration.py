"""Integration test: CMO agent output format is compatible with CFO agent input."""
from backend.agents.cmo_agent import CMOAgent
from backend.agents.cfo_agent import CFOAgent, cfo_node


def test_cmo_output_shape_matches_cfo_expected_market_data(monkeypatch):
    """CMO.run() output should be usable directly as CFO's market_data param."""
    cmo = CMOAgent()
    monkeypatch.setattr(cmo, "analyze_market", lambda idea: {"tam": "$1B", "sam": "$100M", "som": "$5M", "reasoning": "r"})
    monkeypatch.setattr(cmo, "scan_competitors", lambda idea: [{"name": "CompA", "summary": "s"}])
    monkeypatch.setattr(cmo, "generate_persona", lambda idea: {"name": "Alex", "age_range": "25-34", "occupation": "PM"})
    monkeypatch.setattr(cmo, "generate_gtm_strategy", lambda idea, market: "GTM plan")

    cmo_output = cmo.run("AI note-taking app")

    # required keys CFO relies on downstream (calculate_unit_economics, recommend_funding_ask)
    assert "market" in cmo_output
    assert set(["tam", "sam", "som"]).issubset(cmo_output["market"].keys())


def test_cfo_node_consumes_real_cmo_output_shape(monkeypatch):
    """cfo_node() should accept a real CMO-shaped output via state['cmo_output'] without KeyErrors."""
    cmo_output = {
        "market": {"tam": "$1B", "sam": "$100M", "som": "$5M", "reasoning": "r"},
        "competitors": [{"name": "CompA", "summary": "s"}],
        "persona": {"name": "Alex", "age_range": "25-34", "occupation": "PM"},
        "gtm_strategy": "GTM plan",
    }

    monkeypatch.setattr("backend.agents.cfo_agent.classify_idea", lambda idea: "saas")
    monkeypatch.setattr(
        CFOAgent, "project_costs", lambda self, idea, category: {"development_cost": "d", "operational_cost": "o", "reasoning": "r"}
    )
    monkeypatch.setattr(
        CFOAgent, "propose_revenue_models", lambda self, idea, category: [{"model": "subscription", "description": "d"}]
    )

    captured = {}

    def fake_unit_econ(self, idea, category, market_data):
        captured["market_data"] = market_data
        return {"cac": "c", "ltv": "l", "gross_margin": "g", "reasoning": "r"}

    monkeypatch.setattr(CFOAgent, "calculate_unit_economics", fake_unit_econ)
    monkeypatch.setattr(
        CFOAgent, "recommend_funding_ask", lambda self, idea, category, market_data, cost_projection: {"amount": "$250k", "use_of_funds": "u", "reasoning": "r"}
    )

    state = {"idea": "AI note-taking app", "cmo_output": cmo_output}
    result = cfo_node(state)

    assert "cfo_output" in result
    assert result["cfo_output"]["funding_ask"]["amount"] == "$250k"
    # confirms CMO's full output (not just "market" key) reached CFO's calculate_unit_economics
    assert captured["market_data"] == cmo_output