import base64
import json
import os
import uuid
from datetime import datetime, timezone


def save_image(
    base64_data: str,
    output_dir: str,
    filename: str | None = None,
) -> str:
    """Decode base64 image and save as PNG. Returns absolute path."""
    os.makedirs(output_dir, exist_ok=True)
    fname = f"{filename or uuid.uuid4()}.png"
    path = os.path.join(output_dir, fname)
    with open(path, "wb") as f:
        f.write(base64.b64decode(base64_data))
    return os.path.abspath(path)


def save_metadata(
    metadata: dict,
    output_dir: str,
    filename: str | None = None,
) -> str:
    """Save generation metadata as JSON. Returns absolute path."""
    os.makedirs(output_dir, exist_ok=True)
    fname = f"{filename or uuid.uuid4()}_metadata.json"
    path = os.path.join(output_dir, fname)
    metadata["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(path, "w") as f:
        json.dump(metadata, f, indent=2)
    return os.path.abspath(path)
