# main.py
#pip install fastapi uvicorn pygame
import uvicorn
from fastapi import FastAPI
from database import init_db
from game import submit_score, get_scores

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/submit_score")
async def post_score(score: Score):
    submit_score(score.name, score.score)
    return {"message": "Score submitted successfully!"}

@app.get("/get_scores")
async def get_score():
    scores = get_scores()
    return [{"name": name, "score": score} for name, score in scores]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
