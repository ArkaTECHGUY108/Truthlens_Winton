document.addEventListener("DOMContentLoaded", () => {
  const chatWindow = document.getElementById("chat-window");
  const sendBtn = document.getElementById("send-btn");
  const expandBtn = document.getElementById("expand-btn");
  const expandOptions = document.getElementById("expand-options");

  // Toggle expand menu
  expandBtn.addEventListener("click", () => {
    expandOptions.style.display =
      expandOptions.style.display === "flex" ? "none" : "flex";
  });

  // Handle send
  sendBtn.addEventListener("click", async () => {
    const chatField = document.getElementById("chat-field");
    const claimText = document.getElementById("claim-text").value.trim();
    const claimUrl = document.getElementById("claim-url").value.trim();
    const claimImage = document.getElementById("claim-image").files[0];

    let userMessage =
      chatField.value.trim() || claimText || claimUrl || (claimImage && claimImage.name);

    if (!userMessage) return;

    addMessage(userMessage, "user");

    const formData = new FormData();
    if (chatField.value.trim()) {
      formData.append("claim_text", chatField.value.trim());
    } else if (claimText) {
      formData.append("claim_text", claimText);
    }
    if (claimUrl) formData.append("claim_url", claimUrl);
    if (claimImage) formData.append("image", claimImage);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/factcheck", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      showVerdict(data);
      showReasoning(data.reasoning || {});
      showProvenance(data.provenance || {});
      showSocialSignals(data.social_signals || []); // ✅ Social signals panel

      if (data.ledger_status) {
        document.getElementById("ledger-hash").innerText =
          data.ledger_status.ledger_hash || "Recorded";
      }

      enableDownload(data);
    } catch (err) {
      console.error(err);
      addMessage("⚠️ Backend error. Try again later.", "system");
    }

    // Reset fields
    chatField.value = "";
    document.getElementById("claim-text").value = "";
    document.getElementById("claim-url").value = "";
    document.getElementById("claim-image").value = "";
  });

  function addMessage(text, type) {
    const msg = document.createElement("div");
    msg.className = `message ${type}`;
    msg.innerText = text;
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  // Verdict + Gauge
  function showVerdict(data) {
    const card = document.createElement("div");
    card.className = `verdict-card ${data.verdict.toLowerCase()}`;
    const gaugeId = `gauge-${Date.now()}`;

    card.innerHTML = `
      <div id="gauge-wrap" style="text-align:center; margin-bottom:0.3rem;">
        <canvas id="${gaugeId}" width="100" height="60"></canvas>
      </div>
      <h3>${data.verdict} (${data.confidence}%)</h3>
      <div class="sources">
        <strong>Sources:</strong>
        ${
          (data.relevant_sources || [])
            .map(
              (s) =>
                `<a href="${s}" target="_blank">${
                  s.length > 50 ? s.substring(0, 50) + "..." : s
                }</a>`
            )
            .join("") || "No sources available"
        }
      </div>
      ${
        data.deepfake
          ? `<div class="deepfake"><strong>Deepfake Analysis:</strong> ${JSON.stringify(
              data.deepfake
            )}</div>`
          : ""
      }
      <div class="ledger">
        <strong>Ledger:</strong> ${data.ledger_status ? "Recorded" : "Failed"}
      </div>
      <button id="download-json">⬇ Download Full Report</button>
    `;
    chatWindow.appendChild(card);

    // Gauge chart
    new Chart(document.getElementById(gaugeId), {
      type: "doughnut",
      data: {
        datasets: [
          {
            data: [data.confidence, 100 - data.confidence],
            backgroundColor: ["#00f5a0", "#222"],
            borderWidth: 0,
          },
        ],
      },
      options: {
        rotation: -90,
        circumference: 180,
        cutout: "75%",
        plugins: { legend: { display: false } },
      },
    });

    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function showReasoning(reasoning) {
    document.getElementById("fallacies").innerHTML = "";
    document.getElementById("biases").innerHTML = "";
    document.getElementById("debiased").innerText = "";
    document.getElementById("explanation").innerText = "";
    document.getElementById("generative-explainer").innerText = "";

    (reasoning.fallacy || []).forEach((f) => {
      const chip = document.createElement("div");
      chip.className = "chip fallacy";
      chip.innerText = f;
      document.getElementById("fallacies").appendChild(chip);
    });

    (reasoning.bias || []).forEach((b) => {
      const chip = document.createElement("div");
      chip.className = "chip bias";
      chip.innerText = b;
      document.getElementById("biases").appendChild(chip);
    });

    if (reasoning.debiased_text) {
      document.getElementById("debiased").innerText =
        "Debiased: " + reasoning.debiased_text;
    }
    if (reasoning.explanation) {
      document.getElementById("explanation").innerText =
        "Explanation: " + reasoning.explanation;
    }
    if (reasoning.generative_explainer) {
      document.getElementById("generative-explainer").innerText =
        "Generative Explainer: " + reasoning.generative_explainer;
    }
  }

  function showProvenance(provenance) {
    const container = document.getElementById("prov-graph");
    container.innerHTML = "";
    if (!provenance.provenance_graph || !provenance.provenance_graph.nodes) {
      container.innerText = "No provenance data.";
      return;
    }

    const elements = [
      ...provenance.provenance_graph.nodes.map((n) => ({
        data: { id: n.id, label: n.id, role: n.role },
      })),
      ...provenance.provenance_graph.edges.map((e) => ({
        data: { source: e[0], target: e[1] },
      })),
    ];

    cytoscape({
      container,
      elements,
      style: [
        {
          selector: "node[role='origin']",
          style: {
            "background-color": "#00ff88",
            "label": "data(label)",
            "color": "#fff",
            "font-size": "10px",
            "text-outline-width": 2,
            "text-outline-color": "#000",
          },
        },
        {
          selector: "node[role='amplifier']",
          style: {
            "background-color": "#ff8c00",
            "label": "data(label)",
            "color": "#fff",
            "font-size": "10px",
            "text-outline-width": 2,
            "text-outline-color": "#000",
          },
        },
        {
          selector: "node[role='factchecker']",
          style: {
            "background-color": "#00aaff",
            "label": "data(label)",
            "color": "#fff",
            "font-size": "10px",
            "text-outline-width": 2,
            "text-outline-color": "#000",
          },
        },
        {
          selector: "edge",
          style: {
            "line-color": "#00d9f5",
            "target-arrow-color": "#00d9f5",
            "target-arrow-shape": "triangle",
          },
        },
      ],
      layout: { name: "cose", animate: true },
    });
  }

  // ✅ NEW: Social Signals Renderer
  function showSocialSignals(signals) {
    const container = document.getElementById("social-signals");
    if (!container) return;

    container.innerHTML = "";
    if (!signals || signals.length === 0) {
      container.innerHTML = "<p>No social signals found.</p>";
      return;
    }

    signals.forEach((s) => {
      const div = document.createElement("div");
      div.className = "signal-item";
      div.innerHTML = `
        <strong>[${s.platform}]</strong> ${s.user}:
        <a href="${s.url}" target="_blank">${s.text}</a>
        <span class="timestamp">(${s.timestamp})</span>
      `;
      container.appendChild(div);
    });
  }

  function enableDownload(data) {
    const btn = document.getElementById("download-json");
    if (btn) {
      btn.onclick = () => {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "truthlens_report.json";
        a.click();
        URL.revokeObjectURL(url);
      };
    }
  }

  // Community Co-Verification
  document.querySelectorAll(".vote-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const vote = btn.classList.contains("upvote") ? "agree" : "disagree";
      const res = await fetch("http://127.0.0.1:8000/api/community/vote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim: "latest", vote }),
      });
      const data = await res.json();
      document.querySelector(".progress.agree").style.width = `${data.agree}%`;
      document.querySelector(".progress.disagree").style.width = `${data.disagree}%`;
      document.querySelector(".vote-summary").innerText =
        `${data.agree}% agree, ${data.disagree}% disagree`;
    });
  });

  // Ledger Proof -> download as .txt
const ledgerBtn = document.querySelector(".ledger-btn");
if (ledgerBtn) {
  ledgerBtn.addEventListener("click", async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/ledger/proof");
      if (!res.ok) throw new Error("Ledger API error");

      const data = await res.json();
      const ledgerContent = `
🔗 TruthLens Ledger Proof
---------------------------
Ledger Hash : ${data.ledger_hash || "N/A"}
Signed At   : ${data.signed_at || "N/A"}
`;

      const blob = new Blob([ledgerContent], { type: "text/plain" });
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "ledger_proof.txt";   // saved file name
      a.click();

      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Ledger fetch failed:", err);
      alert("⚠️ Could not fetch ledger proof. Please try again.");
    }
  });
}

  // Vanta background
  VANTA.NET({
    el: "body",
    mouseControls: true,
    touchControls: true,
    minHeight: 200,
    minWidth: 200,
    color: 0x00f5a0,
    backgroundColor: 0x0a0f1c,
    points: 12.0,
    maxDistance: 20.0,
    spacing: 15.0,
  });
});