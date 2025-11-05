// Handle chat form submission from index page
const chatForm = document.getElementById("chat-form") as HTMLFormElement | null;

if (chatForm) {
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const input = chatForm.querySelector(
      'input[name="message"]',
    ) as HTMLInputElement;
    const message = input.value.trim();

    if (message) {
      window.location.href = `/chat/?message=${encodeURIComponent(message)}`;
    }
  });
}
