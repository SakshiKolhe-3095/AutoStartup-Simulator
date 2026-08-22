"""Investor-agent: fires adversarial questions based on idea category, scores the pitch."""
import json
import random
from pathlib import Path
from backend.orchestration.state import AgentState
from backend.models.llm_client import call_llm
from backend.tools.idea_classifier import classify_idea


QUESTION_BANK_PATH = Path("data/question_bank.json")


def _load_question_bank() -> dict:
    with open(QUESTION_BANK_PATH, "r") as f:
        return json.load(f)


def select_questions(state: AgentState, n: int = 5) -> dict:
    bank = _load_question_bank()
    idea_category = classify_idea(state.get("idea", ""))

    questions = list(bank.get("general", []))[:2]
    category_qs = bank.get(idea_category, [])
    if category_qs:
        questions.append(random.choice(category_qs))

    for cat in ["market", "product", "financial"]:
        pool = bank.get(cat, [])
        if pool:
            questions.append(random.choice(pool))

    return {"investor_questions": questions[:n], "investor_transcript": [], "idea_category": idea_category}

def score_pitch(state: AgentState) -> dict:
    """LLM-based scoring — evaluates actual answer quality, not just completion count."""
    if state.get("status") == "failed":
        return {}

    transcript = state.get("investor_transcript", [])
    if not transcript:
        return {"investor_score": 0, "status": "done"}

    qa_summary = "\n".join(
        f"Q: {t['q']}\nA: {t.get('a', 'No answer')}" +
        (f"\nRebuttal: {t['rebuttal']}\nDefense: {t['defense']}" if 'rebuttal' in t else "")
        for t in transcript
    )
    prompt = (
        f"Investor Q&A transcript:\n{qa_summary}\n\n"
        "Score this pitch 0-10 based on: specificity of answers, whether numbers/claims "
        "are backed by evidence, and how well rebuttals were defended. Respond with ONLY "
        "a single integer 0-10, no other text."
    )
    raw = call_llm(prompt=prompt, system="You are a skeptical VC scoring pitch quality.", temperature=0.2)
    try:
        score = int(raw.strip())
        score = max(0, min(10, score))
    except (ValueError, TypeError):
        score = 5
    return {"investor_score": score, "status": "done"}

def generate_rebuttal(question: str, ceo_answer: str) -> str:
    """Investor pushes back once on a weak/vague CEO answer."""
    

    prompt = (
        f"Investor question: {question}\n"
        f"CEO answer: {ceo_answer}\n\n"
        "As a skeptical investor, write ONE sharp follow-up pushback if the answer was vague, "
        "generic, or dodged the question. If the answer was genuinely strong and specific, "
        "respond with exactly: NO_REBUTTAL"
    )
    result = call_llm(prompt, system="You are a skeptical VC probing for weaknesses in a pitch.")
    return result.strip()