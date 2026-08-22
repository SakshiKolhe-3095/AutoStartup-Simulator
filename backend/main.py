from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from backend.tools.deck_builder import DeckBuilder
import os
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
os.makedirs("generated_decks", exist_ok=True)
app.mount("/decks", StaticFiles(directory="generated_decks"), name="decks")


class IdeaRequest(BaseModel):
    idea: str


@app.post("/generate")
async def generate(req: IdeaRequest):
    """Runs the full pipeline synchronously, builds a deck, and returns the final state."""
    result = await asyncio.to_thread(_graph.invoke, {"idea": req.idea})

    ceo_output = {
        "idea": result.get("idea"),
        "ceo_narrative": result.get("ceo_narrative"),
        "cmo_output": result.get("cmo_output"),
        "cfo_output": result.get("cfo_output"),
        "cto_output": result.get("cto_output"),
    }

    deck_filename = f"deck_{abs(hash(req.idea)) % 10**8}.pptx"
    deck_path = os.path.join("generated_decks", deck_filename)
    try:
        builder = DeckBuilder()
        await asyncio.to_thread(builder.build_deck, ceo_output, deck_path)
        deck_url = f"http://localhost:8000/decks/{deck_filename}"
    except Exception as e:
        deck_url = None

    return {
        "status": result.get("status", "unknown"),
        "idea": result.get("idea"),
        "ceo_narrative": result.get("ceo_narrative"),
        "cmo_output": result.get("cmo_output"),
        "cfo_output": result.get("cfo_output"),
        "cto_output": result.get("cto_output"),
        "investor_transcript": result.get("investor_transcript"),
        "investor_score": result.get("investor_score"),
        "deck_url": deck_url,
        "errors": result.get("errors", []),
    }


async def real_log_stream(idea: str):
    """Streams coarse-grained progress markers.
    NOTE: still time-based, not tied to actual pipeline node completion (real fix needs
    LangGraph astream — tracked as follow-up). Padded to roughly match real pipeline
    duration (~45s) so 'Done.' doesn't appear before /generate actually finishes."""
    steps = [
        f"Parsing idea: {idea}",
        "CMO agent: analyzing market...",
        "CFO/CTO agents: running in parallel...",
        "CEO agent: synthesizing pitch...",
        "Investor Q&A round...",
        "Finalizing results...",
    ]
    for step in steps:
        yield f"data: {step}\n\n"
        await asyncio.sleep(7)
    yield "data: Done.\n\n"


@app.get("/generate/stream")
async def generate_stream(idea: str):
    return StreamingResponse(real_log_stream(idea), media_type="text/event-stream")