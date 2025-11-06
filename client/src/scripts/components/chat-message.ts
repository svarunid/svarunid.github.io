import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";

@customElement("chat-message")
export class ChatMessage extends LitElement {
  @property({ type: String }) role: "user" | "agent" = "user";
  @property({ type: String }) content = "";
  @property({ type: Boolean }) streaming = false;

  static styles = css`
    :host {
      display: flex;
      width: 100%;
    }

    :host([role="user"]) {
      justify-content: flex-end;
    }

    :host([role="agent"]) {
      justify-content: flex-start;
    }

    .bubble {
      max-width: 80%;
      padding: 0.75rem 1rem;
      border-radius: 0.5rem;
    }

    .bubble.user {
      background-color: #e5e5e5;
      color: #171717;
    }

    .bubble.agent {
      background-color: #f0f0f0;
      color: #171717;
    }

    @media (prefers-color-scheme: dark) {
      .bubble.user {
        background-color: #404040;
        color: #fafafa;
      }

      .bubble.agent {
        background-color: #262626;
        color: #fafafa;
      }
    }

    .content {
      font-size: 0.875rem;
      line-height: 1.25rem;
      white-space: pre-wrap;
      word-break: break-word;
      margin: 0;
      padding: 0;
    }

    .content.streaming {
      animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
      0%,
      100% {
        opacity: 1;
      }
      50% {
        opacity: 0.7;
      }
    }

    .loading {
      display: flex;
      gap: 0.375rem;
      align-items: center;
      min-height: 1.25rem;
    }

    .loading-dot {
      width: 0.5rem;
      height: 0.5rem;
      background-color: #737373;
      border-radius: 50%;
      animation: bounce 1.4s ease-in-out infinite;
    }

    @media (prefers-color-scheme: dark) {
      .loading-dot {
        background-color: #a3a3a3;
      }
    }

    .loading-dot:nth-child(1) {
      animation-delay: 0s;
    }

    .loading-dot:nth-child(2) {
      animation-delay: 0.2s;
    }

    .loading-dot:nth-child(3) {
      animation-delay: 0.4s;
    }

    @keyframes bounce {
      0%,
      60%,
      100% {
        transform: translateY(0);
        opacity: 0.7;
      }
      30% {
        transform: translateY(-0.5rem);
        opacity: 1;
      }
    }
  `;

  render() {
    const isLoading = this.role === "agent" && !this.content;

    return html`
      <div class="bubble ${this.role}">
        ${isLoading
          ? html`
              <div class="loading">
                <span class="loading-dot"></span>
                <span class="loading-dot"></span>
                <span class="loading-dot"></span>
              </div>
            `
          : html`
              <!-- display: inline -->
              <p class="content ${this.streaming ? "streaming" : ""}"
                >${this.content}</p
              >
            `}
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "chat-message": ChatMessage;
  }
}
