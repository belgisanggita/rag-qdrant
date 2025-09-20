from fastapi import FastAPI
from pydantic import BaseModel
from rag import generate_answer
import threading
from watcher import start_watcher  # import watcher

app = FastAPI()

# Jalankan watcher di background
threading.Thread(target=start_watcher, daemon=True).start()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(data: QuestionRequest):
    result = generate_answer(data.question)
    return result