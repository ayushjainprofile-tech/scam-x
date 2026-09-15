# TRUSTX AI — Complete Architecture & Engineering Blueprint
### Step 1: Architecture Lock Document
---

## PART 1 — FINAL PRODUCT DEFINITION

### Product Description
**TRUSTX AI** is a multimodal, conversational AI assistant that analyzes suspicious messages, screenshots, voice recordings, and URLs to help everyday users determine if they are being scammed. It does not just flag scams — it **explains why**, quantifies risk, and tells the user exactly what to do next.

### Target Users
- Primary: Non-technical individuals who received a suspicious WhatsApp/SMS/email message
- Secondary: Elderly users, first-time digital finance users in India
- Tertiary: Consumer protection organizations, bank helpdesks

### Core Problem
Users receive suspicious communication and have no fast, trusted, explainable tool to evaluate it. They either ignore real threats or act on fake ones. Neither outcome is acceptable.

### Core Promise
> Analyze suspicious content → assess risk → explain the evidence → tell you the safest next action.

### Primary Workflow
1. User submits input (text / screenshot / voice / URL)
2. System extracts and normalizes the content
3. AI pipeline analyzes for scam indicators
4. Risk engine produces a score + band
5. Explainability engine ties evidence to actual input
6. Structured response delivered to frontend
7. User sees risk level, evidence, and recommended action

### Main User Journey
```
Receives suspicious message
→ Opens TRUSTX AI
→ Pastes / uploads / speaks the content
→ Sees: RISK BAND + CATEGORY + EVIDENCE + NEXT ACTION
→ Takes informed, safe decision
→ Optionally submits feedback
```

### Key Outputs
- Risk band (LOW / MEDIUM / HIGH / CRITICAL)
- Scam category (KYC_PHISHING, LOTTERY, etc.)
- Confidence level
- Evidence list (tied to actual input)
- Potential harm description
- Recommended actions
- Safe verification path
- Uncertainty disclaimer

### Differentiators
1. **Explainability-first** — not just "scam/not-scam"
2. **Multimodal** — text, image, voice, URL in one system
3. **Deterministic risk engine** — not purely LLM-driven scores
4. **Responsible AI** — explicit uncertainty, no false guarantees
5. **India-context aware** — Hindi, Hinglish, UPI, KYC patterns
6. **RAG-grounded** — evidence from curated reference layer, not hallucinated

### Hackathon Value
Demonstrates: RAG, structured LLM output, multimodal AI, risk engineering, responsible AI, explainability — all in one coherent demo.

### Real-World Value
Could be deployed as a WhatsApp bot, browser extension, or bank app plugin to protect millions of users from financial fraud.

---

### Architecture Diagram — High Level Flow

```
USER
  │
  ▼
INPUT (text / image / voice / URL)
  │
  ▼
INPUT PROCESSING LAYER
  ├── Text: preprocessing + language detection
  ├── OCR: image → text
  ├── STT: audio → text
  └── URL: metadata extraction
  │
  ▼
NORMALIZATION & INDICATOR EXTRACTION
  │
  ▼
AI ANALYSIS PIPELINE
  ├── Rule Engine (deterministic signals)
  ├── NLP Classifier (scam category)
  ├── LLM (semantic understanding + evidence extraction)
  └── RAG (retrieval from curated knowledge base)
  │
  ▼
RISK ENGINE (deterministic weighted scoring)
  │
  ▼
EXPLAINABILITY ENGINE (evidence ↔ input grounding)
  │
  ▼
SAFETY POLICY LAYER (hallucination guard + refusal rules)
  │
  ▼
STRUCTURED JSON RESPONSE
  │
  ▼
FRONTEND (risk card + evidence + action)
```

---

## PART 2 — SYSTEM REQUIREMENTS

### Input Requirements

| Requirement | Priority |
|---|---|
| Accept plain text input | MUST |
| Accept screenshot/image upload | MUST |
| Accept audio/voice recording | SHOULD |
| Accept raw URL | MUST |
| Accept app notification text (paste) | SHOULD |
| Support multilingual input (EN/HI/Hinglish) | MUST |
| Validate and reject malformed inputs | MUST |
| File size limits and format validation | MUST |

### Processing Requirements

| Requirement | Priority |
|---|---|
| Text preprocessing (clean, normalize) | MUST |
| OCR from screenshot | MUST |
| OCR failure handling with user prompt | MUST |
| Speech-to-text transcription | SHOULD |
| Transcription confidence scoring | SHOULD |
| Language detection | MUST |
| Scam indicator extraction | MUST |
| Scam classification (taxonomy-based) | MUST |
| Risk scoring (deterministic engine) | MUST |
| Evidence extraction (grounded to input) | MUST |
| URL metadata analysis (no live crawling of suspicious URLs) | MUST |
| Knowledge retrieval (RAG) | MUST |
| Explanation generation (LLM) | MUST |
| Confidence scoring | MUST |
| Uncertainty flag generation | MUST |

### Output Requirements

| Requirement | Priority |
|---|---|
| Risk band (LOW/MEDIUM/HIGH/CRITICAL) | MUST |
| Risk score (numeric, displayed as band) | SHOULD |
| Scam category | MUST |
| Confidence level | MUST |
| Evidence list (quoted from input) | MUST |
| Potential harm description | MUST |
| Recommended actions (ordered) | MUST |
| Safe verification method | MUST |
| Uncertainty warning when confidence < threshold | MUST |
| Source attribution from RAG | SHOULD |
| Reporting/escalation guidance | SHOULD |
| Multilingual response | SHOULD |

---

## PART 3 — HIGH-LEVEL ARCHITECTURE

```
USER
  │
  ▼
┌─────────────────────────────────────┐
│           FRONTEND                  │
│  (React/Next.js — Input + Results)  │
└────────────────┬────────────────────┘
                 │ HTTPS / REST
                 ▼
┌─────────────────────────────────────┐
│        API GATEWAY / BACKEND        │
│     (FastAPI — routing, auth,       │
│      rate limiting, validation)     │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       INPUT PROCESSING LAYER        │
│  ┌──────┐ ┌─────┐ ┌───────┐ ┌────┐ │
│  │ TEXT │ │ OCR │ │ SPEECH│ │ URL│ │
│  └──────┘ └─────┘ └───────┘ └────┘ │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│         NORMALIZATION LAYER         │
│  (clean text, language detect,      │
│   indicator pre-extraction)         │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│          AI ANALYSIS ENGINE         │
│  ┌───────────┐  ┌────────────────┐  │
│  │RULE ENGINE│  │ NLP CLASSIFIER │  │
│  └───────────┘  └────────────────┘  │
│  ┌───────────┐  ┌────────────────┐  │
│  │    LLM    │  │   RAG/RETRIEV. │  │
│  └───────────┘  └────────────────┘  │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│           RISK ENGINE               │
│  (deterministic weighted scoring)   │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       EXPLAINABILITY ENGINE         │
│  (evidence grounding, harm desc,    │
│   action generation)                │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│         SAFETY POLICY LAYER         │
│  (hallucination guard, output       │
│   sanitization, refusal rules)      │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       STRUCTURED JSON RESPONSE      │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│           FRONTEND                  │
│  (Risk Card, Evidence, Actions)     │
└─────────────────────────────────────┘
```

**Component Responsibilities:**
- **Frontend**: Input collection, result display, accessibility
- **API Gateway/Backend**: Routing, validation, rate limiting, session management
- **Input Processing**: Format-specific extraction — OCR, STT, URL parsing
- **Normalization**: Unified text representation regardless of input type
- **Rule Engine**: Deterministic signal detection (regex, keyword lists)
- **NLP Classifier**: Lightweight scam category classification
- **LLM**: Semantic reasoning, evidence extraction, explanation, structured output
- **RAG**: Retrieves relevant scam patterns and safety guidance from curated knowledge
- **Risk Engine**: Weighted, auditable score computation
- **Explainability Engine**: Maps evidence back to original input spans
- **Safety Policy**: Ensures output is responsible, non-harmful, properly hedged
- **Structured Response**: Validated JSON passed to frontend

---

## PART 4 — INPUT PIPELINE

### A. Text Pipeline

