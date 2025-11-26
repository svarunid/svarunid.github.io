from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel, select


class Session(SQLModel, table=True):
  """
  Session stores conversation turns between user and agent along with metadata.
  """
  id: str = Field(primary_key=True)
  user: str = Field(index=True)
  meta: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
  messages: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
  created_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now()))
  updated_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()))

class Sessions:
  """
  A session store for persist & manage sessions in a database.

  Args:
    db: SQL Database instance.
  """

  def __init__(self, db):
    self.db = db

  async def create_session(self, uid: str, sid: str) -> Session:
    """
    Create a new session.

    Args:
      uid (str): User ID.
      sid (str): Session ID.

    Returns:
      Session: A session instance.
    """
    async with self.db.session() as dbs:
      session = Session(id=sid, user=uid, meta={}, messages=[])
      dbs.add(session)
      await dbs.commit()
      await dbs.refresh(session)
      return session

  async def get_session(self, *, uid: Optional[str] = None, sid: Optional[str] = None) -> List[Session]:
    """
    Get a session by user ID or session ID.

    Args:
      uid (str, optional): User ID.
      sid (str, optional): Session ID.

    Returns:
      List[Session]: A list of sessions.
    """
    async with self.db.session() as dbs:
      if sid:
        result = await dbs.exec(select(Session).where(Session.id == sid))
        return [result.first()]
      if uid:
        result = await dbs.exec(select(Session).where(Session.user == uid))
        return result.all()
      return []

  async def update_session(self, session: Session) -> None:
    async with self.db.session() as dbs:
      dbs.add(session)
      await dbs.commit()
      await dbs.refresh(session)

  # async def update_session(self, sid: str, context: List[str], messages: List[Dict[str, Any]]):
  #   async with self.db.session() as dbs:
  #     result = await dbs.exec(select(Session).where(Session.id == sid))
  #     session = result.first()
  #     if session:
  #       session.context = context
  #       session.messages = messages
  #       await dbs.commit()

  async def delete_session(self, sid: str):
    async with self.db.session() as dbs:
      result = await dbs.exec(select(Session).where(Session.id == sid))
      session = result.first()
      if session:
        await dbs.delete(session)
        await dbs.commit()
