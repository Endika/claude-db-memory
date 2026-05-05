# Changelog

## [0.2.0](https://github.com/Endika/claude-db-memory/compare/v0.1.0...v0.2.0) (2026-05-05)


### Features

* **cli:** argparse dispatcher for memory subcommands ([1064767](https://github.com/Endika/claude-db-memory/commit/10647670e6eeb36c9564ad20f76e8b51837ad264))
* **config:** check config file test ([8f22c58](https://github.com/Endika/claude-db-memory/commit/8f22c588e9f081f9122cbb6cf3954f64506fbccb))
* **db:** SQLite schema with FTS5 and CRUD helpers ([56f0801](https://github.com/Endika/claude-db-memory/commit/56f0801b97eab2b7167ede1f76f79aa71461355f))
* **mcp:** expose operations as MCP tools via FastMCP ([6bbc224](https://github.com/Endika/claude-db-memory/commit/6bbc224b80dd07f7ca404e270cb7f7da0a69af88))
* **md_sync:** parse, write, and index Markdown memories ([06e4e24](https://github.com/Endika/claude-db-memory/commit/06e4e249bc5ccbca7e7c4d8024570a057f934465))
* **models:** Memory dataclass with name/type validation ([f7e8f65](https://github.com/Endika/claude-db-memory/commit/f7e8f65e4c3f9d8651773a5c3b9a20344a0ab93d))
* **ops:** add memory creates row, .md, and updates index ([55caf6c](https://github.com/Endika/claude-db-memory/commit/55caf6c6bc38ed0b87f7f382c93d5368f97de0b5))
* **ops:** delete memory removes row, .md, and reindex ([f256481](https://github.com/Endika/claude-db-memory/commit/f256481daa731d652ff40c1aeec2fb6a0f5ac2f8))
* **ops:** export forces .md regeneration from DB ([ceda7ab](https://github.com/Endika/claude-db-memory/commit/ceda7abe3698d25f61f765e1f25c6b0813df0b00))
* **ops:** full-text search via FTS5 with snippet and bm25 ranking ([3b0b51e](https://github.com/Endika/claude-db-memory/commit/3b0b51e33d1091c253f4e4b838acc32668968c48))
* **ops:** get memory by id or name ([b227f32](https://github.com/Endika/claude-db-memory/commit/b227f32988dd72fc1c4661020b2efba8ba6b74a6))
* **ops:** list memories with filters and pagination ([e0aa89d](https://github.com/Endika/claude-db-memory/commit/e0aa89dfe9f3fb42731e2ea279e431c1a3fc50d8))
* **ops:** reindex rebuilds SQLite from .md files ([ab4a0ab](https://github.com/Endika/claude-db-memory/commit/ab4a0ab990c8fe11181f7e4b6543c2a1c1cad055))
* **ops:** update memory with field validation and reindex ([da2f19b](https://github.com/Endika/claude-db-memory/commit/da2f19b3e0097512c3700022bf9840e20897b511))
* **ops:** verify reports orphans and drift between .md and DB ([7454642](https://github.com/Endika/claude-db-memory/commit/745464233012cb3816073350cede51d30bf675ed))
* **plugin:** plugin manifest and README ([17c35c4](https://github.com/Endika/claude-db-memory/commit/17c35c4fbd50570a0fadcad1341df735a16bcf54))


### Bug Fixes

* **md_sync:** restrict bare-string fallback to known string fields ([9e32ad1](https://github.com/Endika/claude-db-memory/commit/9e32ad1b5bf8ad9293e30b289e9a003416c790fc))


### Documentation

* replace placeholder with actual GitHub user ([49614bc](https://github.com/Endika/claude-db-memory/commit/49614bce3b2fcd88c2b9d176e4d0f72ff3225e2e))

## [0.1.0] - 2026-05-05

### Added
- Initial release.
- SQLite + FTS5 backed memory store.
- MCP tools: add, search, get, update, delete, list, reindex, verify.
- CLI: `memory` with subcommands matching MCP tools, plus `export`.
- Markdown backup layer with auto-regenerated `MEMORY.md` index.
- Per-workspace storage by default; override via `CLAUDE_DB_MEMORY_DIR`.
- Claude Code plugin manifest at `.claude-plugin/plugin.json`.
- GitHub Actions CI on Python 3.9–3.12.
- Developer tooling: Makefile with `install`, `test`, `lint`, `format`, `type-check`, `check`, `clean` targets. Ruff + mypy configured in `pyproject.toml`.
- WAL journal mode and 5s busy timeout for safer concurrent CLI/MCP use.
- 'verify --fix' flag accepted; reports "not yet implemented" with guidance until v0.2.

### Fixed
- Index-regeneration callers (add, update, delete, reindex) now pass an explicit unbounded limit to list_all so MEMORY.md never silently truncates past 1000 memories.