```
USER TEXT INPUT
  │
  ▼
Preprocessing
  (strip HTML, normalize whitespace, Unicode normalization,
   remove personally identifying numbers for logging)
  │
  ▼
Language Detection
  (fasttext-based langdetect → EN / HI / Hinglish / OTHER)
  │
  ▼
Indicator Extraction (Rule Engine pass)
  (regex: OTP request, urgency words, phone numbers,
   UPI IDs, suspicious patterns, financial keywords)
  │
  ▼
AI Analysis (LLM + RAG in parallel)
  │
  ▼
Risk Scoring (Risk Engine)
  │
  ▼
Structured Response Assembly
```

**Every step:**
- Preprocessing: Ensures clean, consistent input to downstream components; prevents injection via formatting tricks
- Language Detection: Selects appropriate model behavior and response language
- Indicator Extraction: Fast, cheap, deterministic first pass — populates initial signal set
- AI Analysis: LLM understands semantics; RAG provides grounded reference context
- Risk Scoring: Combines rule-engine signals + LLM signals deterministically

---

### B. Screenshot Pipeline

```
IMAGE UPLOAD
  │
  ▼
Validation
  (format: PNG/JPG/WEBP, size < 10MB, basic MIME check)
  │
  ▼
Malicious Content Check
  (reject obvious non-image binary, oversized files)
  │
  ▼
OCR (Tesseract / Google Vision API)
  │
  ├── Success → extracted text
  └── Failure / Low confidence
        │
        ▼
      Fallback: Ask user to manually paste the text
      OR: Return partial result with uncertainty flag
  │
  ▼
Text Cleanup
  (OCR artifacts: fix garbled chars, merge line fragments,
   normalize broken words)
  │
  ▼
Language Detection
  │
  ▼
→ Feeds into Text Pipeline (from Language Detection step)
```

**OCR Failure Handling:**
- If OCR confidence < 0.5: flag `ocr_quality: LOW`, add uncertainty warning
- If extracted text < 10 characters: treat as OCR failure, prompt user to paste text
- Never silently proceed with garbage OCR output — always propagate quality signal

---

### C. Voice Pipeline

```
AUDIO UPLOAD / RECORDING
  │
  ▼
Validation
  (format: WAV/MP3/WEBM, duration < 3 min, size limit)
  │
  ▼
Speech-to-Text (Whisper / Google STT)
  │
  ├── Success → transcript + confidence score
  └── Low confidence / garbled
        │
        ▼
      Flag: transcription_confidence: LOW
      Add uncertainty warning to final output
      Ask user to re-record or type manually
  │
  ▼
Language Detection
  │
  ▼
Text Normalization
  (remove filler words, fix STT errors where obvious,
   do NOT alter scam indicators)
  │
  ▼
→ Feeds into Text Pipeline
```

**Transcription Uncertainty:**
- Whisper provides word-level confidence — use average as transcription_confidence
- If < 0.6, append: `"Note: Voice transcription quality was limited. Results may be less accurate."`
- Never correct words that might be scam-relevant indicators — preserve them

---

### D. URL Pipeline

```
URL INPUT
  │
  ▼
Normalization
  (lowercase, strip tracking params, decode URL encoding)
  │
  ▼
Domain Extraction
  (extract apex domain, subdomain, TLD)
  │
  ▼
Safe Metadata Analysis ONLY
  ├── Domain age (WHOIS API — read-only)
  ├── TLD suspicion check (known phishing TLDs)
  ├── Domain similarity (Levenshtein vs known brands: sbi, hdfc, paytm...)
  ├── Subdomain anomalies (sbi-login.freesite.xyz pattern)
  ├── URL structure patterns (excessive hyphens, numeric IPs, etc.)
  └── Check against known phishing/malware blocklists (Google Safe Browsing API)
  │
  ▼
AI / Context Analysis
  (LLM interprets domain name for impersonation intent)
  │
  ▼
Risk Contribution Score
  (added as URL_SIGNAL to risk engine)
```

> ⚠️ **CRITICAL SAFETY RULE:** The system must NEVER open, crawl, fetch, or execute content from a suspicious URL. Only analyze the URL string and metadata. This protects the system from SSRF attacks, malware execution, and credential harvesting page visits.

---

## PART 5 — AI ARCHITECTURE

### Option A — Everything → LLM
```
Input → LLM → Output
```
**Problems:**
- LLM can hallucinate risk scores
- Non-deterministic results (same input, different score)
- Not auditable — can't explain why score is 94 vs 87
- Expensive for every request
- No structured signal separation
- Prompt injection risk is higher with unconstrained LLM
- Single point of failure

### Option B — Rules + NLP + Retrieval + LLM + Risk Engine
```
Input
  ├── Rule Engine → deterministic signals
  ├── Classifier → category probabilities  
  ├── RAG → relevant reference context
  └── LLM → semantic understanding + explanation
        │
        ▼
  Risk Engine → weighted, auditable final score
```
**Advantages:**
- Deterministic, auditable risk scoring
- LLM focuses on what it's good at: understanding, explanation
- Rules catch known patterns reliably without LLM cost
- RAG grounds explanations in real reference data
- Failure of any one component degrades gracefully
- Cheaper overall (not every request hits LLM at full cost)

**Decision: Option B is the correct approach. Non-negotiable for a responsible AI system.**

### Final AI Architecture

```
Normalized Text
  │
  ├──► Rule Engine
  │      (regex + keyword + pattern matching)
  │      Output: {signal_list, initial_flags}
  │
  ├──► RAG Retrieval
  │      (semantic search on knowledge base)
  │      Output: {relevant_docs, scam_patterns}
  │
  └──► LLM (with retrieved context + rule engine signals)
         Prompt: [system instruction + normalized input +
                  rule signals + RAG context + output schema]
         Output: {category, indicators, evidence, explanation,
                  recommended_action, confidence, uncertainty}
         │
         ▼
  Risk Engine
    (combines rule signals + LLM signals → final score + band)
```

---

## PART 6 — LLM RESPONSIBILITIES

### LLM IS responsible for:
- Semantic understanding of scam intent (beyond keyword matching)
- Nuanced scam category classification
- Evidence extraction — identifying specific phrases that are suspicious
- Natural language explanation generation
- Multilingual understanding (Hindi/Hinglish without explicit translation)
- Safe recommendation drafting
- Uncertainty articulation
- Structured JSON output generation

### LLM is NOT responsible for:
- **Final risk score computation** — this is the Risk Engine's job
- **Deciding if a URL is safe** — Safe Browsing API + metadata analysis does this
- **Making absolute guarantees** ("this IS a scam", "this is 100% safe")
- **Financial actions or recommendations** (never "transfer money here instead")
- **Accessing external URLs** — forbidden
- **Storing or repeating sensitive user data** in responses
- **Security-critical binary decisions** without deterministic guard

---

## PART 7 — STRUCTURED OUTPUT SCHEMA

```json
{
  "analysis_id": "uuid-v4",
  "input_type": "TEXT | IMAGE | AUDIO | URL",
  "language_detected": "en | hi | hinglish",
  "ocr_quality": "HIGH | MEDIUM | LOW | N/A",
  "transcription_confidence": 0.87,

  "risk_band": "LOW | MEDIUM | HIGH | CRITICAL",
  "risk_score": 87,
  "scam_category": "KYC_PHISHING",
  "scam_category_display": "KYC / Identity Phishing",
  "confidence": 0.91,

  "indicators": [
    {
      "type": "OTP_REQUEST",
      "quote": "Please share your OTP immediately",
      "weight": "HIGH"
    },
    {
      "type": "URGENCY",
      "quote": "Your account will be blocked in 24 hours",
      "weight": "HIGH"
    },
    {
      "type": "SUSPICIOUS_URL",
      "quote": "sbi-kyc-update.xyz",
      "weight": "CRITICAL"
    }
  ],

  "evidence": [
    "The message requests an OTP, which no legitimate bank ever does via message.",
    "The domain 'sbi-kyc-update.xyz' is not an official SBI domain.",
    "The threat of account blocking creates artificial urgency — a classic phishing tactic."
  ],

  "potential_harm": "Credential theft leading to unauthorized account access and financial loss.",

  "recommended_actions": [
    "Do NOT share any OTP, password, or PIN.",
    "Do NOT click any link in this message.",
    "Contact your bank directly using the number on the back of your card.",
    "Report this message to cybercrime.gov.in."
  ],

  "verification_method": "Visit your bank's official app or type the official URL manually. Never use links from messages.",

  "uncertainty": null,

  "rag_sources": [
    {"title": "RBI Guidelines on OTP Safety", "relevance": "HIGH"}
  ],

  "processing_meta": {
    "latency_ms": 1240,
    "model_used": "gemini-1.5-pro",
    "rag_docs_retrieved": 3,
    "rule_signals_fired": 4
  }
}
```

