"""
CMO Agent - Market Research & GTM Strategy
Owner: Faiza
"""
import json
import ollama
from backend.models.llm_client import call_llm, FAST_MODEL
from backend.utils.logger import get_logger
from backend.config import GROQ_MODEL, OLLAMA_MODEL


logger = get_logger(__name__)


class CMOAgent:
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

    def _call_local_llm(self, prompt: str, system: str) -> str:
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            return response["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Local LLM call failed: {e}")
            return ""

    def analyze_market(self, idea: str) -> dict:
        """Estimate TAM/SAM/SOM for the given startup idea."""
        system = (
            "You are a market research analyst. Given a startup idea, "
            "estimate TAM, SAM, SOM in USD with 1-2 line reasoning each. "
            "Respond ONLY as JSON: {\"tam\": \"...\", \"sam\": \"...\", "
            "\"som\": \"...\", \"reasoning\": \"...\"}"
        )
        raw = call_llm(prompt=f"Startup idea: {idea}", system=system, temperature=0.3, model=FAST_MODEL)
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {"tam": "", "sam": "", "som": "", "reasoning": raw}

    def scan_competitors(self, idea: str) -> list:
        """Search and summarize competitor landscape."""
        from backend.tools.web_search import WebSearchTool
        searcher = WebSearchTool()
        results = searcher.search(f"top competitors alternatives {idea}", max_results=8)

        raw_context = "\n".join(
            f"- {r.get('title','')}: {r.get('content','')[:500]}" for r in results
        )
        system = (
            "You are a market analyst. Extract EVERY distinct competitor "
            "mentioned in the text below — do not limit yourself to one. "
            "Respond ONLY as a JSON list, no other text.\n"
            "Format: [{\"name\": \"...\", \"summary\": \"...\"}]\n"
            "Keep each summary to one short sentence — the list may be long, "
            "so brevity per item matters more than detail."
        )
        # NOTE: FAST_MODEL (gpt-oss-20b) reliably returns empty responses for this
        # long-list extraction prompt — confirmed via isolated testing. Use the
        # default QUALITY_MODEL here; this call only fires once per pipeline run
        # so the token cost difference is negligible.
        raw = call_llm(prompt=raw_context, system=system, temperature=0.3)
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return [{"name": "parse_error", "summary": raw}]

    def generate_persona(self, idea: str) -> dict:
        """Generate target customer persona."""
        system = (
            "You are a UX researcher. Given a startup idea, create one primary "
            "target customer persona. Respond ONLY as JSON: "
            "{\"name\": \"...\", \"age_range\": \"...\", \"occupation\": \"...\", "
            "\"pain_points\": [\"...\"], \"motivations\": [\"...\"]}"
        )
        raw = self._call_local_llm(prompt=f"Startup idea: {idea}", system=system)
        if not raw:
            logger.warning("Local LLM unavailable, falling back to Groq for persona generation")
            raw = call_llm(prompt=f"Startup idea: {idea}", system=system, temperature=0.5, model=FAST_MODEL)
        raw = self._clean_json(raw)
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {"name": "", "age_range": "", "occupation": "", "pain_points": [], "motivations": [], "raw": raw}

    def generate_gtm_strategy(self, idea: str, market_data: dict) -> str:
        """Draft go-to-market strategy."""
        system = (
            "You are a startup growth strategist. Given a startup idea and its "
            "market data, write a concise go-to-market strategy (5-7 sentences) "
            "covering: initial channel, pricing approach, and early growth loop. "
            "Respond as plain text, no JSON."
        )
        prompt = f"Idea: {idea}\nMarket data: {json.dumps(market_data)}"
        return call_llm(prompt=prompt, system=system, temperature=0.6)

    def run(self, idea: str) -> dict:
        """Main entrypoint — orchestrates full CMO analysis."""
        market = self.analyze_market(idea)
        competitors = self.scan_competitors(idea)
        persona = self.generate_persona(idea)
        gtm = self.generate_gtm_strategy(idea, market)
        return {
            "market": market,
            "competitors": competitors,
            "persona": persona,
            "gtm_strategy": gtm,
        }