const systemMessageEl = document.getElementById("system-message");
const lastActionMessageEl = document.getElementById("last-action-message");
const afterStateMessageEl = document.getElementById("after-state-message");
const actionCountEl = document.getElementById("action-count");
const viewInfoEl = document.getElementById("view-info");
const imageEl = document.getElementById("room-image");
const imagePlaceholderEl = document.getElementById("image-placeholder");
const inventoryEl = document.getElementById("inventory");
const triggersEl = document.getElementById("triggers");
const actionsContainer = document.getElementById("actions-container");
const quizSection = document.getElementById("quiz-section");
const quizPromptEl = document.getElementById("quiz-prompt");
const quizForm = document.getElementById("quiz-form");
const quizInput = document.getElementById("quiz-input");
const statusBanner = document.getElementById("status-banner");
statusBanner.dataset.autoClear = "0";
const roomSelect = document.getElementById("room-select");
const loadRoomButton = document.getElementById("load-room");
const resetButton = document.getElementById("reset-button");

const ASSETS_BASE = "../assets/";

window.__VisEscapeGraphs = window.__VisEscapeGraphs || {};

let graphData = null;
let currentStateId = null;
let actionCount = 0;
let lastActionMessage = "";
let afterStateMessage = "";

function loadRoom(roomName) {
  const graphs = window.__VisEscapeGraphs || {};
  const data = graphs[roomName];

  if (!data) {
    console.warn(`Room '${roomName}' not found in preloaded graphs.`);
    graphData = null;
    currentStateId = null;
    setBanner(`Data for '${roomName}' not found.`, "error");
    renderEmpty();
    return;
  }

  graphData = data;
  currentStateId = graphData.initialState;
  actionCount = 0;
  lastActionMessage = graphData.initialMessages?.action || "";
  afterStateMessage = graphData.initialMessages?.after || "";

  systemMessageEl.textContent = graphData.systemMessage || "";
  renderState();
  setBanner(`${roomName} ready.`, "success", 1200);
}

function renderEmpty() {
  actionCountEl.textContent = "Actions: 0";
  viewInfoEl.textContent = "View: -";
  imageEl.hidden = true;
  imagePlaceholderEl.hidden = false;
  inventoryEl.innerHTML = "";
  triggersEl.innerHTML = "";
  actionsContainer.innerHTML = "";
  quizSection.hidden = true;
  lastActionMessageEl.textContent = "";
  afterStateMessageEl.textContent = "";
}

function renderState() {
  if (!graphData || !currentStateId) {
    renderEmpty();
    return;
  }

  const state = graphData.states[currentStateId];
  if (!state) {
    console.warn(`Missing state: ${currentStateId}`);
    renderEmpty();
    return;
  }

  actionCountEl.textContent = `Actions: ${actionCount}`;
  const viewParts = [state.view || "-"];
  if (state.wall) viewParts.push(`Wall: ${state.wall}`);
  if (state.inspected) viewParts.push(`Inspecting: ${state.inspected}`);
  if (state.item) viewParts.push(`Item: ${state.item}`);
  viewInfoEl.textContent = `View: ${viewParts.join(" · ")}`;

  lastActionMessageEl.textContent = lastActionMessage || "";
  afterStateMessageEl.textContent = afterStateMessage || "";

  if (state.image) {
    imageEl.src = ASSETS_BASE + state.image;
    imageEl.hidden = false;
    imagePlaceholderEl.hidden = true;
  } else {
    imageEl.hidden = true;
    imagePlaceholderEl.hidden = false;
  }

  updatePillGroup(inventoryEl, state.inventory, "Inventory empty");
  const triggerNames = Object.keys(state.triggers || {});
  updatePillGroup(triggersEl, triggerNames.length ? triggerNames : null, "No active triggers");

  renderActions(state);
  renderQuiz(state);

  if (state.gameClear) {
    setBanner(`Room cleared in ${actionCount} steps!`, "success");
  } else if (!statusBanner.hidden && statusBanner.dataset.autoClear === "1") {
    // keep current message until timeout clears it
  } else {
    clearBanner();
  }
}

function renderActions(state) {
  actionsContainer.innerHTML = "";
  if (!state.actions || state.actions.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-actions";
    empty.textContent = "No available actions.";
    actionsContainer.appendChild(empty);
    return;
  }

  state.actions.forEach((entry) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = entry.label;
    if (state.gameClear) {
      btn.disabled = true;
    }
    btn.addEventListener("click", () => applyAction(entry));
    actionsContainer.appendChild(btn);
  });
}

