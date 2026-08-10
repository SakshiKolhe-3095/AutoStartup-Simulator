# Agent Roles

## CEO-agent (Yeshita) — backend/agents/ceo_agent.py
- parse_idea: validates/cleans raw idea input
- synthesize: combines CMO+CTO+CFO outputs into narrative (LLM-based synthesis pending Wk3)

## Investor-agent (Yeshita) — backend/agents/investor_agent.py
- select_questions: picks questions from data/question_bank.json
- score_pitch: scores 0-10 based on Q&A (stub — real LLM scoring pending Wk8)

## CMO-agent (Faiza) — backend/agents/cmo_agent.py
- Status: skeleton + web_search integrated (Wk1). Full v1 in progress.

## CFO-agent (Sakshi) — backend/agents/cfo_agent.py
- Status: v1 done (filled in by Lakshit since CTO-agent was already wired), wired into
  graph.py (real `cfo_node`, replaces `cfo_stub`).
- project_costs(idea, category): development + operational cost estimate with reasoning
- propose_revenue_models(idea, category): 2-3 viable revenue model options, grounded
  per-category via REVENUE_MODEL_HINTS (saas/marketplace/mobile_app/consumer)
- calculate_unit_economics(idea, category, market_data): CAC/LTV/gross margin estimates,
  grounded in CMO's market sizing (market_data = state["cmo_output"])
- recommend_funding_ask(idea, category, market_data, cost_projection): raise amount +
  use of funds, grounded in cost projection and market size, not a bare number
- run(idea, category=None, market_data=None): full pipeline, returns dict matching
  backend/agents/schemas.py::CFOOutput — the contract for the deck-builder step and CEO
  synthesis, available at state["cfo_output"]
- Graph dependency: cfo needs cmo's TAM/SAM/SOM as input, so graph.py routes
  parse_idea -> cmo -> [cto, cfo] rather than a flat 3-way fan-out (see graph.py comment
  for why — this LangGraph version double-fires a fan-in node when its incoming branches
  have unequal depth, so cto is also routed through cmo for scheduling symmetry even
  though its node body doesn't use cmo's output)
- Uses the shared backend/models/llm_client.call_llm (Groq), same pattern as CMO/CTO

## CTO-agent (Lakshit) — backend/agents/cto_agent.py
- Status: v1 done, wired into graph.py (real `cto_node`, replaces `cto_stub`).
- design_mvp_spec(idea, category): 4-6 prioritized MVP features
- recommend_tech_stack(idea, category): frontend/backend/database/hosting + rationale,
  grounded per-category via TECH_STACK_HINTS (saas/marketplace/mobile_app/consumer)
- summarize_architecture(idea, tech_stack, mvp_features): short investor-facing summary
- run(idea, category=None): full pipeline, returns dict matching
  backend/agents/schemas.py::CTOOutput — this is the contract for the deck-builder step
  (Sakshi) and CEO synthesis, available at state["cto_output"]
- Landing page codegen: backend/tools/codegen.py — LLM -> single-file HTML+Tailwind,
  generate -> validate -> self-correct loop (backend/tools/html_validator.py), max 3
  retries, falls back to a hardcoded safe template if all retries fail
- "Deploy" step: backend/tools/deploy.py — writes the HTML to data/landing_pages/
  (local only, no paid hosting per project scope)
- Uses the shared backend/models/llm_client.call_llm (Groq) — no separate provider
  abstraction added; no web search needed for this agent

## Orchestration (Yeshita) — backend/orchestration/graph.py
- parse_idea -> cmo -> [cto, cfo] (parallel) -> synthesize -> select_questions ->
  answer_questions -> score_pitch -> END
  (cfo needs cmo's market sizing as input; cto routed through cmo too for LangGraph
  fan-in scheduling symmetry — see CFO-agent section above and graph.py comments)