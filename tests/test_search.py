from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.search import main


def seed():
    add_main({"name": "feedback_commits", "type": "feedback",
              "description": "Never run git writes",
              "body": "User runs git operations themselves",
              "tags": ["git"], "project": None})
    add_main({"name": "project_tramita", "type": "project",
              "description": "Tramita lives in tramita-web",
              "body": "Frontend module is in tramita-web repo",
              "tags": ["frontend"], "project": "tramita"})


def test_search_finds_by_body_term(memory_dir):
    seed()
    res = main({"query": "git"})
    names = {r["name"] for r in res["items"]}
    assert "feedback_commits" in names


def test_search_finds_by_description(memory_dir):
    seed()
    res = main({"query": "tramita"})
    names = {r["name"] for r in res["items"]}
    assert "project_tramita" in names


def test_search_filter_by_type(memory_dir):
    seed()
    res = main({"query": "tramita", "type": "feedback"})
    assert res["items"] == []


def test_search_returns_snippet(memory_dir):
    seed()
    res = main({"query": "git"})
    assert res["items"][0]["snippet"]
