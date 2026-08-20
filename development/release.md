---
name: release
category: development
description: Prepare and execute a software release
triggers:
  patterns:
  - release
  - deploy
  - ship
  - go live
  contexts:
  - deployment
  - release management
  - production
success_indicators:
- Task completed successfully
- Output verified
when_to_use: Use when prepare and execute a software release
when_NOT_to_use: Use specific skills when they better match the task
avg_completion_time_mins: 30
agents_supported:
- claude-code
- nvidia-agent
- helmsman
- aider
---

Automate the full product release pipeline — test, build, package, publish, update Homebrew tap, and record in the vault.

## Usage
- `/release [product-1] 2.2.0` — full release of [product-1] v2.2.0
- `/release [product-2] 1.4.0 --dry-run` — show what would happen without actually releasing

## Arguments

| Position | Required | Description |
|----------|----------|-------------|
| 1 | Yes | Product name (must match the repo mapping table below) |
| 2 | Yes | Version number (semver, no `v` prefix — the skill adds it) |
| `--dry-run` | No | Preview all steps without executing destructive actions |

## Repo Mapping

| Product | Repo path | Language | GitHub org |
|---------|-----------|----------|------------|
| `[product-1]` | `~/Projects/[product-1]` | Go | [your-org] |
| `[product-2]` | `~/Projects/[product-2]` | Swift | [your-org] |
| `[product-3]` | `~/Projects/[product-3]` | Python | [your-org] |

If the product name does not match the table, stop and tell the user. Do not guess.

## Build Type Detection

Determine the build and test commands from the Language column:

| Language | Test command | Build command | Binary location |
|----------|-------------|---------------|-----------------|
| Go | `go test ./...` | `go build -ldflags "-X main.version=VERSION" -o PRODUCT` | `./PRODUCT` |
| Swift | `swift test` | `swift build -c release` | `.build/release/PRODUCT` |
| Python | `python -m pytest` (if pytest exists) or skip | N/A — Python products are not compiled | N/A |

Python products do not produce binaries or tarballs. For Python products, skip the build, tarball, and Homebrew steps — only create the GitHub Release (tag + notes) and update the vault.

## Dry Run Mode

When `--dry-run` is passed, print each step with `[DRY RUN]` prefix showing what would execute, but do NOT:
- Run the actual build
- Create any tarballs or files
- Create a GitHub Release
- Modify the Homebrew formula
- Push anything to any remote
- Modify vault notes

Do still run tests — tests are read-only and safe to execute even in dry-run mode. Report test results as part of the dry-run output.

## Steps

Execute these in order. Stop immediately if any step fails.

### 1. Validate inputs

- Confirm product name exists in the repo mapping table
- Confirm the repo directory exists on disk
- Confirm the version string looks like semver (e.g., `1.0.0`, `2.3.1`)
- Run `gh auth status` to confirm GitHub CLI is authenticated
- Check that no existing GitHub release exists for `vVERSION`: `gh release view vVERSION --repo [your-org]/PRODUCT` — if it already exists, stop and tell the user

### 2. Run tests

```bash
cd REPO_PATH
# Go:
go test ./...
# Swift:
swift test
# Python:
python -m pytest (if tests exist)
```

If tests fail, stop immediately. Report the failure output. Do not proceed.

### 3. Build the versioned binary (Go and Swift only)

**Go:**
```bash
cd REPO_PATH
CGO_ENABLED=0 go build -ldflags "-X main.version=VERSION" -o PRODUCT
```

**Swift:**
```bash
cd REPO_PATH
swift build -c release
```

Confirm the binary exists after build. If it does not, stop and report.

### 4. Determine architecture and create tarball (Go and Swift only)

Detect the current platform:
```bash
GOOS=$(uname -s | tr '[:upper:]' '[:lower:]')   # darwin
GOARCH=$(uname -m)                                # arm64 or x86_64 → map x86_64 to amd64
```

Tarball name: `PRODUCT-VERSION-GOOS-GOARCH.tar.gz`