function renderQuiz(state) {
  const hasInput = state.inputActions && state.inputActions.length > 0 && !state.gameClear;
  quizSection.hidden = !hasInput;
  if (!hasInput) {
    quizPromptEl.textContent = "";
    quizInput.value = "";
    return;
  }

  const question = state.quiz?.question?.trim();
  if (question) {
    quizPromptEl.textContent = question;
  } else {
    quizPromptEl.textContent = "Enter the required answer.";
  }
  setTimeout(() => quizInput.focus(), 50);
}

function applyAction(entry) {
  if (!graphData) return;

  actionCount += 1;
  currentStateId = entry.next;
  lastActionMessage = entry.messages?.action || "";
  afterStateMessage = entry.messages?.after || "";
  setBanner(`Action executed: ${entry.label}`, "success", 1800);
  renderState();
}

function handleQuizSubmit(value) {
  if (!graphData || !currentStateId) return;
  const state = graphData.states[currentStateId];
  if (!state || !state.inputActions) return;

  const trimmed = value.trim();
  if (!trimmed) return;

  const match = state.inputActions.find((action) => action.expected.toLowerCase() === trimmed.toLowerCase());

  if (!match) {
    setBanner("Incorrect answer. Try again!", "error", 1800);
    return;
  }

  actionCount += 1;
  currentStateId = match.next;
  lastActionMessage = match.messages?.action || "";
  afterStateMessage = match.messages?.after || "";
  setBanner("Answer accepted!", "success", 2000);
  quizInput.value = "";
  renderState();
}

function updatePillGroup(container, values, emptyLabel) {
  container.innerHTML = "";
  if (!values || values.length === 0) {
    const pill = document.createElement("span");
    pill.className = "pill empty";
    pill.textContent = emptyLabel;
    container.appendChild(pill);
    return;
  }

  values.forEach((value) => {
    const pill = document.createElement("span");
    pill.className = "pill";
    pill.textContent = value;
    container.appendChild(pill);
  });
}

function setBanner(message, type = "info", timeoutMs) {
  if (!message) {
    clearBanner();
    return;
  }

  statusBanner.textContent = message;
  statusBanner.hidden = false;
  statusBanner.classList.toggle("success", type === "success");
  statusBanner.classList.toggle("error", type === "error");
  statusBanner.dataset.autoClear = timeoutMs ? "1" : "0";

  if (timeoutMs) {
    window.setTimeout(() => {
      if (!graphData) return;
      const state = graphData.states?.[currentStateId];
      if (state && !state.gameClear) {
        clearBanner();
      }
    }, timeoutMs);
  }
}

function clearBanner() {
  statusBanner.hidden = true;
  statusBanner.textContent = "";
  statusBanner.classList.remove("success", "error");
  statusBanner.dataset.autoClear = "0";
}

function resetRun() {
  if (!graphData) return;
  currentStateId = graphData.initialState;
  actionCount = 0;
  lastActionMessage = graphData.initialMessages?.action || "";
  afterStateMessage = graphData.initialMessages?.after || "";
  setBanner("Run reset.", "info", 1200);
  renderState();
}

function populateRoomOptions() {
  const graphs = window.__VisEscapeGraphs || {};
  const roomNames = Object.keys(graphs).sort();

  if (!roomNames.length) {
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "No rooms available";
    placeholder.disabled = true;
    placeholder.selected = true;
    roomSelect.innerHTML = "";
    roomSelect.appendChild(placeholder);
    return [];
  }

  roomSelect.innerHTML = "";
  roomNames.forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    roomSelect.appendChild(option);
  });

  return roomNames;
}

quizForm.addEventListener("submit", (event) => {
  event.preventDefault();
  handleQuizSubmit(quizInput.value);
});

loadRoomButton.addEventListener("click", () => {
  const room = roomSelect.value.trim();
  if (room) {
    loadRoom(room);
  }
});

resetButton.addEventListener("click", resetRun);

window.addEventListener("load", () => {
  const rooms = populateRoomOptions();
  const defaultRoom = rooms[0] || roomSelect.value;
  if (rooms.length) {
    roomSelect.value = defaultRoom;
    loadRoom(defaultRoom);
  } else {
    setBanner("No preloaded rooms available.", "error");
    renderEmpty();
  }
});
