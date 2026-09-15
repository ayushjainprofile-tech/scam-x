"""
SCAMX — URL Processor (Static Analysis Only)
NEVER makes HTTP requests to suspicious URLs.
NEVER executes JavaScript.
NEVER follows redirects to unknown domains.
"""

import re
import uuid
import tldextract
from Levenshtein import distance as levenshtein_distance
from backend.schemas.signals import Signal, Evidence
from backend.schemas.enums import SignalSeverity, DetectionSource, EvidenceType
from backend.utils.constants import (
    TRUSTED_DOMAINS, URL_SHORTENERS, SUSPICIOUS_TLDS,
    BRAND_DOMAINS, PRIVATE_IP_PATTERNS, SUSPICIOUS_PATH_SEGMENTS,
)

_PRIVATE_IP_REGEX = [re.compile(p) for p in PRIVATE_IP_PATTERNS]


class URLProcessor:
    """
    Safe static URL analysis.
    Analyzes URL structure only — no network calls.
    """

    def analyze(self, url: str) -> tuple[list[Signal], list[Evidence]]:
        signals: list[Signal] = []
        evidence_list: list[Evidence] = []

        # Reject private/localhost URLs immediately
        domain_raw = self._extract_domain(url)
        for pat in _PRIVATE_IP_REGEX:
            if pat.match(domain_raw):
                return [], []  # Private IP — don't analyze, don't flag

        # Parse TLD info
        extracted = tldextract.extract(url)
        registered_domain = f"{extracted.domain}.{extracted.suffix}"
        full_domain = f"{extracted.subdomain}.{registered_domain}".lstrip(".")
        tld = extracted.suffix.lower()

        # ── Check: Known trusted domain ─────────────────────────────────────
        if registered_domain in TRUSTED_DOMAINS or full_domain in TRUSTED_DOMAINS:
            return [], []  # Whitelisted — clean

        # ── Check: Known URL shortener ───────────────────────────────────────
        if registered_domain in URL_SHORTENERS:
            sig, evd = self._make_signal_evidence(
                "SIG_URL_SHORTENER", "PHISHING",
                SignalSeverity.MEDIUM, 0.80,
                url, "URL shortener hides the actual destination"
            )
            signals.append(sig)
            evidence_list.append(evd)

        # ── Check: IP address URL ────────────────────────────────────────────
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain_raw):
            sig, evd = self._make_signal_evidence(
                "SIG_IP_URL", "PHISHING",
                SignalSeverity.HIGH, 0.88,
                url, "URL uses an IP address instead of a domain name"
            )
            signals.append(sig)
            evidence_list.append(evd)

        # ── Check: Suspicious TLD ────────────────────────────────────────────
        if tld in SUSPICIOUS_TLDS:
            sig, evd = self._make_signal_evidence(
                "SIG_SUSPICIOUS_TLD", "PHISHING",
                SignalSeverity.MEDIUM, 0.75,
                url, f"Domain uses suspicious TLD: .{tld}"
            )
            signals.append(sig)
            evidence_list.append(evd)

        # ── Check: Lookalike domain (brand impersonation) ─────────────────────
        for brand in BRAND_DOMAINS:
            brand_extracted = tldextract.extract(brand)
            brand_domain_only = brand_extracted.domain
            if brand_domain_only and extracted.domain != brand_domain_only:
                dist = levenshtein_distance(extracted.domain.lower(), brand_domain_only.lower())
                if 0 < dist <= 2:
                    sig, evd = self._make_signal_evidence(
                        "SIG_LOOKALIKE_DOMAIN", "PHISHING",
                        SignalSeverity.HIGH, 0.90,
                        url, f"Domain '{registered_domain}' closely resembles '{brand}'"
                    )
                    signals.append(sig)
                    evidence_list.append(evd)
                    break

        # ── Check: Brand name in subdomain with suspicious root ───────────────
        if extracted.subdomain:
            for brand in BRAND_DOMAINS:
                b_ext = tldextract.extract(brand)
                if b_ext.domain in extracted.subdomain.lower() and registered_domain not in TRUSTED_DOMAINS:
                    sig, evd = self._make_signal_evidence(
                        "SIG_SUBDOMAIN_IMPERSONATION", "PHISHING",
                        SignalSeverity.HIGH, 0.87,
                        url, f"Brand name '{b_ext.domain}' appears in subdomain of untrusted domain"
                    )
                    signals.append(sig)
                    evidence_list.append(evd)
                    break

        # ── Check: Suspicious path segments ─────────────────────────────────
        url_lower = url.lower()
        for segment in SUSPICIOUS_PATH_SEGMENTS:
            if f"/{segment}" in url_lower or f"/{segment}?" in url_lower:
                sig, evd = self._make_signal_evidence(
                    "SIG_SUSPICIOUS_URL", "PHISHING",
                    SignalSeverity.HIGH, 0.82,
                    url, f"URL path contains suspicious segment: /{segment}"
                )
                signals.append(sig)
                evidence_list.append(evd)
                break  # Only flag once

        # Mark overall URL as suspicious if any signals detected
        if signals and not any(s.signal_id == "SIG_SUSPICIOUS_URL" for s in signals):
            sig, evd = self._make_signal_evidence(
                "SIG_SUSPICIOUS_URL", "PHISHING",
                SignalSeverity.MEDIUM, 0.78,
                url, "URL has characteristics associated with scam messages"
            )
            signals.append(sig)
            evidence_list.append(evd)

        return signals, evidence_list

    def _extract_domain(self, url: str) -> str:
        url = re.sub(r"https?://", "", url)
        return url.split("/")[0].split(":")[0]

    def _make_signal_evidence(
        self, signal_id: str, category: str, severity: SignalSeverity,
        confidence: float, url: str, reason: str
    ) -> tuple[Signal, Evidence]:
        sig = Signal(
            signal_id=signal_id,
            category=category,
            severity=severity,
            confidence=confidence,
            detection_source=DetectionSource.URL_ENGINE,
            false_positive_risk="LOW",
        )
        evd = Evidence(
            evidence_id=str(uuid.uuid4()),
            signal_id=signal_id,
            evidence_span=url[:200],
            source_modality="url",
            evidence_type=EvidenceType.STRUCTURAL,
            confidence=confidence,
            verified_in_source=True,
        )
        return sig, evd
