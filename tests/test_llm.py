
from unittest.mock import patch, MagicMock
from utils.llm import extract_structured_data
import json


@patch("utils.llm.requests.post")
def test_extract_structured_data_success(mock_post):
    # Mock successful JSON response from Ollama
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": json.dumps(
            {"patient": {"name": "Test Patient"}, "diagnosis": "Headache"}
        )
    }
    mock_post.return_value = mock_response

    result, model = extract_structured_data(
        "Raw text containing Test Patient and Headache"
    )
    assert model == "mistral"
    assert "error" not in result
    assert result["patient"]["name"] == "Test Patient"
    assert result["diagnosis"] == "Headache"


@patch("utils.llm.requests.post")
def test_extract_structured_data_fallback_markdown(mock_post):
    # Mock JSON response wrapped in markdown code blocks
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": '```json\n{"diagnosis": "Fever"}\n```'
    }
    mock_post.return_value = mock_response

    result, model = extract_structured_data("Some text")
    assert "error" not in result
    assert result["diagnosis"] == "Fever"


@patch("utils.llm.requests.post")
def test_extract_structured_data_connection_error(mock_post):
    from requests.exceptions import ConnectionError

    mock_post.side_effect = ConnectionError("Connection refused")

    result, model = extract_structured_data("Some text")
    assert "error" in result
    assert "Failed to connect to Ollama" in result["error"]
