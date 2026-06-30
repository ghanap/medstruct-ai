from unittest.mock import patch, MagicMock
from utils.llm import extract_document_data
import json


@patch("utils.llm.requests.post")
def test_extract_document_data_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": json.dumps(
            {"patient": {"name": "Test Patient"}, "diagnosis": "Headache"}
        )
    }
    mock_post.return_value = mock_response

    result, model = extract_document_data(
        "Raw text containing Test Patient and Headache"
    )
    assert model == "mistral"
    assert "error" not in result
    assert result["patient"]["name"] == "Test Patient"
    assert result["diagnosis"] == "Headache"


@patch("utils.llm.requests.post")
def test_extract_document_data_fallback_markdown(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": '```json\n{"diagnosis": "Fever"}\n```'
    }
    mock_post.return_value = mock_response

    result, model = extract_document_data("Some text")
    assert "error" not in result
    assert result["diagnosis"] == "Fever"


@patch("utils.llm.requests.post")
def test_extract_document_data_connection_error(mock_post):
    from requests.exceptions import ConnectionError

    mock_post.side_effect = ConnectionError("Connection refused")

    result, model = extract_document_data("Some text")
    assert "error" in result
    assert "Cannot connect to Ollama" in result["error"]
