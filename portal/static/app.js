/**
 * OmniForge Homelab Mission Control Frontend Application
 */

const state = {
  autoScroll: true,
  logWs: null,
  agentWs: null,
  logLines: 0,
};

// -------------------------------------------------------------
// Initialization
// -------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  initTelemetryPolling();
  initLogWebSocket();
  initAgentDispatcher();
  initServiceControls();
  loadAudioGallery();

  document.getElementById("btnRefresh").addEventListener("click", () => {
    fetchTelemetry();
    fetchServices();
    loadAudioGallery();
    showToast("Refreshed homelab data 🔄");
  });

  const scrollBtn = document.getElementById("btnToggleScroll");
  scrollBtn.addEventListener("click", () => {
    state.autoScroll = !state.autoScroll;
    scrollBtn.textContent = `Auto-scroll: ${state.autoScroll ? "ON" : "OFF"}`;
  });

  document.getElementById("btnClearLogs").addEventListener("click", () => {
    document.getElementById("logOutput").textContent = "";
    state.logLines = 0;
  });
});

// -------------------------------------------------------------
// System Telemetry & Metrics
// -------------------------------------------------------------
function initTelemetryPolling() {
  fetchTelemetry();
  fetchServices();
  setInterval(fetchTelemetry, 2500);
  setInterval(fetchServices, 3000);
}

