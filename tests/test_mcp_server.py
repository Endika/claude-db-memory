import asyncio
import importlib

EXPECTED_TOOLS = {
    "tool_add_memory",
    "tool_search_memory",
    "tool_get_memory",
    "tool_update_memory",
    "tool_delete_memory",
    "tool_list_memories",
    "tool_reindex",
    "tool_verify",
}


def test_mcp_server_registers_every_tool(memory_dir):
    mod = importlib.import_module("mcp_server")
    names = {tool.name for tool in asyncio.run(mod.app.list_tools())}
    assert names == EXPECTED_TOOLS


def test_add_memory_tool_declares_its_arguments(memory_dir):
    mod = importlib.import_module("mcp_server")
    tools = {tool.name: tool for tool in asyncio.run(mod.app.list_tools())}
    schema = tools["tool_add_memory"].input_schema
    assert set(schema["required"]) == {"name", "type", "description", "body"}
    assert set(schema["properties"]) == {
        "name",
        "type",
        "description",
        "body",
        "tags",
        "project",
    }


def test_tool_add_then_search(memory_dir):
    mod = importlib.import_module("mcp_server")
    asyncio.run(
        mod.app.call_tool(
            "tool_add_memory",
            {
                "name": "m1",
                "type": "note",
                "description": "findable text",
                "body": "b",
                "tags": [],
                "project": None,
            },
        )
    )
    res = asyncio.run(mod.app.call_tool("tool_search_memory", {"query": "findable"}))
    assert not res.is_error
    assert any(item["name"] == "m1" for item in res.structured_content["items"])
