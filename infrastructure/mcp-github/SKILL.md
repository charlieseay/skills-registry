---
name: mcp-github
description: Query and manage GitHub repositories, PRs, issues, and code via the `github` MCP server. Use when a task needs to search repositories, list/create issues or PRs, query file contents, or access GitHub Actions. This skill covers the local MCP wrapper; note that Claude Code sessions also have direct access to mcp__github__* tools (official remote server) for read-only queries.
---

# GitHub MCP Server

The `github` MCP server (proxy name `github`, wrapper script at
`/Users/charlieseay/.local/bin/github-mcp-wrapper`) wraps the official GitHub
MCP implementation (`github-mcp-server`). The wrapper automatically injects the
current `gh` CLI token from the system keyring:

```bash
# From the wrapper:
export GITHUB_PERSONAL_ACCESS_TOKEN=$(/opt/homebrew/bin/gh auth token)
exec /opt/homebrew/bin/github-mcp-server "$@"
```

**Auth:** Token is pulled fresh from system keyring every time the MCP server
starts. If you get auth errors, run `gh auth login` in a shell first to ensure
the token is current.

## Dual access paths in Claude Code

This session has **two** ways to access GitHub:

1. **Local MCP wrapper** (`mcp:github` via proxy) — Full read/write access via
   this MCP server
2. **Direct MCP tools** (`mcp__github__*`) — Official remote GitHub MCP server,
   pre-loaded in Claude Code sessions

Both connect to the same GitHub API and use the same auth. The direct tools are
faster for simple queries (no proxy overhead); the MCP wrapper is used when this
skill is invoked via the skill system. **Prefer the direct tools
(`mcp__github__search_repositories`, etc.) if available in your session.**

## Tool catalog (60+ tools available; common ones listed)

The wrapper is configured with `--toolsets
repos,issues,pull_requests,actions,dependabot,git` — enabling ~60 tools across
these domains. Use `tools/list` via the MCP proxy if this list feels stale.

### Repository operations

- `search_repositories` — Find repos by name, stars, language, topic
- `list_repository_collaborators` — List who has access to a repo
- `create_repository` — Create a new public/private repo
- `fork_repository` — Fork a repo to your account
- `get_file_contents` — Read a file or list a directory
- `create_or_update_file` — Create/edit a file (commits directly)
- `delete_file` — Remove a file (commits directly)
- `list_branches` — List branches in a repo
- `list_tags` — List release tags
- `list_commits` — List commits with filtering by author, path, date range
- `get_commit` — Get details of a specific commit (diff, message, files)

### Pull request operations

- `search_pull_requests` — Find PRs by title, author, state, label
- `list_pull_requests` — List PRs in a repo with filtering
- `create_pull_request` — Create a new PR (reads template if one exists)
- `update_pull_request` — Change PR title, body, state
- `merge_pull_request` — Merge a PR (options: merge, squash, rebase)
- `pull_request_read` — Get PR details (title, body, state, reviews, comments)
- `pull_request_review_write` — Manage PR reviews (create, comment, submit)
- `add_comment_to_pending_review` — Add line-level comments to a review

### Issue operations

- `search_issues` — Find issues by title, author, state, label, milestone
- `list_issues` — List issues in a repo with filtering
- `issue_write` — Create, edit, or close an issue
- `issue_read` — Get issue details (title, body, state, comments, reactions)
- `add_issue_comment` — Comment on an issue
- `get_label` — Get label details
- `list_issue_fields` — List custom fields (GitHub Projects)
- `list_issue_types` — List issue types in an org (GitHub Projects)

### Actions & workflows

- `list_workflows` — List CI/CD workflows in a repo
- `get_workflow_run` — Get status and logs of a workflow run
- `list_workflow_runs` — List workflow runs (filtering by status, branch)
- `trigger_workflow` — Manually trigger a workflow

### Code search

- `search_code` — Find code snippets across GitHub (global or per-repo)
- `search_commits` — Find commits by message, author, date
- `search_users` — Find GitHub users by name or bio
- `search_issues` — (see above; also works for code-related issues)

### Other

- `get_me` — Get authenticated user's profile
- `run_secret_scanning` — Scan a repo for exposed credentials
- `list_releases` — List releases and download URLs
- `request_copilot_review` — Ask GitHub Copilot to review code (if enabled)

## Key gotchas and configuration details

### 1. Token freshness

The wrapper pulls the token from the system keyring every time the MCP server
starts. If you see auth errors:

```bash
# Refresh token from gh CLI
gh auth login

# Or check current token validity
gh auth status
```

GitHub tokens expire; if you haven't used `gh` in weeks, your keyring token may
be stale. Re-authenticate and the MCP server will pick up the fresh one on next
use.

### 2. Toolsets are pre-selected; not all GitHub tools are enabled

The wrapper is hardcoded to `--toolsets repos,issues,pull_requests,actions,dependabot,git`.
Other toolsets (e.g., `organizations`, `discussions`, `secret_protection`) are
not loaded. If a task needs a tool outside these sets, file a decision to enable
it; don't guess that the tool exists.

**Available toolsets (for reference):**
```
actions, code_quality, code_security, copilot, dependabot, discussions,
gists, git, issues, labels, notifications, orgs, projects,
pull_requests, repos, secret_protection, security_advisories,
stargazers, users
```

### 3. `list_pull_requests` vs. `search_pull_requests`

- **`list_pull_requests`** — Simple retrieval of all PRs in a repo with basic
  filtering (state, branch, sort)
- **`search_pull_requests`** — Targeted queries (author, title text, labels,
  milestones, complex filters)

Use `search_pull_requests` when filtering by author or text; use `list_pull_requests`
when you just need "all open PRs" or "all merged PRs."

