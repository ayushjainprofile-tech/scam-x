"""
SCAMX — Global Constants
Signal weights, thresholds, interaction multipliers.
Change here without touching engine logic.
"""

from backend.schemas.enums import SignalSeverity, RiskBand

# ── Signal severity → numeric weight ───────────────────────────────────────
SEVERITY_WEIGHTS: dict[str, float] = {
    SignalSeverity.CRITICAL: 4.0,
    SignalSeverity.HIGH: 3.0,
    SignalSeverity.MEDIUM: 2.0,
    SignalSeverity.LOW: 1.0,
}

# ── Risk band thresholds (applied to computed base score) ──────────────────
RISK_THRESHOLDS: dict[str, float] = {
    RiskBand.CRITICAL: 18.0,
    RiskBand.HIGH: 10.0,
    RiskBand.MEDIUM: 5.0,
    RiskBand.LOW: 0.0,
}

# ── Interaction multipliers (frozenset of signal IDs → multiplier) ─────────
# Applied when ALL signals in the set are present simultaneously.
INTERACTION_MULTIPLIERS: list[tuple[frozenset, float]] = [
    # Classic KYC/OTP scam
    (frozenset({"SIG_OTP_REQUEST", "SIG_URGENCY", "SIG_BANK_IMPERSONATION"}), 2.2),
    # Remote access — near-always malicious
    (frozenset({"SIG_SCREEN_SHARE"}), 2.5),
    (frozenset({"SIG_REMOTE_SOFTWARE"}), 2.5),
    # Advance fee fraud
    (frozenset({"SIG_PAYMENT_REQUEST", "SIG_ADVANCE_FEE"}), 1.8),
    # Prize + fee combination
    (frozenset({"SIG_LOTTERY", "SIG_ADVANCE_FEE"}), 1.9),
    # Secrecy amplifies credential theft
    (frozenset({"SIG_SECRECY", "SIG_OTP_REQUEST"}), 1.7),
    # URL phishing confirmation
    (frozenset({"SIG_SUSPICIOUS_URL", "SIG_LOGIN_PAGE"}), 1.6),
    # Extortion pattern
    (frozenset({"SIG_THREAT", "SIG_PAYMENT_REQUEST", "SIG_AUTHORITY"}), 2.0),
    # Investment + guarantee
    (frozenset({"SIG_UNREALISTIC_RETURN", "SIG_GUARANTEED_PROFIT"}), 1.8),
    # Government + payment
    (frozenset({"SIG_GOVT_IMPERSONATION", "SIG_PAYMENT_REQUEST"}), 2.0),
]

# ── Known trusted domains (Tier 1) ─────────────────────────────────────────
TRUSTED_DOMAINS: set[str] = {
    "sbi.co.in", "onlinesbi.com", "sbionline.com",
    "hdfcbank.com", "netbanking.hdfcbank.com",
    "icicibank.com", "axisbank.com", "kotak.com",
    "rbi.org.in", "npci.org.in", "upi.npci.org.in",
    "cybercrime.gov.in", "mha.gov.in", "meity.gov.in",
    "trai.gov.in", "sebi.gov.in", "irdai.gov.in",
    "incometax.gov.in", "gstn.org.in",
    "google.com", "apple.com", "microsoft.com",
    "amazon.in", "flipkart.com", "paytm.com",
    "phonepe.com", "gpay.google.com", "bhimupi.org.in",
}

# ── Known URL shorteners ───────────────────────────────────────────────────
URL_SHORTENERS: set[str] = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "short.link", "cutt.ly", "rb.gy", "buff.ly", "dlvr.it",
    "tiny.cc", "is.gd", "soo.gd", "clicky.me",
}

# ── Suspicious TLDs ────────────────────────────────────────────────────────
SUSPICIOUS_TLDS: set[str] = {
    "xyz", "click", "tk", "ml", "ga", "cf", "gq",
    "top", "win", "loan", "work", "date", "review",
    "download", "racing", "webcam", "party", "stream",
}

# ── Known brand domains for lookalike detection ────────────────────────────
BRAND_DOMAINS: list[str] = [
    "sbi.co.in", "hdfcbank.com", "icicibank.com", "axisbank.com",
    "rbi.org.in", "npci.org.in", "amazon.in", "flipkart.com",
    "paytm.com", "phonepe.com", "google.com", "apple.com",
]

# ── Private / reserved IP ranges (reject URL analysis for these) ───────────
PRIVATE_IP_PATTERNS: list[str] = [
    r"^10\.", r"^172\.(1[6-9]|2[0-9]|3[0-1])\.", r"^192\.168\.",
    r"^127\.", r"^0\.", r"^169\.254\.", r"^::1$", r"^localhost$",
]

# ── Suspicious URL path segments ───────────────────────────────────────────
SUSPICIOUS_PATH_SEGMENTS: set[str] = {
    "otp", "verify", "kyc", "login", "signin", "authenticate",
    "confirm", "update-account", "secure", "account-verify",
    "bank-verify", "reward", "claim-prize", "payment-verify",
}

# ── LLM confidence minimum before accepting LLM signal ────────────────────
LLM_MIN_CONFIDENCE: float = 0.5

# ── OCR confidence threshold below which signals are penalized ─────────────
OCR_LOW_CONFIDENCE_THRESHOLD: float = 0.6

# ── Minimum signal count to exit UNCERTAIN band ───────────────────────────
MIN_SIGNALS_FOR_ASSESSMENT: int = 1

# ── Max follow-up questions per session ────────────────────────────────────
MAX_FOLLOW_UP_QUESTIONS: int = 2
