from unittest.mock import MagicMock, patch


def test_ask_rejects_empty_question(client):
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ingest_requires_openai_api_key(client, monkeypatch):
    monkeypatch.setattr("app.api.routes.settings.openai_api_key", "")
    response = client.post("/ingest", json={})
    assert response.status_code == 400
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_ingest_policies_endpoint_success(client, monkeypatch):
    monkeypatch.setattr("app.api.routes.settings.openai_api_key", "test-key")
    mock_session = MagicMock()
    with patch("app.api.routes.SessionLocal", return_value=mock_session), \
         patch(
             "app.api.routes.ingest_policies",
             return_value={
                 "status": "success",
                 "documents_indexed": 15,
                 "chunks_created": 15,
                 "documents_removed": 0,
             },
         ) as mock_ingest:
        response = client.post("/ingest", json={"prune_missing": True})

    assert response.status_code == 200
    body = response.json()
    assert body["documents_indexed"] == 15
    assert body["chunks_created"] == 15
    assert body["documents_removed"] == 0
    mock_ingest.assert_called_once()
    mock_session.close.assert_called_once()


def test_ask_accepts_optional_history(client):
    """Schema accepts history; pipeline is stubbed so the test stays offline."""
    from uuid import uuid4

    from app.retrieval.types import RetrievalHit

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
