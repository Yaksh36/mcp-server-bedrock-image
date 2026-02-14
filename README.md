# mcp-server-bedrock-image

[![CI](https://github.com/Yaksh36/mcp-server-bedrock-image/actions/workflows/ci.yml/badge.svg)](https://github.com/Yaksh36/mcp-server-bedrock-image/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mcp-server-bedrock-image.svg)](https://pypi.org/project/mcp-server-bedrock-image/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://modelcontextprotocol.io/)

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that gives AI agents the ability to generate, edit, and manipulate images using [Stability AI models on AWS Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-stability-diffusion.html).

Connect it to Claude Code, Cursor, Windsurf, VS Code, or any MCP-compatible client — then ask your AI to generate images, remove backgrounds, transfer styles, upscale, and more.

## Tools

| Tool | What it does | Model |
|------|-------------|-------|
| `generate_image` | High-quality text-to-image generation | Stable Image Ultra |
| `generate_image_core` | Faster, lower-cost generation | Stable Image Core |
| `remove_background` | Remove image background | Stability Remove Background v1 |
| `style_transfer` | Apply style from a reference image | Stability Style Transfer v1 |
| `search_and_recolor` | Recolor specific elements by description | Stability Search & Recolor v1 |
| `outpaint` | Extend image in any direction | Stability Outpaint v1 |
| `search_and_replace` | Find and replace objects in an image | Stability Search & Replace v1 |
| `upscale_fast` | 4x resolution upscale | Stability Fast Upscale v1 |
| `upscale_creative` | Creative upscale up to 4K | Stability Creative Upscale v1 |
| `compose_branded` | Composition-aware logo overlay | Local (Pillow — no Bedrock call) |

## Quickstart

### Prerequisites

- Python 3.12+
- AWS account with [Bedrock access to Stability AI models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
- [uv](https://docs.astral.sh/uv/) package manager

### Install & run

```bash
# Run directly (no install needed)
uvx mcp-server-bedrock-image

# Or install globally
uv tool install mcp-server-bedrock-image
```

### Authentication

Two auth modes are supported:

**boto3 mode** (default) — Uses standard [AWS credential chain](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) (env vars, `~/.aws/credentials`, IAM roles, STS):

```bash
export AWS_REGION=us-west-2
```

**Bearer token mode** — Uses [Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html) (no AWS CLI setup needed):

```bash
export BEDROCK_AUTH_MODE=bearer
export AWS_BEARER_TOKEN_BEDROCK=your-api-key-here
export AWS_REGION=us-west-2
```

## Client Configuration

<details>
<summary><strong>Claude Code</strong></summary>

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

For bearer token auth, add `"BEDROCK_AUTH_MODE": "bearer"` and `"AWS_BEARER_TOKEN_BEDROCK": "your-api-key"` to the `env` block.

</details>

<details>
<summary><strong>Cursor</strong></summary>

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "bedrock-image": {
      "command": "uvx",
      "args": ["mcp-server-bedrock-image"],
      "env": {
        "AWS_REGION": "us-west-2"
      }
    }
  }
}
```

</details>

<details>
<summary><strong>VS Code</strong></summary>

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "bedrock-image": {
      "command": "uvx",
      "args": ["mcp-server-bedrock-image"],
      "env": {
        "AWS_REGION": "us-west-2"
      }
    }
  }
}
```

</details>

<details>
<summary><strong>Windsurf</strong></summary>

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "bedrock-image": {
      "command": "uvx",
      "args": ["mcp-server-bedrock-image"],
      "env": {
        "AWS_REGION": "us-west-2"
      }
    }
  }
}
```

</details>

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_REGION` | `us-west-2` | AWS region for Bedrock |
| `BEDROCK_AUTH_MODE` | `boto3` | Auth mode: `boto3` or `bearer` |
| `AWS_BEARER_TOKEN_BEDROCK` | — | Bedrock API key (bearer mode only) |
| `BEDROCK_ENDPOINT` | Auto from region | Override Bedrock runtime endpoint |
| `IMAGE_STORAGE_DIRECTORY` | `/tmp/mcp-server-bedrock-image` | Where to save generated images |
| `SAVE_METADATA` | `true` | Save JSON metadata alongside images |

See [`.env.example`](.env.example) for a template.

## Usage Examples

Once connected, ask your AI agent naturally:

> "Generate a hero image of a modern hotel lobby with warm lighting in 16:9"

> "Remove the background from this product photo"

> "Apply the style of this watercolor painting to the room photo"

> "Add our logo to the generated image in the least busy corner"

Or call tools directly:

```python
# Generate
generate_image(prompt="Modern hotel lobby with warm lighting", aspect_ratio="16:9")

# Edit
remove_background(image_path="/path/to/photo.png")
style_transfer(prompt="Watercolor style", image_path="room.png", style_image_path="ref.png")
search_and_replace(image_path="scene.png", prompt="red chair", search_prompt="blue chair")
outpaint(image_path="photo.png", prompt="extend the garden", right=200, bottom=100)

# Upscale
upscale_fast(image_path="/path/to/small.png")
upscale_creative(image_path="photo.png", prompt="enhance details, sharp textures")

# Brand
compose_branded(image_path="hero.png", logo_path="logo.png", output_path="branded.png")
```

### How `compose_branded` works

The composition-aware branding tool doesn't use Bedrock — it runs locally with Pillow. It divides the image into a 3x3 grid, scores each quadrant by visual complexity (standard deviation of grayscale values), and places the logo in the least complex region. It also auto-selects between light and dark logo variants based on the background brightness.

## Architecture

```
src/mcp_server_bedrock_image/
├── server.py          # FastMCP server — registers all 10 tools
├── config.py          # Environment variables and model IDs
├── bedrock_client.py  # Dual-auth Bedrock client (boto3 + bearer)
├── image_utils.py     # Image save and metadata utilities
└── tools/
    ├── generate.py    # Text-to-image generation
    ├── edit.py        # Background removal, style transfer, recolor, outpaint, search-replace
    ├── upscale.py     # Fast and creative upscaling
    └── compose.py     # Composition-aware logo placement
```

## Development

```bash
# Clone and install
git clone https://github.com/Yaksh36/mcp-server-bedrock-image.git
cd mcp-server-bedrock-image
uv sync --all-extras --dev

# Run tests
uv run pytest -v

# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Contributing

Contributions are welcome. Please:

1. Fork the repo and create a feature branch
2. Add tests for new functionality
3. Ensure `uv run pytest -v` and `uv run ruff check src/ tests/` pass
4. Open a pull request

## License

[MIT](LICENSE)