**Field explanations:**
- `risk_band`: The primary user-facing risk signal — discrete, not numeric
- `risk_score`: Internal use + display only as band to avoid false precision
- `scam_category`: Machine-readable taxonomy ID
- `confidence`: LLM + classifier combined confidence (0–1)
- `indicators`: Specific, quoted evidence with type and weight
- `evidence`: Human-readable explanations for each indicator
- `potential_harm`: Worst-case outcome in plain language
- `recommended_actions`: Ordered, specific, actionable steps
- `verification_method`: Safe alternative to the suspicious action
- `uncertainty`: Populated when confidence < threshold
- `rag_sources`: Attribution — where the safety guidance came from
- `processing_meta`: For observability, not shown to user

---

## PART 8 — RISK ENGINE

### Design Principle
The risk score must be **deterministic, auditable, and explainable**. The LLM cannot set the final score. It provides signals; the engine computes the score.

### Signals & Weights

| Signal | Weight | Severity |
|---|---|---|
| OTP_REQUEST | 25 | CRITICAL |
| PIN_PASSWORD_REQUEST | 25 | CRITICAL |
| SUSPICIOUS_URL | 20 | CRITICAL |
| CREDENTIAL_HARVESTING | 20 | CRITICAL |
| PAYMENT_REQUEST | 18 | HIGH |
| IMPERSONATION (bank/govt) | 15 | HIGH |
| FAKE_AUTHORITY | 15 | HIGH |
| URGENCY + THREAT | 12 | HIGH |
| ACCOUNT_TAKEOVER_LANGUAGE | 12 | HIGH |
| UNREALISTIC_REWARD | 10 | MEDIUM |
| SUSPICIOUS_CONTACT_METHOD | 8 | MEDIUM |
| UNKNOWN_SENDER | 5 | LOW |
| URGENCY (alone, no threat) | 5 | LOW |

### Aggregation
```
raw_score = Σ(weight_i × confidence_i) for each fired signal

# Normalize to 0-100
normalized_score = min(100, raw_score)

# Apply confidence decay
final_score = normalized_score × overall_confidence

# Determine band
CRITICAL: score ≥ 85
HIGH:     score 60–84
MEDIUM:   score 35–59
LOW:      score < 35
```

### Avoiding False Precision
- **Do NOT display "94/100"** to users — it implies false precision
- Display the band: "HIGH RISK" is more defensible than "94%"
- The numeric score is for internal engineering and logging only
- If multiple high-weight signals fire, cap at CRITICAL rather than fabricating 99.8%

### AI Signal Integration
- LLM returns `indicators[]` each with a `signal_type` and `llm_confidence`
- Rule engine independently detects signals with `rule_confidence: 1.0` (deterministic)
- Risk engine takes the **union** of both signal sets
- If both rule engine and LLM agree on a signal → use max weight × 1.1 (corroboration bonus)
- If only LLM fires a signal → use weight × LLM_confidence (discounted)

---

## PART 9 — SCAM TAXONOMY

### Initial Production Taxonomy

| ID | Display Name | Description | Severity | Example Indicators |
|---|---|---|---|---|
| KYC_PHISHING | KYC / Identity Phishing | Fake KYC update requests to steal identity | CRITICAL | OTP request, account block threat, bank impersonation |
| BANKING_FRAUD | Banking Fraud | Fake bank communication to steal credentials | CRITICAL | PIN request, fake bank URL, urgent account alerts |
| UPI_PAYMENT_FRAUD | UPI Payment Fraud | Fake UPI collect requests or payment demands | CRITICAL | "Accept ₹X" scam, fake payment link |
| LOTTERY_PRIZE | Lottery / Prize Scam | Unrealistic rewards requiring payment or data | HIGH | "You've won", advance fee, prize claim link |
| JOB_FRAUD | Job / Work-From-Home Fraud | Fake job offers requiring payment or data | HIGH | "Earn ₹50k/month", registration fee, WhatsApp job |
| INVESTMENT_FRAUD | Investment / Stock Fraud | Fake investment opportunities with guaranteed returns | HIGH | "Double your money", crypto pump, Telegram group |
| DELIVERY_FRAUD | Delivery / Courier Fraud | Fake delivery notifications requiring payment | MEDIUM | "Your package held", customs fee, delivery link |
| GOVT_IMPERSONATION | Government Impersonation | Fake government/police/tax authority messages | CRITICAL | IT refund, police call, Aadhaar block |
| CUSTOMER_SUPPORT_FRAUD | Fake Customer Support | Fraudsters impersonating customer service | HIGH | Remote access request, refund fraud |
| ACCOUNT_TAKEOVER | Account Takeover | Attempts to gain control of user accounts | CRITICAL | OTP phishing, password reset manipulation |
| ROMANCE_FRAUD | Romance / Social Engineering | Emotional manipulation for money extraction | HIGH | Relationship building followed by financial request |
| OTHER | Other / Unknown | Suspicious but doesn't match known categories | MEDIUM | Use when confidence < 0.5 for any category |

### Recommended Actions per Category

Each category in the knowledge base includes:
- `indicators[]`: pattern list
- `examples[]`: real-world anonymized examples  
- `recommended_actions[]`: specific safe steps
- `reporting_guidance`: where to report this specific type
- `severity`: CRITICAL/HIGH/MEDIUM/LOW
- `false_positive_notes`: what legitimate messages might look like

### Taxonomy Expansion
The taxonomy is stored as a JSON/YAML config file. Adding a new category requires:
1. Add entry to `scam_taxonomy.json`
2. Add knowledge documents to RAG store
3. Add example prompts to evaluation set
4. No code changes required

---

## PART 10 — CURATED REFERENCE LAYER / RAG

### What Goes Into the Knowledge Base?

1. **Scam pattern documents** — each taxonomy category with detailed indicators
2. **Official safety guidelines** — RBI OTP guidelines, CERT-In advisories, cybercrime.gov.in guidance
3. **Verification procedures** — how to verify legitimate bank/govt communication
4. **Trusted domain reference** — official domains for major banks, UPI apps, government (lookup only, not live crawling)
5. **Indicator explanations** — why OTP requests are always fraudulent, etc.
6. **Reporting procedures** — National Cyber Crime Helpline (1930), cybercrime.gov.in

> ⚠️ Do NOT fabricate official source URLs. Only include sources that can be verified. Every document in the KB must have a source, date, and confidence level.

### Storage Decision

| Option | Pros | Cons | Hackathon Suitability |
|---|---|---|---|
| JSON files | Zero setup, portable | No semantic search | Sufficient for < 100 docs |
| PostgreSQL + pgvector | Scalable, SQL | Setup overhead | Moderate |
| ChromaDB | Simple vector DB, local | Less production-ready | ✅ Best for hackathon |
| Pinecone | Managed, scalable | Cost, setup | Overkill for hackathon |

**Decision: ChromaDB (local, in-process) for hackathon. Migrate to pgvector or Pinecone for production.**

### Retrieval Design

```
USER INPUT (normalized text)
  │
  ▼
Query Generation
  (embed input using same embedding model as KB)
  │
  ▼
Semantic Search in ChromaDB
  (top-k=5, with metadata filter by language if needed)
  │
  ▼
Metadata Filtering
  (filter by: category_hint if rule engine fired,
   language preference, source_reliability ≥ 0.8)
  │
  ▼
Retrieved Documents (top 3–5)
  │
  ▼
Injected into LLM Prompt as [CONTEXT]
  │
  ▼
LLM generates grounded response citing retrieved context
```

**Source Trust & Updates:**
- Every KB document has: `source`, `date_added`, `last_verified`, `reliability_score`
- Documents from official sources (RBI, CERT-In) get `reliability: 1.0`
- Community-sourced patterns get `reliability: 0.7`
- Documents older than 6 months flagged for re-verification

---

## PART 11 — PROMPT ARCHITECTURE

### Prompt Types

