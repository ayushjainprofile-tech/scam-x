// TRUSTX AI Content Script - Webpage In-Page Security Inspector

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "SHOW_SCAM_RESULT") {
    const result = message.result;
    const score = result.risk_assessment?.risk_score || 85;
    const level = result.risk_assessment?.risk_level || (score >= 75 ? "CRITICAL" : "HIGH");
    const scamType = result.primary_category || result.risk_assessment?.scam_type || "Suspicious Phishing Request";

    showInPageBanner(score, level, scamType, result.explanation || "Potential fraud detected!");
  }
});

function showInPageBanner(score, level, scamType, explanation) {
  let banner = document.getElementById("trustx-security-banner");
  if (banner) banner.remove();

  banner = document.createElement("div");
  banner.id = "trustx-security-banner";
  banner.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 999999;
    width: 340px;
    background: #180C06;
    color: #FBDBAF;
    font-family: 'Inter', system-ui, sans-serif;
    border: 1px solid rgba(251, 219, 175, 0.3);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 16px 40px rgba(0,0,0,0.5);
    backdrop-filter: blur(16px);
  `;

  banner.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
      <span style="font-size:11px; font-weight:700; background:rgba(255,77,77,0.2); color:#FF4D4D; padding:3px 8px; border-radius:4px;">
        🛡️ TRUSTX ${level} (${score}/100)
      </span>
      <button id="trustx-close-btn" style="background:none; border:none; color:#FBDBAF; font-size:16px; cursor:pointer;">✕</button>
    </div>
    <div style="font-size:13px; font-weight:700; color:#FBDBAF; margin-bottom:6px;">${scamType}</div>
    <div style="font-size:12px; color:rgba(251,219,175,0.75); line-height:1.4;">${explanation}</div>
    <div style="margin-top:12px; font-size:11px; font-weight:600; color:#E07020;">
      📞 National Cybercrime Helpline: 1930
    </div>
  `;

  document.body.appendChild(banner);

  document.getElementById("trustx-close-btn").onclick = () => banner.remove();
}
