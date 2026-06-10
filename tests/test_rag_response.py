from unittest.mock import patch

FALLBACK = "I could not find enough information in the indexed sources to answer this confidently."


def test_unrelated_question_returns_fallback(client):
    with patch("app.rag.generator.retrieve", return_value=[]):
        response = client.post("/ask", json={"question": "What is a protein?"})
    assert response.status_code == 200
    assert response.json()["answer"] == FALLBACK
    assert response.json()["sources"] == []


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