#### 1. Scam Analysis Prompt (Primary)
- **System**: Role definition, output schema, constraints, what NOT to do
- **Context**: Retrieved RAG documents, rule engine signal list
- **User Input**: Normalized text
- **Output**: Structured JSON per schema

#### 2. Evidence Extraction Prompt
- **System**: "Quote exact phrases from the input that support each indicator"
- **Constraint**: Quotes must be verbatim substrings of the input — never paraphrase
- **Output**: `indicators[].quote` fields

#### 3. Explanation Prompt
- **System**: "Explain each indicator in plain language a non-technical user can understand"
- **Constraint**: No financial advice, no absolute guarantees
- **Output**: `evidence[]` array

#### 4. Safety Advice Prompt
- **System**: "Generate ordered, specific action steps. No vague advice."
- **Context**: Scam category + identified indicators
- **Output**: `recommended_actions[]`

#### 5. Multilingual Response Prompt
- **System**: "Respond in {detected_language}. Maintain all technical indicators in their original form."
- **Constraint**: Do not translate scam-relevant terms that change meaning

#### 6. Uncertainty Handling
- If confidence < 0.5: "State clearly that there is insufficient evidence to make a determination. List what was observed. Ask user if they can provide more context."
- Never default to "safe" when uncertain — default to "need more information"

### Prompt Constraints (All Prompts)
```
NEVER:
- Claim 100% certainty
- Recommend financial transactions
- Access external URLs
- Include user's sensitive data in output
- Make medical/legal/financial advice claims

ALWAYS:
- Hedge appropriately
- Cite evidence from input
- Use retrieved context before inventing facts
- Return valid JSON matching the schema
- Include uncertainty field when appropriate
```

---

## PART 12 — MULTILINGUAL ARCHITECTURE

### Supported Languages
- English (en)
- Hindi (hi)
- Hinglish (hi-en mixed)

### Language Flow

```
INPUT
  │
  ▼
Language Detection (fasttext-langdetect, fast & local)
  │
  ├── EN → direct analysis
  ├── HI → direct analysis (if model supports Hindi natively)
  ├── Hinglish → direct analysis (treat as mixed, no translation)
  └── OTHER → flag as unsupported, process in EN, warn user
  │
  ▼
Analysis (in detected language)
  │
  ▼
Response Language Selection
  (respond in same language as input by default)
  (user can override to English)
```

### Translation Decision
**Do NOT translate Hindi/Hinglish to English before analysis.**

Reasons:
- Translation loses scam-relevant nuance ("urgent karo abhi" urgency is partially lost)
- Gemini 1.5 Pro handles Hindi natively at high quality
- Translation adds latency and potential error propagation
- Scam indicators should be quoted verbatim in the output

### Preserving Indicators
- Urgency words like "अभी", "तुरंत", "account band" must be preserved in quotes
- Do not normalize regional variations of brand names
- If a message mixes scripts, preserve the mixed form

---

## PART 13 — EXPLAINABILITY ENGINE

### User-Facing Explanation Structure

```
┌─────────────────────────────────────────┐
│  ⚠️  HIGH RISK                          │
│  Confidence: High                       │
├─────────────────────────────────────────┤
│  📂 Category: KYC / Identity Phishing   │
├─────────────────────────────────────────┤
│  🔍 Evidence Found in Your Message:     │
│                                         │
│  • OTP Request                          │
│    "Please share your OTP immediately"  │
│                                         │
│  • Urgency + Threat                     │
│    "account will be blocked in 24 hrs"  │
│                                         │
│  • Suspicious Domain                    │
│    "sbi-kyc-update.xyz"                 │
├─────────────────────────────────────────┤
│  💥 Potential Harm:                     │
│    Account takeover, financial loss     │
├─────────────────────────────────────────┤
│  ✅ Recommended Actions:               │
│  1. Do NOT share any OTP               │
│  2. Do NOT click any link              │
│  3. Call your bank directly            │
│  4. Report to cybercrime.gov.in        │
├─────────────────────────────────────────┤
│  🔒 Safe Verification:                  │
│  Open your bank's official app or type  │
│  the URL manually in your browser.      │
└─────────────────────────────────────────┘
```

### Evidence Grounding Rule
- Every indicator must have a `quote` — a verbatim substring from the actual user input
- The LLM is instructed: "Only quote text that appears EXACTLY in the provided input"
- If an indicator is inferred (not explicitly stated), mark as `"inferred": true` and explain reasoning
- This prevents the most common hallucination: fabricating evidence that isn't in the input

---

## PART 14 — UNCERTAINTY DESIGN

### Three States

#### 🔴 HIGH CONFIDENCE (confidence ≥ 0.80)
- Multiple strong indicators present
- Rule engine and LLM agree
- RAG retrieval found matching patterns
- Display: Risk band without hedging, but never "100% scam"

#### 🟡 UNCERTAIN (confidence 0.40–0.79)
- Some indicators present but ambiguous
- LLM and rule engine partially disagree
- Display: "We detected some suspicious patterns, but cannot make a high-confidence determination. Here's what we found..."
- Ask user: "Can you provide more context? (e.g., who sent this?)"

#### 🟢 LIKELY SAFE (confidence < 0.40, no strong signals)
- No significant indicators detected
- Display: **"No strong scam indicators were detected in this message. However, this does not guarantee the message is legitimate. If in doubt, verify through official channels."**
- NEVER say: "This message is safe." or "This is not a scam."

### When to Ask for More Information
- Input is < 20 characters
- OCR quality was LOW
- Transcription confidence < 0.6
- Language detected as UNKNOWN
- Input is a single URL with no message context
- Confidence < 0.5 after full analysis

---

## PART 15 — SAFETY ARCHITECTURE

### AI Safety

| Threat | Mitigation |
|---|---|
| Prompt Injection | System prompt uses clear delimiters; user input is never trusted as instruction; output validated against schema |
| Hallucinated Evidence | Evidence quotes validated as substrings of actual input |
| Overconfident Output | Risk band displayed, not raw score; uncertainty field mandatory |
| Model Jailbreak | Safety policy layer validates all outputs before returning |
| Biased Classification | Evaluation set tests false positive rate on legitimate messages |

### Application Security

| Threat | Mitigation |
|---|---|
| Malicious Image Upload | MIME validation, file size limits, sandboxed OCR processing |
| SSRF via URL | Never fetch suspicious URLs; only analyze string + safe metadata APIs |
| Malicious File Execution | No code execution from user input, ever |
| Rate Limit Abuse | Per-IP rate limiting at API gateway |
| Data Exfiltration | No user data logged beyond anonymized analysis metadata |

### User Privacy

| Threat | Mitigation |
|---|---|
| Sensitive Data Exposure | Phone numbers, OTPs, account numbers masked in logs |
| Voice Recording Retention | Audio deleted immediately after transcription |
| Screenshot Retention | Image deleted after OCR; only extracted text retained temporarily |
| LLM Provider Data | Use API with data processing agreements; minimal PII in prompts |

---

## PART 16 — PRIVACY ARCHITECTURE

### Data Minimization
- Extract only what's needed for analysis
- Do not send full raw screenshots to LLM — send OCR-extracted text only
- Mask any detected OTPs, account numbers, phone numbers before storing

### What Must NEVER Be Stored
- Raw OTP values
- Raw passwords or PINs
- Voice recordings (after transcription)
- Full screenshots (after OCR)
- Complete user messages verbatim in logs
- Any PII linkable to an individual without consent

### Temporary Processing Model
```
Input received
  → Processed in memory
  → Result generated
  → Raw input deleted after N minutes (configurable, default: 0 — immediate)
  → Only anonymized analysis metadata stored (risk_band, category, timestamp)
```

### Logging Policy
```
LOG: analysis_id, timestamp, input_type, language, risk_band, category, confidence, latency_ms, errors
DO NOT LOG: raw_input_text, extracted_quotes verbatim, any PII
```

### Encryption
- All data in transit: TLS 1.3
- All data at rest: AES-256
- API keys: Environment variables, never in code

---

## PART 17 — DATABASE DESIGN

### Minimum Tables

**`analyses`**
```
analysis_id     UUID PK
created_at      TIMESTAMP
input_type      ENUM(TEXT, IMAGE, AUDIO, URL)
language        VARCHAR(10)
risk_band       ENUM(LOW, MEDIUM, HIGH, CRITICAL)
risk_score      INT
scam_category   VARCHAR(50)
confidence      FLOAT
processing_ms   INT
model_used      VARCHAR(50)
```

