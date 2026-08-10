"""Tests for CTOAgent"""
from backend.agents.cto_agent import CTOAgent


def test_clean_json_strips_fences():
    agent = CTOAgent()
    raw = '```json\n[{"name": "x"}]\n```'
    result = agent._clean_json(raw)
    assert result == '[{"name": "x"}]'


def test_clean_json_passthrough_plain():
    agent = CTOAgent()
    raw = '[{"name": "x"}]'
    result = agent._clean_json(raw)
    assert result == '[{"name": "x"}]'


def test_design_mvp_spec_returns_list(monkeypatch):
    agent = CTOAgent()
    monkeypatch.setattr(
        "backend.agents.cto_agent.call_llm",
        lambda prompt, system, temperature=0.4: (
            '[{"name": "Signup", "description": "Email capture", "priority": "must_have"}]'
        ),
    )
    result = agent.design_mvp_spec("AI note-taking app", "saas")
    assert isinstance(result, list)
    assert result[0]["name"] == "Signup"


def test_design_mvp_spec_handles_bad_json(monkeypatch):
    agent = CTOAgent()
    monkeypatch.setattr(
        "backend.agents.cto_agent.call_llm", lambda prompt, system, temperature=0.4: "not json"
    )
    result = agent.design_mvp_spec("AI note-taking app", "saas")
    assert result[0]["name"] == "parse_error"


def test_recommend_tech_stack_returns_dict_keys(monkeypatch):
    agent = CTOAgent()
    monkeypatch.setattr(
        "backend.agents.cto_agent.call_llm",
        lambda prompt, system, temperature=0.3: (
            '{"frontend": "Next.js", "backend": "FastAPI", "database": "Postgres", '
            '"hosting": "Render", "rationale": "lean and free-tier friendly"}'
        ),
    )
    result = agent.recommend_tech_stack("AI note-taking app", "saas")
    assert set(["frontend", "backend", "database", "hosting", "rationale"]).issubset(result.keys())


def test_run_produces_full_output(monkeypatch):
    agent = CTOAgent()
    monkeypatch.setattr("backend.agents.cto_agent.classify_idea", lambda idea: "saas")
    monkeypatch.setattr(
        agent,
        "design_mvp_spec",
        lambda idea, category: [{"name": "Signup", "description": "d", "priority": "must_have"}],
    )
    monkeypatch.setattr(
        agent,
        "recommend_tech_stack",
        lambda idea, category: {
            "frontend": "Next.js",
            "backend": "FastAPI",
            "database": "Postgres",
            "hosting": "Render",
            "rationale": "r",
        },
    )
    monkeypatch.setattr(
        agent, "summarize_architecture", lambda idea, tech_stack, mvp_features: "Simple architecture."
    )
    monkeypatch.setattr(
        "backend.agents.cto_agent.generate_landing_page",
        lambda idea, mvp_features, tech_stack: (
            "<!DOCTYPE html><html><head></head><body></body></html>",
            {"valid": True, "attempts": 1, "errors": [], "fallback": False},
        ),
    )
    monkeypatch.setattr(
        "backend.agents.cto_agent.save_landing_page",
        lambda idea, html: "data/landing_pages/test.html",
    )

    result = agent.run("AI note-taking app")
    assert result["category"] == "saas"
    assert result["landing_page_path"] == "data/landing_pages/test.html"
    assert result["tech_stack"]["frontend"] == "Next.js"
    assert result["landing_page_validation"]["valid"] is True


def test_cto_node_returns_cto_output_key(monkeypatch):
    from backend.agents.cto_agent import cto_node

    monkeypatch.setattr(
        "backend.agents.cto_agent.CTOAgent.run", lambda self, idea, category=None: {"category": "saas"}
    )
    result = cto_node({"idea": "AI note-taking app"})
    assert result == {"cto_output": {"category": "saas"}}