### 4. Creating a PR auto-reads the PR template if one exists

`create_pull_request` looks for `.github/pull_request_template.md` or
`pull_request_template.md` in the repo root and pre-fills the body if found.
The tool description says so, but many agents miss this — **always search for
the template first** before assuming the body needs to be written from scratch.

### 5. Merging a PR has three strategies; pick the right one

- `merge` — Merge commit (preserves full history, creates a merge commit)
- `squash` — Squash all commits into one (cleaner history, loses individual
  commits)
- `rebase` — Rebase onto target branch (linear history, forces push if branch
  is behind)

**Charlie's repos:** Check git conventions in each repo before picking a merge
strategy. Astro repos typically prefer squash; infrastructure repos may prefer
merge for traceability.

### 6. `get_file_contents` returns directory listings with optional fields

When querying a directory (not a single file), the tool can return a compact
listing:

```
# Returns name, type, size for each entry (default)
get_file_contents(owner, repo, path="/src")

# Or request only specific fields to reduce response size
get_file_contents(owner, repo, path="/src", fields=["name", "type"])
```

Use `fields` when you only need names/types and want to minimize response size
for large directories.

### 7. `create_or_update_file` commits directly; no staging

Calling this tool commits the change to the specified branch immediately:

```
create_or_update_file(owner, repo, path, content, message, branch="main")
# → File is committed and pushed; no "staging" step
```

Be cautious with production branches. Consider creating a feature branch first,
testing, then merging via PR.

### 8. Search tools have rate limits; use pagination

GitHub search rate-limits at 30 requests per minute for authenticated users. The
MCP tools support `page` and `perPage` parameters:

```
search_repositories(query="...", page=1, perPage=10)
# If results > 10, fetch page 2:
search_repositories(query="...", page=2, perPage=10)
```

Always paginate large result sets rather than fetching all results in one call.

### 9. `run_secret_scanning` is not real-time

GitHub's secret scanning is a background job. Running this tool triggers a scan,
but results come back async. Don't expect immediate detection of newly pushed
secrets — the scan takes minutes to complete.

## Workflow patterns for common tasks

### Search for a repository

```
search_repositories(query="react language:typescript stars:>1000")
→ Returns: Repo name, description, URL, star count, language
→ Use repo name/owner for subsequent calls
```

### List PRs in a repo

```
list_pull_requests(owner="charlieseay", repo="charlieseay.com", state="open")
→ Returns: PR titles, numbers, authors, state, created/updated dates
→ Use PR number for get details or merge
```

### Get PR review status

```
pull_request_read(owner="charlieseay", repo="charlieseay.com", number=42)
→ Returns: Full PR details including reviews, approval state, mergeable status
```

### Search for code across GitHub

```
search_code(query="function authenticate language:typescript")
→ Returns: File paths, repo names, matching lines (limited to ~10 results)
```

### Create a PR with the repo's template

```
1. search_repositories to find the repo
2. get_file_contents to verify template exists (.github/pull_request_template.md)
3. create_pull_request(owner, repo, title, body, head, base)
   → Body is pre-filled from template if found
```

### Merge a PR after review

```
1. pull_request_read to confirm it's approved and mergeable
2. merge_pull_request(owner, repo, number, merge_method="squash")
   → Confirm merge_method matches repo conventions first
```

### Review code for security issues (local tool; no Copilot needed)

```
run_secret_scanning(owner, repo)
→ Triggers GitHub's secret scanning backend
→ Results available minutes later in GitHub's web UI
```

## Known environment facts

- **Auth:** Pulled from `gh` system keyring every time MCP server starts
- **Default repo:** Charlie's personal repos are at `github.com/charlieseay/`
- **Org access:** Token should have access to any orgs Charlie is part of
- **Rate limit:** 30 searches/minute; use pagination for large result sets
- **Direct tools in Claude Code:** mcp__github__* tools are also available in
  sessions for read-only queries (faster, no proxy)

## When to use direct mcp__github__* tools vs. this MCP

| Task | Use | Why |
|------|-----|-----|
| Search repos/code | `mcp__github__search_repositories` | Direct, faster |
| List open issues | `mcp__github__list_issues` | Direct, no proxy |
| Get file contents | `mcp__github__get_file_contents` | Direct, no proxy |
| Create/merge PR | This MCP (`mcp:github`) | Write operations need auth setup |
| Trigger workflow | This MCP (`mcp:github`) | Write operations |
| Post PR review | This MCP (`mcp:github`) | Write operations |

Both paths use the same auth; direct tools are marginally faster for reads.

## Quick self-check for this skill

```bash
# Verify wrapper script exists and has token injection
cat /Users/charlieseay/.local/bin/github-mcp-wrapper
# Should show: export GITHUB_PERSONAL_ACCESS_TOKEN=$(/opt/homebrew/bin/gh auth token)

# Verify gh CLI is authenticated
/opt/homebrew/bin/gh auth status
# Should show: "Logged in to github.com as <username>"

# Verify MCP proxy has github configured
grep -A 5 '"github":' /Users/charlieseay/.config/mcp-proxy/config.json
# Should show: wrapper command and stdio args

# Test token freshness (manually)
/opt/homebrew/bin/gh auth token | wc -c
# Should return token length (~50+ chars)
```

---

**Last Updated:** 2026-09-30  
**Server version:** 1.5.0+ (verified via wrapper help output)  
**Toolsets enabled:** repos, issues, pull_requests, actions, dependabot, git
(60+ tools)  
**Note:** This is the local MCP wrapper. Claude Code sessions also have direct
access to `mcp__github__*` tools (official remote server) — prefer those for
read-only queries.
