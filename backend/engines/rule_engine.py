"""
SCAMX — Rule Engine
Deterministic regex + keyword detection. Zero LLM dependency.
Every rule is independently testable.

Design principles:
  - Rules detect PATTERNS, not isolated words.
  - Context matters: OTP delivery ≠ OTP sharing request.
  - Each rule returns a Signal with confidence and evidence.
  - Rules are the fastest path: < 10ms for any input.
"""

import re
import uuid
from dataclasses import dataclass, field
from typing import Optional
from backend.schemas.signals import Signal, Evidence
from backend.schemas.enums import SignalSeverity, DetectionSource, EvidenceType


# ── Rule definition ─────────────────────────────────────────────────────────

@dataclass
class Rule:
    signal_id: str
    category: str
    severity: SignalSeverity
    confidence: float
    false_positive_risk: str
    # Patterns that MUST match for this rule to fire
    match_patterns: list[str] = field(default_factory=list)
    # If any of these patterns match, the rule is SUPPRESSED (false-positive guard)
    suppression_patterns: list[str] = field(default_factory=list)
    # Compiled regexes (populated at load time)
    _compiled_match: list[re.Pattern] = field(default_factory=list, repr=False)
    _compiled_suppress: list[re.Pattern] = field(default_factory=list, repr=False)

    def compile(self) -> "Rule":
        self._compiled_match = [
            re.compile(p, re.IGNORECASE | re.UNICODE) for p in self.match_patterns
        ]
        self._compiled_suppress = [
            re.compile(p, re.IGNORECASE | re.UNICODE) for p in self.suppression_patterns
        ]
        return self

    def evaluate(self, text: str) -> Optional[tuple[bool, str]]:
        """
        Returns (matched, evidence_span) or None if no match.
        Suppression patterns prevent false positives.
        """
        # Check suppression first
        for sup in self._compiled_suppress:
            if sup.search(text):
                return None  # Suppressed — likely a legitimate message

        # Check match patterns
        for pat in self._compiled_match:
            m = pat.search(text)
            if m:
                # Return the matched span as evidence
                span = text[max(0, m.start() - 20): m.end() + 30].strip()
                return True, span

        return None


# ── Rule definitions ─────────────────────────────────────────────────────────

