"""LangGraph state machine wiring CEO -> [CMO|CTO|CFO stubs] -> CEO synthesize -> Investor."""
from langgraph.graph import StateGraph, END
from backend.orchestration.state import AgentState
from backend.agents.ceo_agent import parse_idea, synthesize, answer_investor_questions
from backend.agents.investor_agent import select_questions, score_pitch
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# --- stub nodes until Faiza/Lakshit/Sakshi wire real agents in ---
# def cmo_stub(state: AgentState) -> dict:
#     return {"cmo_output": {"tam": "TBD - stub", "competitors": [], "persona": "TBD"}}

def cmo_node(state: AgentState) -> dict:
    from backend.agents.cmo_agent import CMOAgent
    agent = CMOAgent()
    result = agent.run(state["idea"])
    return {"cmo_output": result}


def cto_stub(state: AgentState) -> dict:
    return {"cto_output": {"mvp_features": "TBD - stub", "landing_page_url": None}}


def cfo_stub(state: AgentState) -> dict:
    return {"cfo_output": {"funding_ask": "TBD - stub", "revenue_model": "TBD"}}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("parse_idea", parse_idea)
    # graph.add_node("cmo", cmo_stub)
    graph.add_node("cmo", cmo_node)
    graph.add_node("cto", cto_stub)
    graph.add_node("cfo", cfo_stub)
    graph.add_node("synthesize", synthesize)
    graph.add_node("select_questions", select_questions)
    graph.add_node("answer_questions", answer_investor_questions)
    graph.add_node("score_pitch", score_pitch)

    graph.set_entry_point("parse_idea")

    # fan-out (parallel-ish — LangGraph runs these as separate edges from parse_idea)
    graph.add_edge("parse_idea", "cmo")
    graph.add_edge("parse_idea", "cto")
    graph.add_edge("parse_idea", "cfo")

    # fan-in
    graph.add_edge("cmo", "synthesize")
    graph.add_edge("cto", "synthesize")
    graph.add_edge("cfo", "synthesize")

    graph.add_edge("synthesize", "select_questions")
    graph.add_edge("select_questions", "answer_questions")
    graph.add_edge("answer_questions", "score_pitch")
    graph.add_edge("score_pitch", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    logger.info("Starting pipeline run...")
    result = app.invoke({"idea": "AI-powered plant disease detector for farmers"})
    logger.info(f"Pipeline finished with status={result['status']}, score={result.get('investor_score')}")
    print(result)