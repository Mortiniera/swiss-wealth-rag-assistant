from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.retrieval.types import RetrievalHit


def test_ask_rejects_empty_question(client):
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ingest_missing_folder_returns_404(client):
    response = client.post("/ingest", json={"source_dir": "data/does_not_exist"})
    assert response.status_code == 404


def test_ask_accepts_optional_history(client):
    """Schema accepts history; pipeline is stubbed so the test stays offline."""
    hit = RetrievalHit(
        chunk_id=uuid4(),
        document_id="POL-COM-001",
        document_title="Client Communication Standards",
        department="Client Service",
        source_file="data/policies/POL-COM-001.md",
        category="client_communication",
        text="Use recorded channels only.",
        score=0.02,
        channel="hybrid",
    )
    with patch("app.assistant.orchestrator.classify_intent", return_value="RAG_QUERY"), \
         patch(
             "app.assistant.orchestrator.rewrite_query",
             return_value="client communication standards",
         ), \
         patch("app.rag.generator.retrieve_policies", return_value=[hit]), \
         patch("app.rag.generator.SessionLocal", return_value=MagicMock()), \
         patch("app.rag.generator.configure_llm"), \
         patch("app.rag.generator.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = "Use recorded channels."
        response = client.post(
            "/ask",
            json={
                "question": "What are the communication standards?",
                "history": [
                    {"role": "user", "content": "Tell me about client email."},
                    {
                        "role": "assistant",
                        "content": "Email must match communication preferences.",
                    },
                ],
            },
        )
    assert response.status_code == 200
