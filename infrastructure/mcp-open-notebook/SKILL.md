---
name: mcp-open-notebook
description: Search or write to open-notebook, the fleet-wide knowledge base, via the `kb` CLI (~/.local/bin/kb) or the raw open-notebook MCP/API at http://192.168.68.90:5055. Use whenever a task needs to search prior lessons/handoffs/runbooks/project state, or needs to persist a finding so future sessions and other agents can find it. Also use when a `kb write -n handoffs` or `kb search -n handoffs` call seems to return the wrong content — there is a known notebook-name collision documented below.
---

# open-notebook (the `kb` CLI)

`kb` (`~/.local/bin/kb`, 462 lines, Python) is the wrapper every skill and
agent is supposed to use instead of hand-rolling curl against open-notebook's
REST API at `http://192.168.68.90:5055` (`$OPEN_NOTEBOOK_URL`). Read it
directly (`cat ~/.local/bin/kb`) if this skill goes stale — it's short enough
to re-verify in under a minute.

```
kb search <query> [--notebook N] [--notebooks N1,N2] [--limit N] [--all] [--show-source] [--force]
kb write --notebook N --title T --file F     # upsert by title
kb write --notebook N --title T --text "..."  # inline
kb cache stats / kb cache clear [--notebook N]
```

## The one critical landmine: `-n handoffs` does NOT go where you think

**`kb`'s alias table silently redirects `-n handoffs` to the `projects`
notebook — even though a REAL, separate notebook literally named `handoffs`
also exists and is unreachable through this CLI.** Confirmed live
(2026-10-01): `kb search "..." -n handoffs` and `kb search "..." -n projects`
return byte-identical results, both tagged `[projects]` in `--show-source`
output. `kb`'s `ALIASES` dict (around line 52) maps `handoffs → projects` and
`portfolio → projects`. This is a real bug in the tool, not a misunderstanding
— see helmsman lesson #4035.

**Practical implication:** if a skill or your own habit says `kb write -n
handoffs -t "..."`, it is actually writing to `projects`. This isn't wrong
*enough* to break anything (projects is a reasonable place for session
handoffs to live), but it means the real `handoffs` notebook
(`notebook:zkmvn6u0bre5vj68cgpl`) is currently dead weight — nothing written
through the CLI's `-n` flag can ever reach it under its own name. If you
specifically need that notebook, you must call the raw API with its ID, not
`kb -n handoffs`. Don't "fix" this yourself by guessing at the alias table —
check whether it's been patched since 2026-10-01 before assuming either
behavior.

Full real alias table as of this writing (`grep -A 10 "^ALIASES" ~/.local/bin/kb`):
```
rules, scheduled→tools-kb, tickets/bugs/features→tickets-kb,
diagnostics→diagnostics-kb, runbooks→runbooks-kb, agents→agents-core-kb,
standards→standards-security-kb, handoffs/portfolio→projects, tech→tech-kb,
scratchpad/scratch→agent-scratchpad
```
Any notebook name NOT in this table resolves literally (e.g. `-n lessons`
really does hit the `lessons` notebook — only the aliased names redirect).

## Write-then-search can return stale results — no cache invalidation on write

`kb write` never touches the query cache. Searches cache to
`/tmp/kb-cache/` with a 24h TTL (7 days for the three "stable" notebooks:
`tech-kb`, `templates-kb`, `rules-kb`). If you write a note and then
immediately search for it in the same session, a cached result from before
the write can shadow it for up to 24 hours. **Always pass `--force` when
verifying something you just wrote**, or when the content needs to be fresh
(e.g. checking whether a lesson you just filed is actually searchable).

## Write behavior you should know before calling it

- **Upsert is by exact title match**, case-sensitive, against notes already
  in that notebook (`cmd_write` fetches `/api/notes?notebook_id=X`, builds a
  `title -> id` map, and does `PUT` on exact match or `POST` otherwise). A
  near-duplicate title (different capitalization, trailing punctuation)
  creates a second note instead of updating the first — if you want "always
  update the same note," reuse the exact title string every time, verbatim.
- **Content is truncated at 180,000 characters** on write
  (`content[:180000]`) with no warning if your input was longer — if writing
  a large file, check its size first; silent truncation produces a note that
  looks complete but cuts off mid-sentence.
- **Credential-scrubbing is mandatory and can hard-refuse the write.** Every
  body is passed through `scrub()` (strips common key/token/secret patterns,
  base64-looking 40+ char blobs, basic-auth URLs) and then re-checked by a
  `RESIDUAL` regex; if anything still looks credential-shaped after
  scrubbing, `kb write` exits with an error rather than publishing. If you
  hit this and the content is NOT actually a secret (e.g. a long hash, a
  non-secret token-like ID), you'll need to reformat it (e.g. wrap in
  backticks won't help — break up the exact pattern, like inserting a space)
  rather than fight the regex blind.

## Notebook list is large and growing — always check live, don't guess from memory

As of 2026-10-01 there are 70+ notebooks (`curl -s
http://192.168.68.90:5055/api/notebooks`), including per-agent scratch
notebooks (`agent-talos`, `agent-helmsman`, `agent-b3ck`, etc.), per-domain
KBs (`security-kb`, `product-kb`, `api-design-kb`...), and project-specific
ones (`hone-kb`, `stdout-kb`, `bridge-kb`). Don't assume a notebook exists or
guess its exact name — query the list or use `kb search --all` to search
across everything if you're not sure which notebook holds what you want.

## Query logging and caching are best-effort, not an API contract

`kb search` appends one JSON line per query to `~/.kb-queries.log`
(timestamp, query, notebook, result count, latency, top score, cache hit) —
useful for auditing what's actually been searched, but writes are wrapped in
a bare `except: pass`, so a broken log file never breaks a query. Same
pattern for the disk cache (`get_cache`/`set_cache` silently no-op on any
I/O error) — don't rely on either for anything load-bearing; they're
performance/observability conveniences, not guarantees.

## Quick self-check for this skill

```bash
# Confirm the handoffs/projects collision is still live before trusting this section:
diff <(kb search "test" -n handoffs -l 1 --show-source 2>&1) \
     <(kb search "test" -n projects -l 1 --show-source 2>&1)
# Empty diff = bug still present. Non-empty = it's been fixed, update this skill.
```
