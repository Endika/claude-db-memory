from __future__ import annotations

from typing import Any

from claude_db_memory import db
from claude_db_memory.md_sync import delete_md, regenerate_index


def main(args: dict[str, Any]) -> dict[str, Any]:
    key = args["id_or_name"]
    conn = db.connect()
    m = None
    if key.isdigit():
        m = db.get_by_id(conn, int(key))
    if m is None:
        m = db.get_by_name(conn, key)
    if m is None:
        raise KeyError(f"Memory not found: {key}")
    db.delete_memory(conn, m.id)
    delete_md(m.name)
    regenerate_index(db.list_all(conn))
    return {"deleted": True, "name": m.name}
