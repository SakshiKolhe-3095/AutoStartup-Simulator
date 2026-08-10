"""
CFO Agent - Cost Projection, Revenue Model & Unit Economics
Owner: Lakshit (filling in for Sakshi's unstarted slot)
"""
import json
from typing import Any, Dict, List, Optional

from backend.models.llm_client import call_llm
from backend.utils.logger import get_logger
from backend.orchestration.state import AgentState
from backend.tools.idea_classifier import classify_idea

logger = get_logger(__name__)

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
        )
        prompt = f"Startup idea: {idea}\nCategory: {category}"
        raw = call_llm(prompt=prompt, system=system, temperature=0.3)
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {"development_cost": "", "operational_cost": "", "reasoning": raw}

    def propose_revenue_models(self, idea: str, category: str) -> List[Dict[str, str]]:
        """Propose 2-3 viable revenue models for this idea/category."""
        hint = REVENUE_MODEL_HINTS.get(category, "")
        system = (
            "You are a startup CFO proposing revenue models. Given a startup idea and "
            "category, propose 2-3 viable revenue models. Respond ONLY as JSON: "
            '[{"model": "...", "description": "..."}]'
        )
        prompt = f"Startup idea: {idea}\nCategory: {category}\nGuidance: {hint}"
        raw = call_llm(prompt=prompt, system=system, temperature=0.4)
        raw = self._clean_json(raw)
        try:
            options = json.loads(raw)
            return options if isinstance(options, list) else []
        except (json.JSONDecodeError, TypeError):
            return [{"model": "parse_error", "description": raw}]

    def calculate_unit_economics(self, idea: str, category: str, market_data: Dict[str, Any]) -> Dict[str, str]:
        """Estimate CAC, LTV, and gross margin, grounded in CMO's market sizing."""
        system = (
            "You are a startup CFO estimating unit economics. These are rough, clearly-"
            "labeled estimates, not precise figures — ground them in the market data given "
            "and explain your reasoning briefly. Respond ONLY as JSON: "
            '{"cac": "...", "ltv": "...", "gross_margin": "...", "reasoning": "..."}'
        )
        prompt = (
            f"Startup idea: {idea}\nCategory: {category}\n"
            f"Market sizing (from CMO): {json.dumps(market_data)}"
        )
        raw = call_llm(prompt=prompt, system=system, temperature=0.3)
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
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
        )
        prompt = (
            f"Startup idea: {idea}\nCategory: {category}\n"
            f"Market sizing (from CMO): {json.dumps(market_data)}\n"
            f"Cost projection: {json.dumps(cost_projection)}"
        )
        raw = call_llm(prompt=prompt, system=system, temperature=0.3)
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
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


def cfo_node(state: AgentState) -> dict:
    """LangGraph node — replaces graph.py's cfo_stub with the real CFO-agent."""
    idea = state.get("idea", "")
    market_data = state.get("cmo_output") or {}
    agent = CFOAgent()
    output = agent.run(idea, market_data=market_data)
    return {"cfo_output": output}
