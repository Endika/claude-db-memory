from __future__ import annotations

from dataclasses import asdict
from typing import Any

from claude_db_memory import db


def main(args: dict[str, Any]) -> dict[str, Any]:
    conn = db.connect()
    type_ = args.get("type")
    project = args.get("project")
    limit = int(args.get("limit") or 20)
    offset = int(args.get("offset") or 0)
    items = db.list_all(conn, type_=type_, project=project, limit=limit, offset=offset)
    total_rows = conn.execute(
        "SELECT COUNT(*) FROM memories WHERE (? IS NULL OR type = ?) AND (? IS NULL OR project = ?)",
        (type_, type_, project, project),
    ).fetchone()[0]
    return {"items": [asdict(m) for m in items], "total": int(total_rows)}
