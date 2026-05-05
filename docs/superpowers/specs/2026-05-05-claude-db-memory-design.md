# claude-db-memory — Design Spec

- **Date:** 2026-05-05
- **Status:** Draft (pending review)
- **Author:** brainstorming session with Claude Code

## 1. Summary

`claude-db-memory` is a Claude Code plugin that replaces the native flat-file memory system with a SQLite-backed long-term memory store offering full-text search, structured filtering, and a Markdown backup layer. It is designed to scale beyond the ~200-line auto-load truncation limit of Claude Code's native memory while remaining compatible with it.

Distribution target: open-source GitHub repository, installable as a Claude Code plugin by any user.

## 2. Motivation

The native auto-memory system stores knowledge as Markdown files indexed by `MEMORY.md`, which Claude Code auto-loads into the system prompt at session start. This works at small scale but has structural limits:

- `MEMORY.md` is truncated after ~200 lines, so memories beyond that limit silently disappear from context.
- No search: finding relevant memories requires scanning the full index manually.
- No structured filtering by type, project, tags, or recency.
- No safe way to grow knowledge beyond a few dozen entries without losing access to it.

This plugin removes those limits while preserving compatibility with the native auto-load mechanism.

## 3. Goals

- Provide a SQLite + FTS5 backed memory store with CRUD operations exposed via MCP and CLI.
- Generate a compact, auto-managed `MEMORY.md` index that fits within Claude Code's auto-load budget regardless of total memory count.
- Maintain a Markdown backup layer (`.md` files) as the human-readable, git-versionable safety net.
- Be installable as a single-command Claude Code plugin with zero non-stdlib runtime dependencies.
- Offer integrity verification and reindex commands so the system is self-healing.

## 4. Non-goals

- **Vector / semantic search.** Out of scope for v1. FTS5 covers the bulk of search needs. Vector support (sqlite-vec + embeddings) is deferred to a future version as an additive feature.
- **Replacing Claude Code's native memory mechanism.** The plugin lives alongside it and feeds into the same `MEMORY.md` auto-load convention.
- **Cross-machine sync.** Each install has a local SQLite. Users who want sync can git-version the `.md` backup directory.
- **GUI.** CLI + MCP only.
- **Multi-tenant / multi-user.** Single-user, local-first.

## 5. Architecture

### High-level diagram

```
+--------------+        MCP protocol        +-----------------+
| Claude Code  | <------------------------> |  mcp_server.py  |
+--------------+                            +-----------------+
                                                    |
+--------------+   python scripts/<op>.py   +-----------------+
|  User (CLI)  | -------------------------> |   scripts/*.py  |
+--------------+                            +-----------------+
                                                    |
                                            +-----------------+
                                            |     lib/db.py   |
                                            |   lib/md_sync.py|
                                            |   lib/config.py |
                                            +-----------------+
                                                    |
                          +-------------------------+--------------------------+
                          |                         |                          |
                  +---------------+         +----------------+        +----------------+
                  |  memory.db    |         |  memories/     |        |  MEMORY.md     |
                  | (SQLite+FTS5) |         |  (.md backup)  |        | (auto-loaded   |
                  | local, gitig) |         | (git optional) |        |  index)        |
                  +---------------+         +----------------+        +----------------+
```

### Components

- **`mcp_server.py`** — Thin MCP server (~50 lines). Registers tools that dispatch to `scripts/<op>.py` via `subprocess.run`. Returns the script's stdout as the tool result.
- **`scripts/<op>.py`** — One file per operation (`add`, `search`, `get`, `update`, `delete`, `list`, `reindex`, `verify`, `export`). Each is independently runnable from the terminal as a CLI utility.
- **`lib/db.py`** — SQLite connection management, schema creation, FTS5 virtual table setup, sync triggers.
- **`lib/md_sync.py`** — Parsing and serializing `.md` files, regenerating `MEMORY.md`.
- **`lib/config.py`** — Path resolution (env vars, defaults, per-workspace mapping).
- **`lib/models.py`** — `Memory` dataclass and validation.

### Why subprocess instead of in-process

With FTS5-only (no embedding model state to share), subprocess overhead is ~100ms — negligible for human-paced operations. The benefit is that each script is also a standalone CLI tool, testable and runnable without the MCP layer. If embeddings are added in v2, the architecture can migrate to in-process without breaking the external API.

## 6. Data model

### Table `memories`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK AUTOINCREMENT | |
| `name` | TEXT UNIQUE NOT NULL | Slug, e.g. `feedback_commits`. Maps to `<name>.md` |
| `type` | TEXT NOT NULL | One of: `user`, `feedback`, `project`, `reference`, `note` |
| `description` | TEXT NOT NULL | One-line summary. Used in `MEMORY.md` index |
| `body` | TEXT NOT NULL | Full Markdown content |
| `tags` | TEXT | JSON array, e.g. `["python", "auth"]` |
| `project` | TEXT | Optional, for filtering |
| `created_at` | TEXT NOT NULL | ISO 8601 |
| `updated_at` | TEXT NOT NULL | ISO 8601 |
| `source_file` | TEXT NOT NULL | Relative path to backup `.md` |

