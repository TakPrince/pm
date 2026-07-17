import os
import pytest
from unittest.mock import patch, MagicMock
from backend.app.ai import query_openrouter, AIError


@patch("backend.app.ai.httpx.Client")
def test_query_openrouter_success(mock_client_class):
    """Test successful chat completions from OpenRouter."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "4"
                }
            }
        ]
    }
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        result = query_openrouter([{"role": "user", "content": "What is 2+2?"}])
        assert result == "4"
        mock_client.post.assert_called_once()
        _, kwargs = mock_client.post.call_args
        assert kwargs["json"]["model"] == "openai/gpt-oss-120b"
        assert kwargs["json"]["messages"] == [{"role": "user", "content": "What is 2+2?"}]


def test_query_openrouter_missing_api_key():
    """Test that missing API key raises AIError."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(AIError, match="OPENROUTER_API_KEY environment variable is not set"):
            query_openrouter([{"role": "user", "content": "What is 2+2?"}])


@patch("backend.app.ai.httpx.Client")
def test_query_openrouter_api_error(mock_client_class):
    """Test that non-200 API response raises AIError."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with pytest.raises(AIError, match="OpenRouter API returned status 400"):
            query_openrouter([{"role": "user", "content": "What is 2+2?"}])


@patch("backend.app.ai.httpx.Client")
def test_query_openrouter_malformed_response(mock_client_class):
    """Test that malformed JSON response raises AIError."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}  # Malformed structure
    mock_response.text = "{}"
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with pytest.raises(AIError, match="Unexpected response structure"):
            query_openrouter([{"role": "user", "content": "What is 2+2?"}])


def test_validate_and_sanitize_board_update_healing():
    """Test that validate_and_sanitize_board_update automatically heals incomplete card models."""
    from backend.app.ai import validate_and_sanitize_board_update
    from backend.app.database import DEFAULT_BOARD_DATA
    import json
    
    current_board = json.loads(json.dumps(DEFAULT_BOARD_DATA))
    
    # Simulate an AI update where a card is missing id and details
    updated_board = json.loads(json.dumps(DEFAULT_BOARD_DATA))
    new_card_id = "card-1a2b3c"
    
    # Insert new card missing id and details, only title is present
    updated_board["cards"][new_card_id] = {
        "title": "Simple BBA Study Guide"
    }
    updated_board["columns"][0]["cardIds"].append(new_card_id)
    
    # Call validation/healing
    sanitized = validate_and_sanitize_board_update(current_board, updated_board)
    
    # Assert card is healed
    healed_card = sanitized["cards"][new_card_id]
    assert healed_card["id"] == new_card_id
    assert healed_card["title"] == "Simple BBA Study Guide"
    assert healed_card["details"] == ""


def test_process_ai_chat_truncated_json_extraction():
    """Test that process_ai_chat extracts the reply string using regex when the response is truncated JSON."""
    from backend.app.ai import process_ai_chat
    from unittest.mock import patch
    
    truncated_response = (
        '{ "reply": "I\'ve added a \'6th Grade Study Schedule\' card.", "board": { "columns": ['
    )
    
    with patch("backend.app.ai.query_openrouter", return_value=truncated_response):
        res = process_ai_chat("mock message", [], {})
        assert "6th Grade Study Schedule" in res["reply"]
        assert "visual board could not be updated" in res["reply"]
        assert res["board"] is None
