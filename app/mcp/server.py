from typing import Any

from mcp.server import MCPServer

from app.api.dependencies import get_engine
from app.mcp.tools import MCPToolService

mcp = MCPServer("NexusRAG")


def get_tool_service() -> MCPToolService:
    """Resolve the shared NexusRAG application engine lazily."""

    return MCPToolService(
        get_engine()
    )


@mcp.tool()
def list_documents() -> list[dict[str, Any]]:
    """List documents currently known to NexusRAG."""

    return (
        get_tool_service()
        .list_documents()
    )


@mcp.tool()
def search_documents(
    query: str,
    top_k: int = 5,
    document_id: str | None = None,
    source: str | None = None,
    file_type: str | None = None,
) -> list[dict[str, Any]]:
    """Search the private knowledge base for relevant evidence."""

    return (
        get_tool_service()
        .search_documents(
            query=query,
            top_k=top_k,
            document_id=document_id,
            source=source,
            file_type=file_type,
        )
    )


@mcp.tool()
def ask_documents(
    question: str,
    top_k: int = 5,
    document_id: str | None = None,
    source: str | None = None,
    file_type: str | None = None,
) -> dict[str, Any]:
    """Answer using only indexed NexusRAG evidence."""

    return (
        get_tool_service()
        .ask_documents(
            question=question,
            top_k=top_k,
            document_id=document_id,
            source=source,
            file_type=file_type,
        )
    )


def main() -> None:
    """Run NexusRAG over MCP stdio transport."""

    mcp.run(
        transport="stdio"
    )


if __name__ == "__main__":
    main()