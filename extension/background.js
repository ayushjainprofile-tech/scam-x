// TRUSTX AI Chrome Extension Background Service Worker

chrome.runtime.onInstalled.addListener(() => {
  // Create Context Menu item for analyzing selected text or URLs
  chrome.contextMenus.create({
    id: "trustx-analyze-selection",
    title: "🛡️ Analyze with TRUSTX AI Engine",
    contexts: ["selection", "link"]
  });
  console.log("TRUSTX AI Extension installed & context menus created.");
});

// Handle Context Menu click
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "trustx-analyze-selection") {
    const textToAnalyze = info.selectionText || info.linkUrl || "";
    if (!textToAnalyze) return;

    try {
      const response = await fetch("http://localhost:8000/api/analyze/text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToAnalyze })
      });

      const data = await response.json();
      
      // Store analysis result in local storage for popup
      await chrome.storage.local.set({ lastAnalysis: data, analyzedText: textToAnalyze });

      // Notify content script or open badge
      if (tab?.id) {
        chrome.tabs.sendMessage(tab.id, { action: "SHOW_SCAM_RESULT", result: data });
      }
    } catch (err) {
      console.error("TRUSTX Background Analysis Error:", err);
    }
  }
});
