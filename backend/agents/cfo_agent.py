"""
CFO Agent - Cost Projection, Revenue Model & Unit Economics
Owner: Lakshit (filling in for Sakshi's unstarted slot)
"""
import json
import time
from typing import Any, Dict, List, Optional
from backend.models.llm_client import call_llm, FAST_MODEL

from backend.utils.logger import get_logger
from backend.orchestration.state import AgentState
from backend.tools.idea_classifier import classify_idea

logger = get_logger(__name__)

# Same root-cause fix as cmo_agent.py's generate_persona (Ollama-down -> falls back to
# Groq): a failed LLM call must not silently resolve to blank-but-valid-looking fields.
# CFO's functions only ever call Groq (no second provider like CMO's local Ollama to fall
# back to), so the adaptation here is a bounded retry of the same call instead of a
# provider swap — llm_client.call_llm() catches every exception generically and returns
# "" (see its `except Exception`), so a 429/rate-limit can't be distinguished from any
# other failure at this layer; an empty response is the only signal available.
_RETRY_DELAYS_SECONDS = [1, 2]


def _call_llm_with_retry(prompt: str, system: str, temperature: float, context: str, model: str = FAST_MODEL) -> str:
    raw = call_llm(prompt=prompt, system=system, temperature=temperature, model=model)
    for delay in _RETRY_DELAYS_SECONDS:
        if raw:
            return raw
        logger.warning(f"{context}: LLM call returned empty (possible Groq rate-limit) — retrying in {delay}s")
        time.sleep(delay)
        raw = call_llm(prompt=prompt, system=system, temperature=temperature, model=model)
    if not raw:
        logger.warning(f"{context}: LLM call still empty after retries")
    return raw

# Category-specific hints keep revenue-model prompts grounded to the 4 supported
# categories instead of fully open-ended generation.
REVENUE_MODEL_HINTS = {
    "saas": "typical options: tiered monthly subscription, per-seat pricing, usage-based billing",
    "marketplace": "typical options: take-rate/commission on transactions, listing fees, "
                   "featured-placement upsells",
    "mobile_app": "typical options: freemium + in-app purchases, ad-supported free tier, "
                  "subscription for premium features",
    "consumer": "typical options: one-time purchase, subscription/replenishment box, "
                "bundle upsells",
}

# Appended to every system prompt below — keeps JSON responses short enough to never
# get truncated by max_tokens, and reduces token spend per call (Groq free-tier TPM/TPD).
_CONCISE_SUFFIX = " Keep the JSON compact — 1-2 short sentences per field, no long paragraphs."