Constraints:

- `type` is enforced via `CHECK` constraint to keep the enum stable.
- `name` is unique and `[a-z0-9_]+` (validated at insert time, not via DB constraint, to allow clearer error messages).

### Virtual table `memories_fts` (FTS5)

Indexes: `name`, `description`, `body`, `tags`, `project`.

Maintained by triggers `AFTER INSERT`, `AFTER UPDATE`, and `AFTER DELETE` on `memories`. The triggers keep `memories_fts` in lockstep with `memories` without application-level coordination.

### Migrations

A `schema_version` table holds a single integer. On startup, `lib/db.py` reads it and applies migrations in order if needed. v0.1.0 ships at version 1.

## 7. API surface

### MCP tools

| Tool | Parameters | Returns |
|---|---|---|
| `add_memory` | `name, type, description, body, tags?, project?` | `{id, name}` |
| `search_memory` | `query, type?, project?, limit?=10` | `[{id, name, type, description, snippet, score}]` |
| `get_memory` | `id_or_name` | Full `Memory` object |
| `update_memory` | `id_or_name, fields` | Updated `Memory` |
| `delete_memory` | `id_or_name` | `{deleted: true}` |
| `list_memories` | `type?, project?, limit?=20, offset?=0` | `{items: [...], total}` |
| `reindex` | — | `{rebuilt: N, errors: [...]}` |
| `verify` | — | `{orphan_rows: [...], orphan_files: [...], drift: [...]}` |

### CLI

```bash
memory add --type feedback --name commits --description "..." --body "..." [--tags "a,b"] [--project X]
memory search "tramita" [--type project] [--project X] [--limit 5]
memory get commits
memory update commits --description "new"
memory delete commits
memory list [--type feedback] [--project X]
memory reindex
memory verify [--fix]
memory export
```

CLI is a single entrypoint (`memory`) installed via `pyproject.toml` `[project.scripts]`, e.g. `memory = "claude_db_memory.cli:main"`. The CLI dispatcher imports the same `scripts/<op>.py` modules used by the MCP. Output is human-readable by default; JSON with `--json` for piping.

## 8. File layout (repo)

```
claude-db-memory/
├── .claude-plugin/
│   └── plugin.json
├── mcp_server.py
├── scripts/
│   ├── add.py
│   ├── search.py
│   ├── get.py
│   ├── update.py
│   ├── delete.py
│   ├── list_.py
│   ├── reindex.py
│   ├── verify.py
│   └── export.py
├── lib/
│   ├── __init__.py
│   ├── db.py
│   ├── md_sync.py
│   ├── config.py
│   └── models.py
├── tests/
│   ├── conftest.py
│   ├── test_db.py
│   ├── test_add.py
│   ├── test_search.py
│   ├── test_sync.py
│   ├── test_reindex.py
│   └── test_verify.py
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── .gitignore
```

`.gitignore` includes `*.db`, `*.db-wal`, `*.db-shm`, `__pycache__/`, `.venv/`.

## 9. Storage layout (per install)

Default path resolution in `lib/config.py`:

```python
def resolve_memory_dir() -> Path:
    if env := os.getenv("CLAUDE_DB_MEMORY_DIR"):
        return Path(env)
    workspace = Path.cwd().resolve()
    encoded = str(workspace).replace("/", "-")
    return Path.home() / ".claude" / "projects" / encoded / "memory"
```

This makes the default per-workspace path identical to the one Claude Code already uses for native memory, so `MEMORY.md` is auto-loaded without further configuration.

Resulting layout:

```
~/.claude/projects/<workspace>/memory/
├── MEMORY.md            # auto-generated, auto-loaded by Claude Code
├── memory.db            # SQLite, gitignored
└── memories/            # .md backup files
    ├── feedback_*.md
    ├── project_*.md
    └── ...
```

For users who prefer a single global memory across workspaces, setting `CLAUDE_DB_MEMORY_DIR=~/.claude/memory` overrides the default.

## 10. Sync mechanics

### Write path (`add` / `update`)

1. Validate input. Reject if `name` violates slug rules or `type` is unknown.
2. Insert/update row in `memories`. Triggers update `memories_fts`.
3. Serialize the memory to `memories/<name>.md` with frontmatter (`name`, `description`, `type`, `tags`, `project`, `created_at`, `updated_at`).
4. Regenerate `MEMORY.md` by querying all rows ordered by `(type, updated_at DESC)` and writing a one-line entry per memory.

### Delete path

1. Delete row from `memories` (cascade to `memories_fts` via trigger).
2. Delete `memories/<name>.md`.
3. Regenerate `MEMORY.md`.

### Reindex (recovery)

1. Delete `memory.db`.
2. Recreate schema.
3. Walk `memories/*.md`. For each: parse frontmatter + body, insert row.
4. Regenerate `MEMORY.md`.

This is the canonical recovery path when the SQLite file is lost or corrupted.

### Verify (drift detection)

For each `.md` file: check a row exists with matching content hash.
For each row in `memories`: check the corresponding `.md` exists.
Report:

