# models.py
from pydantic import BaseModel

class Score(BaseModel):
    name: str
    score: int

