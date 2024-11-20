from persistent.db.base import Base, WithId
from sqlalchemy import column, text


# таблица со столбцом player_score
class Score(Base, WithId):
	__tablename__ = "score"

	player_score = column(int, nullable=False)
