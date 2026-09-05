# Changelog

## [0.4.0](https://github.com/Endika/claude-db-memory/compare/v0.3.4...v0.4.0) (2026-09-05)


### Features

* **mcp:** migrate server from FastMCP to MCPServer and unpin mcp 2.x ([9880e0f](https://github.com/Endika/claude-db-memory/commit/9880e0f28966ef02ef8624f61eed1f23e8cfd32d))

## [0.3.4](https://github.com/Endika/claude-db-memory/compare/v0.3.3...v0.3.4) (2026-09-05)


### Bug Fixes

* pin mcp below 2 to keep the v1 FastMCP API ([20f9eb9](https://github.com/Endika/claude-db-memory/commit/20f9eb92ea48f0a6bf51c597bda8475836e59e1f))

## [0.3.3](https://github.com/Endika/claude-db-memory/compare/v0.3.2...v0.3.3) (2026-05-05)


### Documentation

* replace YAML data blocks with runnable memory add commands ([79a2067](https://github.com/Endika/claude-db-memory/commit/79a2067d800ecbcfad091ce788d885682515a51b))

## [0.3.2](https://github.com/Endika/claude-db-memory/compare/v0.3.1...v0.3.2) (2026-05-05)


### Documentation

* add 'When does this plugin make sense?' section with scaling table ([71ac819](https://github.com/Endika/claude-db-memory/commit/71ac8195881b1ad177ad7acdce350dd6bbe88167))
* replace examples with realistic scenarios and visual flow ([e338bc7](https://github.com/Endika/claude-db-memory/commit/e338bc7d851187f5c8988f523958058ec87f9c9d))

## [0.3.1](https://github.com/Endika/claude-db-memory/compare/v0.3.0...v0.3.1) (2026-05-05)


### Bug Fixes

* **plugin:** use github source type for wider Claude Code compatibility ([be9afd3](https://github.com/Endika/claude-db-memory/commit/be9afd37f768abc1d265eecaf7580e0fba561b5c))

## [0.3.0](https://github.com/Endika/claude-db-memory/compare/v0.2.0...v0.3.0) (2026-05-05)


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
* **plugin:** add marketplace.json so /plugin install works ([0f9edbf](https://github.com/Endika/claude-db-memory/commit/0f9edbf24311f744a6204acf653e8355fbe5198f))
* **plugin:** plugin manifest and README ([17c35c4](https://github.com/Endika/claude-db-memory/commit/17c35c4fbd50570a0fadcad1341df735a16bcf54))


### Bug Fixes

* **ci:** drop Python 3.9 (mcp requires &gt;=3.10) and catch format issues ([0f745f0](https://github.com/Endika/claude-db-memory/commit/0f745f09d193098a793b8deaa212ae2cc7d66178))
* **deps:** pin ruff and mypy to compatible ranges; reformat with ruff 0.15 ([504c675](https://github.com/Endika/claude-db-memory/commit/504c67595a119749e86a60704901732bb6547686))
* **md_sync:** restrict bare-string fallback to known string fields ([9e32ad1](https://github.com/Endika/claude-db-memory/commit/9e32ad1b5bf8ad9293e30b289e9a003416c790fc))


### Documentation

* replace placeholder with actual GitHub user ([49614bc](https://github.com/Endika/claude-db-memory/commit/49614bce3b2fcd88c2b9d176e4d0f72ff3225e2e))

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

* **ci:** drop Python 3.9 (mcp requires &gt;=3.10) and catch format issues ([6221248](https://github.com/Endika/claude-db-memory/commit/6221248bc9d742d2fa90daccf5b5b44866c807cf))
* **deps:** pin ruff and mypy to compatible ranges; reformat with ruff 0.15 ([67d09ee](https://github.com/Endika/claude-db-memory/commit/67d09ee1826191b7b307da3b9b5e26dc8dec8b7d))
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
