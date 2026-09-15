# SCAMX — AI Scam Risk Intelligence & Decision Engine

[![Pytest Status](https://img.shields.io/badge/Pytest-8%2F8%20Passed-emerald)](file:///C:/Users/12chi/scamX/tests)
[![Build Status](https://img.shields.io/badge/Vite%20Build-0%20Errors-cyan)](file:///C:/Users/12chi/scamX/frontend)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue)](file:///C:/Users/12chi/scamX/backend)
[![React Version](https://img.shields.io/badge/React-18.3-indigo)](file:///C:/Users/12chi/scamX/frontend)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**SCAMX** (`TRUSTX AI`) is a production-grade, multimodal AI scam safety assistant built for **Problem Statement 1: "Is this a scam?"** (Financial Safety & Consumer Protection).

The platform empowers users to instantly analyze suspicious text messages, screenshots, voice call audio, and URLs to detect fraud indicators, verify entities against official bank & government databases, understand transparent evidence breakdowns, and receive deterministic, safe next steps.

---

## 🌟 Core Promise
> **Analyze suspicious content → detect scam signals → show grounded evidence → assess 0–100 risk score → recommend the safest next action & trigger 1930 Cyber Helpline reporting.**

---

## 🏗️ 4-Tier Hybrid Architecture

```
                  ┌──────────────────┐
                  │   USER INPUT     │  (Text / Screenshot / Voice / URL)
                  └────────┬─────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   INPUT NORMALIZER     │  (Cyrillic mapping, zero-width strip, PII redaction)
              └───────────┬────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
  │ RULE ENGINE │  │  URL PROC   │  │ OCR / STT    │
  │ (< 10ms)    │  │ (Static)    │  │ (Multimodal) │
  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ PURE-PYTHON RAG STORE  │  (Govt 1930 / RBI / Bank Advisories)
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ DETERMINISTIC RISK GAUGE│ (0–100 Score Computation)
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ SAFETY POLICY ENGINE   │  (Non-Bypassable DOs & DON'Ts)
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ GEMINI FLASH SYNTHESIS │  (Structured JSON Output)
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ REACT GLASSMORPHISM UI │
              └───────────┬────────────┘
```

1. **Sub-10ms Rule Engine (`rule_engine.py`)**: Runs deterministic regex matching for explicit fraud signals (OTP, PIN, CVV, Password, APK download, remote access). Zero network calls.
2. **Safe Static URL Engine (`url_processor.py`)**: Evaluates TLD risk (`.top`, `.xyz`, `.tech`), typosquatting distance (Levenshtein distance), IP URLs, and path entropy **without making dangerous HTTP network requests**.
3. **Pure-Python Reference Vector RAG (`vector_store.py`)**: Pre-seeded reference knowledge base indexing RBI guidelines, official bank domains, and CERT-In advisories (0 C++ build dependencies).
4. **Non-Bypassable Safety Engine (`safety_engine.py`)**: Enforces mandatory DOs, DON'Ts, and 1-tap call triggers to the **National Cyber Crime Helpline 1930**. Includes **Incident Containment Mode** for past compromise scenarios ("I shared my OTP").
5. **Contextual LLM Synthesizer**: Formats natural language explanations strictly grounded in extracted evidence quotes via Gemini Flash structured output.

---

## 📁 Repository Structure

```
scamX/
├── backend/
│   ├── main.py                  # FastAPI Application Entry & Routing
│   ├── config.py                # Environment Configuration & Settings
│   ├── requirements.txt         # Backend Python Dependencies (0 C++ dependencies)
│   ├── api/
│   │   └── analyze.py           # Multi-modal Analysis & Feedback API Endpoints
│   ├── core/
│   │   ├── normalizer.py        # Input Normalizer & PII Redactor
│   │   └── orchestrator.py      # Core Analysis Pipeline Orchestrator
│   ├── engines/
│   │   ├── rule_engine.py       # Sub-10ms Deterministic Regex Pattern Matcher
│   │   ├── risk_engine.py       # Deterministic Risk Gauge Engine (0–100 Score)
│   │   └── safety_engine.py     # Non-Bypassable Safe Action Policy Generator
│   ├── multimodal/
│   │   ├── ocr_processor.py     # Gemini Vision OCR Extraction Engine
│   │   ├── stt_processor.py     # Whisper Audio Transcriber
│   │   └── url_processor.py     # Safe Static URL Threat Analyzer (0 HTTP calls)
│   ├── rag/
│   │   └── vector_store.py      # Pure-Python Reference Layer Store
│   └── schemas/
│       ├── analysis.py          # Data Models for Analysis & Recommendations
│       ├── enums.py             # Risk Level, Severity, Signal Categories
│       ├── input.py             # Multimodal Input Schemas
│       └── signals.py           # Signal & Evidence Contracts
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main Layout & Tab Router
│   │   ├── index.css            # Dark Glassmorphism CSS Design System
│   │   ├── api/client.ts        # Axios API Client + Offline Simulator Fallback
│   │   ├── components/
│   │   │   ├── Header.tsx       # SCAMX Header with Live Engine Status
│   │   │   ├── InputTabs.tsx    # Multi-tab Input Form & Demo Presets
│   │   │   ├── RiskMeter.tsx    # Visual Score Gauge (0–100 Score & Level)
│   │   │   ├── EvidenceCards.tsx# Signals & Reference Verification Checks
│   │   │   ├── ActionPlan.tsx   # Recommended Action Plan & 1930 Helpline Triggers
│   │   │   └── FeedbackSection.tsx # Accuracy Feedback & Educational Tips Card
│   │   └── types/index.ts       # TypeScript Data Contracts
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docs/                        # Complete Step-by-Step Architecture & Strategy Docs
│   ├── step6_validation_and_redteam.md
│   ├── step7_final_hardening_and_submission.md
│   ├── step8_winning_strategy_and_judge_battle.md
│   ├── step9_final_scorecard_optimization.md
│   ├── step10_final_execution_command_center.md
│   ├── step11_final_verification_and_victory_readiness.md
│   ├── step12_build_execution_and_integration.md
│   └── step13_product_polish_and_demo_excellence.md
└── tests/
    ├── unit/
    │   ├── test_heuristic_rules.py  # Rule Engine Unit Tests
    │   └── test_url_processor.py    # Static URL Analyzer Tests
    └── security/
        └── test_input_sanitization.py # Homoglyph & PII Sanitization Tests
```

---

## ⚡ Quick Start Guide

### 1. Clone & Set Up Backend

```bash
cd backend
python -m venv venv
# Activate venv:
# Windows: .\venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Launch Backend API Server

```bash
$env:PYTHONPATH=".."
python -m uvicorn main:app --reload --port 8000
```
Backend Swagger API docs available at `http://localhost:8000/docs`.

### 3. Launch Frontend Development Server

```bash
cd ../frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 🧪 Running Automated Tests & Production Build

### Run Pytest Test Suite
```bash
$env:PYTHONPATH="."; python -m pytest tests/
```
Output: `8/8 PASSED` in 1.12 seconds.

### Test Production Bundle Build
```bash
cd frontend
npm run build
```
Output: Built production bundle (`dist/`) with 0 errors and 0 warnings in 3.25 seconds.

---

## 🔒 Security & Privacy Boundaries

1. **Zero HTTP Execution**: URL static analyzer evaluates domain structure without making network calls to suspicious links.
2. **PII Masking**: Aadhaar numbers (12 digits), PAN cards, credit card numbers, and OTP codes are redacted at ingestion before logging or LLM synthesis.
3. **Prompt Injection Isolation**: User inputs are placed inside non-executable `<user_content>` delimiters. Safety policy rules operate downstream of the LLM in Python code.
4. **Zero Credential Persistence**: Analysis payloads are processed in memory buffers and discarded immediately.

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
