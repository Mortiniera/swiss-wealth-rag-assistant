from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.agent.intent import OUT_OF_SCOPE_MESSAGE
from app.retrieval.types import RetrievalFilters, RetrievalHit

FALLBACK = "I could not find enough information in the indexed sources to answer this confidently."


def _mock_hit(**overrides) -> RetrievalHit:
    base = dict(
        chunk_id=uuid4(),
        document_id="POL-TEST-001",
        document_title="Test Policy",
        department="Compliance",
        source_file="data/policies/POL-TEST-001.md",
        category="kyc_refresh",
        text="KYC refresh content.",
        score=0.016393,
        channel="hybrid",
    )
    base.update(overrides)
    return RetrievalHit(**base)


def _patch_ask(*, retrieve_return, rewritten=None):
    """Common patches so /ask tests never call OpenAI or Postgres."""
    rewritten = rewritten or "rewritten question"
    return (
        patch("app.agent.nodes.classify.classify_intent", return_value="RAG_QUERY"),
        patch("app.agent.nodes.rewrite.rewrite_query", return_value=rewritten),
        patch("app.rag.generator.retrieve_policies", return_value=retrieve_return),
        patch("app.rag.generator.SessionLocal", return_value=MagicMock()),
        patch("app.rag.generator.configure_llm"),
        patch("app.rag.generator.LlamaSettings"),
    )


def test_out_of_scope_question_returns_refusal(client):
    with patch("app.agent.nodes.classify.classify_intent", return_value="OUT_OF_SCOPE"), \
         patch("app.rag.generator.retrieve_policies") as mock_retrieve:
        response = client.post("/ask", json={"question": "What is a protein?"})
    assert response.status_code == 200
    assert response.json()["answer"] == OUT_OF_SCOPE_MESSAGE
    assert response.json()["sources"] == []
    mock_retrieve.assert_not_called()


def test_source_schema_is_valid(client):
    hit = _mock_hit(text="Sustainability content.", department="Advisory")
    patches = _patch_ask(retrieve_return=[hit])
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5] as mock_settings:
        mock_settings.llm.complete.return_value.text = "  Grounded answer.  "
        response = client.post("/ask", json={"question": "KYC refresh rules?"})
    assert response.status_code == 200
    source = response.json()["sources"][0]
    assert set(source.keys()) == {
        "institution",
        "document_title",
        "source_file",
        "chunk_id",
        "score",
        "text",
    }
    assert source["institution"] == "Advisory"
    assert source["text"] == "Sustainability content."


def test_history_is_passed_to_prompt(client):
    hit = _mock_hit(
        text="Client communication standards content.",
        department="Client Service",
        document_title="Client Communication Standards",
    )
    patches = _patch_ask(
        retrieve_return=[hit],
        rewritten="How should RMs communicate with clients?",
    )
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5] as mock_settings:
        mock_settings.llm.complete.return_value.text = "Communication answer."
        response = client.post(
            "/ask",
            json={
                "question": "And for email?",
                "history": [
                    {
                        "role": "user",
                        "content": "What are the client communication standards?",
                    },
                    {
                        "role": "assistant",
                        "content": "Use recorded channels and match preferences.",
                    },
                ],
            },
        )

    assert response.status_code == 200
    prompt = mock_settings.llm.complete.call_args[0][0]
    assert "What are the client communication standards?" in prompt
    assert "And for email?" in prompt


def test_retrieval_uses_rewritten_query(client):
    hit = _mock_hit()
    rewritten = "KYC refresh when identity documents expired"
    patches = _patch_ask(retrieve_return=[hit], rewritten=rewritten)
    with patches[0], patches[1], patches[2] as mock_retrieve, patches[3], patches[4], patches[5] as mock_settings:
        mock_settings.llm.complete.return_value.text = "KYC answer."
        response = client.post(
            "/ask",
            json={
                "question": "And if the passport expired?",
                "history": [
                    {
                        "role": "user",
                        "content": "What is the KYC refresh policy?",
                    },
                    {
                        "role": "assistant",
                        "content": "Active KYC refresh intervals depend on risk tier.",
                    },
                ],
            },
        )

    assert response.status_code == 200
    assert mock_retrieve.call_args.args[1] == rewritten
    assert mock_retrieve.call_args.kwargs["filters"] == RetrievalFilters(status="active")


def test_no_hits_rag_query_returns_fallback(client):
    patches = _patch_ask(retrieve_return=[])
    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        response = client.post("/ask", json={"question": "What is a protein?"})

    assert response.status_code == 200
    assert response.json()["answer"] == FALLBACK
    assert response.json()["sources"] == []
