"""Tests for structured facts formatting and evidence chips."""

from app.agent.facts import evidence_from_tool_results, format_structured_facts


def test_format_facts_leads_with_kyc_signal():
    facts = format_structured_facts(
        [
            {
                "tool": "get_client_profile",
                "ok": True,
                "data": {
                    "client_code": "CLI-SCEN-01",
                    "full_name": "Helena Vogt",
                    "status": "active",
                    "segment": "hnwi",
                    "residency_country": "CH",
                    "kyc_status": "expired",
                    "kyc_document_type": "passport",
                    "kyc_document_expiry": "2024-01-01",
                    "primary_rm_name": "Elena Meier",
                },
            }
        ]
    )
    assert facts is not None
    assert "Helena Vogt" in facts
    assert "Primary signal: KYC expired" in facts
    assert "enhanced-review" in facts


def test_evidence_chips_from_profile():
    evidence = evidence_from_tool_results(
        [
            {
                "tool": "get_client_profile",
                "ok": True,
                "data": {
                    "kyc_status": "expired",
                    "kyc_document_expiry": "2024-01-01",
                    "segment": "hnwi",
                    "primary_rm_name": "Elena Meier",
                },
            }
        ]
    )
    assert evidence[0] == {
        "label": "KYC",
        "value": "expired",
        "source": "client_profile",
    }
    assert any(item["label"] == "Doc expiry" for item in evidence)
    assert any(item["label"] == "Primary RM" for item in evidence)


def test_failed_tools_yield_no_evidence():
    assert evidence_from_tool_results(
        [{"tool": "get_client_profile", "ok": False, "error": {"code": "not_found"}}]
    ) == []
