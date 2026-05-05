from __future__ import annotations

from dataclasses import asdict
from typing import Any

from claude_db_memory import db


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
    return asdict(m)
