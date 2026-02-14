import base64

from mcp_server_bedrock_image.tools.generate import (
    build_generate_body,
    parse_generate_response,
)


def test_build_generate_body_basic():
    body = build_generate_body(prompt="a luxury hotel lobby at sunset")
    assert body["prompt"] == "a luxury hotel lobby at sunset"
    assert body["output_format"] == "png"
    assert body["mode"] == "text-to-image"


def test_build_generate_body_with_negative():
    body = build_generate_body(
        prompt="hotel lobby",
        negative_prompt="people, text, watermark",
    )
    assert body["negative_prompt"] == "people, text, watermark"


def test_build_generate_body_with_dimensions():
    body = build_generate_body(
        prompt="hotel",
        aspect_ratio="16:9",
    )
    assert body["aspect_ratio"] == "16:9"


def test_parse_generate_response():
    fake_b64 = base64.b64encode(b"fakepng").decode()
    response = {"images": [fake_b64], "seeds": [42]}
    images, seeds = parse_generate_response(response)
    assert len(images) == 1
    assert seeds == [42]


def test_parse_generate_response_no_seeds():
    fake_b64 = base64.b64encode(b"fakepng").decode()
    response = {"images": [fake_b64]}
    images, seeds = parse_generate_response(response)
    assert len(images) == 1
    assert seeds == []
