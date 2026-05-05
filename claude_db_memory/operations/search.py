from __future__ import annotations

from typing import Any

from claude_db_memory import db


def main(args: dict[str, Any]) -> dict[str, Any]:
    query = args["query"]
    type_ = args.get("type")
    project = args.get("project")
    limit = int(args.get("limit") or 10)
    conn = db.connect()
    sql = """
        SELECT m.id, m.name, m.type, m.description, m.project,
               snippet(memories_fts, -1, '[', ']', '...', 10) AS snippet,
               bm25(memories_fts) AS score
        FROM memories_fts
        JOIN memories m ON m.id = memories_fts.rowid
        WHERE memories_fts MATCH ?
    """
    params: list = [query]
    if type_:
        sql += " AND m.type = ?"
        params.append(type_)
    if project:
        sql += " AND m.project = ?"
        params.append(project)
    sql += " ORDER BY score LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    items = [
        {
            "id": r["id"], "name": r["name"], "type": r["type"],
            "description": r["description"], "project": r["project"],
            "snippet": r["snippet"], "score": r["score"],
        }
        for r in rows
    ]
    return {"items": items}
