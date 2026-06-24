from unittest.mock import patch

from app.assistant.query_rewriter import rewrite_query
from app.models.schemas import ChatMessage


def test_empty_history_returns_original_question_without_llm_call():

    question = "Compare UBS and Pictet"

    with patch("app.assistant.query_rewriter.configure_llm") as mock_configure_llm, \
         patch("app.assistant.query_rewriter.LlamaSettings") as mock_settings:
        
        result = rewrite_query(question, [])
        
    assert result == question
    mock_configure_llm.assert_not_called()
    mock_settings.llm.complete.assert_not_called()


def test_with_history_returns_rewritten_query():
    question = "And what about Pictet?"

    history = [
        ChatMessage(role="user", content="How does UBS approach sustainable investing?"),
        ChatMessage(role="assistant", content="UBS integrates ESG into as part of its investing strategy."),
    ]
    rewritten_query = "How does Pictet approach sustainable investing compared to UBS?"

    with patch("app.assistant.query_rewriter.configure_llm"), \
         patch("app.assistant.query_rewriter.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = f"  {rewritten_query}  "
        result = rewrite_query(question, history)

    assert result == rewritten_query
    mock_settings.llm.complete.assert_called_once()
    prompt = mock_settings.llm.complete.call_args[0][0]
    assert "How does UBS approach sustainable investing?" in prompt
    assert question in prompt

def test_empty_llm_response_fallsback_to_original_question():
    question = "And what about Pictet?"

    history = [
        ChatMessage(role="user", content="How does UBS approach sustainable investing?"),
        ChatMessage(role="assistant", content="UBS integrates ESG into as part of its investing strategy."),
    ]

    with patch("app.assistant.query_rewriter.configure_llm"), \
         patch("app.assistant.query_rewriter.LlamaSettings") as mock_settings:
        mock_settings.llm.complete.return_value.text = ""
        result = rewrite_query(question, history)

    assert result == question



        
