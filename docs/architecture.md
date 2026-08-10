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