**`indicators`**
```
indicator_id    UUID PK
analysis_id     UUID FK → analyses
signal_type     VARCHAR(50)
weight          ENUM(LOW, MEDIUM, HIGH, CRITICAL)
source          ENUM(RULE_ENGINE, LLM, BOTH)
```

**`feedback`**
```
feedback_id     UUID PK
analysis_id     UUID FK → analyses
user_rating     ENUM(CORRECT, INCORRECT, UNSURE)
comment         TEXT (optional, max 500 chars)
created_at      TIMESTAMP
```

**`knowledge_documents`** (RAG metadata — actual vectors in ChromaDB)
```
doc_id          UUID PK
title           VARCHAR(200)
category        VARCHAR(50)
source          VARCHAR(200)
reliability     FLOAT
language        VARCHAR(10)
last_verified   DATE
```

### What Stays in Config Files (Not DB)
- Scam taxonomy definitions (`scam_taxonomy.json`)
- Risk signal weights (`risk_weights.json`)
- Prompt templates (`prompts/`)
- Safe domain reference list (`trusted_domains.json`)
- Supported language list

---

## PART 18 — API DESIGN

### Endpoints

#### `POST /analyze/text`
```
Request:
  Content-Type: application/json
  Body: { "text": "string (max 5000 chars)", "language_hint": "en|hi|auto" }

Response:
  200: AnalysisResult (full JSON schema)
  400: { "error": "INVALID_INPUT", "detail": "..." }
  422: { "error": "INPUT_TOO_SHORT", "detail": "..." }
  429: { "error": "RATE_LIMIT_EXCEEDED" }
  500: { "error": "ANALYSIS_FAILED", "fallback": "..." }
```

#### `POST /analyze/image`
```
Request:
  Content-Type: multipart/form-data
  Body: { "file": <image>, "language_hint": "auto" }
  Limits: Max 10MB, formats: PNG/JPG/WEBP

Response:
  200: AnalysisResult (with ocr_quality field)
  400: { "error": "INVALID_FILE_FORMAT" }
  413: { "error": "FILE_TOO_LARGE" }
```

#### `POST /analyze/audio`
```
Request:
  Content-Type: multipart/form-data
  Body: { "file": <audio>, "language_hint": "auto" }
  Limits: Max 25MB, formats: WAV/MP3/WEBM, max 3 min

Response:
  200: AnalysisResult (with transcription_confidence field)
```

#### `POST /analyze/url`
```
Request:
  Content-Type: application/json
  Body: { "url": "string", "context": "optional surrounding message text" }

Response:
  200: AnalysisResult (URL-specific risk signals)
```

#### `GET /analysis/{id}`
```
Response: Stored AnalysisResult by analysis_id
```

#### `POST /feedback/{id}`
```
Request: { "rating": "CORRECT|INCORRECT|UNSURE", "comment": "..." }
Response: 200 OK
```

### Cross-Cutting Concerns
- **Rate Limiting**: 20 req/min per IP (text), 5 req/min (image/audio) — configurable
- **Auth**: None for hackathon; API key for production
- **CORS**: Restricted to frontend origin
- **Validation**: Pydantic models on all inputs
- **Errors**: Consistent error schema with `error_code` + `detail`
- **Timeouts**: 30s hard timeout on all analysis endpoints

---

## PART 19 — FRONTEND ARCHITECTURE

### Screen 1 — Landing Page
- Headline: "Is this a scam? Find out in seconds."
- Sub: Multilingual, multimodal, explainable AI
- CTA: "Analyze Now" → goes to Input screen
- Trust badges: "No data stored" · "Powered by AI" · "Free"

### Screen 2 — Input
- Tab selector: Text | Image | Voice | URL
- Text: Large textarea with character count
- Image: Drag-and-drop upload zone with preview
- Voice: Record button (browser Web Audio API) + upload option
- URL: Single input field + optional "paste surrounding message" textarea
- Submit button: "Analyze" with loading state

### Screen 3 — Analysis / Loading
- Animated progress with status messages:
  - "Reading your message..."
  - "Checking for suspicious patterns..."
  - "Consulting safety database..."
  - "Generating your safety report..."
- Never fake progress — tie to actual API stages

### Screen 4 — Risk Result (Primary Card)
- Large visual: RISK BAND in color (RED=CRITICAL, ORANGE=HIGH, YELLOW=MEDIUM, GREEN=LOW)
- Category badge
- One-line summary
- "See Evidence" + "What Should I Do?" CTAs

### Screen 5 — Evidence
- Expandable cards per indicator
- **Highlight the exact quote** from the original message
- Brief explanation per indicator
- Visual: Warning icon per indicator type

### Screen 6 — Recommended Action
- Ordered action list with checkboxes (user can mark done)
- Safe verification method (prominent)
- Report links (cybercrime.gov.in, 1930 helpline)

### Screen 7 — Feedback
- "Was this assessment helpful?"
- 3-option: ✅ Correct · ❌ Wrong · 🤔 Not sure
- Optional text comment
- Dismissible — don't block user

### UX Principles
- Mobile-first (primary users are on phones)
- High contrast, large text for elderly users
- No technical jargon in user-facing text
- Every screen accessible via back button
- No required login

---

## PART 20 — LIVE DEMO ARCHITECTURE

### Demo 1 — Text Analysis
Input: Known phishing SMS text (KYC fraud)
Expected: HIGH/CRITICAL, KYC_PHISHING, OTP indicator highlighted, clear recommended actions

### Demo 2 — Screenshot Analysis
Input: Screenshot of fake bank KYC WhatsApp message
Expected: OCR succeeds, same analysis as Demo 1, highlighted quote in image context

### Demo 3 — Voice Analysis
Input: Pre-recorded audio of scammer call script
Expected: Transcription shown, GOVT_IMPERSONATION detected, recommended actions

**Recommended to DEFINITELY demo: Demo 1 (Text) + Demo 2 (Screenshot)** — most reliable and visually impressive

### Demo Failure Mitigation

| Failure | Mitigation |
|---|---|
| API latency > 5s | Show realistic loading animation; set timeout expectations |
| LLM API down | Pre-cache demo results in JSON; "demo mode" flag returns cached response |
| OCR fails | Have fallback text pre-pasted; OCR failure is itself demonstrable |
| Microphone issues | Use pre-uploaded audio file instead of live recording |
| Network down | Local fallback server with mock responses |

**Demo Mode Design:**
- `/demo` flag in frontend uses hardcoded responses
- These responses are real analyses run during development — not fabricated
- State clearly: "Using pre-analyzed example" if in demo mode
- Do NOT fake results — use real prior analysis output

---

## PART 21 — TECH STACK DECISION

### Frontend

| Option | Pros | Cons | Suitability |
|---|---|---|---|
| React (Vite) | Fast, flexible, good DX | Slightly more setup | ✅ Best |
| Next.js | SSR, good for SEO | Overkill for SPA | OK |
| Vanilla JS | Zero deps | Slow dev for complex UI | No |

**Decision: React + Vite** — fast dev server, good component model, no SSR needed

### Backend

| Option | Pros | Cons | Suitability |
|---|---|---|---|
| FastAPI (Python) | Async, Pydantic, Python ecosystem | - | ✅ Best |
| Node/Express | Flexible | Worse AI library support | No |
| Django | Full-featured | Too heavy | No |

**Decision: FastAPI** — Python AI ecosystem, async, automatic OpenAPI docs, Pydantic validation

### LLM

| Option | Quality | Latency | Cost | Multimodal | Structured Output |
|---|---|---|---|---|---|
| Gemini 1.5 Pro | ★★★★★ | Medium | $ | ✅ | ✅ |
| GPT-4o | ★★★★★ | Medium | $$ | ✅ | ✅ |
| Claude 3.5 Sonnet | ★★★★★ | Low | $ | ✅ | ✅ |
| Gemini Flash 1.5 | ★★★★ | Low | $$ cheap | ❌ images | ✅ |

**Decision: Gemini 1.5 Pro** — native Hindi support, multimodal (can handle images directly), excellent structured output, Google ecosystem fits hackathon

### OCR

