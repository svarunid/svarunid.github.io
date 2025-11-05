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
      border: 1px solid rgb(64, 64, 64);
      border-radius: 0.5rem;
    }

    .bubble.user {
      background-color: rgb(38, 38, 38);
    }

    .bubble.agent {
      background-color: rgb(23, 23, 23);
    }

    .content {
      font-size: 0.875rem;
      line-height: 1.25rem;
      color: rgb(250, 250, 250);
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
  `;

  render() {
    // prettier-ignore
    return html`
      <div class="bubble ${this.role}">
        <p class="content ${(this.streaming ? "streaming" : "")}">${this.content}</p>
      </div>
    `;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "chat-message": ChatMessage;
  }
}
