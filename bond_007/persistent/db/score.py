from persistent.db.base import Base, WithId
from sqlalchemy import column, text


# таблица со столбцами player и player_score
class Score(Base, WithId):
	__tablename__ = "score"

	player = column(text)
	player_score = column(int, nullable=False)
