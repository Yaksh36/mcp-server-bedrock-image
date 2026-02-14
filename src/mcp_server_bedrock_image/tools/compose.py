"""Branded image composition using Pillow — composition-aware logo placement."""

import os

import numpy as np
from PIL import Image


def analyze_quadrants(image_path: str) -> list[dict]:
    """Divide image into 3x3 grid and score each quadrant for visual complexity."""
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]
    qh, qw = h // 3, w // 3

    quadrants = []
    for row in range(3):
        for col in range(3):
            region = arr[row * qh : (row + 1) * qh, col * qw : (col + 1) * qw]
            gray = np.mean(region, axis=2)
            complexity = float(np.std(gray))
            avg_brightness = float(np.mean(gray))
            quadrants.append(
                {
                    "row": row,
                    "col": col,
                    "complexity": complexity,
                    "avg_brightness": avg_brightness,
                }
            )
    return quadrants


def find_best_logo_quadrant(image_path: str) -> dict:
    """Find the least complex quadrant and recommend logo variant."""
    quadrants = analyze_quadrants(image_path)
    best = min(quadrants, key=lambda q: q["complexity"])
    best["logo_variant"] = "light" if best["avg_brightness"] < 128 else "dark"
    return best


def compose_branded_image(
    image_path: str,
    logo_path: str,
    output_path: str,
    logo_variant: str = "auto",
    logo_scale: float = 0.08,
) -> str:
    """Compose a branded image with composition-aware logo placement.

    Args:
        image_path: Path to the source image.
        logo_path: Path to the logo (RGBA PNG).
        output_path: Where to save the branded image.
        logo_variant: "light", "dark", or "auto" (auto-detect from image).
        logo_scale: Logo size as fraction of image width.

    Returns:
        Absolute path to the branded image.
    """
    img = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    # Scale logo
    logo_w = int(img.width * logo_scale)
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

    # Find best quadrant
    best = find_best_logo_quadrant(image_path)
    qh, qw = img.height // 3, img.width // 3

    # Position logo in center of best quadrant
    margin = 10
    x = best["col"] * qw + (qw - logo_w) // 2
    y = best["row"] * qh + (qh - logo_h) // 2

    # Clamp to image bounds with margin
    x = max(margin, min(x, img.width - logo_w - margin))
    y = max(margin, min(y, img.height - logo_h - margin))

    # Composite
    img.paste(logo, (x, y), logo)

    # Save as RGB PNG
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG")
    return os.path.abspath(output_path)
