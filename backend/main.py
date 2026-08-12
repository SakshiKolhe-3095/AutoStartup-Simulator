from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class IdeaRequest(BaseModel):
    idea: str

@app.post("/generate")
def generate(req: IdeaRequest):
    return {"status": "received", "idea": req.idea}