| Option | Quality | Cost | Setup |
|---|---|---|---|
| Google Vision API | ★★★★★ | $ per call | Easy |
| Tesseract (local) | ★★★ | Free | Easy |
| Gemini Vision | ★★★★★ | Same LLM call | Zero extra setup |

**Decision: Gemini 1.5 Pro Vision (same call)** — send image directly to Gemini for OCR + analysis in one call. Fallback to Tesseract for cost control.

### Speech-to-Text

| Option | Quality | Hindi Support | Cost |
|---|---|---|---|
| OpenAI Whisper (local) | ★★★★ | ✅ | Free |
| Google STT | ★★★★★ | ✅ | $ per min |
| Gemini Audio | ★★★★ | ✅ | Same LLM |

**Decision: OpenAI Whisper (local, medium model)** — free, good Hindi support, no API dependency

### Vector Database
**Decision: ChromaDB** — local, no server required, Python-native, perfect for hackathon

### Database
**Decision: SQLite** (via SQLAlchemy) for hackathon. Zero setup, file-based, upgrade path to PostgreSQL.

### Hosting
**Decision: Railway.app** — simple Python + frontend deployment, free tier, fast setup

### Monitoring
**Decision: Basic structured logging (Python logging + JSON format)** — no Datadog/Sentry for hackathon. Log to file, review manually.

---

### ✅ RECOMMENDED STACK

```
Frontend:  React + Vite + TypeScript
Backend:   FastAPI (Python 3.11+)
LLM:       Gemini 1.5 Pro (primary) / Flash (fallback)
OCR:       Gemini Vision (primary) / Tesseract (fallback)
STT:       Whisper (local, medium model)
RAG:       ChromaDB + sentence-transformers
Database:  SQLite → PostgreSQL (prod)
Hosting:   Railway.app (backend) + Vercel (frontend)
Monitoring: Structured JSON logging
```

---

## PART 22 — FOLDER STRUCTURE

