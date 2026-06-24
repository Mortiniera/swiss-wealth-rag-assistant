from unittest.mock import patch
from app.assistant.intent import OUT_OF_SCOPE_MESSAGE

FALLBACK = "I could not find enough information in the indexed sources to answer this confidently."


def test_out_of_scope_question_returns_refusal(client):
    with patch("app.assistant.orchestrator.classify_intent", return_value="OUT_OF_SCOPE"), \
         patch("app.rag.generator.retrieve") as mock_retrieve:
        response = client.post("/ask", json={"question": "What is a protein?"})
    assert response.status_code == 200
    assert response.json()["answer"] == OUT_OF_SCOPE_MESSAGE
    assert response.json()["sources"] == []
    mock_retrieve.assert_not_called()


def test_source_schema_is_valid(client):
    mock_chunks = [{
        "text": "Sustainability content.",
        "institution": "Lombard Odier",
        "document_title": "Sustainable Investing Overview",
        "source_file": "lombard_odier.txt",
        "chunk_id": "test-chunk-id",
        "score": 0.72,
    }]

    with patch("app.rag.generator.retrieve", return_value=mock_chunks), \
         patch("app.rag.generator.configure_llm"), \
         patch("app.rag.generator.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = "  Grounded answer.  "
        response = client.post("/ask", json={"question": "Sustainable investing?"})
    assert response.status_code == 200
    source = response.json()["sources"][0]
    assert set(source.keys()) == {"institution", "document_title", "source_file", "chunk_id", "score"}



def test_history_is_passed_to_prompt(client):
    mock_chunks = [{
        "text": "Pictet sustainable finance content.",
        "institution": "Pictet",
        "document_title": "Sustainable Finance",
        "source_file": "pictet_sustainable_finance.txt",
        "chunk_id": "test-chunk-id",
        "score": 0.72,
    }]

    with patch("app.assistant.orchestrator.rewrite_query", return_value="How does Pictet approach sustainable investing?"), \
        patch("app.rag.generator.retrieve", return_value=mock_chunks), \
         patch("app.rag.generator.configure_llm"), \
         patch("app.rag.generator.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = "Pictet answer."
        response = client.post(
            "/ask",
            json={
                "question": "And what about Pictet?",
                "history": [
                    {
                        "role": "user",
                        "content": "How does UBS approach sustainable investing?",
                    },
                    {
                        "role": "assistant",
                        "content": "UBS integrates ESG into advisory workflows.",
                    },
                ],
            },
        )

    assert response.status_code == 200
    prompt = mock_settings.llm.complete.call_args[0][0]
    assert "How does UBS approach sustainable investing?" in prompt
    assert "And what about Pictet?" in prompt


def test_retrieval_uses_rewritten_query(client):
    mock_chunks = [{
        "text": "Pictet sustainable finance content.",
        "institution": "Pictet",
        "document_title": "Sustainable Finance",
        "source_file": "pictet_sustainable_finance.txt",
        "chunk_id": "test-chunk-id",
        "score": 0.72,
    }]

    with patch("app.rag.generator.retrieve") as mock_retrieve, \
         patch("app.assistant.orchestrator.rewrite_query", return_value="Compare Pictet and UBS sustainable investing"), \
         patch("app.rag.generator.configure_llm"), \
         patch("app.rag.generator.LlamaSettings") as mock_settings:
        
        mock_retrieve.return_value = mock_chunks
        mock_settings.llm.complete.return_value.text = "Comparison answer."
        response = client.post("/ask", json={
            "question": "And compared to UBS?",
            "history": [
                {
                    "role": "user",
                    "content": "How does Pictet approach sustainable investing?",
                },
                {
                    "role": "assistant",
                    "content": "Pictet focuses on thematic sustainable strategies.",
                },
            ],
        })

    assert response.status_code == 200
    mock_retrieve.assert_called_once_with("Compare Pictet and UBS sustainable investing")


def test_low_relevance_rag_query_returns_fallback(client):
    with patch("app.assistant.orchestrator.classify_intent", return_value="RAG_QUERY"), \
         patch("app.rag.generator.retrieve", return_value=[]):
        response = client.post("/ask", json={"question": "What is a protein?"})

    assert response.status_code == 200
    assert response.json()["answer"] == FALLBACK
    assert response.json()["sources"] == []