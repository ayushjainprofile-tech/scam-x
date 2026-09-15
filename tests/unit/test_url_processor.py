import sys
from pathlib import Path
import pytest

root_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_path))

from backend.multimodal.url_processor import URLProcessor

@pytest.fixture
def processor():
    return URLProcessor()

def test_suspicious_tld(processor):
    signals, evidence = processor.analyze("http://sbi-kyc-verify.top/login")
    assert len(signals) > 0

def test_url_shortener(processor):
    signals, evidence = processor.analyze("http://bit.ly/claim-prize-now")
    assert len(signals) > 0

def test_legitimate_url(processor):
    signals, evidence = processor.analyze("https://www.onlinesbi.sbi")
    # Whitelisted legitimate domain
    assert len(signals) == 0
