from unittest.mock import patch

from app.assistant.intent import (
    ASSISTANT_META_MESSAGE,
    OUT_OF_SCOPE_MESSAGE,
    classify_intent,
)


def test_policy_question_classified_as_rag_query():
    question = "What should an RM do if they notice unusual fragmented transfers?"

    with patch("app.assistant.intent.configure_llm"), \
         patch("app.assistant.intent.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = "RAG_QUERY"
        result = classify_intent(question)

    assert result == "RAG_QUERY"
    mock_settings.llm.complete.assert_called_once()
    prompt = mock_settings.llm.complete.call_args[0][0]
    assert question in prompt
    assert "Helvetia" in prompt
    assert "AML" in prompt or "KYC" in prompt


def test_meta_question_classified_as_assistant_meta():
    question = "What can you do?"

    with patch("app.assistant.intent.configure_llm"), \
         patch("app.assistant.intent.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = "ASSISTANT_META"
        result = classify_intent(question)

    assert result == "ASSISTANT_META"


def test_sports_question_classified_as_out_of_scope():
    question = "Who won the football match yesterday?"

    with patch("app.assistant.intent.configure_llm"), \
         patch("app.assistant.intent.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = "OUT_OF_SCOPE"
        result = classify_intent(question)

    assert result == "OUT_OF_SCOPE"


def test_noisy_llm_output_is_parsed_correctly():
    question = "When must KYC be refreshed for elevated-risk clients?"

    with patch("app.assistant.intent.configure_llm"), \
         patch("app.assistant.intent.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = "  RAG_QUERY.  "
        result = classify_intent(question)

    assert result == "RAG_QUERY"


def test_unknown_label_defaults_to_rag_query():
    question = "Explain the transfer review procedure"

    with patch("app.assistant.intent.configure_llm"), \
         patch("app.assistant.intent.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = "BANANA"
        result = classify_intent(question)

    assert result == "RAG_QUERY"


def test_out_of_scope_and_meta_messages_mention_helvetia_policies():
    assert "Helvetia" in OUT_OF_SCOPE_MESSAGE
    assert "policies" in OUT_OF_SCOPE_MESSAGE.lower()
    assert "Helvetia" in ASSISTANT_META_MESSAGE
    assert "UBS" not in OUT_OF_SCOPE_MESSAGE
    assert "Pictet" not in ASSISTANT_META_MESSAGE
