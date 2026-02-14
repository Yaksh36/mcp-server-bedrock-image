import base64
import json

import pytest
from unittest.mock import MagicMock, patch

from mcp_server_bedrock_image.bedrock_client import BedrockImageClient


@pytest.fixture
def mock_boto3_client():
    client = MagicMock()
    pixel = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100).decode()
    response_body = json.dumps({"images": [pixel]}).encode()
    body_mock = MagicMock()
    body_mock.read.return_value = response_body
    client.invoke_model.return_value = {"body": body_mock}
    return client


def test_boto3_mode_calls_bedrock(mock_boto3_client):
    bic = BedrockImageClient(auth_mode="boto3", boto3_client=mock_boto3_client)
    result = bic.invoke_model(
        model_id="stability.stable-image-ultra-v1:1",
        body={"prompt": "a hotel lobby"},
    )
    mock_boto3_client.invoke_model.assert_called_once()
    assert "images" in result


def test_boto3_mode_raises_on_error():
    client = MagicMock()
    client.invoke_model.side_effect = Exception("Bedrock error")
    bic = BedrockImageClient(auth_mode="boto3", boto3_client=client)
    with pytest.raises(Exception, match="Bedrock error"):
        bic.invoke_model(
            model_id="stability.stable-image-ultra-v1:1",
            body={"prompt": "a hotel lobby"},
        )


@patch("mcp_server_bedrock_image.bedrock_client.requests.post")
def test_bearer_mode_calls_endpoint(mock_post):
    pixel = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100).decode()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"images": [pixel]}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    bic = BedrockImageClient(
        auth_mode="bearer",
        bearer_token="test-token-123",
        endpoint="https://bedrock-runtime.us-east-1.amazonaws.com",
    )
    result = bic.invoke_model(
        model_id="stability.stable-image-ultra-v1:1",
        body={"prompt": "a hotel lobby"},
    )
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "Bearer test-token-123" in call_args[1]["headers"]["Authorization"]
    assert "stability.stable-image-ultra-v1:1" in call_args[0][0]
    assert "images" in result


@patch("mcp_server_bedrock_image.bedrock_client.requests.post")
def test_bearer_mode_raises_on_http_error(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = Exception("403 Forbidden")
    mock_post.return_value = mock_response

    bic = BedrockImageClient(
        auth_mode="bearer",
        bearer_token="bad-token",
        endpoint="https://bedrock-runtime.us-east-1.amazonaws.com",
    )
    with pytest.raises(Exception, match="403"):
        bic.invoke_model(
            model_id="stability.stable-image-ultra-v1:1",
            body={"prompt": "test"},
        )


def test_invalid_auth_mode_raises():
    with pytest.raises(ValueError, match="auth_mode"):
        BedrockImageClient(auth_mode="invalid")
