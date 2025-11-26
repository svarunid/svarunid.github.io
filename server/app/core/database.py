import importlib.resources

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


class Database:
  """Database class for managing database connections."""
  def __init__(self, db_url: str):
    """Initialize the database connection."""
    self._engine = create_async_engine(
      f"sqlite+aiosqlite:///{db_url}",
      echo=False,
    )

    self._sessionmaker = async_sessionmaker(self._engine, class_=AsyncSession)

  async def initialize(self):
    async with self._engine.begin() as conn:
      sqlite_vector = importlib.resources.files("sqlite_vector.binaries") / "vector"

      raw_conn = await conn.get_raw_connection()
      await raw_conn.driver_connection.enable_load_extension(True)
      await raw_conn.driver_connection.load_extension(str(sqlite_vector))
      await raw_conn.driver_connection.enable_load_extension(False)

      await conn.run_sync(SQLModel.metadata.create_all)

  def session(self):
    """Get a new database session."""
    return self._sessionmaker()

  async def close(self):
    """Close the database connection."""
    await self._engine.dispose()
