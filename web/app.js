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
const leaderboardBody = document.getElementById("leaderboard-body");
const leaderboardSection = document.getElementById("leaderboard-section");
const toggleLeaderboardBtn = document.getElementById("toggle-leaderboard");

// Modal elements
const modalEl = document.getElementById("congrats-modal");
const modalTurnsEl = document.getElementById("modal-turns");
const modalCloseBtn = document.getElementById("modal-close");
const modalViewBtn = document.getElementById("modal-view-leaderboard");

const ASSETS_BASE = "../assets/";

window.__VisEscapeGraphs = window.__VisEscapeGraphs || {};

let graphData = null;
let currentStateId = null;
let actionCount = 0;
let lastActionMessage = "";
let afterStateMessage = "";
let congratsShown = false;

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

  if (systemMessageEl) {
    systemMessageEl.textContent = graphData.systemMessage || "";
  }
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
  if (lastActionMessageEl) lastActionMessageEl.textContent = "";
  if (afterStateMessageEl) afterStateMessageEl.textContent = "";
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

  if (lastActionMessageEl) lastActionMessageEl.textContent = lastActionMessage || "";
  if (afterStateMessageEl) afterStateMessageEl.textContent = afterStateMessage || "";

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
    updateLeaderboardWithYou(actionCount);
    if (leaderboardSection) leaderboardSection.hidden = false; // auto-show on clear
    if (!congratsShown) {
      showCongratsPopup(actionCount);
      congratsShown = true;
    }
  } else if (!statusBanner.hidden && statusBanner.dataset.autoClear === "1") {
    // keep current message until timeout clears it
  } else {
    clearBanner();
  }
}

function updateLeaderboardWithYou(turns) {
  if (!leaderboardBody) return;

  // Build rows data from current table
  const rows = Array.from(leaderboardBody.querySelectorAll("tr")).map((tr) => {
    const cells = tr.querySelectorAll("td");
    return {
      rank: parseInt(cells[0].textContent.trim(), 10),
      model: cells[1].textContent.trim(),
      turns: parseInt(cells[2].textContent.trim(), 10),
    };
  });

  // If YOU already exists, update if better; otherwise add
  const existingIndex = rows.findIndex((r) => r.model.toUpperCase() === "YOU");
  if (existingIndex >= 0) {
    if (turns >= rows[existingIndex].turns) return;
    rows[existingIndex].turns = turns;
  } else {
    rows.push({ rank: 0, model: "YOU", turns });
  }

  // Sort ascending by turns
  rows.sort((a, b) => a.turns - b.turns);

  // Re-rank and rebuild tbody
  leaderboardBody.innerHTML = "";
  rows.forEach((entry, idx) => {
    const tr = document.createElement("tr");
    const tdRank = document.createElement("td");
    tdRank.textContent = String(idx + 1);
    const tdModel = document.createElement("td");
    tdModel.textContent = entry.model;
    const tdTurns = document.createElement("td");
    tdTurns.textContent = String(entry.turns);
    tr.appendChild(tdRank);
    tr.appendChild(tdModel);
    tr.appendChild(tdTurns);
    leaderboardBody.appendChild(tr);
  });
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
  congratsShown = false;
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

function showCongratsPopup(turns) {
  if (!modalEl) return;
  if (modalTurnsEl) modalTurnsEl.textContent = String(turns);
  modalEl.hidden = false;
}

function hideCongratsPopup() {
  if (!modalEl) return;
  modalEl.hidden = true;
}

if (modalCloseBtn) {
  modalCloseBtn.addEventListener("click", hideCongratsPopup);
}

if (modalViewBtn) {
  modalViewBtn.addEventListener("click", () => {
    hideCongratsPopup();
    if (leaderboardSection) {
      leaderboardSection.hidden = false;
      leaderboardSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
}

if (modalEl) {
  modalEl.addEventListener("click", (e) => {
    if (e.target === modalEl || e.target.classList.contains("modal-backdrop")) {
      hideCongratsPopup();
    }
  });
}

if (toggleLeaderboardBtn && leaderboardSection) {
  toggleLeaderboardBtn.addEventListener("click", () => {
    const willShow = leaderboardSection.hidden;
    leaderboardSection.hidden = !willShow;
    if (willShow) {
      leaderboardSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
}
