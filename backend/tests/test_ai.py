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
