---
name: mcp-vault
description: Read and search the SeaynicNet Obsidian vault via the `vault` MCP server (raw note read/search/list). Use when you need direct access to vault notes by path, or to search across Projects/Standards/Research/Ideas for keywords. Distinct from `audit-vault` which is a higher-level workflow that compares vault state against code repos.
---

# Obsidian Vault MCP (vault)

The `vault` MCP server (proxy name `vault`, Python bridge at `/Volumes/data/containers/n8n-control/state/helmsman-state/vault_mcp_bridge.py`) exposes **read-only** access to the iCloud-synced Obsidian vault on the mac. The bridge runs locally, reads files directly from `/Users/charlieseay/Library/Mobile Documents/iCloud~md~obsidian/Documents/SeaynicNet/`, and forwards requests via stdio to mcp-proxy.

**Auth note:** No auth required — this is local filesystem access. The bridge enforces `_safe_path()` to block directory traversal, but any agent can read files in the vault that are under `VAULT_ROOT` and in the searchable directories.

**Relationship to other vault workflows:**
- This MCP exposes the **raw read/search/list primitives** (vault_read, vault_search, vault_list_folders, vault_list_notes)
- `audit-vault` is a **higher-level workflow** that uses this MCP + repo state to detect drift and suggest fixes
- `kb` (open-notebook CLI) searches the **fleet-wide knowledge base**, not this local vault
- These are three separate systems; don't confuse them

## The one critical design principle: searchable vs. non-searchable directories

**SEARCHABLE_DIRS** (vault_search only digs here) per vault_mcp_bridge.py:27:
```python
SEARCHABLE_DIRS = ["Projects", "Standards", "Research", "Ideas", "Agents", "Personas", "Templates"]
```

**Practical implication:** if a note lives outside these dirs (e.g., `Archive/`, `Daily/`, `Attachments/`), `vault_search()` will never find it, even if the note exists. You **can** still read it with `vault_read()` if you know its path, but search won't find it. This is intentional — it keeps search fast and focused.

## Tool catalog (4 tools, confirmed live 2026-10-01 against /Volumes/data/containers/n8n-control/state/helmsman-state/vault_mcp_bridge.py:133-186)

**Search across vault:**
- `vault_search(query, max_results=20)` — grep for a keyword/phrase across all .md files in SEARCHABLE_DIRS
  - Case-insensitive pattern matching via `re.compile(re.escape(query), re.IGNORECASE)`
  - Returns markdown list: `- \`file/path\` (L123): matching line (truncated to 200 chars)`
  - Line numbers included so you can find context quickly
  - `max_results` clamped to 1-50 (default 20); stops at first match per directory
  - Returns `"No matches found for \`query\`."` if nothing matches (not an error)
  - **Only searches:** Projects/, Standards/, Research/, Ideas/, Agents/, Personas/, Templates/

**Read single note:**
- `vault_read(path)` — read a single note by vault-relative path
  - `path` is relative to vault root, e.g., `Projects/Lab/foo.md` or `Standards/deployment.md`
  - Returns full markdown content as a single string
  - **Size cap:** 200 KB per read (MAX_FILE_SIZE = 200_000 bytes per vault_mcp_bridge.py:28)
  - If file larger than 200 KB: returns error `"Error: file too large (X bytes, max 200000). Use vault_search to find specific lines."`
  - Returns error if path is outside vault, doesn't exist, or is not a file
  - **Path traversal protection:** `_safe_path()` rejects any path that resolves outside VAULT_ROOT, even with `../` tricks

**Browse vault structure:**
- `vault_list_folders(path="")` — list immediate subfolders (non-recursive)
  - `path` defaults to empty string, which lists vault root level
  - Returns markdown list: `- Folder1`, `- Folder2`, etc., sorted alphabetically
  - Excludes hidden folders (those starting with `.`)
  - Returns `"No subfolders in (root)"` if empty

- `vault_list_notes(folder, max_count=50)` — list .md files in a specific folder (non-recursive)
  - `folder` required (relative to vault root), e.g., `Projects` or `Projects/Lab/Apps`
  - Returns markdown list of .md files only: `- note1.md`, `- note2.md`, etc., sorted alphabetically
  - `max_count` clamped to 1-200 (default 50); useful for large folders
  - Returns `"No .md files in folder"` if empty
  - Returns error if `folder` doesn't exist or isn't a directory

