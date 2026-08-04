"""Unit tests for synthetic seed helpers (KYC date coherence)."""

from datetime import date
from random import Random

from app.database.seed import kyc_document_expiry_for_status


def test_expired_kyc_always_past_expiry():
    today = date(2026, 8, 4)
    rng = Random(42)
    for _ in range(40):
        expiry = kyc_document_expiry_for_status("expired", today=today, rng=rng)
        assert expiry < today


def test_valid_kyc_always_future_expiry():
    today = date(2026, 8, 4)
    rng = Random(7)
    for _ in range(40):
        expiry = kyc_document_expiry_for_status("valid", today=today, rng=rng)
        assert expiry > today


def test_incomplete_kyc_near_term_future():
    today = date(2026, 8, 4)
    rng = Random(99)
    expiry = kyc_document_expiry_for_status("incomplete", today=today, rng=rng)
    delta = (expiry - today).days
    assert 7 <= delta <= 60
