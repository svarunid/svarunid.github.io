from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel, select


class Session(SQLModel, table=True):
  """Database model for storing conversation sessions.

  Stores conversation turns between user and agent along with metadata.
  Each session is associated with a user and contains a list of messages.

  Attributes:
    id: Unique session identifier.
    user: User identifier associated with this session.
    meta: Metadata dictionary for additional session information.
    messages: List of conversation messages in chronological order.
    created_at: Timestamp when the session was created.
    updated_at: Timestamp when the session was last updated.
  """
  id: Mapped[str] = Field(primary_key=True)
  user: Mapped[str] = Field(index=True)
  meta: Mapped[Dict[str, Any]] = Field(default_factory=dict, sa_column=Column(JSON))
  messages: Mapped[List[Dict[str, Any]]] = Field(default_factory=list, sa_column=Column(JSON))
  created_at: Mapped[datetime] = Field(sa_column=Column(DateTime, server_default=func.now()))
  updated_at: Mapped[datetime] = Field(sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()))

class Sessions:
  """Session store for persisting and managing conversation sessions.

  Provides methods for creating, retrieving, updating, and deleting sessions
  in a database.

  Attributes:
    db: Database instance for session storage.
  """

  def __init__(self, db):
    self.db = db

  async def create_session(self, uid: str, sid: str) -> Session:
    """Create a new conversation session.

    Args:
      uid: User identifier.
      sid: Session identifier (should be unique).

    Returns:
      Session: The newly created session instance.
    """
    async with self.db.session() as dbs:
      session = Session(id=sid, user=uid, meta={}, messages=[])
      dbs.add(session)
      await dbs.commit()
      await dbs.refresh(session)
      return session

  async def get_session(self, *, uid: Optional[str] = None, sid: Optional[str] = None) -> List[Session]:
    """Retrieve session(s) by user ID or session ID.

    Args:
      uid: Optional user identifier to retrieve all sessions for a user.
      sid: Optional session identifier to retrieve a specific session.

    Returns:
      List[Session]: List of matching sessions. Returns a single-item list
        if sid is provided, multiple sessions if uid is provided, or an
        empty list if no matches are found.
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
    """Update an existing session in the database.

    Args:
      session: Session instance with updated data to persist.
    """
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
    """Delete a session from the database.

    Args:
      sid: Session identifier of the session to delete.
    """
    async with self.db.session() as dbs:
      result = await dbs.exec(select(Session).where(Session.id == sid))
      session = result.first()
      if session:
        await dbs.delete(session)
        await dbs.commit()
