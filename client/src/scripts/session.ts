// Session storage for uid/sid
export interface ChatSession {
  uid: string | null;
  sid: string | null;
}

export const getChatSession = (): ChatSession => ({
  uid: sessionStorage.getItem("chat_uid"),
  sid: sessionStorage.getItem("chat_sid"),
});

export const setChatSession = (uid: string, sid: string): void => {
  sessionStorage.setItem("chat_uid", uid);
  sessionStorage.setItem("chat_sid", sid);
};
