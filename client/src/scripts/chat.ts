import { getChatSession, setChatSession } from "./session";
import { API_BASE_URL } from "./config";
import "./components/chat-message";

// Handle chat page functionality
const chatInput = document.getElementById(
  "chat-input",
) as HTMLInputElement | null;
const messagesContainer = document.getElementById("messages");

// Initialize after custom element is defined
const urlParams = new URLSearchParams(window.location.search);
const initialMessage = urlParams.get("message");

if (initialMessage && messagesContainer) {
  // Clean up URL first
  window.history.replaceState({}, "", "/chat");
  // Wait for custom element to be fully defined
  customElements.whenDefined("chat-message").then(() => {
    sendMessage(initialMessage);
  });
}

if (chatInput && messagesContainer) {
  // Handle form submission
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

async function sendMessage(message: string): Promise<void> {
  const messagesContainer = document.getElementById("messages");
  if (!messagesContainer) return;

  // Ensure custom element is defined
  await customElements.whenDefined("chat-message");

  // Add user message
  const userMessage = document.createElement("chat-message");
  userMessage.setAttribute("role", "user");
  userMessage.setAttribute("content", message);
  messagesContainer.appendChild(userMessage);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  // Create agent message for streaming
  const agentMessage = document.createElement("chat-message");
  agentMessage.setAttribute("role", "agent");
  agentMessage.setAttribute("streaming", "true");
  messagesContainer.appendChild(agentMessage);

  // Wait a tick for the element to be connected and upgraded
  await new Promise((resolve) => setTimeout(resolve, 0));

  agentMessage.setAttribute("content", "");
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  try {
    const { uid, sid } = getChatSession();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    // Add uid/sid to headers if they exist
    if (uid) headers["X-Chat-UID"] = uid;
    if (sid) headers["X-Chat-SID"] = sid;

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify({ message }),
    });

    // Store uid/sid from response headers
    const responseUid = response.headers.get("X-Chat-UID");
    const responseSid = response.headers.get("X-Chat-SID");
    if (responseUid && responseSid) {
      setChatSession(responseUid, responseSid);
    }

    // Handle streaming response
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (reader) {
      let accumulatedText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        accumulatedText += chunk;

        const splitMarker = "<|split|>";
        const splitIndex = accumulatedText.indexOf(splitMarker);

        if (splitIndex !== -1) {
          const contentBeforeSplit = accumulatedText.substring(0, splitIndex);
          currentMessage.setAttribute("content", contentBeforeSplit);
          currentMessage.removeAttribute("streaming");

          const newAgentMessage = document.createElement("chat-message");
          newAgentMessage.setAttribute("role", "agent");
          newAgentMessage.setAttribute("streaming", "true");
          newAgentMessage.setAttribute("content", "");
          messagesContainer.appendChild(newAgentMessage);
          currentMessage = newAgentMessage;

          accumulatedText = accumulatedText.substring(
            splitIndex + splitMarker.length,
          );
        } else {
          currentMessage.setAttribute("content", accumulatedText);
        }

        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }

      // Stop streaming indicator
      agentMessage.removeAttribute("streaming");
    }
  } catch (error) {
    console.error("Error sending message:", error);
    agentMessage.setAttribute(
      "content",
      "Sorry, an error occurred. Please try again.",
    );
    agentMessage.removeAttribute("streaming");
  }
}
