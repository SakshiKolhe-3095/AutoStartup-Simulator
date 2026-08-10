"""
CTO Agent - MVP Spec, Tech Stack & Landing Page Codegen
Owner: Lakshit
"""
import json
from typing import Any, Dict, List, Optional

from backend.models.llm_client import call_llm
from backend.utils.logger import get_logger
from backend.orchestration.state import AgentState
from backend.tools.idea_classifier import classify_idea
from backend.tools.codegen import generate_landing_page
from backend.tools.deploy import save_landing_page

logger = get_logger(__name__)

# Category-specific hints keep prompts grounded to the 4 supported categories
# instead of fully open-ended tech stack generation.
TECH_STACK_HINTS = {
    "saas": "typical stack: React/Next.js frontend, FastAPI or Node backend, Postgres, "
            "deployed on Vercel/Render free tier",
    "marketplace": "typical stack: Next.js frontend for buyer/seller listings, FastAPI "
                   "backend, Postgres with search indexing, payments noted but not implemented",
    "mobile_app": "typical stack: React Native or Flutter client, FastAPI backend, Postgres, "
                  "push notifications via a free-tier provider",
    "consumer": "typical stack: lightweight storefront (Next.js), FastAPI backend, Postgres, "
                "CDN-hosted static assets",
}


class CTOAgent:
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

    def design_mvp_spec(self, idea: str, category: str) -> List[Dict[str, Any]]:
        """Produce a prioritized MVP feature list."""
        system = (
            "You are a pragmatic CTO scoping an MVP. Given a startup idea and category, "
            "list 4-6 MVP features. Respond ONLY as JSON: "
            '[{"name": "...", "description": "...", "priority": "must_have"|"nice_to_have"}]'
        )
        prompt = f"Startup idea: {idea}\nCategory: {category}"
        raw = call_llm(prompt=prompt, system=system, temperature=0.4)
        raw = self._clean_json(raw)
        try:
            features = json.loads(raw)
            return features if isinstance(features, list) else []
        except (json.JSONDecodeError, TypeError):
            return [{"name": "parse_error", "description": raw, "priority": "must_have"}]

    def recommend_tech_stack(self, idea: str, category: str) -> Dict[str, str]:
        """Recommend a lean, free-tier-friendly tech stack."""
        hint = TECH_STACK_HINTS.get(category, "")
        system = (
            "You are a CTO recommending a lean, free-tier-friendly tech stack. "
            'Respond ONLY as JSON: {"frontend": "...", "backend": "...", '
            '"database": "...", "hosting": "...", "rationale": "..."}'
        )
        prompt = f"Startup idea: {idea}\nCategory: {category}\nGuidance: {hint}"
        raw = call_llm(prompt=prompt, system=system, temperature=0.3)
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {"frontend": "", "backend": "", "database": "", "hosting": "", "rationale": raw}

    def summarize_architecture(
        self, idea: str, tech_stack: Dict[str, Any], mvp_features: List[Dict[str, Any]]
    ) -> str:
        """Write a short, investor-facing architecture summary."""
        system = (
            "You are a CTO writing a short architecture summary for investors. "
            "3-5 sentences, plain text, no JSON, no fluff."
        )
        prompt = (
            f"Idea: {idea}\n"
            f"Tech stack: {json.dumps(tech_stack)}\n"
            f"MVP features: {json.dumps(mvp_features)}"
        )
        return call_llm(prompt=prompt, system=system, temperature=0.5)

    def run(self, idea: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Main entrypoint — orchestrates full CTO analysis + landing page generation.

        Returns a dict matching backend.agents.schemas.CTOOutput's shape.
        """
        category = category or classify_idea(idea)
        mvp_features = self.design_mvp_spec(idea, category)
        tech_stack = self.recommend_tech_stack(idea, category)
        architecture_summary = self.summarize_architecture(idea, tech_stack, mvp_features)
        landing_page_html, validation = generate_landing_page(idea, mvp_features, tech_stack)
        landing_page_path = save_landing_page(idea, landing_page_html)

        return {
            "category": category,
            "mvp_features": mvp_features,
            "tech_stack": tech_stack,
            "architecture_summary": architecture_summary or "Architecture summary generation failed — check GROQ_API_KEY.",
            "landing_page_html": landing_page_html,
            "landing_page_path": landing_page_path,
            "landing_page_validation": validation,
            "code_repo": None,
        }


def cto_node(state: AgentState) -> dict:
    """LangGraph node — replaces graph.py's cto_stub with the real CTO-agent."""
    idea = state.get("idea", "")
    agent = CTOAgent()
    output = agent.run(idea)
    return {"cto_output": output}
