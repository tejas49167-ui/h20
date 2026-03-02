async function sendMessage() {
  const input = document.getElementById("userInput");
  const message = input.value;

  if (!message) return;

  addMessage(message, "user");
  input.value = "";

  const response = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message })
  });

  const data = await response.json();
  addMessage(data.reply, "harshith");
}

function addMessage(text, className) {
  const chat = document.getElementById("chat");
  const p = document.createElement("p");
  p.className = className;
  p.innerText = text;
  chat.appendChild(p);
}