**Go:**
```bash
tar czf PRODUCT-VERSION-GOOS-GOARCH.tar.gz PRODUCT
```

**Swift:**
```bash
tar czf PRODUCT-VERSION-GOOS-GOARCH.tar.gz -C .build/release PRODUCT
```

### 5. Get SHA256

```bash
shasum -a 256 PRODUCT-VERSION-GOOS-GOARCH.tar.gz | awk '{print $1}'
```

Save the hash — it is needed for the Homebrew formula.

### 6. Create GitHub Release

```bash
cd REPO_PATH
gh release create vVERSION PRODUCT-VERSION-GOOS-GOARCH.tar.gz \
  --repo [your-org]/PRODUCT \
  --title "vVERSION" \
  --generate-notes
```

For Python products (no tarball):
```bash
cd REPO_PATH
gh release create vVERSION \
  --repo [your-org]/PRODUCT \
  --title "vVERSION" \
  --generate-notes
```

Capture the release URL from the output.

### 7. Update Homebrew formula (Go and Swift only)

The Homebrew tap is at `~/Projects/homebrew-tap`. The formula file is at:
```
~/Projects/homebrew-tap/Formula/PRODUCT.rb
```

If the formula file does not exist, skip this step and warn the user that no Homebrew formula was found.

If it exists, update these three values in the formula:
- `version` — set to the new VERSION
- `url` — set to `https://github.com/[your-org]/PRODUCT/releases/download/vVERSION/PRODUCT-VERSION-GOOS-GOARCH.tar.gz`
- `sha256` — set to the hash from Step 5

Read the formula first to understand its exact structure before editing. The formula may use different patterns — match whatever exists.

### 8. Commit and push Homebrew tap (Go and Swift only)

```bash
cd ~/Projects/homebrew-tap
git add Formula/PRODUCT.rb
git commit -m "$(cat <<'EOF'
Update PRODUCT to VERSION

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
git push
```

### 9. Update vault notes

Two updates:

**a) Project note** — find the project note at the vault path. Use the repo-to-note mapping from `/checkpoint` if available, or look for `Projects/PRODUCT/PRODUCT.md` (case-insensitive search). Add or update a "Releases" or "Version History" section with:
```
- **vVERSION** (YYYY-MM-DD) — [Release notes](RELEASE_URL)
```

**b) Shipping log** — append to `Daily Notes/YYYY-MM-DD.md` (today's daily note):
```
- Released **PRODUCT vVERSION** — RELEASE_URL
```

If the daily note does not exist, create it with standard frontmatter.

### 10. Clean up

Remove the tarball from the repo directory (the release already has it attached):
```bash
rm -f REPO_PATH/PRODUCT-VERSION-GOOS-GOARCH.tar.gz
```

For Go builds, also remove the local binary:
```bash
rm -f REPO_PATH/PRODUCT
```

### 11. Report

Print a summary:

```
Release complete: PRODUCT vVERSION

  Tests:     passed
  Binary:    PRODUCT-VERSION-GOOS-GOARCH.tar.gz (SHA256: HASH)
  Release:   RELEASE_URL
  Homebrew:  Formula/PRODUCT.rb updated and pushed
  Vault:     project note and daily note updated

Next: run /checkpoint to push vault changes to GitHub.
```

For Python products, omit the Binary and Homebrew lines.

## Notes
- Always use absolute paths — `~` must be expanded
- The `gh` CLI handles authentication via the keychain — no tokens needed
- Tarballs are created in the repo directory, then cleaned up after upload
- The Homebrew tap is a separate repo (`[your-org]/homebrew-tap`) — it gets its own commit and push
- Python products skip build, tarball, SHA256, and Homebrew steps — they only get a GitHub Release tag and vault updates
- Do NOT run `/checkpoint` automatically at the end — the user may want to review vault changes first. Suggest it in the report.
- If any step fails, report exactly what failed, what the error output was, and which steps were skipped