class CFOAgent:
    def __init__(self):
        pass

    @staticmethod
    def _clean_json(raw: str) -> str:
        """Strip markdown code fences that LLMs sometimes wrap JSON in."""
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            raw = raw.rsplit("```", 1)[0]
        return raw.strip()

    def project_costs(self, idea: str, category: str) -> Dict[str, str]:
        """Estimate development + operational cost for the MVP."""
        system = (
            "You are a startup CFO estimating lean MVP costs on free-tier/bootstrapped "
            "infrastructure. Respond ONLY as JSON: "
            '{"development_cost": "...", "operational_cost": "...", "reasoning": "..."}'
            + _CONCISE_SUFFIX
        )
        prompt = f"Startup idea: {idea}\nCategory: {category}"
        raw = _call_llm_with_retry(prompt, system, 0.3, context="project_costs")
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"project_costs: failed to parse LLM response as JSON — returning blank fields. raw={raw!r}")
            return {"development_cost": "", "operational_cost": "", "reasoning": raw}

    def propose_revenue_models(self, idea: str, category: str) -> List[Dict[str, str]]:
        """Propose 2-3 viable revenue models for this idea/category."""
        hint = REVENUE_MODEL_HINTS.get(category, "")
        system = (
            "You are a startup CFO proposing revenue models. Given a startup idea and "
            "category, propose 2-3 viable revenue models. Respond ONLY as JSON: "
            '[{"model": "...", "description": "..."}]'
            + _CONCISE_SUFFIX
        )
        prompt = f"Startup idea: {idea}\nCategory: {category}\nGuidance: {hint}"
        raw = _call_llm_with_retry(prompt, system, 0.4, context="propose_revenue_models")
        raw = self._clean_json(raw)
        try:
            options = json.loads(raw)
            return options if isinstance(options, list) else []
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"propose_revenue_models: failed to parse LLM response as JSON — returning blank fields. raw={raw!r}")
            return [{"model": "parse_error", "description": raw}]

    def calculate_unit_economics(self, idea: str, category: str, market_data: Dict[str, Any]) -> Dict[str, str]:
        """Estimate CAC, LTV, and gross margin, grounded in CMO's market sizing."""
        system = (
            "You are a startup CFO estimating unit economics. These are rough, clearly-"
            "labeled estimates, not precise figures — ground them in the market data given "
            "and explain your reasoning briefly. Respond ONLY as JSON: "
            '{"cac": "...", "ltv": "...", "gross_margin": "...", "reasoning": "..."}'
            + _CONCISE_SUFFIX
        )
        prompt = (
            f"Startup idea: {idea}\nCategory: {category}\n"
            f"Market sizing (from CMO): {json.dumps(market_data)}"
        )
        raw = _call_llm_with_retry(prompt, system, 0.3, context="calculate_unit_economics")
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"calculate_unit_economics: failed to parse LLM response as JSON — returning blank fields. raw={raw!r}")
            return {"cac": "", "ltv": "", "gross_margin": "", "reasoning": raw}

    def recommend_funding_ask(
        self,
        idea: str,
        category: str,
        market_data: Dict[str, Any],
        cost_projection: Dict[str, Any],
    ) -> Dict[str, str]:
        """Recommend a funding raise amount grounded in cost projection and market size."""
        system = (
            "You are a startup CFO recommending a funding ask. Ground the amount in the "
            "cost projection and market size given, with brief reasoning — no bare numbers "
            "without justification. Respond ONLY as JSON: "
            '{"amount": "...", "use_of_funds": "...", "reasoning": "..."}'
            + _CONCISE_SUFFIX
        )
        prompt = (
            f"Startup idea: {idea}\nCategory: {category}\n"
            f"Market sizing (from CMO): {json.dumps(market_data)}\n"
            f"Cost projection: {json.dumps(cost_projection)}"
        )
        raw = _call_llm_with_retry(prompt, system, 0.3, context="recommend_funding_ask")
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"recommend_funding_ask: failed to parse LLM response as JSON — returning blank fields. raw={raw!r}")
            return {"amount": "", "use_of_funds": "", "reasoning": raw}

    def run(self, idea: str, category: Optional[str] = None, market_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main entrypoint — orchestrates full CFO analysis.

        market_data should be CMO-agent's output (state["cmo_output"]) so funding ask and
        unit economics are grounded in real market sizing rather than invented independently.
        Returns a dict matching backend.agents.schemas.CFOOutput's shape.
        """
        category = category or classify_idea(idea)
        market_data = market_data or {}

        cost_projection = self.project_costs(idea, category)
        revenue_model_options = self.propose_revenue_models(idea, category)
        unit_economics = self.calculate_unit_economics(idea, category, market_data)
        funding_ask = self.recommend_funding_ask(idea, category, market_data, cost_projection)

        return {
            "category": category,
            "cost_projection": cost_projection,
            "revenue_model_options": revenue_model_options,
            "unit_economics": unit_economics,
            "funding_ask": funding_ask,
        }

    def revenue_model_options(self, idea: str) -> list:
        """
        Skeleton: returns candidate revenue models for the idea.
        TODO: refine with LLM call.
        """
        return ["subscription", "freemium", "one-time purchase", "ads"]

    def unit_economics(self, revenue_per_user: float, cost_per_user: float) -> dict:
        """
        Skeleton: basic unit economics calc.
        """
        margin = revenue_per_user - cost_per_user
        margin_pct = (margin / revenue_per_user * 100) if revenue_per_user else 0
        return {
            "revenue_per_user": revenue_per_user,
            "cost_per_user": cost_per_user,
            "margin": margin,
            "margin_pct": round(margin_pct, 2),
        }


def cfo_node(state: AgentState) -> dict:
    """LangGraph node — replaces graph.py's cfo_stub with the real CFO-agent."""
    idea = state.get("idea", "")
    market_data = state.get("cmo_output") or {}
    agent = CFOAgent()
    output = agent.run(idea, market_data=market_data)
    return {"cfo_output": output}