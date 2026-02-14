import base64
import json
import os
import struct
import zlib

import pytest

from mcp_server_bedrock_image.image_utils import save_image, save_metadata


@pytest.fixture
def tmp_output(tmp_path):
    return str(tmp_path)


def _make_fake_png() -> str:
    """Create a minimal valid base64-encoded PNG (1x1 red pixel)."""

    def chunk(chunk_type, data):
        c = chunk_type + data
        return (
            struct.pack(">I", len(data))
            + c
            + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        )

    raw = b"\x00\xff\x00\x00"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(raw))
    png += chunk(b"IEND", b"")
    return base64.b64encode(png).decode()


def test_save_image_writes_png(tmp_output):
    b64 = _make_fake_png()
    path = save_image(b64, output_dir=tmp_output, filename="test_img")
    assert os.path.exists(path)
    assert path.endswith(".png")
    with open(path, "rb") as f:
        assert f.read(4) == b"\x89PNG"


def test_save_image_auto_generates_filename(tmp_output):
    b64 = _make_fake_png()
    path = save_image(b64, output_dir=tmp_output)
    assert os.path.exists(path)


def test_save_metadata_writes_json(tmp_output):
    meta = {"prompt": "hotel lobby", "model": "ultra", "seed": 42}
    path = save_metadata(meta, output_dir=tmp_output, filename="test_img")
    assert os.path.exists(path)
    with open(path) as f:
        data = json.load(f)
    assert data["prompt"] == "hotel lobby"
    assert "timestamp" in data