```
scamX/                          ← repo root
│
├── frontend/                   ← React + Vite
│   ├── src/
│   │   ├── components/        ← RiskCard, EvidenceList, ActionList, InputTabs
│   │   ├── pages/             ← Landing, Input, Loading, Result, Feedback
│   │   ├── hooks/             ← useAnalysis, useRecorder
│   │   ├── api/               ← API client functions
│   │   ├── types/             ← TypeScript interfaces (AnalysisResult, etc.)
│   │   └── utils/             ← formatters, constants
│   └── public/
│
├── backend/
│   ├── api/
│   │   ├── routes/            ← analyze.py, feedback.py, health.py
│   │   └── middleware/        ← rate_limit.py, cors.py, error_handler.py
│   │
│   ├── services/
│   │   ├── ocr_service.py     ← image → text (Gemini Vision + Tesseract fallback)
│   │   ├── stt_service.py     ← audio → text (Whisper)
│   │   ├── url_service.py     ← URL metadata analysis
│   │   └── language_service.py ← language detection
│   │
│   ├── ai/
│   │   ├── llm_client.py      ← Gemini API wrapper
│   │   ├── prompt_builder.py  ← prompt assembly
│   │   ├── output_parser.py   ← JSON schema validation
│   │   └── analysis_pipeline.py ← orchestrates all AI components
│   │
│   ├── rag/
│   │   ├── vector_store.py    ← ChromaDB interface
│   │   ├── retriever.py       ← query + filter logic
│   │   └── indexer.py         ← knowledge base ingestion
│   │
│   ├── risk/
│   │   ├── rule_engine.py     ← deterministic signal detection
│   │   ├── risk_scorer.py     ← weighted aggregation
│   │   └── signal_definitions.py ← weights, thresholds
│   │
│   ├── safety/
│   │   ├── input_validator.py ← file validation, injection detection
│   │   ├── output_guard.py    ← hallucination detection, policy enforcement
│   │   └── privacy_filter.py  ← PII masking for logs
│   │
│   └── models/
│       ├── analysis.py        ← Pydantic models (request/response)
│       ├── database.py        ← SQLAlchemy models
│       └── schemas.py         ← shared type definitions
│
├── knowledge/
│   ├── scam_taxonomy.json     ← taxonomy definitions
│   ├── risk_weights.json      ← signal weight configuration
│   ├── trusted_domains.json   ← official domain reference
│   └── documents/             ← raw knowledge base documents (markdown)
│       ├── banking/
│       ├── kyc/
│       ├── government/
│       └── general_safety/
│
├── evaluation/
│   ├── test_cases/            ← labeled scam + legitimate messages
│   ├── eval_runner.py         ← automated evaluation
│   └── metrics.py             ← precision, recall, F1 per category
│
├── tests/
│   ├── unit/                  ← rule_engine, risk_scorer, parser tests
│   ├── integration/           ← API endpoint tests
│   └── security/              ← prompt injection, malicious input tests
│
├── docs/
│   ├── architecture.md        ← this document
│   ├── api_spec.md
│   └── knowledge_base_guide.md
│
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## PART 23 — OBSERVABILITY

### What to Track

```python
# Every analysis logs:
{
  "event": "analysis_complete",
  "analysis_id": "uuid",
  "timestamp": "ISO8601",
  "input_type": "TEXT",
  "language": "hi",
  "pipeline_stages": {
    "preprocessing_ms": 12,
    "language_detection_ms": 8,
    "rule_engine_ms": 15,
    "rag_retrieval_ms": 180,
    "llm_call_ms": 890,
    "risk_scoring_ms": 5,
    "total_ms": 1110
  },
  "risk_band": "HIGH",
  "category": "KYC_PHISHING",
  "confidence": 0.91,
  "signals_fired": 4,
  "rag_docs_retrieved": 3,
  "llm_tokens_used": 847,
  "errors": [],
  "ocr_quality": "N/A",
  "transcription_confidence": null
}
```

### What NOT to Log
- Raw user input text
- Quoted evidence verbatim
- Any PII

### Alerts (for production)
- LLM call failure rate > 5% → alert
- Average latency > 5s → alert
- OCR failure rate > 20% → alert
- Classification confidence < 0.4 > 30% of calls → model drift alert

---

## PART 24 — TESTING STRATEGY

### Unit Tests
- `rule_engine.py`: Test each signal against positive and negative examples
- `risk_scorer.py`: Test aggregation math, band thresholds
- `output_parser.py`: Test JSON validation against schema
- `url_service.py`: Test domain extraction, TLD detection, similarity scoring
- `privacy_filter.py`: Test PII masking accuracy

### Integration Tests
- Full pipeline: Text input → JSON response, validate schema
- Full pipeline: Image → OCR → analysis
- OCR failure path: corrupted image → uncertainty flag
- Rate limiting: 21st request returns 429
- Invalid input: oversized file, wrong format

### AI Evaluation Tests (Eval Matrix)

| Test Set | Input | Expected | Metric |
|---|---|---|---|
| Known scams (50 examples) | Labeled scam messages | HIGH/CRITICAL | Recall ≥ 0.90 |
| Legitimate messages (30) | Real bank/delivery msgs | LOW/MEDIUM | Precision ≥ 0.85 |
| Edge cases (20) | Ambiguous messages | UNCERTAIN band | Uncertainty rate |
| Multilingual (20) | Hindi/Hinglish scams | Correct category | Category F1 |
| Prompt injection (10) | Injection attempts | Rejected/safe output | 100% safe |

### Security Tests
- Prompt injection: Attempt to override system prompt via user text
- Oversized file: Test file size limits
- Malicious MIME: Send executable as image
- SSRF: Provide localhost/internal URLs
- XSS: Submit script tags in text input

---

## PART 25 — FAILURE MODES & GRACEFUL DEGRADATION

| Component | Failure | Response |
|---|---|---|
| OCR | Low quality / fails | Request user to paste text; flag `ocr_quality: LOW`; continue with partial if > 50% legible |
| LLM unavailable | API error / timeout | Return rule-engine-only result with `uncertainty: "AI analysis unavailable — showing pattern-based assessment only"` |
| LLM hallucination | Evidence not in input | Output validator rejects non-substring quotes; re-prompt or flag `evidence_verified: false` |
| URL analysis | WHOIS API down | Skip URL signals; proceed without URL risk contribution; flag in meta |
| STT | Poor transcription | Flag confidence, ask user to re-record or type; never silently proceed |
| RAG retrieval | ChromaDB error | Proceed without retrieval; LLM works from system prompt knowledge only; flag in output |
| Risk engine | Config parse error | Fall back to LLM-estimated risk band with `source: LLM_FALLBACK` warning |
| All AI down | Total failure | Return: "System temporarily unavailable. Please call 1930 for immediate scam assistance." |
| Malicious input | Injection attempt | Input validator rejects; log security event; return 400 |

---

## PART 26 — SCALABILITY ROADMAP

### 100 Users (Hackathon)
- Single FastAPI server, SQLite, local ChromaDB
- Synchronous processing
- Single LLM API key
- File-based logging

### 10,000 Users (Post-Hackathon)
- Switch to PostgreSQL + pgvector
- Add Redis for response caching (same message = same analysis, TTL 1h)
- Async job queue (Celery + Redis) for image/audio processing
- Multiple LLM API keys with rotation
- Move to managed hosting (Railway → Render → AWS)

### 1 Million Users (Production)
- Horizontal scaling: FastAPI behind load balancer
- CDN for frontend
- Dedicated vector DB (Pinecone or Weaviate)
- LLM routing: Fast pre-classifier → route simple cases to Flash, complex to Pro
- Read replicas for database
- Async processing queue for heavy inputs (image, audio)
- Rate limiting per user (authenticated) not just IP
- Model cost optimization: cache embeddings, batch similar queries
- Regional deployment (India datacenter for latency)
- A/B testing infrastructure for prompt improvements

---

## PART 27 — COST & LATENCY

### Latency Breakdown (estimated, single request)

| Stage | Estimated Time |
|---|---|
| Input validation | < 10ms |
| OCR (Gemini Vision) | 500–1500ms |
| STT (Whisper local) | 2000–5000ms |
| Language detection | < 20ms |
| Rule engine | < 20ms |
| RAG retrieval | 100–300ms |
| LLM call (Gemini Pro) | 800–2000ms |
| Risk scoring | < 10ms |
| **Total (text)** | **~1000–2500ms** |
| **Total (image)** | **~1500–3500ms** |
| **Total (audio)** | **~3000–7000ms** |

### Cost Reduction Strategies
1. **Caching**: Identical/near-identical inputs → cached result (Redis, TTL 1h)
2. **Two-stage routing**: Rule engine catches obvious high-confidence scams (OTP request + suspicious URL) → skip LLM for these
3. **Gemini Flash**: Use for simple text; Pro only for images and ambiguous cases
4. **Prompt optimization**: Minimize tokens — concise system prompt, no redundant context
5. **Embedding caching**: Cache RAG embeddings for common queries

---

## PART 28 — RECRUITER VALUE MAP

| Component | Skill Demonstrated | Recruiter Value |
|---|---|---|
| RAG (ChromaDB + retrieval) | Retrieval-augmented generation, vector search | ⭐⭐⭐⭐⭐ Very High |
| Structured LLM output (JSON schema) | LLM engineering, output parsing | ⭐⭐⭐⭐⭐ Very High |
| Risk engine (deterministic scoring) | AI + backend systems, responsible AI | ⭐⭐⭐⭐⭐ Very High |
| Gemini Vision OCR pipeline | Multimodal AI, computer vision | ⭐⭐⭐⭐ High |
| Whisper STT pipeline | Audio AI, speech processing | ⭐⭐⭐⭐ High |
| Prompt architecture (6 prompt types) | Prompt engineering, LLM systems design | ⭐⭐⭐⭐⭐ Very High |
| Explainability engine (quote grounding) | Responsible AI, XAI | ⭐⭐⭐⭐⭐ Very High |
| Multilingual handling | NLP, language-aware systems | ⭐⭐⭐⭐ High |
| Security layer (injection, SSRF) | Security engineering, responsible AI | ⭐⭐⭐⭐⭐ Very High |
| Eval framework (precision/recall) | ML engineering, evaluation | ⭐⭐⭐⭐⭐ Very High |
| Rule engine + LLM hybrid | Systems thinking, AI architecture | ⭐⭐⭐⭐⭐ Very High |
| FastAPI + async | Backend engineering | ⭐⭐⭐ Medium |
| React frontend | Frontend | ⭐⭐⭐ Medium |

> All skills listed above will be genuinely demonstrated by this implementation. No inflated claims.

---

## PART 29 — HACKATHON SCOPE

### 4-Hour Plan (Bare Minimum Demo)
- **Build**: Text input → Gemini LLM → basic JSON response → simple React UI showing risk band
- **Skip**: Image, audio, URL, RAG, rule engine, proper risk scoring, multilingual
- **Demo quality**: Can demo text analysis only
- **Risk**: Brittle, no fallbacks, no explainability depth

### 8-Hour Plan (Good Demo)
- **Build**: Text + Image (Gemini Vision OCR) → rule engine → LLM → risk engine → React UI with evidence display
- **Skip**: Audio, sophisticated RAG, URL analysis, multilingual UI
- **Demo quality**: Text + screenshot demo, proper evidence highlighting
- **Risk**: Image pipeline might need debugging

### 12-Hour Plan (Strong Demo)
- **Build**: Text + Image + basic RAG (10–20 docs) + rule engine + risk engine + full React UI (all screens)
- **Skip**: Audio (complex), full multilingual, comprehensive knowledge base
- **Demo quality**: 2-demo strong presentation, proper explainability
- **Risk**: RAG ingestion takes time to prepare

### 24-Hour Plan (Impressive Demo)
- **Build**: Full text + image + audio (Whisper) + URL analysis + RAG (50+ docs) + Hindi support + full UI + feedback
- **Skip**: Full evaluation framework, production-grade observability
- **Demo quality**: Full 3-demo presentation, multilingual, polished UI
- **Risk**: Audio integration and Hindi testing need time

### 36-Hour Plan (Submission-Ready)
- **Build**: Everything above + evaluation set + security tests + polished UI + demo mode + README
- **Risk**: Scope creep — stay focused

### Cut Priority (If Running Out of Time)
1. Cut first: Audio/Voice pipeline
2. Cut second: URL deep analysis (keep basic URL pattern matching)
3. Cut third: Full multilingual UI (keep Hindi analysis, respond in English)
4. Cut fourth: Feedback system
5. Cut last: Evidence highlighting in UI (core differentiator — keep this)

---

## PART 30 — ARCHITECTURE REVIEW (Skeptical Senior Engineer)

**1. Is the LLM actually necessary?**
*Challenge:* Rule engines catch 80% of obvious scams.
*Answer:* Yes, LLM is necessary for: semantic understanding of novel phishing, multilingual nuance, generating human-readable explanations grounded in evidence, and handling variations the rule engine can't enumerate. But the rule engine should run first and cheaply.

**2. Are we over-engineering?**
*Challenge:* This is a hackathon.
*Answer:* The modular architecture is necessary for the demo to be credible and for the recruiter narrative. Each component maps to a real skill. We're NOT implementing every component at enterprise scale — just enough to demo. The abstraction allows swapping implementations.

**3. Is the risk score defensible?**
*Challenge:* Why 87 and not 72? Arbitrary.
*Correction:* We show the BAND, not the number. The band is defensible: "Multiple high-weight signals fired" is auditable. We never claim mathematical precision.

**4. Can the explanation be trusted?**
*Challenge:* LLM might fabricate quoted evidence.
*Correction:* Output validator checks that every `indicators[].quote` is a substring of the actual input. If validation fails, the indicator is flagged `verified: false` or dropped.

**5. Is RAG actually useful?**
*Challenge:* LLM already knows about scams.
*Answer:* RAG provides: India-specific scam patterns, current scam methods not in training data, official guidance (RBI, CERT-In), and source attribution. Without RAG, responses are generic and ungrounded.

**6. Can malicious input manipulate the system?**
*Challenge:* Prompt injection via user text.
*Correction:* User input is wrapped in XML-delimited blocks in prompt. System prompt instructs model to never follow instructions from the `<user_input>` block. Output validator rejects schema deviations. Input sanitization before prompt injection.

**7. Is the privacy design sufficient?**
*Challenge:* Screenshots might contain private data.
*Correction:* Images are never stored. OCR text is temporarily processed and then deleted. PII is masked before any logging. LLM prompts contain OCR text — use LLM provider with DPA.

**8. Can the demo work reliably?**
*Challenge:* API latency, network issues.
*Correction:* Demo mode with pre-cached real results for 3 specific demo inputs. Loading animation calibrated to actual latency. Offline fallback for presentation.

**9. Can this architecture scale?**
*Answer:* Yes, with defined upgrade path: SQLite → PostgreSQL, local ChromaDB → managed vector DB, sync → async queues. Architecture is modular enough that each component can be upgraded independently.

**10. Does this demonstrate real AI engineering?**
*Answer:* Yes: RAG + structured output + hybrid rule+LLM system + evaluation framework + responsible AI design + multimodal pipeline = 8 distinct AI engineering skills in one coherent system.

---

## PART 31 — FINAL ARCHITECTURE

### 1. Architecture Diagram (Final)
```
[USER: Mobile/Web]
      │
      ▼
