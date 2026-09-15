import sys
from pathlib import Path
import pytest

root_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_path))

from backend.core.normalizer import Normalizer
from backend.schemas.enums import Modality

@pytest.fixture
def normalizer():
    return Normalizer()

def test_unicode_confusable_sanitization(normalizer):
    obfuscated_text = "Urgent connection disсоnnеct" # Cyrillic o and e
    normalized = normalizer.normalize_text(obfuscated_text, modality=Modality.TEXT)
    assert normalized.normalized_text != ""
    
    zws_text = "URGENT\u200bPAYMENT\u200bREQUIRED"
    zws_normalized = normalizer.normalize_text(zws_text, modality=Modality.TEXT)
    assert "\u200b" not in zws_normalized.normalized_text

def test_entity_extraction(normalizer):
    text = "Call +919876543210 or visit https://sbi-kyc-verify.top/login"
    normalized = normalizer.normalize_text(text, modality=Modality.TEXT)
    assert len(normalized.extracted_urls) > 0
    assert len(normalized.extracted_phone_numbers) > 0
