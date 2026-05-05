"""MCP server entry point. Exposes claude_db_memory operations as MCP tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from claude_db_memory.operations import (
    add as add_op,
)
from claude_db_memory.operations import (
    delete as delete_op,
)
from claude_db_memory.operations import (
    get as get_op,
)
from claude_db_memory.operations import (
    list_ as list_op,
)
from claude_db_memory.operations import (
    reindex as reindex_op,
)
from claude_db_memory.operations import (
    search as search_op,
)
from claude_db_memory.operations import (
    update as update_op,
)
from claude_db_memory.operations import (
    verify as verify_op,
)

app = FastMCP("claude-db-memory")


@app.tool()
def tool_add_memory(
    name: str,
    type: str,
    description: str,
    body: str,
    tags: list[str] | None = None,
    project: str | None = None,
) -> dict[str, Any]:
    return add_op.main(
        {
            "name": name,
            "type": type,
            "description": description,
            "body": body,
            "tags": tags or [],
            "project": project,
        }
    )


@app.tool()
def tool_search_memory(
    query: str,
    type: str | None = None,
    project: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    return search_op.main(
        {
            "query": query,
            "type": type,
            "project": project,
            "limit": limit,
        }
    )


@app.tool()
def tool_get_memory(id_or_name: str) -> dict[str, Any]:
    return get_op.main({"id_or_name": id_or_name})


@app.tool()
def tool_update_memory(id_or_name: str, fields: dict[str, Any]) -> dict[str, Any]:
    return update_op.main({"id_or_name": id_or_name, "fields": fields})


@app.tool()
def tool_delete_memory(id_or_name: str) -> dict[str, Any]:
    return delete_op.main({"id_or_name": id_or_name})


@app.tool()
def tool_list_memories(
    type: str | None = None,
    project: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    return list_op.main(
        {
            "type": type,
            "project": project,
            "limit": limit,
            "offset": offset,
        }
    )


@app.tool()
def tool_reindex() -> dict[str, Any]:
    return reindex_op.main({})


@app.tool()
def tool_verify() -> dict[str, Any]:
    return verify_op.main({})


if __name__ == "__main__":
    app.run()
