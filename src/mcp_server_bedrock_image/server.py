"""FastMCP server exposing Stability AI image tools on AWS Bedrock."""

import base64
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .config import IMAGE_STORAGE_DIRECTORY, MODELS, SAVE_METADATA
from .image_utils import save_image, save_metadata
from .tools.compose import compose_branded_image
from .tools.edit import (
    build_outpaint_body,
    build_recolor_body,
    build_remove_background_body,
    build_search_replace_body,
    build_style_transfer_body,
)
from .tools.generate import build_generate_body, parse_generate_response
from .tools.upscale import build_upscale_creative_body, build_upscale_fast_body

INSTRUCTIONS = """# Bedrock Image Generation MCP Server

Generate and manipulate images using Stability AI models on AWS Bedrock.

## Available Tools

- generate_image: High-quality image generation (Stable Image Ultra)
- generate_image_core: Faster generation (Stable Image Core)
- remove_background: Remove image background
- style_transfer: Apply style from a reference image
- search_and_recolor: Recolor specific elements
- outpaint: Extend image in any direction
- search_and_replace: Replace objects in an image
- upscale_fast: 4x resolution enhancement
- upscale_creative: Up to 4K creative upscale
- compose_branded: Overlay logo with composition-aware placement
"""

mcp = FastMCP(
    "mcp-server-bedrock-image",
    instructions=INSTRUCTIONS,
    dependencies=["boto3", "pillow", "numpy", "pydantic"],
)

_bedrock = None


def _get_bedrock():
    """Lazy-init BedrockImageClient so import doesn't require AWS credentials."""
    global _bedrock
    if _bedrock is None:
        from .bedrock_client import BedrockImageClient

        _bedrock = BedrockImageClient()
    return _bedrock


