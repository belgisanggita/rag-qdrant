from fastapi import FastAPI
from pydantic import BaseModel
from app.rag import generate_answer

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(data: QuestionRequest):
    result = generate_answer(data.question)
    return result
