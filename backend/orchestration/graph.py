"""LangGraph state machine wiring CEO -> CMO -> [CTO, CFO] -> CEO synthesize -> Investor."""
from langgraph.graph import StateGraph, END
from backend.orchestration.state import AgentState
from backend.agents.ceo_agent import parse_idea, synthesize, answer_investor_questions
from backend.agents.investor_agent import select_questions, score_pitch
from backend.agents.cto_agent import cto_node
from backend.agents.cfo_agent import cfo_node
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def cmo_node(state: AgentState) -> dict:
    from backend.agents.cmo_agent import CMOAgent
    agent = CMOAgent()
    result = agent.run(state["idea"])
    return {"cmo_output": result}


def route_after_parse(state: AgentState) -> str:
    """If parse_idea failed, skip straight to END instead of running the rest of the pipeline."""
    if state.get("status") == "failed":
        return "end"
    return "continue"

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("parse_idea", parse_idea)
    graph.add_node("cmo", cmo_node)
    graph.add_node("cto", cto_node)
    graph.add_node("cfo", cfo_node)
    graph.add_node("synthesize", synthesize)
    graph.add_node("select_questions", select_questions)
    graph.add_node("answer_questions", answer_investor_questions)
    graph.add_node("score_pitch", score_pitch)

    graph.set_entry_point("parse_idea")

    # cfo needs cmo's market sizing (TAM/SAM/SOM) as input, so it can't run in cmo's own
    # parallel branch — it has to fire after cmo completes. cto has no such dependency, but
    # this LangGraph version (0.2.60) double-fires a fan-in node when its incoming branches
    # have unequal depth (verified: a node with one direct predecessor and one two-hop
    # predecessor gets invoked once per depth, since there's no `defer=True` on add_node in
    # this version to force a true "wait for all branches" join). So cto is also routed
    # through cmo to keep both branches the same depth into synthesize — cto's node body
    # still doesn't read cmo_output, this is scheduling-only.
    graph.add_edge("parse_idea", "cmo")
    graph.add_edge("cmo", "cto")
    graph.add_edge("cmo", "cfo")

    # fan-in — both branches are exactly one hop past cmo, so synthesize fires exactly once.
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