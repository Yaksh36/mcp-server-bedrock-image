import base64

from mcp_server_bedrock_image.tools.upscale import (
    build_upscale_creative_body,
    build_upscale_fast_body,
)


def _fake_image_b64():
    return base64.b64encode(b"fakepngdata").decode()


def test_upscale_fast_body():
    body = build_upscale_fast_body(image=_fake_image_b64())
    assert body["image"] == _fake_image_b64()
    assert body["output_format"] == "png"


def test_upscale_creative_body():
    body = build_upscale_creative_body(
        image=_fake_image_b64(),
        prompt="enhance hotel lobby detail",
    )
    assert body["prompt"] == "enhance hotel lobby detail"


def test_upscale_creative_with_negative():
    body = build_upscale_creative_body(
        image=_fake_image_b64(),
        prompt="enhance",
        negative_prompt="blur, noise",
    )
    assert body["negative_prompt"] == "blur, noise"
