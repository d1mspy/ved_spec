from persistent.db.base import Base, WithId
from sqlalchemy import Column, Integer


# таблица со столбцом player_score
class Score(Base, WithId):
	__tablename__ = "score"

	player_score = Column(Integer)
