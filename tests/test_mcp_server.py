import importlib


def test_mcp_module_exposes_tool_handlers(memory_dir):
    mod = importlib.import_module("mcp_server")
    assert callable(mod.tool_add_memory)
    assert callable(mod.tool_search_memory)
    assert callable(mod.tool_get_memory)
    assert callable(mod.tool_update_memory)
    assert callable(mod.tool_delete_memory)
    assert callable(mod.tool_list_memories)
    assert callable(mod.tool_reindex)
    assert callable(mod.tool_verify)


def test_tool_add_then_search(memory_dir):
    mod = importlib.import_module("mcp_server")
    mod.tool_add_memory(
        name="m1",
        type="note",
        description="findable text",
        body="b",
        tags=[],
        project=None,
    )
    res = mod.tool_search_memory(query="findable")
    assert any(item["name"] == "m1" for item in res["items"])
