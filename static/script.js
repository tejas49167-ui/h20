const authView = document.getElementById("authView");
const chatView = document.getElementById("chatView");
const currentUser = document.getElementById("currentUser");
const statusMessage = document.getElementById("statusMessage");
const logoutButton = document.getElementById("logoutButton");
const messagesContainer = document.getElementById("messages");
const registerForm = document.getElementById("registerForm");
const loginForm = document.getElementById("loginForm");
const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("messageInput");

let activeUser = null;
let refreshTimer = null;

function setStatus(message, type = "info") {
  statusMessage.textContent = message;
  statusMessage.className = `status-message ${type}`;
}

function clearStatus() {
  statusMessage.textContent = "";
  statusMessage.className = "status-message hidden";
}

async function apiFetch(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Request failed.");
  }
  return data;
}

function renderMessages(messages) {
  messagesContainer.innerHTML = "";

  if (!messages.length) {
    const emptyState = document.createElement("div");
    emptyState.className = "empty-state";
    emptyState.textContent = "No messages yet. Be the first to post.";
    messagesContainer.appendChild(emptyState);
    return;
  }

  messages.forEach((message) => {
    const card = document.createElement("article");
    const isOwnMessage = activeUser && message.username === activeUser.username;
    card.className = `message-card${isOwnMessage ? " own-message" : ""}`;

    const meta = document.createElement("div");
    meta.className = "message-meta";
    meta.innerHTML = `<strong>${message.username}</strong><span>${new Date(message.created_at).toLocaleString()}</span>`;

    const body = document.createElement("p");
    body.textContent = message.body;

    card.append(meta, body);
    messagesContainer.appendChild(card);
  });

  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showAuthView() {
  activeUser = null;
  authView.classList.remove("hidden");
  chatView.classList.add("hidden");
  logoutButton.classList.add("hidden");
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
}

function showChatView(user) {
  activeUser = user;
  currentUser.textContent = user.username;
  authView.classList.add("hidden");
  chatView.classList.remove("hidden");
  logoutButton.classList.remove("hidden");
  if (!refreshTimer) {
    refreshTimer = setInterval(loadMessages, 5000);
  }
}

async function loadSession() {
  try {
    const data = await apiFetch("/api/session", { method: "GET" });
    if (data.authenticated && data.user) {
      showChatView(data.user);
      await loadMessages();
    } else {
      showAuthView();
    }
  } catch (error) {
    setStatus(error.message, "error");
  }
}

async function loadMessages() {
  try {
    const data = await apiFetch("/api/messages", { method: "GET" });
    showChatView(data.user);
    renderMessages(data.messages);
    clearStatus();
  } catch (error) {
    if (error.message === "Authentication required.") {
      showAuthView();
      setStatus("Please log in to see the shared feed.", "info");
      return;
    }
    setStatus(error.message, "error");
  }
}

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearStatus();

  try {
    const payload = {
      username: document.getElementById("registerUsername").value.trim(),
      password: document.getElementById("registerPassword").value
    };
    const data = await apiFetch("/api/register", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    registerForm.reset();
    loginForm.reset();
    setStatus(data.message, "success");
    showChatView(data.user);
    await loadMessages();
  } catch (error) {
    setStatus(error.message, "error");
  }
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearStatus();

  try {
    const payload = {
      username: document.getElementById("loginUsername").value.trim(),
      password: document.getElementById("loginPassword").value
    };
    const data = await apiFetch("/api/login", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    loginForm.reset();
    setStatus(data.message, "success");
    showChatView(data.user);
    await loadMessages();
  } catch (error) {
    setStatus(error.message, "error");
  }
});

messageForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearStatus();

  try {
    await apiFetch("/api/messages", {
      method: "POST",
      body: JSON.stringify({ message: messageInput.value.trim() })
    });
    messageInput.value = "";
    await loadMessages();
  } catch (error) {
    setStatus(error.message, "error");
  }
});

logoutButton.addEventListener("click", async () => {
  try {
    const data = await apiFetch("/api/logout", { method: "POST" });
    showAuthView();
    messagesContainer.innerHTML = "";
    setStatus(data.message, "success");
  } catch (error) {
    setStatus(error.message, "error");
  }
});

loadSession();