async function fetchTelemetry() {
  try {
    const res = await fetch("/api/system");
    if (!res.ok) throw new Error("Telemetry fetch failed");
    const data = await res.json();

    document.getElementById("hostname").textContent = data.hostname || "Homelab Host";
    document.getElementById("osSub").textContent = data.os || "Linux";

    // CPU
    const cpuPct = data.cpu.percent || 0;
    document.getElementById("cpuValue").textContent = `${cpuPct}%`;
    document.getElementById("cpuSub").textContent = `${data.cpu.cores_logical} cores • load ${data.cpu.load_avg.map(v => v.toFixed(1)).join(", ")}`;
    document.getElementById("cpuBar").style.width = `${Math.min(100, Math.max(0, cpuPct))}%`;

    // RAM
    const ramPct = data.memory.percent || 0;
    document.getElementById("ramValue").textContent = `${ramPct}%`;
    document.getElementById("ramSub").textContent = `${data.memory.used_mb} / ${data.memory.total_mb} MB`;
    document.getElementById("ramBar").style.width = `${Math.min(100, Math.max(0, ramPct))}%`;

    // Disk
    const diskPct = data.disk.percent || 0;
    document.getElementById("diskValue").textContent = `${diskPct}%`;
    document.getElementById("diskSub").textContent = `${data.disk.free_gb} GB free of ${data.disk.total_gb} GB`;
    document.getElementById("diskBar").style.width = `${Math.min(100, Math.max(0, diskPct))}%`;

    // Uptime
    const sec = data.uptime_seconds || 0;
    const days = Math.floor(sec / 86400);
    const hrs = Math.floor((sec % 86400) / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    document.getElementById("uptimeValue").textContent = days > 0 ? `${days}d ${hrs}h ${mins}m` : `${hrs}h ${mins}m`;

    updateConnStatus(true);
  } catch (err) {
    updateConnStatus(false);
  }
}

function updateConnStatus(connected) {
  const label = document.getElementById("connLabel");
  const pill = document.getElementById("connStatus");
  if (connected) {
    label.textContent = "Connected";
    pill.style.color = "var(--accent-emerald)";
  } else {
    label.textContent = "Reconnecting...";
    pill.style.color = "var(--accent-rose)";
  }
}

// -------------------------------------------------------------
// Service Supervision
// -------------------------------------------------------------
async function fetchServices() {
  try {
    const res = await fetch("/api/services");
    if (!res.ok) return;
    const data = await res.json();
    const svc = (data.services || [])[0];
    if (!svc) return;

    const dot = document.getElementById("svcDot");
    const meta = document.getElementById("svcMeta");

    if (svc.active) {
      dot.className = "status-indicator active";
      meta.textContent = `State: ${svc.state.toUpperCase()} • PID: ${svc.pid || "--"} • RAM: ${svc.memory_mb || 0} MB • systemd`;
      document.getElementById("btnStartSvc").style.display = "none";
      document.getElementById("btnStopSvc").style.display = "inline-flex";
    } else {
      dot.className = "status-indicator inactive";
      meta.textContent = `State: ${svc.state.toUpperCase()} • Inactive`;
      document.getElementById("btnStartSvc").style.display = "inline-flex";
      document.getElementById("btnStopSvc").style.display = "none";
    }
  } catch (e) {
    console.error("Failed to query services:", e);
  }
}

function initServiceControls() {
  document.getElementById("btnRestartSvc").addEventListener("click", () => handleServiceAction("restart"));
  document.getElementById("btnStopSvc").addEventListener("click", () => handleServiceAction("stop"));
  document.getElementById("btnStartSvc").addEventListener("click", () => handleServiceAction("start"));
}

async function handleServiceAction(action) {
  showToast(`Executing ${action} on omniforge.service... ⏳`);
  try {
    const res = await fetch(`/api/services/omniforge.service/${action}`, { method: "POST" });
    const data = await res.json();
    if (res.ok) {
      showToast(`omniforge.service ${action} successful! ✅`);
      fetchServices();
    } else {
      showToast(`Error: ${data.detail || data.message}`, true);
    }
  } catch (e) {
    showToast(`Network error triggering ${action}`, true);
  }
}

// -------------------------------------------------------------
// Live WebSocket Log Streaming
// -------------------------------------------------------------
function initLogWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/logs/omniforge.service`;

  state.logWs = new WebSocket(wsUrl);
  const logElem = document.getElementById("logOutput");

  state.logWs.onopen = () => {
    logElem.textContent = "[System] Live journalctl WebSocket log stream connected.\n";
  };

  state.logWs.onmessage = (event) => {
    state.logLines++;
    if (state.logLines > 800) {
      logElem.textContent = logElem.textContent.substring(logElem.textContent.indexOf("\n") + 1);
    }
    logElem.appendChild(document.createTextNode(event.data + "\n"));
    if (state.autoScroll) {
      logElem.scrollTop = logElem.scrollHeight;
    }
  };

  state.logWs.onclose = () => {
    setTimeout(initLogWebSocket, 3000);
  };
}

// -------------------------------------------------------------
// Antigravity CLI Agent Dispatcher
// -------------------------------------------------------------
function initAgentDispatcher() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/agent`;

  const input = document.getElementById("agentPromptInput");
  const btn = document.getElementById("btnDispatchAgent");
  const output = document.getElementById("agentStreamOutput");

  function connectAgentWs() {
    state.agentWs = new WebSocket(wsUrl);
    state.agentWs.onmessage = (event) => {
      const data = event.data;
      if (data === "[[AGENT_RUN_COMPLETE]]") {
        btn.disabled = false;
        btn.textContent = "🚀 Dispatch";
        return;
      }
      output.appendChild(document.createTextNode(data + "\n"));
      output.scrollTop = output.scrollHeight;
    };
    state.agentWs.onclose = () => {
      setTimeout(connectAgentWs, 3000);
    };
  }
  connectAgentWs();

  function sendPrompt(promptText) {
    if (!promptText || !state.agentWs || state.agentWs.readyState !== WebSocket.OPEN) {
      showToast("Agent WebSocket is connecting... please wait", true);
      return;
    }
    output.style.display = "block";
    output.textContent = "";
    btn.disabled = true;
    btn.textContent = "⏳ Executing...";
    showToast(`Dispatched task to Antigravity CLI 🧠`);
    state.agentWs.send(JSON.stringify({ prompt: promptText }));
  }

  btn.addEventListener("click", () => {
    sendPrompt(input.value.trim());
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      sendPrompt(input.value.trim());
    }
  });

  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      input.value = chip.dataset.prompt;
      sendPrompt(chip.dataset.prompt);
    });
  });
}

// -------------------------------------------------------------
// Generated Audio & Media Gallery
// -------------------------------------------------------------
async function loadAudioGallery() {
  const container = document.getElementById("audioGallery");
  try {
    const res = await fetch("/api/assets");
    if (!res.ok) throw new Error("Failed to load assets");
    const data = await res.json();
    const assets = (data.assets || []).filter(a => a.type === "audio");

    if (!assets.length) {
      container.innerHTML = `<div class="gallery-empty">No generated bedtime stories found in output/ yet.</div>`;
      return;
    }

    container.innerHTML = assets.map(a => `
      <div class="audio-card">
        <div class="audio-header">
          <span class="audio-title" title="${a.filename}">🎧 ${a.filename}</span>
          <span class="audio-date">${a.size_kb} KB • ${a.modified_str}</span>
        </div>
        <audio controls preload="none">
          <source src="${a.url}" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="gallery-empty">Error loading audio assets.</div>`;
  }
}

// -------------------------------------------------------------
// UI Toast Notifications
// -------------------------------------------------------------
function showToast(msg, isError = false) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast";
  if (isError) toast.style.borderColor = "var(--accent-rose)";
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
