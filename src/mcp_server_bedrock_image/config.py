import os

AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
IMAGE_STORAGE_DIRECTORY = os.environ.get(
    "IMAGE_STORAGE_DIRECTORY", "/tmp/mcp-server-bedrock-image"
)
SAVE_METADATA = os.environ.get("SAVE_METADATA", "true").lower() == "true"

# Authentication mode: "boto3" (STS/IAM credentials) or "bearer" (Bedrock API key)
AUTH_MODE = os.environ.get("BEDROCK_AUTH_MODE", "boto3")
BEARER_TOKEN = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")

# Bedrock runtime endpoint (used in bearer mode)
BEDROCK_ENDPOINT = os.environ.get(
    "BEDROCK_ENDPOINT",
    f"https://bedrock-runtime.{AWS_REGION}.amazonaws.com",
)

# Stability AI model IDs on Bedrock
MODELS = {
    "ultra": "stability.stable-image-ultra-v1:1",
    "core": "stability.stable-image-core-v1:1",
    "sd35": "stability.sd3-5-large-v1:0",
    "remove_background": "stability.stable-image-remove-background-v1:0",
    "style_transfer": "stability.stable-style-transfer-v1:0",
    "recolor": "stability.stable-image-search-recolor-v1:0",
    "outpaint": "stability.stable-image-outpaint-v1:0",
    "upscale_fast": "stability.stable-fast-upscale-v1:0",
    "upscale_creative": "stability.stable-creative-upscale-v1:0",
    "structure": "stability.stable-image-control-structure-v1:0",
    "search_replace": "stability.stable-image-search-replace-v1:0",
}
