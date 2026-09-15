"""
SCAMX — Safety Policy Engine
Deterministic, signal-driven safety recommendations.

Rules:
  - The LLM may personalize wording but CANNOT remove or weaken a policy action.
  - Safety actions are always generated BEFORE LLM explanation.
  - Official contacts come ONLY from this engine (sourced from RAG Tier 1 docs).
  - In incident_response mode, recovery actions are prepended at highest priority.
"""

from backend.schemas.signals import Signal
from backend.schemas.analysis import SafeAction, OfficialContact, FollowUpQuestion
from backend.schemas.enums import (
    SignalSeverity, RiskBand, ScamCategory, ActionType, UncertaintyLevel, UserState
)


# ── Per-signal mandatory safety actions ──────────────────────────────────────
# These fire whenever the signal is present, regardless of category.

SIGNAL_POLICIES: dict[str, list[SafeAction]] = {
    "SIG_OTP_REQUEST": [
        SafeAction(action="Do NOT share your OTP with anyone — including callers claiming to be from your bank.", action_type=ActionType.DO_NOT, priority=1),
        SafeAction(action="Your bank will NEVER ask for your OTP over the phone, SMS, or chat.", action_type=ActionType.DO_NOT, priority=2),
    ],
    "SIG_PIN_REQUEST": [
        SafeAction(action="Do NOT share your ATM or app PIN with anyone.", action_type=ActionType.DO_NOT, priority=1),
    ],
    "SIG_CVV_REQUEST": [
        SafeAction(action="Do NOT share your card CVV with anyone.", action_type=ActionType.DO_NOT, priority=1),
    ],
    "SIG_PASSWORD_REQUEST": [
        SafeAction(action="Do NOT share your password or login credentials with anyone.", action_type=ActionType.DO_NOT, priority=1),
    ],
    "SIG_SCREEN_SHARE": [
        SafeAction(action="Do NOT install AnyDesk, TeamViewer, or any remote access software at a stranger's request.", action_type=ActionType.DO_NOT, priority=1),
        SafeAction(action="If you already installed such software, uninstall it immediately and disconnect from the internet.", action_type=ActionType.DO, priority=2),
        SafeAction(action="No legitimate bank or government body will ever ask you to install remote access software.", action_type=ActionType.DO_NOT, priority=3),
    ],
    "SIG_REMOTE_SOFTWARE": [
        SafeAction(action="Do NOT grant remote access to your device to any unknown person.", action_type=ActionType.DO_NOT, priority=1),
    ],
    "SIG_SUSPICIOUS_URL": [
        SafeAction(action="Do NOT click the link in this message.", action_type=ActionType.DO_NOT, priority=1),
        SafeAction(action="If you need to visit the website, type the official address directly into your browser.", action_type=ActionType.DO, priority=2),
    ],
    "SIG_ADVANCE_FEE": [
        SafeAction(action="Do NOT pay any fee, tax, or charge to receive a prize, loan, or job offer.", action_type=ActionType.DO_NOT, priority=1),
        SafeAction(action="Legitimate lenders, employers, and prize organizations do not charge fees upfront.", action_type=ActionType.DO_NOT, priority=2),
    ],
    "SIG_PAYMENT_REQUEST": [
        SafeAction(action="Do NOT transfer money without independently verifying the request through official channels.", action_type=ActionType.DO_NOT, priority=1),
    ],
    "SIG_QR_PAYMENT": [
        SafeAction(action="Do NOT scan QR codes sent to you for 'receiving' money — QR codes only send money FROM you.", action_type=ActionType.DO_NOT, priority=1),
    ],
}


# ── Category-specific safety actions ─────────────────────────────────────────

