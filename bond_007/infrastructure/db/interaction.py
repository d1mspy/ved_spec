from persistent.db.score import Score
from infrastructure.db.connect import sqlite_connection
from sqlalchemy import insert


class ScoreRepository:

	def __init__(self) -> None:
		self._sessionmaker = sqlite_connection()


	async def save_score(self, score: int) -> None:
		"""
		INSERT INTO score(player_score) VALUES({score})
		"""
		stmp = insert(Score).values({"player_score": score})

		async with self._sessionmaker() as session:
			await session.execute(stmp)
			await session.commit()
	