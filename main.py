from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

@app.post("/chat_completion")
async def chat_completion(history: List[Message]) -> Dict[str, str]:
    return {"response": "This is a sample response."}
