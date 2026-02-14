import base64

from mcp_server_bedrock_image.tools.edit import (
    build_outpaint_body,
    build_recolor_body,
    build_remove_background_body,
    build_search_replace_body,
    build_style_transfer_body,
)


def _fake_image_b64():
    return base64.b64encode(b"fakepngdata").decode()


def test_remove_background_body():
    body = build_remove_background_body(image=_fake_image_b64())
    assert body["image"] == _fake_image_b64()
    assert body["output_format"] == "png"


def test_style_transfer_body():
    body = build_style_transfer_body(
        prompt="hotel lobby in brand style",
        image=_fake_image_b64(),
        style_image=_fake_image_b64(),
    )
    assert body["prompt"] == "hotel lobby in brand style"
    assert "image" in body
    assert "style_image" in body


def test_recolor_body():
    body = build_recolor_body(
        image=_fake_image_b64(),
        prompt="a car",
        select_prompt="the red car",
        recolor_prompt="indigo #4F46E5",
    )
    assert body["select_prompt"] == "the red car"
    assert body["recolor_prompt"] == "indigo #4F46E5"


def test_outpaint_body():
    body = build_outpaint_body(
        image=_fake_image_b64(),
        prompt="extend the hotel scene",
        left=100,
        right=100,
    )
    assert body["left"] == 100
    assert body["right"] == 100
    assert body["top"] == 0
    assert body["bottom"] == 0


def test_search_replace_body():
    body = build_search_replace_body(
        image=_fake_image_b64(),
        prompt="a blue sofa",
        search_prompt="the red sofa",
    )
    assert body["search_prompt"] == "the red sofa"
    assert body["prompt"] == "a blue sofa"
