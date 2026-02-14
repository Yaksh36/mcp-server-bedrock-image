"""Bedrock runtime client with dual auth: boto3 (STS/IAM) and Bearer token (API key)."""

import json
from typing import Any

import boto3
import requests

from .config import AUTH_MODE, AWS_REGION, BEARER_TOKEN, BEDROCK_ENDPOINT


class BedrockImageClient:
    """Wrapper around Bedrock runtime supporting boto3 and bearer token auth.

    Auth modes:
        - "boto3": Standard AWS credentials chain (env vars, ~/.aws, IAM roles, STS).
        - "bearer": Bedrock API key auth via Authorization: Bearer header.
          See: https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html
    """

    def __init__(
        self,
        auth_mode: str | None = None,
        boto3_client=None,
        bearer_token: str | None = None,
        endpoint: str | None = None,
        region: str | None = None,
    ):
        self.auth_mode = auth_mode or AUTH_MODE
        self.region = region or AWS_REGION

        if self.auth_mode == "boto3":
            self._boto3_client = boto3_client or boto3.client(
                "bedrock-runtime", region_name=self.region
            )
        elif self.auth_mode == "bearer":
            self._bearer_token = bearer_token or BEARER_TOKEN
            self._endpoint = endpoint or BEDROCK_ENDPOINT
            if not self._bearer_token:
                raise ValueError(
                    "Bearer token required. Set AWS_BEARER_TOKEN_BEDROCK env var "
                    "or pass bearer_token parameter."
                )
        else:
            raise ValueError(
                f"Invalid auth_mode: '{self.auth_mode}'. Must be 'boto3' or 'bearer'."
            )

    def invoke_model(self, model_id: str, body: dict) -> dict[str, Any]:
        """Invoke a Bedrock image model and return parsed JSON response."""
        if self.auth_mode == "boto3":
            return self._invoke_boto3(model_id, body)
        return self._invoke_bearer(model_id, body)

    def _invoke_boto3(self, model_id: str, body: dict) -> dict[str, Any]:
        response = self._boto3_client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
        )
        return json.loads(response["body"].read().decode("utf-8"))

    def _invoke_bearer(self, model_id: str, body: dict) -> dict[str, Any]:
        url = f"{self._endpoint}/model/{model_id}/invoke"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._bearer_token}",
        }
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
