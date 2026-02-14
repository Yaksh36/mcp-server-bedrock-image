"""Image upscaling tools for Stability AI models on Bedrock."""


def build_upscale_fast_body(
    image: str,
    output_format: str = "png",
) -> dict:
    return {"image": image, "output_format": output_format}


def build_upscale_creative_body(
    image: str,
    prompt: str,
    negative_prompt: str | None = None,
    output_format: str = "png",
) -> dict:
    body = {
        "image": image,
        "prompt": prompt,
        "output_format": output_format,
    }
    if negative_prompt:
        body["negative_prompt"] = negative_prompt
    return body
