import sys
from pathlib import Path
import pytest

root_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_path))

from backend.engines.rule_engine import RuleEngine

@pytest.fixture
def engine():
    return RuleEngine()

def test_urgency_detection(engine):
    text = "URGENT NOTICE: Your electricity connection will be disconnected within 2 hours if bill is not updated."
    signals, evidence = engine.detect(text)
    signal_ids = [s.signal_id for s in signals]
    assert len(signals) > 0
    assert "SIG_URGENCY" in signal_ids or any("URGENT" in sid for sid in signal_ids)

def test_financial_request_detection(engine):
    text = "Kindly send money to UPI ID scammer@ybl immediately or download APK file."
    signals, evidence = engine.detect(text)
    assert len(signals) > 0

def test_clean_text_safety(engine):
    text = "Hi mom, I will reach home by 7 PM for dinner."
    signals, evidence = engine.detect(text)
    assert len(signals) == 0
