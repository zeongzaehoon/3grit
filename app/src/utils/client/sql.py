import os
import asyncpg
from contextlib import asynccontextmanager



class PostgresClient:
	def __init__(self, host=None, port=None, db=None, user=None, password=None):
		self.host = host or os.getenv('SQL_DB_HOST')
		self.port = port or os.getenv('SQL_DB_PORT')
		self.user = user or os.getenv('SQL_DB_USER')
		self.password = password or os.getenv('SQL_DB_PASSWORD')
		self.db = db or os.getenv('SQL_DB_NAME')

	async def init_pool(self):
		self._pool = await asyncpg.create_pool(
			host=self.host,
			port=self.port,
			user=self.user,
			password=self.password,
			database=self.db
		)

	@asynccontextmanager
	async def connection(self):
		if not hasattr(self, '_pool'):
			await self.init_pool()
		async with self._pool.acquire() as conn:
			try:
				yield conn
			except Exception as e:
				await conn.execute('ROLLBACK')
				raise e

	async def execute(self, query: str, params: tuple = ()):
		async with self.connection().transaction() as client:
			await client.execute(query, params)
			await client.commit()

	async def execute_many(self, query: str, params: list[tuple]):
		async with self.connection().transaction() as client:
			await client.executemany(query, params)
			await client.commit()

	async def fetchone(self, query: str, params: tuple = ()):
		async with self.connection() as client:
			try:
				return await client.fetchrow(query, params)
			except Exception as e:
				await client.execute('ROLLBACK')
				raise e

	async def fetchall(self, query: str, params: tuple = ()):
		async with self.connection() as client:
			try:
				return await client.fetch(query, params)
			except Exception as e:
				await client.execute('ROLLBACK')
				raise e

