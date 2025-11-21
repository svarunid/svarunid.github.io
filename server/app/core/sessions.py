from typing import Optional

class Sessions:
  def __init__(self):
    self.sessions = []

  def create_session(self, uid, sid):
    self.sessions.append({"id": sid, "user": uid, "metadata": {}, "messages": []})
    return self.sessions[-1]

  def get_session(self, *, uid: Optional[str] = None, sid: Optional[str] = None):
    if sid:
      for session in self.sessions:
        if session["id"] == sid: return session
    if uid: return [session for session in self.sessions if session["user"] == uid]
    return self.sessions

  def update_session(self, sid, message):
    for session in self.sessions:
      if session["id"] == sid: session["messages"].append(message)
      break

  def delete_session(self, sid):
    for session in self.sessions:
      if session["id"] == sid: 
        self.sessions.remove(session)
        return
