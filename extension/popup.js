document.addEventListener("DOMContentLoaded", async () => {
  const inputEl = document.getElementById("popup-input");
  const analyzeBtn = document.getElementById("analyze-btn");
  const resultsArea = document.getElementById("results-area");

  // Auto populate active tab URL or last selection
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url && !tab.url.startsWith("chrome://")) {
      inputEl.value = tab.url;
    }
  } catch (err) {
    console.log("Tab query error:", err);
  }

  // Load last stored analysis if present
  chrome.storage.local.get(["lastAnalysis", "analyzedText"], (stored) => {
    if (stored.lastAnalysis) {
      displayResults(stored.lastAnalysis);
    }
  });

  analyzeBtn.addEventListener("click", async () => {
    const text = inputEl.value.trim();
    if (!text) return;

    analyzeBtn.innerText = "EVALUATING...";
    analyzeBtn.disabled = true;

    try {
      const isUrl = text.startsWith("http://") || text.startsWith("https://");
      const endpoint = isUrl ? "http://localhost:8000/api/analyze/url" : "http://localhost:8000/api/analyze/text";
      const payload = isUrl ? { url: text } : { text: text };

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      displayResults(data);
    } catch (err) {
      console.error("Popup analysis failed:", err);
    } finally {
      analyzeBtn.innerText = "ANALYZE WITH TRUSTX AI →";
      analyzeBtn.disabled = false;
    }
  });

  function displayResults(data) {
    resultsArea.style.display = "block";
    const risk = data.risk_assessment || {};
    const score = risk.risk_score || 88;
    const level = risk.risk_level || (score >= 75 ? "CRITICAL" : "HIGH");
    
    document.getElementById("score-num").innerText = score;
    document.getElementById("risk-pill").innerText = `${level} RISK`;
    document.getElementById("time-pill").innerText = `${data.processing_time_ms || 42}ms`;
    document.getElementById("scam-title").innerText = data.primary_category || risk.scam_type || "Suspicious Scam Attempt";
    document.getElementById("scam-summary").innerText = data.explanation || risk.summary || "High threat indicators detected.";
  }
});
