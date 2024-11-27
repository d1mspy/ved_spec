from persistent.db.score import Score
from infrastructure.db.connect import sqlite_connection, create_all_tables
from sqlalchemy import insert, select


class ScoreRepository:

	def __init__(self) -> None:
		self._sessionmaker = sqlite_connection()
		create_all_tables()

	async def save_score(self, player: str, score: int) -> None:
		"""
		INSERT INTO score(id, player, player_score) VALUES({player, player_score})
		"""
		stmp = insert(Score).values({"player": player, "player_score": score})

		async with self._sessionmaker() as session:
			await session.execute(stmp)
			await session.commit()
	