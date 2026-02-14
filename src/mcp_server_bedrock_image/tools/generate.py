"""Text-to-image generation tools for Stability AI models on Bedrock."""


def build_generate_body(
    prompt: str,
    negative_prompt: str | None = None,
    aspect_ratio: str | None = None,
    seed: int | None = None,
    output_format: str = "png",
) -> dict:
    """Build the request body for Stability AI image generation on Bedrock."""
    body = {
        "prompt": prompt,
        "mode": "text-to-image",
        "output_format": output_format,
    }
    if negative_prompt:
        body["negative_prompt"] = negative_prompt
    if aspect_ratio:
        body["aspect_ratio"] = aspect_ratio
    if seed is not None:
        body["seed"] = seed
    return body


def parse_generate_response(response: dict) -> tuple[list[str], list[int]]:
    """Parse Bedrock response, returning (base64_images, seeds)."""
    images = response.get("images", [])
    seeds = response.get("seeds", [])
    return images, seeds