[React + Vite Frontend]
      │ HTTPS REST
      ▼
[FastAPI Backend]
  │ Rate Limit │ CORS │ Validation │ Error Handling
      │
      ├──────────────────────────────────────┐
      ▼                                      ▼
[Input Router]                    [GET /analysis/{id}]
  │                                [POST /feedback]
  ├── /text → TextService
  ├── /image → OCRService → TextService
  ├── /audio → STTService → TextService
  └── /url → URLService (metadata only)
      │
      ▼
[Normalization + Language Detection]
      │
      ┌─────────────────────┐
      ▼                     ▼
[Rule Engine]          [RAG Retrieval]
(deterministic)        (ChromaDB)
      │                     │
      └──────────┬──────────┘
                 ▼
         [LLM: Gemini 1.5 Pro]
         [Structured JSON Output]
                 │
                 ▼
         [Output Validator]
         (schema check + quote verification)
                 │
                 ▼
         [Risk Engine]
         (weighted signal aggregation → band)
                 │
                 ▼
         [Safety Policy Layer]
         (uncertainty injection, hallucination guard)
                 │
                 ▼
         [Structured Response → Frontend]
                 │
                 ▼
         [SQLite: analysis log]
```

### 2. Component List
1. React + Vite Frontend
2. FastAPI Backend
3. Input Routers (Text, OCR, STT, URL)
4. Normalization Service
5. Language Detection (fasttext)
6. Rule Engine (regex + patterns)
7. RAG Retriever (ChromaDB)
8. LLM Client (Gemini 1.5 Pro)
9. Prompt Builder
10. Output Parser + Validator
11. Risk Engine
12. Safety Policy Layer
13. Privacy Filter
14. SQLite Database
15. Structured JSON Response

### 3-10. Data/AI/RAG/Risk/Security/Frontend/API/Deployment Flows
(Detailed in respective parts above — all interconnected through structured JSON schema)

---

## PART 32 — FINAL DECISION TABLE

| Decision | Final Choice |
|---|---|
| Product | TRUSTX AI |
| Primary Input | Text (+ Image, Audio, URL) |
| AI Approach | Hybrid: Rule Engine + RAG + LLM + Deterministic Risk Engine |
| LLM | Gemini 1.5 Pro (Flash as fallback) |
| OCR | Gemini Vision (primary) / Tesseract (fallback) |
| Speech-to-Text | Whisper (local, medium model) |
| RAG | ChromaDB + sentence-transformers |
| Database | SQLite (hackathon) → PostgreSQL (prod) |
| Backend | FastAPI (Python 3.11+) |
| Frontend | React + Vite + TypeScript |
| Risk Engine | Deterministic weighted signal aggregation |
| Deployment | Railway.app (backend) + Vercel (frontend) |

### Feature Classification

🟢 **MUST BUILD**
- Text analysis pipeline (full end-to-end)
- Rule engine (signal detection)
- LLM integration with structured output
- Basic RAG (10–20 curated documents)
- Risk engine (weighted scoring → band)
- Evidence display with input quotes
- React UI: Input, Loading, Result, Evidence, Actions screens
- OCR (via Gemini Vision)
- Demo mode with cached results

🟡 **SHOULD BUILD**
- URL analysis (metadata only)
- Hindi/Hinglish support
- Feedback mechanism
- Scam taxonomy (full 12 categories)
- Knowledge base (50+ documents)
- Confidence + uncertainty display
- Reporting links (cybercrime.gov.in, 1930)

🔵 **OPTIONAL**
- Voice/audio pipeline (Whisper)
- Multilingual UI text
- Full evaluation framework
- Advanced URL analysis (WHOIS, Safe Browsing API)
- Animation polish on loading screen

🔴 **CUT**
- User authentication/accounts
- Push notifications
- WhatsApp bot integration
- Mobile app (React Native)
- Real-time collaborative analysis
- Enterprise admin dashboard
- Full production observability (Datadog, Sentry)
- Production database (keep SQLite for hackathon)
- CI/CD pipeline

---

## ARCHITECTURE LOCKED

TRUSTX AI is a multimodal, explainable scam detection system built on a hybrid AI architecture. Input arrives as text, image, audio, or URL. Each input type has a dedicated extraction pipeline (OCR via Gemini Vision, STT via Whisper, URL metadata analysis). Extracted text is normalized and processed in parallel by a deterministic rule engine (signal extraction) and a RAG retriever (ChromaDB knowledge base). The LLM (Gemini 1.5 Pro) receives rule signals, retrieved context, and normalized input; it returns structured JSON containing indicators with quoted evidence, explanations, category, and recommendations. A deterministic risk engine computes the final risk band from weighted signals. A safety policy layer validates output for hallucinations and policy compliance. The React frontend renders a risk card, evidence list with highlighted quotes, and ordered recommended actions.

---

## MVP LOCKED

1. Text input → full analysis pipeline → structured JSON response
2. Image input → Gemini Vision OCR → text pipeline
3. Rule engine detecting: OTP request, urgency, impersonation, suspicious URL patterns
4. Gemini 1.5 Pro with structured JSON output schema
5. ChromaDB RAG with 10–20 curated knowledge documents
6. Deterministic risk engine → LOW/MEDIUM/HIGH/CRITICAL band
7. Evidence display with verbatim input quotes
8. Recommended actions per scam category
9. React UI: Input tabs, loading states, result card, evidence, actions
10. Demo mode with 3 pre-cached real analyses

---

## WOW FEATURES LOCKED

1. **Live evidence highlighting** — visually highlight the exact suspicious phrases from the user's original message in the result view
2. **Voice input** — speak the call you received, get instant analysis
3. **Hinglish understanding** — handles mixed Hindi-English without translation loss
4. **"Verify safely" card** — proactively shows official contact details for impersonated organization (SBI → sbi.co.in, SBI helpline)
5. **Side-by-side screenshot view** — original screenshot + annotated suspicious zones

---

## TECH STACK LOCKED

```
Frontend:  React + Vite + TypeScript
Backend:   FastAPI (Python 3.11+)
LLM:       Gemini 1.5 Pro
OCR:       Gemini Vision (same API call)
STT:       OpenAI Whisper (local)
RAG:       ChromaDB + all-MiniLM-L6-v2
DB:        SQLite (SQLAlchemy)
Hosting:   Railway + Vercel
```

---

## BIGGEST TECHNICAL RISKS

1. **LLM latency under demo pressure** — Gemini Pro can be 2–5s; have Flash fallback + demo cache ready
2. **Evidence hallucination** — LLM fabricates quotes not in input; mitigated by output validator but needs thorough testing
3. **OCR quality on real screenshots** — Compressed WhatsApp screenshots degrade OCR; need test with real examples early
4. **RAG relevance** — If knowledge base is too small or poorly indexed, RAG adds noise; test retrieval quality before LLM integration
5. **Prompt injection via malicious input** — A sophisticated attacker can attempt to override the system prompt; needs early security testing, not as an afterthought

---

## NEXT STEP

**Step 2 Objective: Knowledge Base Construction + Prompt Engineering**

1. Finalize the `scam_taxonomy.json` with all 12 categories, indicators, and examples
2. Write 20–30 curated knowledge documents for ChromaDB (banking, KYC, government impersonation priorities first)
3. Design and write the 6 prompt templates (analysis, evidence extraction, explanation, safety advice, multilingual, uncertainty)
4. Build the `rule_engine.py` with signal definitions and regex patterns
5. Define the complete Pydantic output schema in code
6. Test prompts manually with 5–10 real scam examples before writing backend code

Do not start writing API routes until prompts are tested and knowledge base is indexed.
