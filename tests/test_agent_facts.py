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
    assert "Primary signal(s)" in facts
    assert "KYC expired" in facts
    assert "enhanced-review" in facts


def test_format_facts_includes_restriction_and_kyc_primaries():
    facts = format_structured_facts(
        [
            {
                "tool": "get_client_profile",
                "ok": True,
                "data": {
                    "client_code": "CLI-000238",
                    "full_name": "Adrian Baumann",
                    "status": "dormant",
                    "segment": "hnwi",
                    "residency_country": "CH",
                    "kyc_status": "expired",
                    "kyc_document_type": "passport",
                    "kyc_document_expiry": "2027-04-13",
                    "primary_rm_name": "Elena Brunner",
                },
            },
            {
                "tool": "get_account_restrictions",
                "ok": True,
                "data": {
                    "restriction_count": 1,
                    "restrictions": [
                        {
                            "account_code": "ACC-000602",
                            "restriction_type": "debit_block",
                            "reason_code": "manual_review",
                            "status": "active",
                        }
                    ],
                },
            },
        ]
    )
    assert facts is not None
    assert "KYC expired" in facts
    assert "ACC-000602" in facts
    assert "debit block" in facts


def test_evidence_chips_from_profile_and_restrictions():
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
            },
            {
                "tool": "get_account_restrictions",
                "ok": True,
                "data": {
                    "restrictions": [
                        {
                            "account_code": "ACC-000602",
                            "restriction_type": "debit_block",
                        }
                    ],
                },
            },
        ]
    )
    assert evidence[0] == {
        "label": "KYC",
        "value": "expired",
        "source": "client_profile",
    }
    assert any(
        item["label"] == "Restriction"
        and item["source"] == "account_restrictions"
        and "ACC-000602" in item["value"]
        for item in evidence
    )


def test_format_facts_empty_transactions_does_not_invent_pending():
    facts = format_structured_facts(
        [
            {
                "tool": "get_client_profile",
                "ok": True,
                "data": {
                    "client_code": "CLI-EMPTY",
                    "full_name": "No Txn Client",
                    "status": "active",
                    "segment": "hnwi",
                    "residency_country": "CH",
                    "kyc_status": "valid",
                    "kyc_document_type": "passport",
                    "kyc_document_expiry": "2030-01-01",
                    "primary_rm_name": "Elena Meier",
                },
            },
            {
                "tool": "get_recent_transactions",
                "ok": True,
                "data": {
                    "transaction_count": 0,
                    "returned_count": 0,
                    "pending_or_unusual_count": 0,
                    "transactions": [],
                    "pending_or_unusual": [],
                },
            },
        ]
    )
    assert facts is not None
    assert "none on file" in facts
    assert "Do not invent a pending outbound" in facts


def test_evidence_empty_transactions_chip():
    evidence = evidence_from_tool_results(
        [
            {
                "tool": "get_recent_transactions",
                "ok": True,
                "data": {
                    "transaction_count": 0,
                    "pending_or_unusual": [],
                },
            }
        ]
    )
    assert evidence == [
        {
            "label": "Transactions",
            "value": "none on file",
            "source": "recent_transactions",
        }
    ]


def test_evidence_open_sr_none_and_present():
    none_chip = evidence_from_tool_results(
        [
            {
                "tool": "get_open_service_requests",
                "ok": True,
                "data": {"open_count": 0, "open_requests": []},
            }
        ]
    )
    assert none_chip == [
        {"label": "Open SR", "value": "none", "source": "open_service_requests"}
    ]

    present = evidence_from_tool_results(
        [
            {
                "tool": "get_open_service_requests",
                "ok": True,
                "data": {
                    "open_requests": [
                        {
                            "request_code": "SRQ-SCEN-01",
                            "request_type": "aml_review",
                        }
                    ],
                },
            }
        ]
    )
    assert present[0]["value"] == "SRQ-SCEN-01 · aml review"


def test_failed_tools_yield_no_evidence():
    assert evidence_from_tool_results(
        [{"tool": "get_client_profile", "ok": False, "error": {"code": "not_found"}}]
    ) == []
