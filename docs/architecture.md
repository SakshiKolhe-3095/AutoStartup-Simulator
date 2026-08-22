## Week 1 status (Yeshita side)
- Repo structure, README, requirements-gpu.txt/requirements-cpu.txt — done
- AgentState schema (backend/orchestration/state.py) — done
- CEO-agent skeleton: parse_idea, synthesize (stub) — done
- Investor-agent skeleton: select_questions, score_pitch (stub), question_bank.json — done
- CMO-agent (Faiza): skeleton + web_search integration — done
- CFO-agent (Sakshi): skeleton + deck_builder skeleton — done
- CTO-agent (Lakshit): not applicable — idle Week 1-4 per plan

## Week 2 status (Yeshita side)
- orchestration/graph.py: full stub pipeline wired (parse_idea -> [cmo|cto|cfo stubs] -> synthesize -> select_questions -> score_pitch) — done
- backend/utils/logger.py: shared logger, wired into graph.py + ceo_agent.py — done
- tests/test_orchestration.py: initial pipeline tests (valid idea, empty idea, score range) — done
- Bug fixed: parallel fan-out nodes must return delta dict only, not full state (InvalidUpdateError) — documented as team-wide rule
- docs/agent_roles.md: created, per-agent status tracked
- CMO-agent (Faiza): market-research prompt chain, competitor-scan, persona-gen, GTM draft — done
- CFO-agent (Sakshi): frontend scaffold (Streamlit), revenue-model logic, unit economics — done

## Week 3 status (Yeshita side)
- backend/tools/idea_classifier.py: rule-based category classifier (saas/marketplace/mobile_app/consumer) — done
- Question bank expanded with category-specific questions — done
- backend/models/llm_client.py: Groq LLM client wrapper (call_llm) — done
- CEO-agent: real LLM-based synthesis (replaced stub narrative) — done
- Investor-agent: Q&A loop v1 (single round, no rebuttal) — done
- tests/test_idea_classifier.py: added — done
- tests/test_orchestration.py: updated to mock call_llm — done
- pytest.ini added (pythonpath + asyncio fixture scope fix) — done
- .gitignore added (venv, __pycache__, .env, pytest cache) — done
- CMO-agent (Faiza): local LLM (Ollama) integration for summarization — done
- CFO-agent (Sakshi): pytest setup, deck-builder auto-populate from CEO output — done

## Week 4 status (Yeshita side)
- CEO-agent: parse, synthesize, answer_investor_questions, defend_rebuttal — done
- Investor-agent: question selection (category-aware), rebuttal generation, scoring — done
- Rebuttal loop: capped at 5 questions, max 2 rebuttal rounds — done
- CMO-agent (Faiza): in progress, behind schedule — pending final merge
- CFO-agent (Sakshi): status TBD — pending check
- CTO-agent (Lakshit): not started, scheduled Week 5

## Week 5 status (Lakshit side)
- CTO-agent (backend/agents/cto_agent.py): v1 done — MVP feature spec, tech stack
  recommendation, architecture summary, all category-grounded (saas/marketplace/
  mobile_app/consumer)
- Landing page codegen (backend/tools/codegen.py + html_validator.py): LLM -> single-file
  HTML+Tailwind, generate -> validate -> self-correct retry loop (max 3 attempts), hardcoded
  fallback template on repeated failure
- Local "deploy" step (backend/tools/deploy.py): writes generated page to
  data/landing_pages/<slug>.html
- backend/agents/schemas.py added: pydantic CTOOutput/MVPFeature/TechStackRecommendation/
  LandingPageValidation — documents the exact contract CTOAgent.run() returns for the
  deck-builder step and CEO synthesis
- graph.py: cto_stub replaced with real cto_node
- Reused the existing shared backend/models/llm_client.call_llm (Groq) rather than adding a
  second LLM provider abstraction — CTO-agent doesn't need web search, so Tavily/web_search.py
  wasn't touched either
- tests/test_cto_agent.py, tests/test_landing_page_gen.py, tests/test_deploy.py added

## Week 6 status (Lakshit side)
- Fixed graph.py: PR #20's merge conflict with upstream/main had been resolved via
  GitHub's web UI leaving literal `<<<<<<<`/`=======`/`>>>>>>>` markers committed —
  origin/main and upstream/main were both broken (SyntaxError on import) until this
  branch fixed it. Flagged separately for a direct hotfix on main.