CATEGORY_POLICIES: dict[str, list[SafeAction]] = {
    ScamCategory.KYC: [
        SafeAction(action="Contact your bank directly using the number on the back of your card or their official website.", action_type=ActionType.VERIFY, priority=5),
        SafeAction(action="Banks send KYC notices in writing — not via phone calls demanding immediate action.", action_type=ActionType.DO_NOT, priority=6),
    ],
    ScamCategory.BANKING: [
        SafeAction(action="Call your bank's official customer care number to verify any such communication.", action_type=ActionType.VERIFY, priority=5),
    ],
    ScamCategory.PHISHING: [
        SafeAction(action="Do NOT enter your username, password, or any credentials on links received in messages.", action_type=ActionType.DO_NOT, priority=3),
        SafeAction(action="Access your bank's website by typing its address directly in your browser.", action_type=ActionType.DO, priority=4),
    ],
    ScamCategory.GOVERNMENT_IMPERSONATION: [
        SafeAction(action="TRAI, RBI, and CBI do NOT suspend phone numbers or accounts via phone calls.", action_type=ActionType.DO_NOT, priority=3),
        SafeAction(action="Disconnect the call and do not call back on numbers provided by the caller.", action_type=ActionType.DO, priority=4),
    ],
    ScamCategory.REMOTE_ACCESS: [
        SafeAction(action="Immediately disconnect any existing remote session.", action_type=ActionType.EMERGENCY, priority=1),
        SafeAction(action="Do not use your device for banking until verified clean by a professional.", action_type=ActionType.DO_NOT, priority=2),
        SafeAction(action="Change all passwords from a DIFFERENT device.", action_type=ActionType.DO, priority=3),
    ],
    ScamCategory.INVESTMENT: [
        SafeAction(action="No investment scheme guarantees returns. If it sounds too good, it is a scam.", action_type=ActionType.DO_NOT, priority=3),
        SafeAction(action="Never invest money in schemes promoted via WhatsApp groups or unknown callers.", action_type=ActionType.DO_NOT, priority=4),
    ],
    ScamCategory.LOTTERY: [
        SafeAction(action="You cannot win a lottery you did not enter.", action_type=ActionType.DO_NOT, priority=3),
        SafeAction(action="Do not pay any amount to 'claim' a prize.", action_type=ActionType.DO_NOT, priority=4),
    ],
    ScamCategory.JOB: [
        SafeAction(action="Legitimate employers do not ask for registration fees, security deposits, or advance payments.", action_type=ActionType.DO_NOT, priority=3),
    ],
}


# ── Incident response actions ─────────────────────────────────────────────────

INCIDENT_RESPONSE_OTP = [
    SafeAction(action="CALL YOUR BANK IMMEDIATELY using the number on the back of your card.", action_type=ActionType.EMERGENCY, priority=1),
    SafeAction(action="Ask the bank to temporarily freeze your account.", action_type=ActionType.EMERGENCY, priority=2),
    SafeAction(action="Monitor your recent transactions for unauthorized activity.", action_type=ActionType.DO, priority=3),
    SafeAction(action="File a cybercrime complaint at cybercrime.gov.in or call 1930.", action_type=ActionType.REPORT, priority=4),
    SafeAction(action="Do NOT share any more information with the caller/sender.", action_type=ActionType.DO_NOT, priority=5),
]

INCIDENT_RESPONSE_LINK = [
    SafeAction(action="Change your banking and email passwords IMMEDIATELY from a different device.", action_type=ActionType.EMERGENCY, priority=1),
    SafeAction(action="Enable two-factor authentication on all accounts.", action_type=ActionType.DO, priority=2),
    SafeAction(action="Check recent login activity on your accounts.", action_type=ActionType.DO, priority=3),
    SafeAction(action="Contact your bank's fraud department if you entered banking credentials.", action_type=ActionType.EMERGENCY, priority=4),
    SafeAction(action="Report the incident at cybercrime.gov.in or call 1930.", action_type=ActionType.REPORT, priority=5),
]

INCIDENT_RESPONSE_MONEY = [
    SafeAction(action="Contact your bank fraud department IMMEDIATELY — the first few hours are critical.", action_type=ActionType.EMERGENCY, priority=1),
    SafeAction(action="Note the transaction ID, time, and amount for your complaint.", action_type=ActionType.DO, priority=2),
    SafeAction(action="File a cybercrime complaint at cybercrime.gov.in or call 1930 with the transaction details.", action_type=ActionType.REPORT, priority=3),
    SafeAction(action="Do NOT transfer more money to 'recover' your lost amount — this is a secondary scam.", action_type=ActionType.DO_NOT, priority=4),
]

