import os

import numpy as np
import pytest
from PIL import Image

from mcp_server_bedrock_image.tools.compose import (
    analyze_quadrants,
    compose_branded_image,
    find_best_logo_quadrant,
)


@pytest.fixture
def sample_image(tmp_path):
    """Create a 300x300 test image: dark left half, light right half."""
    arr = np.zeros((300, 300, 3), dtype=np.uint8)
    arr[:, 150:, :] = 240  # right half is light
    img = Image.fromarray(arr)
    path = str(tmp_path / "test.png")
    img.save(path)
    return path


@pytest.fixture
def sample_logo(tmp_path):
    """Create a tiny 50x50 logo with transparency."""
    img = Image.new("RGBA", (50, 50), (79, 70, 229, 200))
    path = str(tmp_path / "logo.png")
    img.save(path)
    return path


def test_analyze_quadrants(sample_image):
    scores = analyze_quadrants(sample_image)
    assert len(scores) == 9
    for s in scores:
        assert "row" in s
        assert "col" in s
        assert "complexity" in s
        assert "avg_brightness" in s


def test_find_best_logo_quadrant(sample_image):
    quadrant = find_best_logo_quadrant(sample_image)
    assert quadrant["row"] in (0, 1, 2)
    assert quadrant["col"] in (0, 1, 2)
    assert "logo_variant" in quadrant
    assert quadrant["logo_variant"] in ("light", "dark")


def test_find_best_prefers_low_complexity(sample_image):
    """The dark solid-color left side should have lower complexity than the boundary."""
    quadrant = find_best_logo_quadrant(sample_image)
    assert quadrant["col"] == 0


def test_compose_branded_image(sample_image, sample_logo, tmp_path):
    output = str(tmp_path / "branded.png")
    result = compose_branded_image(
        image_path=sample_image,
        logo_path=sample_logo,
        output_path=output,
        logo_variant="auto",
    )
    assert os.path.exists(result)
    img = Image.open(result)
    assert img.size == (300, 300)


def test_compose_branded_image_creates_parent_dirs(sample_image, sample_logo, tmp_path):
    output = str(tmp_path / "nested" / "dir" / "branded.png")
    result = compose_branded_image(
        image_path=sample_image,
        logo_path=sample_logo,
        output_path=output,
    )
    assert os.path.exists(result)
