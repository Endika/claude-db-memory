import pytest

from claude_db_memory.config import md_dir
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.delete import main


def test_delete_removes_row_and_md(memory_dir):
    add_main(
        {"name": "d1", "type": "note", "description": "d", "body": "b", "tags": [], "project": None}
    )
    md = md_dir() / "d1.md"
    assert md.exists()
    res = main({"id_or_name": "d1"})
    assert res["deleted"] is True
    assert not md.exists()


def test_delete_missing_raises(memory_dir):
    with pytest.raises(KeyError):
        main({"id_or_name": "missing"})