INCIDENT_RESPONSE_SOFTWARE = [
    SafeAction(action="Disconnect your device from the internet IMMEDIATELY.", action_type=ActionType.EMERGENCY, priority=1),
    SafeAction(action="Do NOT use the device for banking, email, or sensitive accounts until it is cleaned.", action_type=ActionType.DO_NOT, priority=2),
    SafeAction(action="Contact a trusted technician or the device manufacturer's official support.", action_type=ActionType.DO, priority=3),
    SafeAction(action="Change all passwords from a DIFFERENT device.", action_type=ActionType.DO, priority=4),
    SafeAction(action="Report the incident at cybercrime.gov.in or call 1930.", action_type=ActionType.REPORT, priority=5),
]

# ── Official contacts (Tier 1 — from public official sources) ────────────────

OFFICIAL_CONTACTS: list[OfficialContact] = [
    OfficialContact(organization="National Cybercrime Helpline", channel="Phone", contact="1930", source_tier=1, source_url="https://cybercrime.gov.in"),
    OfficialContact(organization="Cybercrime Reporting Portal", channel="Online", contact="cybercrime.gov.in", source_tier=1, source_url="https://cybercrime.gov.in"),
    OfficialContact(organization="SBI Customer Care", channel="Phone", contact="1800-11-2211 (toll free)", source_tier=1, source_url="https://sbi.co.in"),
    OfficialContact(organization="HDFC Bank Customer Care", channel="Phone", contact="1800-202-6161 (toll free)", source_tier=1, source_url="https://hdfcbank.com"),
    OfficialContact(organization="ICICI Bank Customer Care", channel="Phone", contact="1800-1080 (toll free)", source_tier=1, source_url="https://icicibank.com"),
    OfficialContact(organization="RBI Complaints", channel="Online", contact="cms.rbi.org.in", source_tier=1, source_url="https://rbi.org.in"),
]

# ── Follow-up questions ───────────────────────────────────────────────────────

FOLLOW_UP_QUESTIONS: dict[str, FollowUpQuestion] = {
    "FUQ_OTP_SHARED": FollowUpQuestion(
        question_id="FUQ_OTP_SHARED",
        question="Did you already share the OTP with the caller or on a website?",
        purpose="Determine if immediate account recovery steps are needed",
        if_yes_state=UserState.INCIDENT_RESPONSE,
        if_no_state=UserState.PREVENTION,
    ),
    "FUQ_LINK_CLICKED": FollowUpQuestion(
        question_id="FUQ_LINK_CLICKED",
        question="Did you click the link and enter any information (password, credentials)?",
        purpose="Determine if credential compromise response is needed",
        if_yes_state=UserState.INCIDENT_RESPONSE,
        if_no_state=UserState.PREVENTION,
    ),
    "FUQ_MONEY_SENT": FollowUpQuestion(
        question_id="FUQ_MONEY_SENT",
        question="Did you transfer or send any money as requested?",
        purpose="Determine if financial recovery steps are needed",
        if_yes_state=UserState.INCIDENT_RESPONSE,
        if_no_state=UserState.PREVENTION,
    ),
    "FUQ_SOFTWARE_INSTALLED": FollowUpQuestion(
        question_id="FUQ_SOFTWARE_INSTALLED",
        question="Did you install any software or app at their request?",
        purpose="Determine if device compromise response is needed",
        if_yes_state=UserState.INCIDENT_RESPONSE,
        if_no_state=UserState.PREVENTION,
    ),
}


# ── Safety Engine ─────────────────────────────────────────────────────────────

