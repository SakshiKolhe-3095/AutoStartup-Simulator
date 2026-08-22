# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class IdeaRequest(BaseModel):
#     idea: str

# @app.post("/generate")
# def generate(req: IdeaRequest):
#     return {"status": "received", "idea": req.idea}









from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class IdeaRequest(BaseModel):
    idea: str


@app.post("/generate")
def generate(req: IdeaRequest):
    return {"status": "received", "idea": req.idea}


async def fake_log_stream(idea: str):
    """Mock log stream — TODO Wk7: replace with real pipeline log events."""
    steps = [
        f"Parsing idea: {idea}",
        "CMO agent: analyzing market...",
        "CFO agent: projecting costs...",
        "CTO agent: generating MVP...",
        "CEO agent: synthesizing pitch...",
        "Done.",
    ]
    for step in steps:
        yield f"data: {step}\n\n"
        await asyncio.sleep(1)


@app.get("/generate/stream")
async def generate_stream(idea: str):
    return StreamingResponse(fake_log_stream(idea), media_type="text/event-stream")