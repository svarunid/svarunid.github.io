import { render, html } from "lit-html";
import { unsafeHTML } from "lit-html/directives/unsafe-html.js";

import { API_BASE_URL } from "./config";
import { parseMarkdown } from "./utils/markdown";

interface ChatSession {
  uid: string | null;
  sid: string | null;
}

const splitMarker = "|split|";

const chatInput = document.getElementById("chatbox") as HTMLInputElement | null;
const messagesContainer = document.getElementById("messages");

const urlParams = new URLSearchParams(window.location.search);
const initialMessage = urlParams.get("message");

if (initialMessage && messagesContainer) {
  window.history.replaceState({}, "", "/chat");
  sendMessage(initialMessage);
}

if (chatInput && messagesContainer) {
  const chatPageForm = chatInput.closest("form");
  if (chatPageForm) {
    chatPageForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (message) {
        sendMessage(message);
        chatInput.value = "";
      }
    });
  }
}

function getChatSession(): ChatSession {
  return {
    uid: localStorage.getItem("uid"),
    sid: sessionStorage.getItem("chat_sid")
  }
}

function setChatSession(uid: string, sid: string): void {
  localStorage.setItem("uid", uid);
  sessionStorage.setItem("chat_sid", sid);
}

function renderMessage(
  role: "user" | "agent",
  content: string,
  streaming: boolean = false,
) {
  const isLoading = role === "agent" && streaming && !content;

  return html`
    <div
      class="flex w-full ${role === "user" ? "justify-end" : "justify-start"}">
      <div
        class="max-w-[80%] px-4 py-3 rounded-lg ${role === "user"
      ? "bg-neutral-200 dark:bg-neutral-700 text-neutral-900 dark:text-neutral-50"
      : "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-50"}">
        ${isLoading
      ? html`
              <div class="flex gap-1.5 items-center min-h-5">
                <span
                  class="w-2 h-2 bg-neutral-500 dark:bg-neutral-400 rounded-full animate-bounce [animation-delay:0s]"></span>
                <span
                  class="w-2 h-2 bg-neutral-500 dark:bg-neutral-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                <span
                  class="w-2 h-2 bg-neutral-500 dark:bg-neutral-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
              </div>
            `
      : html`
              <div
                class="prose prose-sm prose-neutral dark:prose-invert max-w-none ${streaming
          ? "animate-pulse"
          : ""}">
                ${unsafeHTML(parseMarkdown(content))}
              </div>
            `}
      </div>
    </div>
  `;
}

async function sendMessage(message: string): Promise<void> {
  const messagesContainer = document.getElementById("messages");
  if (!messagesContainer) return;

  const userMessage = document.createElement("div");
  messagesContainer.appendChild(userMessage);
  render(renderMessage("user", message, false), userMessage);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  const agentMessage = document.createElement("div");
  messagesContainer.appendChild(agentMessage);
  render(renderMessage("agent", "", true), agentMessage);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  try {
    const { uid, sid } = getChatSession();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (uid) headers["X-Chat-UID"] = uid;
    if (sid) headers["X-Chat-SID"] = sid;

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify({ message }),
    });

    const responseUid = response.headers.get("X-Chat-UID");
    const responseSid = response.headers.get("X-Chat-SID");
    if (responseUid && responseSid) {
      setChatSession(responseUid, responseSid);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (reader) {
      let accumulatedText = "";
      let currentMessage = agentMessage;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        accumulatedText += chunk;

        const splitIndex = accumulatedText.indexOf(splitMarker);
        if (splitIndex !== -1) {
          const contentBeforeSplit = accumulatedText.substring(0, splitIndex);
          render(
            renderMessage("agent", contentBeforeSplit.trim(), false),
            currentMessage,
          );

          currentMessage = document.createElement("div");
          messagesContainer.appendChild(currentMessage);

          accumulatedText = accumulatedText.substring(
            splitIndex + splitMarker.length,
          );

          messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
      }

      render(
        renderMessage("agent", accumulatedText.trim(), false),
        currentMessage,
      );
    }
  } catch (error) {
    console.error("Error sending message:", error);
    render(
      renderMessage(
        "agent",
        "Sorry, an error occurred. Please try again.",
        false,
      ),
      agentMessage,
    );
  }
}
