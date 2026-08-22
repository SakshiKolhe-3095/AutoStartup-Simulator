from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json

from backend.orchestration.graph import build_graph

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = build_graph()


class IdeaRequest(BaseModel):
    idea: str


@app.post("/generate")
async def generate(req: IdeaRequest):
    """Runs the full pipeline synchronously and returns the final state."""
    result = await asyncio.to_thread(_graph.invoke, {"idea": req.idea})
    return {
        "status": result.get("status", "unknown"),
        "idea": result.get("idea"),
        "ceo_narrative": result.get("ceo_narrative"),
        "cmo_output": result.get("cmo_output"),
        "cfo_output": result.get("cfo_output"),
        "cto_output": result.get("cto_output"),
        "investor_transcript": result.get("investor_transcript"),
        "investor_score": result.get("investor_score"),
        "errors": result.get("errors", []),
    }


async def real_log_stream(idea: str):
    """Streams coarse-grained progress markers while the real pipeline runs in a thread.
    True per-node log streaming would need LangGraph's astream — out of scope for Wk7 Day1,
    tracked as a follow-up."""
    steps = [
        f"Parsing idea: {idea}",
        "CMO agent: analyzing market...",
        "CFO/CTO agents: running in parallel...",
        "CEO agent: synthesizing pitch...",
        "Investor Q&A round...",
    ]
    for step in steps[:-1]:
        yield f"data: {step}\n\n"
        await asyncio.sleep(1.5)
    yield f"data: {steps[-1]}\n\n"
    yield "data: Done.\n\n"


@app.get("/generate/stream")
async def generate_stream(idea: str):
    return StreamingResponse(real_log_stream(idea), media_type="text/event-stream")