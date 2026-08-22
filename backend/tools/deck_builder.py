"""
Deck Builder — auto-generates pitch deck slides using python-pptx.
Owner: Sakshi
"""
from pptx import Presentation
from pptx.util import Inches, Pt


class DeckBuilder:
    def __init__(self, template_path: str = None):
        self.template_path = template_path
    
    @staticmethod
    def _narrative_to_bullets(narrative: str) -> list:
        """Split a narrative paragraph into clean sentence-level bullets."""
        if not narrative:
            return ["Narrative not available."]
        raw_sentences = narrative.replace("\n", " ").split(". ")
        bullets = [s.strip().rstrip(".") + "." for s in raw_sentences if s.strip()]
        return bullets or ["Narrative not available."]

    def build_deck(self, ceo_output: dict, output_path: str = "output_deck.pptx"):
        """
        Auto-populates slides from CEO-agent output.
        ceo_output expected keys: idea, ceo_narrative, cmo_output, cfo_output
        """
        prs = Presentation(self.template_path) if self.template_path else Presentation()

        idea = ceo_output.get("idea", "Untitled Startup")
        narrative = ceo_output.get("ceo_narrative", "")
        cmo = ceo_output.get("cmo_output", {}) or {}
        cfo = ceo_output.get("cfo_output", {}) or {}

        # Slide 1: Title
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = idea
        slide.placeholders[1].text = "AutoStartup Simulator — Pitch Deck"

        # Slide 2: Pitch narrative — split into sentence-level bullets
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "The Pitch"
        body = slide.placeholders[1].text_frame
        body.clear()
        sentences = self._narrative_to_bullets(narrative)
        for i, sentence in enumerate(sentences):
            p = body.paragraphs[0] if i == 0 else body.add_paragraph()
            p.text = sentence

        # Slide 3: Market (from CMO)
        market = cmo.get("market", {})
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Market Opportunity"
        slide.placeholders[1].text = (
            f"TAM: {market.get('tam', 'N/A')}\n"
            f"SAM: {market.get('sam', 'N/A')}\n"
            f"SOM: {market.get('som', 'N/A')}"
        )

        # Slide 4: Financials (from CFO)
        funding = cfo.get("funding_ask", {})
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Financials"
        slide.placeholders[1].text = (
            f"Funding ask: {funding.get('amount', 'N/A')}\n"
            f"Use of funds: {funding.get('use_of_funds', 'N/A')}"
        )

        prs.save(output_path)
        return output_path


if __name__ == "__main__":
    builder = DeckBuilder()
    sample_output = {
        "idea": "AI note-taking app",
        "ceo_narrative": "We help busy professionals capture ideas instantly.",
        "cmo_output": {"market": {"tam": "$1B", "sam": "$100M", "som": "$5M"}},
        "cfo_output": {"funding_ask": {"amount": "$250k", "use_of_funds": "hiring + infra"}},
    }
    path = builder.build_deck(sample_output)
    print(f"Deck saved: {path}")