- CFO-agent (backend/agents/cfo_agent.py): v1 done (Sakshi's slot was still unstarted) —
  cost projection, revenue model options, unit economics, funding ask, all grounded in
  CMO's market sizing and category-hinted like CTO's tech stack recommendations
- backend/agents/schemas.py: added CFOOutput/CostProjection/RevenueModelOption/
  UnitEconomics/FundingAsk, same conventions as CTOOutput
- graph.py: cfo_stub replaced with real cfo_node; topology changed from a flat 3-way
  parse_idea -> [cmo, cto, cfo] fan-out to parse_idea -> cmo -> [cto, cfo] — cfo genuinely
  needs cmo's output, and this LangGraph version (0.2.60) double-fires a fan-in node when
  its incoming branches have unequal depth (no `defer=True` support here), so cto is
  routed through cmo too for scheduling symmetry, even though cto's node body still
  doesn't touch cmo_output
- tests/test_cfo_agent.py added; tests/test_orchestration.py updated to mock
  WebSearchTool + cmo/cfo call_llm (previously only ceo_agent.call_llm was mocked, which
  broke once cmo_stub/cfo_stub were replaced with real nodes) and to cover cfo_output


  ## Milestone — Full pipeline first successful end-to-end run (real agents)
All four agents (CMO/CTO/CFO/Investor) now run with real logic (no stubs remaining).
Verified: 42/42 tests passing, landing page generated + validated + saved locally,
CFO output correctly grounded in CMO's market sizing, investor Q&A + rebuttal loop working.
Fixed: missing beautifulsoup4 dependency in requirements files (added post-merge).
Known non-blocking issue: CMO persona generation still returns empty fields when local
Ollama LLM is unreachable (WinError 10061) — falls back silently, not yet investigated.

## Update — persona-gen fix verified
Confirmed working: Ollama down -> Groq fallback fires -> persona fields fully populated (tested by Yeshita).

## New issue found — CFO funding_ask returns empty under Groq rate-limiting
Same symptom as the persona bug: `funding_ask` in cfo_output came back all-empty during a 
run that hit multiple Groq 429s (TPM limit 12000). Likely same root cause — a call inside 
recommend_funding_ask silently failing without fallback/retry when rate-limited. Needs the 
same fix pattern applied to persona-gen. Flagged to Lakshit.

## Rate-limiting is now a real bottleneck
Groq 429s are frequent enough (multiple per pipeline run) that they're both slowing runs 
significantly (~50s+ retry overhead in one run) AND causing silent data-quality bugs when 
retries aren't handled properly. Needs addressing before Wk9 hardening — options: reduce 
LLM calls per node, add proactive rate-limit-aware backoff, or spread calls across the 
pipeline more evenly instead of bursting them.


## CRITICAL — Groq free-tier daily token limit (100k TPD) is a real demo risk
Batch testing hit Groq's DAILY limit after ~2 full pipeline runs (~19:50, Aug 13). 
Subsequent calls failed with waits up to 15+ minutes. This means:
- Cannot run the pipeline more than ~5-8 times/day on this API key
- Live demo day is at risk if multiple practice runs happen before the actual demo
- Batch/stress testing at scale is not feasible on free tier as currently built
Needs a team decision: multiple Groq API keys rotated? Cache/mock mode for repeated 
demo practice? Switch some agents to local Ollama entirely to reduce Groq load?

## Week 9 — Model migration + token/quota hardening (Yeshita)
- Discovered Groq deprecated llama-3.3-70b-versatile / llama-3.1-8b-instant (404s on 
  fresh accounts). Migrated to openai/gpt-oss-120b (quality) and openai/gpt-oss-20b 
  (fast, structured calls) in llm_client.py.
- New daily quota: 200k tokens/day (vs old 100k) — real capacity improvement.
- Found & fixed: max_tokens=512 truncated JSON mid-response on new models — reverted 
  to 1024, added concise-response instructions to CFO/CMO system prompts instead.
- Batch hardening script added (scripts/batch_test.py) — 10 diverse ideas, not yet 
  run to completion on fresh quota (blocked by exhausted daily limit during testing).
- Known non-blocking issue carried over: CMO local Ollama call still fails silently 
  on this machine (WinError 10061), falls back to Groq correctly.
- STILL TO DO: run scripts/batch_test.py end-to-end tomorrow with fresh quota to 
  confirm real-world fix; review results for any remaining parse/truncation issues.