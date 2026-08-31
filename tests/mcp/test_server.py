from mcp.server import MCPServer

from app.mcp.server import mcp


def test_mcp_server_is_mcp_server_instance() -> None:
    assert isinstance(
        mcp,
        MCPServer,
    )