## Known vault structure facts (from vault root /Users/charlieseay/Library/Mobile Documents/iCloud~md~obsidian/Documents/SeaynicNet/)

- **Projects/** — project notes (handoffs, README, architecture, status)
  - **Projects/Lab/** — infrastructure & tooling lab
  - **Projects/Talos/** — Talos (ICM) notes
  - **Projects/Hone/** — Hone learning platform
  - etc.
- **Standards/** — deployment, security, and operational standards
- **Research/** — technical research, explorations, papers
- **Ideas/** — raw ideas, brainstorms, product concepts
- **Agents/** — agent briefs, routing, personas
- **Personas/** — character / persona definitions
- **Templates/** — note templates, boilerplate
- **Daily/** (exists but NOT searchable via vault_search)
- **Archive/** (exists but NOT searchable via vault_search)

Full directory structure can be discovered via `vault_list_folders("")` then recursive calls to `vault_list_folders(each_folder)`.

## Real error modes confirmed by reading source (2026-10-01)

**Query validation** (vault_mcp_bridge.py:49-50):
```python
if not query or not query.strip():
    return "Error: query is required"
```
Empty query returns this error, not a no-matches result.

**Path traversal blocking** (vault_mcp_bridge.py:32-41):
```python
def _safe_path(rel_path: str) -> Path | None:
    if not rel_path:
        return None
    candidate = (VAULT_ROOT / rel_path).resolve()
    try:
        candidate.relative_to(VAULT_ROOT.resolve())
    except ValueError:
        return None  # Out of bounds
    return candidate
```
Any `..` or absolute path that escapes VAULT_ROOT returns None, which becomes an error: `"Error: invalid or out-of-vault path: ..."`

**File size enforcement** (vault_mcp_bridge.py:90-91):
```python
if full.stat().st_size > MAX_FILE_SIZE:
    return f"Error: file too large ({...} bytes, max {MAX_FILE_SIZE}). Use vault_search to find specific lines."
```
Large files are rejected outright; there's no streaming or pagination. For a 200 KB+ note, search for the specific section first, then ask what the exact filename+folder path is, and whether it's under 200 KB.

**Directory that doesn't exist** (vault_mcp_bridge.py:102):
```python
if base is None or not base.exists() or not base.is_dir():
    return f"Error: not a directory: {path or '(root)'}"
```
vault_list_folders/vault_list_notes both return this error for missing folders.

## Gotchas and design tradeoffs

**vault_search only looks in SEARCHABLE_DIRS** — if you're looking for something in Archive or Daily, you must know the exact path and use `vault_read()` directly (and it must be under 200 KB).

**Results truncated to 200 chars per matching line** — vault_search shows only the first 200 characters of each matching line. If you need the full context, use `vault_read()` on the file path returned.

**max_results stops at first match per directory** — if you search for "foo" with max_results=5, and Projects/ has 5+ matches, the search returns those 5 and stops without checking Standards/, Research/, etc. To get matches from all directories, you may need to call search multiple times with different queries or check each directory manually.

**Case-insensitive search only** — no regex support, only literal string + case-insensitive matching. Query is escaped (`re.escape()`) so special regex chars are treated literally.

**I/O errors are silent** — if a file is unreadable (permissions, encoding issues), the search skips it and continues. You won't be warned of skipped files; the result is just fewer matches than expected.

## Quick verification pattern for this skill

```bash
# Test that vault is reachable and contains expected directories
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"vault_list_folders","arguments":{"path":""}}}' | \
  /opt/homebrew/bin/python3.13 /Volumes/data/containers/n8n-control/state/helmsman-state/vault_mcp_bridge.py 2>/dev/null | \
  python3 -c "import sys, json; r = json.load(sys.stdin); print('PASS: vault reachable' if 'result' in r and 'content' in r['result'] else 'FAIL')"

# Test that a known search query finds results (requires vault.md or similar to exist)
# This is difficult to test generically, but a search for "test" should find something:
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"vault_search","arguments":{"query":"test","max_results":1}}}' | \
  /opt/homebrew/bin/python3.13 /Volumes/data/containers/n8n-control/state/helmsman-state/vault_mcp_bridge.py 2>/dev/null | \
  grep -q "Found\|No matches" && echo "PASS: vault_search responds" || echo "FAIL"
```

If these fail:
- Check that the vault path exists and is synced (iCloud may have not synced)
- Check that vault_mcp_bridge.py is still at the expected location
- Check that the bridge's Python dependencies (pathlib, json, re — all stdlib) are available
