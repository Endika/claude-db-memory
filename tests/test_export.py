from claude_db_memory.config import md_dir, index_path
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.export import main


def test_export_writes_md_for_all_rows(memory_dir):
    add_main({"name": "e1", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    add_main({"name": "e2", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    (md_dir() / "e1.md").unlink()
    res = main({})
    assert res["exported"] == 2
    assert (md_dir() / "e1.md").exists()
    assert (md_dir() / "e2.md").exists()
    assert index_path().exists()