class SafetyEngine:

    def get_actions(
        self,
        signals: list[Signal],
        category: str,
        risk_band: RiskBand,
        user_state: UserState = UserState.PREVENTION,
        session_context=None,
    ) -> dict:
        """
        Returns a dict with:
          immediate_actions, verification_steps, official_contacts,
          incident_response_actions, follow_up_questions
        """
        immediate: list[SafeAction] = []
        seen_actions: set[str] = set()

        # ── 1. Signal-specific mandatory actions ─────────────────────────────
        signal_ids = {sig.signal_id for sig in signals}
        for sig_id in signal_ids:
            for action in SIGNAL_POLICIES.get(sig_id, []):
                if action.action not in seen_actions:
                    immediate.append(action)
                    seen_actions.add(action.action)

        # ── 2. Category-specific actions ──────────────────────────────────────
        for action in CATEGORY_POLICIES.get(category, []):
            if action.action not in seen_actions:
                immediate.append(action)
                seen_actions.add(action.action)

        # Sort by priority (lower number = more urgent)
        immediate.sort(key=lambda a: a.priority)

        # ── 3. Verification steps ─────────────────────────────────────────────
        verification: list[SafeAction] = [
            SafeAction(
                action="Contact the organization directly using a number from their official website or the back of your card — NOT a number given in this message.",
                action_type=ActionType.VERIFY,
                priority=1,
            )
        ]

        # ── 4. Official contacts ──────────────────────────────────────────────
        contacts = [OFFICIAL_CONTACTS[0], OFFICIAL_CONTACTS[1]]  # Always include cybercrime helpline

        # ── 5. Incident response actions ──────────────────────────────────────
        incident_actions: list[SafeAction] = []
        if user_state == UserState.INCIDENT_RESPONSE or self._already_acted(session_context):
            incident_actions = self._get_incident_actions(signal_ids, session_context)

        # ── 6. Follow-up questions ─────────────────────────────────────────────
        follow_ups = self._select_follow_up_questions(signal_ids, session_context)

        return {
            "immediate_actions": immediate,
            "verification_steps": verification,
            "official_contacts": contacts,
            "incident_response_actions": incident_actions,
            "follow_up_questions": follow_ups,
        }

    def _already_acted(self, ctx) -> bool:
        if ctx is None:
            return False
        return any([ctx.otp_shared, ctx.link_clicked, ctx.money_sent, ctx.software_installed])

    def _get_incident_actions(self, signal_ids: set, ctx) -> list[SafeAction]:
        if ctx is None:
            return INCIDENT_RESPONSE_OTP  # Default to most common

        if ctx.otp_shared:
            return INCIDENT_RESPONSE_OTP
        if ctx.money_sent:
            return INCIDENT_RESPONSE_MONEY
        if ctx.software_installed:
            return INCIDENT_RESPONSE_SOFTWARE
        if ctx.link_clicked:
            return INCIDENT_RESPONSE_LINK

        # Infer from signals if no context
        if "SIG_OTP_REQUEST" in signal_ids:
            return INCIDENT_RESPONSE_OTP
        if "SIG_SCREEN_SHARE" in signal_ids or "SIG_REMOTE_SOFTWARE" in signal_ids:
            return INCIDENT_RESPONSE_SOFTWARE
        return INCIDENT_RESPONSE_LINK

    def _select_follow_up_questions(self, signal_ids: set, ctx) -> list[FollowUpQuestion]:
        """Select the most relevant follow-up questions (max 2)."""
        if ctx and self._already_acted(ctx):
            return []  # Already in incident mode, no need to ask

        questions: list[FollowUpQuestion] = []
        priority_map = [
            ("SIG_OTP_REQUEST", "FUQ_OTP_SHARED"),
            ("SIG_SUSPICIOUS_URL", "FUQ_LINK_CLICKED"),
            ("SIG_PAYMENT_REQUEST", "FUQ_MONEY_SENT"),
            ("SIG_ADVANCE_FEE", "FUQ_MONEY_SENT"),
            ("SIG_SCREEN_SHARE", "FUQ_SOFTWARE_INSTALLED"),
            ("SIG_REMOTE_SOFTWARE", "FUQ_SOFTWARE_INSTALLED"),
        ]
        seen_q_ids: set[str] = set()
        for sig_id, q_id in priority_map:
            if sig_id in signal_ids and q_id not in seen_q_ids:
                questions.append(FOLLOW_UP_QUESTIONS[q_id])
                seen_q_ids.add(q_id)
            if len(questions) >= 2:
                break

        return questions
