# Changelog

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