def _read_image_as_b64(path: str) -> str:
    """Read a local image file and return base64-encoded string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _output_dir() -> str:
    return IMAGE_STORAGE_DIRECTORY


@mcp.tool(name="generate_image")
async def tool_generate_image(
    prompt: str = Field(description="Text description of the image to generate (max 10000 chars)"),
    negative_prompt: Optional[str] = Field(default=None, description="What to exclude from the image"),
    aspect_ratio: Optional[str] = Field(default=None, description="Aspect ratio, e.g. '16:9', '1:1', '9:16'"),
    seed: Optional[int] = Field(default=None, description="Seed for reproducibility"),
    filename: Optional[str] = Field(default=None, description="Output filename without extension"),
    output_dir: Optional[str] = Field(default=None, description="Override output directory"),
) -> dict:
    """Generate a high-quality image using Stable Image Ultra on Bedrock."""
    body = build_generate_body(prompt=prompt, negative_prompt=negative_prompt, aspect_ratio=aspect_ratio, seed=seed)
    response = _get_bedrock().invoke_model(model_id=MODELS["ultra"], body=body)
    images, seeds = parse_generate_response(response)
    out = output_dir or _output_dir()
    paths = [save_image(img, output_dir=out, filename=filename) for img in images]
    if SAVE_METADATA:
        save_metadata({"prompt": prompt, "negative_prompt": negative_prompt, "model": "ultra", "seeds": seeds}, output_dir=out, filename=filename)
    return {"status": "success", "paths": paths, "seeds": seeds}


@mcp.tool(name="generate_image_core")
async def tool_generate_image_core(
    prompt: str = Field(description="Text description of the image to generate"),
    negative_prompt: Optional[str] = Field(default=None, description="What to exclude"),
    aspect_ratio: Optional[str] = Field(default=None, description="Aspect ratio"),
    seed: Optional[int] = Field(default=None, description="Seed"),
    filename: Optional[str] = Field(default=None, description="Output filename"),
    output_dir: Optional[str] = Field(default=None, description="Override output directory"),
) -> dict:
    """Generate an image using Stable Image Core (faster, lower cost)."""
    body = build_generate_body(prompt=prompt, negative_prompt=negative_prompt, aspect_ratio=aspect_ratio, seed=seed)
    response = _get_bedrock().invoke_model(model_id=MODELS["core"], body=body)
    images, seeds = parse_generate_response(response)
    out = output_dir or _output_dir()
    paths = [save_image(img, output_dir=out, filename=filename) for img in images]
    if SAVE_METADATA:
        save_metadata({"prompt": prompt, "model": "core", "seeds": seeds}, output_dir=out, filename=filename)
    return {"status": "success", "paths": paths, "seeds": seeds}


@mcp.tool(name="remove_background")
async def tool_remove_background(
    image_path: str = Field(description="Path to the image file"),
    filename: Optional[str] = Field(default=None, description="Output filename"),
    output_dir: Optional[str] = Field(default=None, description="Override output directory"),
) -> dict:
    """Remove the background from an image."""
    image_b64 = _read_image_as_b64(image_path)
    body = build_remove_background_body(image=image_b64)
    response = _get_bedrock().invoke_model(model_id=MODELS["remove_background"], body=body)
    images, _ = parse_generate_response(response)
    out = output_dir or _output_dir()
    paths = [save_image(img, output_dir=out, filename=filename) for img in images]
    return {"status": "success", "paths": paths}


@mcp.tool(name="style_transfer")
async def tool_style_transfer(
    prompt: str = Field(description="Description of desired output"),
    image_path: str = Field(description="Path to the source image"),
    style_image_path: str = Field(description="Path to the style reference image"),
    negative_prompt: Optional[str] = Field(default=None, description="What to exclude"),
    filename: Optional[str] = Field(default=None, description="Output filename"),
    output_dir: Optional[str] = Field(default=None, description="Override output directory"),
) -> dict:
    """Apply the style of a reference image to a source image."""
    image_b64 = _read_image_as_b64(image_path)
    style_b64 = _read_image_as_b64(style_image_path)
    body = build_style_transfer_body(prompt=prompt, image=image_b64, style_image=style_b64, negative_prompt=negative_prompt)
    response = _get_bedrock().invoke_model(model_id=MODELS["style_transfer"], body=body)
    images, _ = parse_generate_response(response)
    out = output_dir or _output_dir()
    paths = [save_image(img, output_dir=out, filename=filename) for img in images]
    return {"status": "success", "paths": paths}


@mcp.tool(name="search_and_recolor")
async def tool_search_and_recolor(
    image_path: str = Field(description="Path to the image file"),
    prompt: str = Field(description="Description of the scene"),
    select_prompt: str = Field(description="What to select for recoloring"),
    recolor_prompt: str = Field(description="New color/appearance for the selected element"),
    filename: Optional[str] = Field(default=None, description="Output filename"),
    output_dir: Optional[str] = Field(default=None, description="Override output directory"),
) -> dict:
    """Recolor specific elements in an image."""
    image_b64 = _read_image_as_b64(image_path)
    body = build_recolor_body(image=image_b64, prompt=prompt, select_prompt=select_prompt, recolor_prompt=recolor_prompt)
    response = _get_bedrock().invoke_model(model_id=MODELS["recolor"], body=body)
    images, _ = parse_generate_response(response)
    out = output_dir or _output_dir()
    paths = [save_image(img, output_dir=out, filename=filename) for img in images]
    return {"status": "success", "paths": paths}


@mcp.tool(name="outpaint")
async def tool_outpaint(
    image_path: str = Field(description="Path to the image file"),
    prompt: str = Field(description="Description for the extended area"),
    left: int = Field(default=0, description="Pixels to extend left"),
    right: int = Field(default=0, description="Pixels to extend right"),
    top: int = Field(default=0, description="Pixels to extend top"),
    bottom: int = Field(default=0, description="Pixels to extend bottom"),
    filename: Optional[str] = Field(default=None, description="Output filename"),
    output_dir: Optional[str] = Field(default=None, description="Override output directory"),
) -> dict:
    """Extend an image in any direction while maintaining visual consistency."""
    image_b64 = _read_image_as_b64(image_path)
    body = build_outpaint_body(image=image_b64, prompt=prompt, left=left, right=right, top=top, bottom=bottom)
    response = _get_bedrock().invoke_model(model_id=MODELS["outpaint"], body=body)
    images, _ = parse_generate_response(response)
    out = output_dir or _output_dir()
    paths = [save_image(img, output_dir=out, filename=filename) for img in images]
    return {"status": "success", "paths": paths}


@mcp.tool(name="search_and_replace")
async def tool_search_and_replace(
    image_path: str = Field(description="Path to the image file"),
    prompt: str = Field(description="What to replace with"),
    search_prompt: str = Field(description="What to find and replace"),
    filename: Optional[str] = Field(default=None, description="Output filename"),
    output_dir: Optional[str] = Field(default=None, description="Override output directory"),
) -> dict:
    """Replace objects or elements in an image."""
    image_b64 = _read_image_as_b64(image_path)
    body = build_search_replace_body(image=image_b64, prompt=prompt, search_prompt=search_prompt)
    response = _get_bedrock().invoke_model(model_id=MODELS["search_replace"], body=body)
    images, _ = parse_generate_response(response)
    out = output_dir or _output_dir()
    paths = [save_image(img, output_dir=out, filename=filename) for img in images]
    return {"status": "success", "paths": paths}


@mcp.tool(name="upscale_fast")
async def tool_upscale_fast(
    image_path: str = Field(description="Path to the image file"),
    filename: Optional[str] = Field(default=None, description="Output filename"),
    output_dir: Optional[str] = Field(default=None, description="Override output directory"),
) -> dict:
    """Upscale image resolution by 4x."""
    image_b64 = _read_image_as_b64(image_path)
    body = build_upscale_fast_body(image=image_b64)
    response = _get_bedrock().invoke_model(model_id=MODELS["upscale_fast"], body=body)
    images, _ = parse_generate_response(response)
    out = output_dir or _output_dir()
    paths = [save_image(img, output_dir=out, filename=filename) for img in images]
    return {"status": "success", "paths": paths}


@mcp.tool(name="upscale_creative")
async def tool_upscale_creative(
    image_path: str = Field(description="Path to the image file"),
    prompt: str = Field(description="Description to guide creative upscaling"),
    negative_prompt: Optional[str] = Field(default=None, description="What to exclude"),
    filename: Optional[str] = Field(default=None, description="Output filename"),
    output_dir: Optional[str] = Field(default=None, description="Override output directory"),
) -> dict:
    """Creatively upscale image up to 4K resolution."""
    image_b64 = _read_image_as_b64(image_path)
    body = build_upscale_creative_body(image=image_b64, prompt=prompt, negative_prompt=negative_prompt)
    response = _get_bedrock().invoke_model(model_id=MODELS["upscale_creative"], body=body)
    images, _ = parse_generate_response(response)
    out = output_dir or _output_dir()
    paths = [save_image(img, output_dir=out, filename=filename) for img in images]
    return {"status": "success", "paths": paths}


@mcp.tool(name="compose_branded")
async def tool_compose_branded(
    image_path: str = Field(description="Path to the source image"),
    logo_path: str = Field(description="Path to the logo file (RGBA PNG)"),
    output_path: str = Field(description="Where to save the branded image"),
    logo_variant: str = Field(default="auto", description="'light', 'dark', or 'auto'"),
    logo_scale: float = Field(default=0.08, description="Logo size as fraction of image width"),
) -> dict:
    """Overlay logo with composition-aware placement."""
    path = compose_branded_image(
        image_path=image_path,
        logo_path=logo_path,
        output_path=output_path,
        logo_variant=logo_variant,
        logo_scale=logo_scale,
    )
    return {"status": "success", "path": path}


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
