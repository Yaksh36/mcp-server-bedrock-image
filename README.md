# mcp-server-bedrock-image

MCP server for image generation and manipulation using Stability AI models on AWS Bedrock.

## Tools

| Tool | Description | Bedrock Model |
|------|-------------|---------------|
| `generate_image` | High-quality image generation | `stability.stable-image-ultra-v1:1` |
| `generate_image_core` | Faster, lower-cost generation | `stability.stable-image-core-v1:1` |
| `remove_background` | Remove image background | `stability.stable-image-remove-background-v1:0` |
| `style_transfer` | Apply style from reference image | `stability.stable-style-transfer-v1:0` |
| `search_and_recolor` | Recolor specific elements | `stability.stable-image-search-recolor-v1:0` |
| `outpaint` | Extend image in any direction | `stability.stable-image-outpaint-v1:0` |
| `search_and_replace` | Replace objects in an image | `stability.stable-image-search-replace-v1:0` |
| `upscale_fast` | 4x resolution upscale | `stability.stable-fast-upscale-v1:0` |
| `upscale_creative` | Creative upscale up to 4K | `stability.stable-creative-upscale-v1:0` |
| `compose_branded` | Composition-aware logo overlay | Local (Pillow) |

## Setup

### Prerequisites

- Python 3.12+
- AWS account with Bedrock access to Stability AI models
- [uv](https://docs.astral.sh/uv/) package manager

### Authentication

Two auth modes are supported:

**boto3 mode** (default) — Uses standard AWS credential chain (env vars, `~/.aws/credentials`, IAM roles, STS):

```bash
export AWS_REGION=us-west-2
```

**Bearer token mode** — Uses [Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html):

```bash
export BEDROCK_AUTH_MODE=bearer
export AWS_BEARER_TOKEN_BEDROCK=your-api-key-here
export AWS_REGION=us-west-2
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_REGION` | `us-west-2` | AWS region for Bedrock |
| `BEDROCK_AUTH_MODE` | `boto3` | Auth mode: `boto3` or `bearer` |
| `AWS_BEARER_TOKEN_BEDROCK` | — | Bedrock API key (bearer mode only) |
| `BEDROCK_ENDPOINT` | Auto from region | Override Bedrock runtime endpoint |
| `IMAGE_STORAGE_DIRECTORY` | `/tmp/mcp-server-bedrock-image` | Where to save generated images |
| `SAVE_METADATA` | `true` | Save JSON metadata alongside images |

## Claude Code Configuration

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "bedrock-image": {
      "command": "uvx",
      "args": ["mcp-server-bedrock-image"],
      "env": {
        "AWS_REGION": "us-west-2",
        "IMAGE_STORAGE_DIRECTORY": ".content-workspace/images"
      }
    }
  }
}
```

For bearer token auth:

```json
{
  "mcpServers": {
    "bedrock-image": {
      "command": "uvx",
      "args": ["mcp-server-bedrock-image"],
      "env": {
        "AWS_REGION": "us-west-2",
        "BEDROCK_AUTH_MODE": "bearer",
        "AWS_BEARER_TOKEN_BEDROCK": "your-api-key",
        "IMAGE_STORAGE_DIRECTORY": ".content-workspace/images"
      }
    }
  }
}
```

## Usage Examples

### Generate an image

```
generate_image(prompt="Modern hotel lobby with warm lighting", aspect_ratio="16:9")
```

### Remove background

```
remove_background(image_path="/path/to/photo.png")
```

### Style transfer

```
style_transfer(
    prompt="Hotel room in watercolor style",
    image_path="/path/to/room.png",
    style_image_path="/path/to/watercolor-ref.png"
)
```

### Composition-aware branding

```
compose_branded(
    image_path="/path/to/generated.png",
    logo_path="/path/to/logo.png",
    output_path="/path/to/branded.png",
    logo_variant="auto"
)
```

The `compose_branded` tool analyzes the image using a 9-quadrant grid, finds the least complex region, and places the logo there with automatic light/dark variant selection.

## Development

```bash
# Install dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest -v

# Run specific test
uv run pytest tests/test_server.py -v
```

## License

MIT
