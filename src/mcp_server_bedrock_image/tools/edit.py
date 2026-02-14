"""Image editing tools for Stability AI models on Bedrock."""


def build_remove_background_body(
    image: str,
    output_format: str = "png",
) -> dict:
    return {"image": image, "output_format": output_format}


def build_style_transfer_body(
    prompt: str,
    image: str,
    style_image: str,
    negative_prompt: str | None = None,
    output_format: str = "png",
) -> dict:
    body = {
        "prompt": prompt,
        "image": image,
        "style_image": style_image,
        "output_format": output_format,
    }
    if negative_prompt:
        body["negative_prompt"] = negative_prompt
    return body


def build_recolor_body(
    image: str,
    prompt: str,
    select_prompt: str,
    recolor_prompt: str,
    output_format: str = "png",
) -> dict:
    return {
        "image": image,
        "prompt": prompt,
        "select_prompt": select_prompt,
        "recolor_prompt": recolor_prompt,
        "output_format": output_format,
    }


def build_outpaint_body(
    image: str,
    prompt: str,
    left: int = 0,
    right: int = 0,
    top: int = 0,
    bottom: int = 0,
    output_format: str = "png",
) -> dict:
    return {
        "image": image,
        "prompt": prompt,
        "left": left,
        "right": right,
        "top": top,
        "bottom": bottom,
        "output_format": output_format,
    }


def build_search_replace_body(
    image: str,
    prompt: str,
    search_prompt: str,
    output_format: str = "png",
) -> dict:
    return {
        "image": image,
        "prompt": prompt,
        "search_prompt": search_prompt,
        "output_format": output_format,
    }
