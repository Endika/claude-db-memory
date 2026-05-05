from __future__ import annotations

import argparse
import json
import sys

from claude_db_memory.operations import (
    add as add_op,
    delete as delete_op,
    export as export_op,
    get as get_op,
    list_ as list_op,
    reindex as reindex_op,
    search as search_op,
    update as update_op,
    verify as verify_op,
)


def _parse_tags(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]


def _emit(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="Output JSON")

    p = argparse.ArgumentParser(prog="memory", parents=[common])
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", parents=[common])
    a.add_argument("--name", required=True)
    a.add_argument("--type", required=True)
    a.add_argument("--description", required=True)
    a.add_argument("--body", required=True)
    a.add_argument("--tags", default=None, help="comma-separated")
    a.add_argument("--project", default=None)

    g = sub.add_parser("get", parents=[common])
    g.add_argument("id_or_name")

    lst = sub.add_parser("list", parents=[common])
    lst.add_argument("--type", default=None)
    lst.add_argument("--project", default=None)
    lst.add_argument("--limit", type=int, default=20)
    lst.add_argument("--offset", type=int, default=0)

    d = sub.add_parser("delete", parents=[common])
    d.add_argument("id_or_name")

    s = sub.add_parser("search", parents=[common])
    s.add_argument("query")
    s.add_argument("--type", default=None)
    s.add_argument("--project", default=None)
    s.add_argument("--limit", type=int, default=10)

    u = sub.add_parser("update", parents=[common])
    u.add_argument("id_or_name")
    u.add_argument("--description", default=None)
    u.add_argument("--body", default=None)
    u.add_argument("--tags", default=None)
    u.add_argument("--project", default=None)
    u.add_argument("--type", default=None)

    sub.add_parser("reindex", parents=[common])

    v = sub.add_parser("verify", parents=[common])
    v.add_argument("--fix", action="store_true")

    sub.add_parser("export", parents=[common])
    return p


def _dispatch(ns: argparse.Namespace) -> dict:
    if ns.cmd == "add":
        return add_op.main({
            "name": ns.name, "type": ns.type,
            "description": ns.description, "body": ns.body,
            "tags": _parse_tags(ns.tags), "project": ns.project,
        })
    if ns.cmd == "get":
        return get_op.main({"id_or_name": ns.id_or_name})
    if ns.cmd == "list":
        return list_op.main({
            "type": ns.type, "project": ns.project,
            "limit": ns.limit, "offset": ns.offset,
        })
    if ns.cmd == "delete":
        return delete_op.main({"id_or_name": ns.id_or_name})
    if ns.cmd == "search":
        return search_op.main({
            "query": ns.query, "type": ns.type,
            "project": ns.project, "limit": ns.limit,
        })
    if ns.cmd == "update":
        fields: dict = {}
        for k in ("description", "body", "project", "type"):
            v = getattr(ns, k)
            if v is not None:
                fields[k] = v
        if ns.tags is not None:
            fields["tags"] = _parse_tags(ns.tags)
        return update_op.main({"id_or_name": ns.id_or_name, "fields": fields})
    if ns.cmd == "reindex":
        return reindex_op.main({})
    if ns.cmd == "verify":
        return verify_op.main({})
    if ns.cmd == "export":
        return export_op.main({})
    raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        ns = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2
    try:
        result = _dispatch(ns)
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _emit(result, getattr(ns, "json", False))
    return 0