- **Orphan rows**: row exists, no `.md`. Suggest exporting the row to disk.
- **Orphan files**: `.md` exists, no row. Suggest importing.
- **Drift**: both exist but content differs. Suggest which side to trust (default: `.md` wins, since it is the human-editable layer).

`verify --fix` resolves drift by trusting `.md` over the DB row (re-imports the file). Orphan files are imported into the DB. Orphan rows are exported to disk unless `--prune-orphans` is passed, in which case they are deleted from the DB.

### MEMORY.md generation

Always regenerated as a derived artifact, never edited by hand. Format:

```markdown
# Memory Index

## feedback
- [feedback_commits](memories/feedback_commits.md) — Never run git write operations
- [feedback_generated_files](memories/feedback_generated_files.md) — Don't edit auto-generated files
...

## project
- [project_tramita_frontend](memories/project_tramita_frontend.md) — Tramita lives in tramita-web
...
```

Sorted by type, then by `updated_at DESC` within each type. Designed to stay well under 200 lines even at hundreds of memories (one line each).

## 11. Plugin manifest

`.claude-plugin/plugin.json` (format to be verified against current Claude Code plugin docs at implementation time):

```json
{
  "name": "claude-db-memory",
  "version": "0.1.0",
  "description": "SQLite-backed long-term memory for Claude Code with FTS5 search and Markdown backup",
  "homepage": "https://github.com/<user>/claude-db-memory",
  "license": "MIT",
  "mcpServers": {
    "claude-db-memory": {
      "command": "python3",
      "args": ["${CLAUDE_PLUGIN_ROOT}/mcp_server.py"]
    }
  }
}
```

Installation by end users:

```bash
/plugin install github:<user>/claude-db-memory
```

Or manual:

```bash
git clone https://github.com/<user>/claude-db-memory ~/.claude/plugins/claude-db-memory
```

Claude Code detects the manifest and auto-registers the MCP server.

## 12. Configuration

| Variable | Default | Purpose |
|---|---|---|
| `CLAUDE_DB_MEMORY_DIR` | per-workspace path under `~/.claude/projects/.../memory` | Override storage root |
| `CLAUDE_DB_MEMORY_INDEX_LIMIT` | `200` | Hard cap on lines in generated `MEMORY.md` |
| `CLAUDE_DB_MEMORY_FTS_RANK` | `bm25` | FTS5 ranking function |

No config file is required. Environment variables only.

## 13. Testing strategy

- **Framework:** `pytest`. No other test deps in v1.
- **Isolation:** every test uses a `tmp_path` fixture; no test touches real user data.
- **Layers:**
  - Unit tests for each `lib/*.py` module.
  - Per-script tests under `tests/test_<op>.py` exercising both happy path and error cases.
  - Integration test: full lifecycle (`add` → `search` → `update` → `delete` → `reindex` → `verify`) on a synthetic dataset.
- **CI:** GitHub Actions workflow runs `pytest` on push and PR. Matrix: Python 3.9, 3.10, 3.11, 3.12.
- **Coverage targets:** ≥80% on `lib/`, ≥60% overall.

## 14. Token budget impact

Adding the MCP server costs roughly 400-800 tokens of permanent tool-schema overhead per session. Search and filtering reduce per-query token cost as memory volume grows. Net effect:

| Memory count | Net token impact |
|---|---|
| 5-20 | Slightly negative (overhead not yet amortized) |
| 20-80 | Break-even |
| 80-200 | Net positive |
| 200+ | Strongly positive (native system would be truncating) |

Token efficiency is a side benefit. The primary value is **scaling beyond the 200-line auto-load truncation** of the native system.

## 15. Open questions

1. Exact format and feature support of the current Claude Code `.claude-plugin/plugin.json` manifest needs verification against latest docs at implementation time.
2. Whether `MEMORY.md` should also include a tag cloud or stay strictly title-based.
3. Whether `.md` backup files should default to being git-tracked (currently leaning yes, but `memory.db` always gitignored).

## 16. Future work

- **v0.2 — sqlite-vec + embeddings**: additive layer for semantic search. Local (Ollama) or pluggable provider. Schema gains an `embedding BLOB` column, FTS5 stays.
- **v0.3 — broader knowledge ingestion**: indexing of project documentation, decision records, snippets.
- **v0.4 — sync / multi-machine**: optional cloud sync for teams (out of scope for personal use).

## 17. Implementation phasing

1. Repository scaffolding, `pyproject.toml`, license, gitignore, README skeleton.
2. `lib/config.py`, `lib/db.py`, `lib/models.py` with tests.
3. `lib/md_sync.py` (parse/serialize, MEMORY.md generation) with tests.
4. `scripts/add.py`, `scripts/get.py`, `scripts/list_.py`, `scripts/delete.py` with tests.
5. `scripts/search.py` (FTS5) with tests.
6. `scripts/update.py` with tests.
7. `scripts/reindex.py`, `scripts/verify.py`, `scripts/export.py` with tests.
8. `mcp_server.py` and end-to-end MCP integration test.
9. `.claude-plugin/plugin.json`, README, CHANGELOG, GitHub Actions CI.
10. Manual smoke test by installing the plugin in a real Claude Code session.
