import pytest

from claude_db_memory.config import md_dir
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.update import main


def test_update_changes_description_and_md(memory_dir):
    add_main({"name": "u1", "type": "note", "description": "old", "body": "b",
              "tags": [], "project": None})
    res = main({"id_or_name": "u1", "fields": {"description": "new"}})
    assert res["description"] == "new"
    md = (md_dir() / "u1.md").read_text()
    assert "new" in md


def test_update_missing_raises(memory_dir):
    with pytest.raises(KeyError):
        main({"id_or_name": "missing", "fields": {"description": "x"}})


def test_update_rejects_unknown_field(memory_dir):
    add_main({"name": "u2", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    with pytest.raises(ValueError):
        main({"id_or_name": "u2", "fields": {"unknown_field": "x"}})
