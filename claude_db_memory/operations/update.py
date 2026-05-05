from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from claude_db_memory import db
from claude_db_memory.md_sync import write_md, regenerate_index


def main(args: dict[str, Any]) -> dict[str, Any]:
    key = args["id_or_name"]
    fields = dict(args["fields"])
    fields["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conn = db.connect()
    m = None
    if key.isdigit():
        m = db.get_by_id(conn, int(key))
    if m is None:
        m = db.get_by_name(conn, key)
    if m is None:
        raise KeyError(f"Memory not found: {key}")
    db.update_memory(conn, m.id, fields)
    updated = db.get_by_id(conn, m.id)
    write_md(updated)
    regenerate_index(db.list_all(conn))
    return asdict(updated)
