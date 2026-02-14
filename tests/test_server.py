from mcp_server_bedrock_image.server import mcp


def test_server_has_tools():
    """Verify all expected tools are registered."""
    tool_names = [t.name for t in mcp._tool_manager.list_tools()]
    expected = [
        "generate_image",
        "generate_image_core",
        "remove_background",
        "style_transfer",
        "search_and_recolor",
        "outpaint",
        "search_and_replace",
        "upscale_fast",
        "upscale_creative",
        "compose_branded",
    ]
    for name in expected:
        assert name in tool_names, f"Missing tool: {name}"
