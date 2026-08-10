"""Tests for CFOAgent"""
from backend.agents.cfo_agent import CFOAgent


def test_clean_json_strips_fences():
    agent = CFOAgent()
    raw = '```json\n{"key": "value"}\n```'
    result = agent._clean_json(raw)
    assert result == '{"key": "value"}'


def test_clean_json_passthrough_plain():
    agent = CFOAgent()
    raw = '{"key": "value"}'
    result = agent._clean_json(raw)
    assert result == '{"key": "value"}'


def test_project_costs_returns_dict_keys(monkeypatch):
    agent = CFOAgent()
    monkeypatch.setattr(
        "backend.agents.cfo_agent.call_llm",
        lambda prompt, system, temperature=0.3: (
            '{"development_cost": "$15k", "operational_cost": "$500/mo", "reasoning": "lean MVP"}'
        ),
    )
    result = agent.project_costs("AI note-taking app", "saas")
    assert set(["development_cost", "operational_cost", "reasoning"]).issubset(result.keys())


def test_project_costs_handles_bad_json(monkeypatch):
    agent = CFOAgent()
    monkeypatch.setattr(
        "backend.agents.cfo_agent.call_llm", lambda prompt, system, temperature=0.3: "not json"
    )
    result = agent.project_costs("AI note-taking app", "saas")
    assert result["reasoning"] == "not json"


def test_propose_revenue_models_returns_list(monkeypatch):
    agent = CFOAgent()
    monkeypatch.setattr(
        "backend.agents.cfo_agent.call_llm",
        lambda prompt, system, temperature=0.4: (
            '[{"model": "subscription", "description": "monthly tiers"}, '
            '{"model": "freemium", "description": "free tier + paid upgrade"}]'
        ),
    )
    result = agent.propose_revenue_models("AI note-taking app", "saas")
    assert isinstance(result, list)
    assert result[0]["model"] == "subscription"


def test_calculate_unit_economics_returns_dict_keys(monkeypatch):
    agent = CFOAgent()
    monkeypatch.setattr(
        "backend.agents.cfo_agent.call_llm",
        lambda prompt, system, temperature=0.3: (
            '{"cac": "$40", "ltv": "$300", "gross_margin": "70%", "reasoning": "based on TAM"}'
        ),
    )
    result = agent.calculate_unit_economics(
        "AI note-taking app", "saas", {"market": {"tam": "$1B", "sam": "$100M", "som": "$5M"}}
    )
    assert set(["cac", "ltv", "gross_margin", "reasoning"]).issubset(result.keys())


def test_recommend_funding_ask_returns_dict_keys(monkeypatch):
    agent = CFOAgent()
    monkeypatch.setattr(
        "backend.agents.cfo_agent.call_llm",
        lambda prompt, system, temperature=0.3: (
            '{"amount": "$250k", "use_of_funds": "hiring + infra", "reasoning": "12mo runway"}'
        ),
    )
    result = agent.recommend_funding_ask(
        "AI note-taking app", "saas", {"market": {"tam": "$1B"}}, {"development_cost": "$15k"}
    )
    assert set(["amount", "use_of_funds", "reasoning"]).issubset(result.keys())


def test_run_produces_full_output(monkeypatch):
    agent = CFOAgent()
    monkeypatch.setattr("backend.agents.cfo_agent.classify_idea", lambda idea: "saas")
    monkeypatch.setattr(
        agent, "project_costs", lambda idea, category: {"development_cost": "d", "operational_cost": "o", "reasoning": "r"}
    )
    monkeypatch.setattr(
        agent,
        "propose_revenue_models",
        lambda idea, category: [{"model": "subscription", "description": "monthly tiers"}],
    )
    monkeypatch.setattr(
        agent,
        "calculate_unit_economics",
        lambda idea, category, market_data: {"cac": "c", "ltv": "l", "gross_margin": "g", "reasoning": "r"},
    )
    monkeypatch.setattr(
        agent,
        "recommend_funding_ask",
        lambda idea, category, market_data, cost_projection: {
            "amount": "$250k",
            "use_of_funds": "u",
            "reasoning": "r",
        },
    )

    result = agent.run("AI note-taking app", market_data={"market": {"tam": "$1B"}})
    assert result["category"] == "saas"
    assert result["funding_ask"]["amount"] == "$250k"
    assert result["revenue_model_options"][0]["model"] == "subscription"


def test_run_defaults_market_data_to_empty_dict(monkeypatch):
    agent = CFOAgent()
    monkeypatch.setattr("backend.agents.cfo_agent.call_llm", lambda prompt, system, temperature=0.3: "{}")
    result = agent.run("AI note-taking app", category="saas")
    assert result["category"] == "saas"


def test_cfo_node_passes_cmo_output_as_market_data(monkeypatch):
    from backend.agents.cfo_agent import cfo_node

    captured = {}

    def fake_run(self, idea, category=None, market_data=None):
        captured["market_data"] = market_data
        return {"category": "saas"}

    monkeypatch.setattr("backend.agents.cfo_agent.CFOAgent.run", fake_run)
    result = cfo_node({"idea": "AI note-taking app", "cmo_output": {"market": {"tam": "$1B"}}})
    assert result == {"cfo_output": {"category": "saas"}}
    assert captured["market_data"] == {"market": {"tam": "$1B"}}


def test_cfo_node_defaults_missing_cmo_output_to_empty_dict(monkeypatch):
    from backend.agents.cfo_agent import cfo_node

    captured = {}

    def fake_run(self, idea, category=None, market_data=None):
        captured["market_data"] = market_data
        return {"category": "saas"}

    monkeypatch.setattr("backend.agents.cfo_agent.CFOAgent.run", fake_run)
    cfo_node({"idea": "AI note-taking app"})
    assert captured["market_data"] == {}
