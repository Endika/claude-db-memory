import pytest

from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.get import main


def test_get_by_name(memory_dir):
    add_main({"name": "n1", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    res = main({"id_or_name": "n1"})
    assert res["name"] == "n1"
    assert res["body"] == "b"


def test_get_by_id(memory_dir):
    res_add = add_main({"name": "n2", "type": "note", "description": "d", "body": "b",
                        "tags": [], "project": None})
    res = main({"id_or_name": str(res_add["id"])})
    assert res["name"] == "n2"


def test_get_missing_raises(memory_dir):
    with pytest.raises(KeyError):
        main({"id_or_name": "does_not_exist"})