RULES: list[Rule] = [

    # ═══════════════════════════════════════════════════════════
    # CREDENTIAL THEFT
    # ═══════════════════════════════════════════════════════════

    Rule(
        signal_id="SIG_OTP_REQUEST",
        category="CREDENTIAL_THEFT",
        severity=SignalSeverity.CRITICAL,
        confidence=0.92,
        false_positive_risk="LOW",
        match_patterns=[
            # Asking user to SHARE/SEND/GIVE OTP (outbound request)
            r"\b(share|send|give|tell|provide|enter|submit|bata|dena|bhejo|batao)\b.{0,30}\b(otp|one.?time.?password|verification.?code|pin)\b",
            r"\b(otp|one.?time.?password)\b.{0,20}\b(share|send|give|tell|provide|batao|bhejo)\b",
            r"otp.{0,10}(immediately|abhi|jaldi|urgently|now)",
        ],
        suppression_patterns=[
            # OTP delivered TO user (inbound) — not a scam
            r"your otp (is|:)\s*\d{4,8}",
            r"otp sent to your",
            r"otp for .{0,30}(login|transaction|verification)",
            r"do not share.{0,30}otp",  # Bank's own warning in delivery message
        ],
    ).compile(),

    Rule(
        signal_id="SIG_PIN_REQUEST",
        category="CREDENTIAL_THEFT",
        severity=SignalSeverity.CRITICAL,
        confidence=0.95,
        false_positive_risk="VERY_LOW",
        match_patterns=[
            r"\b(share|send|give|tell|provide|enter|submit)\b.{0,20}\b(atm.?pin|debit.?pin|credit.?pin|your.?pin|4.?digit.?pin)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_CVV_REQUEST",
        category="CREDENTIAL_THEFT",
        severity=SignalSeverity.CRITICAL,
        confidence=0.97,
        false_positive_risk="VERY_LOW",
        match_patterns=[
            r"\b(share|send|give|tell|provide|enter|submit)\b.{0,20}\b(cvv|cvc|card.?verification)\b",
            r"\bcvv\b.{0,20}\b(number|code|verify|share|send)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_PASSWORD_REQUEST",
        category="CREDENTIAL_THEFT",
        severity=SignalSeverity.CRITICAL,
        confidence=0.95,
        false_positive_risk="VERY_LOW",
        match_patterns=[
            r"\b(share|send|give|tell|provide)\b.{0,20}\b(password|passcode|login.?id|username.?and.?password)\b",
        ],
    ).compile(),

    # ═══════════════════════════════════════════════════════════
    # SOCIAL ENGINEERING
    # ═══════════════════════════════════════════════════════════

    Rule(
        signal_id="SIG_URGENCY",
        category="SOCIAL_ENGINEERING",
        severity=SignalSeverity.MEDIUM,
        confidence=0.72,
        false_positive_risk="HIGH",
        match_patterns=[
            r"\b(immediately|urgent|urgently|right now|within.{0,10}(hour|minute|24|48)|last chance|final warning|expire|expiring|jaldi|abhi|turant)\b",
            r"\b(account.{0,20}(block|suspend|close|freeze).{0,20}(hour|minute|today|soon|immediately))\b",
            r"\b(act now|respond immediately|do not delay|time.sensitive)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_THREAT",
        category="SOCIAL_ENGINEERING",
        severity=SignalSeverity.HIGH,
        confidence=0.82,
        false_positive_risk="MEDIUM",
        match_patterns=[
            r"\b(legal action|police complaint|fir|arrest|arrested|case registered|cyber crime|money laundering)\b.{0,40}\b(against you|against your|aapke khilaf)\b",
            r"\b(will be arrested|will face|criminal case|warrant|summon)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_SECRECY",
        category="SOCIAL_ENGINEERING",
        severity=SignalSeverity.HIGH,
        confidence=0.90,
        false_positive_risk="VERY_LOW",
        match_patterns=[
            r"\b(do not (tell|share|inform|discuss|mention)|keep (this|it) (secret|confidential|between us)|kisi ko mat batao|secret rakho)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_AUTHORITY",
        category="SOCIAL_ENGINEERING",
        severity=SignalSeverity.MEDIUM,
        confidence=0.75,
        false_positive_risk="HIGH",
        match_patterns=[
            r"\b(rbi|reserve bank|sebi|npci|trai|income tax|cbi|ed |enforcement directorate|cyber crime cell|cybercrime police)\b",
        ],
    ).compile(),

    # ═══════════════════════════════════════════════════════════
    # IMPERSONATION
    # ═══════════════════════════════════════════════════════════

    Rule(
        signal_id="SIG_BANK_IMPERSONATION",
        category="IMPERSONATION",
        severity=SignalSeverity.HIGH,
        confidence=0.78,
        false_positive_risk="HIGH",
        match_patterns=[
            r"\b(calling|speaking|writing).{0,20}(from|on behalf of).{0,20}(sbi|hdfc|icici|axis|kotak|punjab national|pnb|canara|bank of baroda|bob|yes bank|idbi)\b",
            r"\b(sbi|hdfc|icici|axis).{0,20}(fraud|security|kyc|verification|helpdesk|customer care)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_GOVT_IMPERSONATION",
        category="IMPERSONATION",
        severity=SignalSeverity.HIGH,
        confidence=0.82,
        false_positive_risk="MEDIUM",
        match_patterns=[
            r"\b(calling|speaking).{0,20}(from|on behalf of).{0,20}(trai|rbi|sebi|income tax|cbi|ed|enforcement|police|cybercrime)\b",
            r"trai.{0,30}(suspend|block|disconnect).{0,30}(number|sim|mobile)",
            r"income tax.{0,30}(notice|action|raid|recovery)",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_SUPPORT_IMPERSONATION",
        category="IMPERSONATION",
        severity=SignalSeverity.MEDIUM,
        confidence=0.76,
        false_positive_risk="MEDIUM",
        match_patterns=[
            r"\b(amazon|flipkart|swiggy|zomato|paytm|phonepe|google pay|gpay).{0,30}(customer (care|support|service)|helpdesk|refund)\b",
        ],
    ).compile(),

    # ═══════════════════════════════════════════════════════════
    # FINANCIAL MANIPULATION
    # ═══════════════════════════════════════════════════════════

    Rule(
        signal_id="SIG_ADVANCE_FEE",
        category="FINANCIAL_MANIPULATION",
        severity=SignalSeverity.HIGH,
        confidence=0.86,
        false_positive_risk="LOW",
        match_patterns=[
            r"\b(pay|deposit|transfer).{0,30}(fee|charge|tax|processing|registration|security deposit).{0,30}(to receive|to claim|to get|to collect|to release)\b",
            r"\b(processing fee|registration fee|delivery charge|customs duty|security deposit).{0,30}(₹|rs|inr|\d+)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_REFUND_MANIPULATION",
        category="FINANCIAL_MANIPULATION",
        severity=SignalSeverity.HIGH,
        confidence=0.84,
        false_positive_risk="LOW",
        match_patterns=[
            r"\b(refund|cashback).{0,30}(scan|qr|upi|transfer|send).{0,20}(to receive|to process|for verification)\b",
            r"refund.{0,20}(share your upi|scan this qr|enter account)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_QR_PAYMENT",
        category="FINANCIAL_MANIPULATION",
        severity=SignalSeverity.HIGH,
        confidence=0.80,
        false_positive_risk="MEDIUM",
        match_patterns=[
            r"\b(scan.{0,15}(this|the).{0,15}(qr|code)|qr code.{0,20}(to pay|to verify|to complete|for refund))\b",
        ],
        suppression_patterns=[
            # Legitimate merchant payment context
            r"\b(pay (for|at|to)|payment (for|at))\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_UPI_REQUEST",
        category="FINANCIAL_MANIPULATION",
        severity=SignalSeverity.MEDIUM,
        confidence=0.74,
        false_positive_risk="MEDIUM",
        match_patterns=[
            r"\b(share|send|give|provide).{0,20}(your|upi id|upi number|vpa)\b",
            r"\b(upi id|upi number|vpa).{0,20}(to receive|to process|for refund)\b",
        ],
    ).compile(),

    # ═══════════════════════════════════════════════════════════
    # REMOTE ACCESS
    # ═══════════════════════════════════════════════════════════

    Rule(
        signal_id="SIG_SCREEN_SHARE",
        category="REMOTE_ACCESS",
        severity=SignalSeverity.CRITICAL,
        confidence=0.95,
        false_positive_risk="LOW",
        match_patterns=[
            r"\b(anydesk|teamviewer|quick support|rustdesk|ultraviewer|remote desktop|screen share|screen.?sharing)\b.{0,30}\b(install|download|open|share|allow|grant|access)\b",
            r"\b(install|download).{0,30}\b(anydesk|teamviewer|quick support|rustdesk)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_REMOTE_SOFTWARE",
        category="REMOTE_ACCESS",
        severity=SignalSeverity.CRITICAL,
        confidence=0.94,
        false_positive_risk="LOW",
        match_patterns=[
            r"\b(give (us|me|them) (access|control)|allow (remote|access)|grant.{0,15}permission.{0,15}(device|phone|computer))\b",
            r"\b(install this app.{0,30}(to fix|to verify|to help|to update))\b",
        ],
    ).compile(),

    # ═══════════════════════════════════════════════════════════
    # PHISHING / SUSPICIOUS URL
    # ═══════════════════════════════════════════════════════════

    Rule(
        signal_id="SIG_ACCOUNT_SUSPENSION",
        category="PHISHING",
        severity=SignalSeverity.HIGH,
        confidence=0.80,
        false_positive_risk="MEDIUM",
        match_patterns=[
            r"\b(account.{0,30}(suspend|block|close|freeze|deactivate|restrict)).{0,50}(click|verify|update|login|link)\b",
            r"\b(to (avoid|prevent).{0,30}(block|suspend|close|restrict)).{0,30}(click|verify|update)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_LOGIN_PAGE",
        category="PHISHING",
        severity=SignalSeverity.HIGH,
        confidence=0.82,
        false_positive_risk="MEDIUM",
        match_patterns=[
            r"\b(login|sign in|log in).{0,30}(here|now|to verify|to continue|to update|to confirm)\b",
            r"\b(enter.{0,20}(credentials|username|password|login id)).{0,30}(verify|confirm|update)\b",
        ],
    ).compile(),

    # ═══════════════════════════════════════════════════════════
    # REWARD / INVESTMENT SCAMS
    # ═══════════════════════════════════════════════════════════

    Rule(
        signal_id="SIG_LOTTERY",
        category="REWARD",
        severity=SignalSeverity.HIGH,
        confidence=0.90,
        false_positive_risk="LOW",
        match_patterns=[
            r"\b(you (have|'ve).{0,20}(won|win|selected|chosen|picked)).{0,30}(prize|lottery|lucky draw|reward|cash|lakh|crore)\b",
            r"\b(congratulations.{0,30}(won|winner|selected)).{0,30}(prize|lottery|reward)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_UNREALISTIC_RETURN",
        category="INVESTMENT",
        severity=SignalSeverity.HIGH,
        confidence=0.88,
        false_positive_risk="LOW",
        match_patterns=[
            r"\b(guaranteed|100%.{0,20}return|double.{0,20}money|triple.{0,20}investment|assured return)\b",
            r"\b(\d{2,3}%.{0,20}return|profit (per|in) (day|week)|daily (income|earning) of ₹)\b",
        ],
    ).compile(),

    # ═══════════════════════════════════════════════════════════
    # JOB SCAM
    # ═══════════════════════════════════════════════════════════

    Rule(
        signal_id="SIG_JOB_UPFRONT",
        category="JOB_SCAM",
        severity=SignalSeverity.HIGH,
        confidence=0.85,
        false_positive_risk="LOW",
        match_patterns=[
            r"\b(work from home|wfh|part.?time).{0,50}(pay|deposit|fee|registration|₹\s*\d+)\b",
            r"\b(job offer|hiring|vacancy).{0,50}(registration fee|security deposit|pay ₹|advance)\b",
            r"\b(₹\s*\d+\,?\d+.{0,15}(per|a|every).{0,10}(day|week|month)).{0,30}(no experience|anyone|immediate)\b",
        ],
    ).compile(),

    # ═══════════════════════════════════════════════════════════
    # KYC SCAM
    # ═══════════════════════════════════════════════════════════

    Rule(
        signal_id="SIG_UTILITY_DISCONNECTION",
        category="UTILITY_SCAM",
        severity=SignalSeverity.CRITICAL,
        confidence=0.96,
        false_positive_risk="VERY_LOW",
        match_patterns=[
            r"\b(electricity|power|light|connection|meter).{0,40}\b(disconnect|disconnected|cut|suspended|tonight|night)\b",
            r"\b(bill|payment).{0,30}(unpaid|pending|due).{0,30}(contact|call|update|officer|apk)\b",
            r"\b(power officer|electricity officer|bill officer)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_PACKAGE_COURIER",
        category="COURIER_SCAM",
        severity=SignalSeverity.HIGH,
        confidence=0.88,
        false_positive_risk="LOW",
        match_patterns=[
            r"\b(customs|courier|parcel|package|fedex|delhivery|dhl|post).{0,40}\b(held|seized|illegal|narcotics|drugs|pay|address)\b",
            r"\b(parcel|package).{0,30}(update address|confirm delivery|pay customs)\b",
        ],
    ).compile(),

    Rule(
        signal_id="SIG_KYC_URGENCY",
        category="KYC",
        severity=SignalSeverity.HIGH,
        confidence=0.86,
        false_positive_risk="MEDIUM",
        match_patterns=[
            r"\b(kyc.{0,30}(pending|update|verify|expire|incomplete|urgent|immediately|failed))\b",
            r"\b(update.{0,20}kyc.{0,20}(to avoid|prevent|or).{0,20}(block|suspend|close))\b",
            r"\b(pan|aadhaar|account).{0,30}(linked|update|verify).{0,20}(link|click|here)\b",
        ],
    ).compile(),
]


# ── Engine class ─────────────────────────────────────────────────────────────

class RuleEngine:
    """
    Fast, deterministic signal detection.
    No network calls. No LLM. Runs in < 10ms.
    """

    def __init__(self, rules: list[Rule] = RULES) -> None:
        self._rules = rules

    def detect(self, text: str, source_modality: str = "text") -> tuple[list[Signal], list[Evidence]]:
        """
        Run all rules against the text.
        Returns (signals, evidence) — both empty lists if no rules fire.
        """
        signals: list[Signal] = []
        evidence_list: list[Evidence] = []

        for rule in self._rules:
            result = rule.evaluate(text)
            if result is None:
                continue

            _, evidence_span = result
            signal_id = f"{id(rule)}"  # unique per rule instance

            sig = Signal(
                signal_id=rule.signal_id,
                category=rule.category,
                severity=rule.severity,
                confidence=rule.confidence,
                detection_source=DetectionSource.RULE,
                false_positive_risk=rule.false_positive_risk,
            )

            evd = Evidence(
                evidence_id=str(uuid.uuid4()),
                signal_id=rule.signal_id,
                evidence_span=evidence_span[:200],  # Cap span length
                source_modality=source_modality,
                evidence_type=EvidenceType.DIRECT_QUOTE,
                confidence=rule.confidence,
                verified_in_source=True,  # Rule match is always from source text
            )

            signals.append(sig)
            evidence_list.append(evd)

        return signals, evidence_list
