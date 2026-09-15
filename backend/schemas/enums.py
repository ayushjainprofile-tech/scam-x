"""
SCAMX — All enumerations.
Lock these before coding any other module.
Team agreement required to add/change values mid-hackathon.
"""
from enum import Enum


class Modality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    URL = "url"


class RiskBand(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNCERTAIN = "UNCERTAIN"


class SignalSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UncertaintyLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class EvidenceType(str, Enum):
    DIRECT_QUOTE = "DIRECT_QUOTE"   # Exact substring from source
    INFERRED = "INFERRED"           # Semantic inference — lower confidence
    STRUCTURAL = "STRUCTURAL"       # Based on URL pattern, QR presence, etc.


class DetectionSource(str, Enum):
    RULE = "rule"
    LLM = "llm"
    HYBRID = "hybrid"
    URL_ENGINE = "url_engine"


class ScamCategory(str, Enum):
    BANKING = "BANKING"
    KYC = "KYC"
    PHISHING = "PHISHING"
    PAYMENT = "PAYMENT"
    JOB = "JOB"
    INVESTMENT = "INVESTMENT"
    DELIVERY = "DELIVERY"
    LOTTERY = "LOTTERY"
    GOVERNMENT_IMPERSONATION = "GOVERNMENT_IMPERSONATION"
    CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"
    ACCOUNT_TAKEOVER = "ACCOUNT_TAKEOVER"
    REMOTE_ACCESS = "REMOTE_ACCESS"
    LOAN = "LOAN"
    ROMANCE = "ROMANCE"
    CRYPTO = "CRYPTO"
    OTHER = "OTHER"
    UNCERTAIN = "UNCERTAIN"


class ActionType(str, Enum):
    DO_NOT = "DO_NOT"
    DO = "DO"
    VERIFY = "VERIFY"
    REPORT = "REPORT"
    EMERGENCY = "EMERGENCY"


class UserState(str, Enum):
    PREVENTION = "prevention"
    INCIDENT_RESPONSE = "incident_response"
