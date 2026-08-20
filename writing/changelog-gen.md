---
name: changelog-gen
description: Generate CHANGELOG.md from git commits since last tag
---

# CHANGELOG Generator

Generates or updates CHANGELOG.md by reading commits since the last git tag and grouping them by conventional commit type.

## When to invoke

- Before creating a release or PR
- After completing a milestone
- When asked to "update the changelog"
- Auto-invoked by `/checkpoint --ship`

## Workflow

### Step 1: Detect project context

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
_PROJECT=$(basename "$(pwd)")
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "Project: $_PROJECT"
echo "Branch: $_BRANCH"
```

### Step 2: Find last version tag

```bash
_LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$_LAST_TAG" ]; then
  echo "No previous tags found — will include all commits"
  _RANGE="HEAD"
else
  echo "Last tag: $_LAST_TAG"
  _RANGE="${_LAST_TAG}..HEAD"
fi
```

### Step 3: Extract commits and group by type

```bash
# Get commits with conventional commit format: type(scope): message
git log $_RANGE --pretty=format:"%s" | grep -E "^(feat|fix|chore|docs|style|refactor|perf|test|build|ci)(\(.+\))?:" > /tmp/changelog-commits.txt 2>/dev/null || true

# Also get commits without conventional format
git log $_RANGE --pretty=format:"%s" | grep -vE "^(feat|fix|chore|docs|style|refactor|perf|test|build|ci)(\(.+\))?:" > /tmp/changelog-other.txt 2>/dev/null || true

_FEAT_COUNT=$(grep "^feat" /tmp/changelog-commits.txt 2>/dev/null | wc -l | tr -d ' ')
_FIX_COUNT=$(grep "^fix" /tmp/changelog-commits.txt 2>/dev/null | wc -l | tr -d ' ')
_OTHER_COUNT=$(wc -l < /tmp/changelog-other.txt 2>/dev/null | tr -d ' ')

echo "Found commits:"
echo "  Features: $_FEAT_COUNT"
echo "  Fixes: $_FIX_COUNT"
echo "  Other: $_OTHER_COUNT"
```

### Step 4: Determine new version

If no CHANGELOG.md exists or no version can be detected, ask the user:

```
D1 — What version should this be?
Project: $_PROJECT
Branch: $_BRANCH

ELI10: We need to tag this release with a semantic version number (major.minor.patch). 
Looking at the commits since last tag, we have $_FEAT_COUNT new features and $_FIX_COUNT bug fixes.

Stakes if we pick wrong: Version numbers are permanent in git history and communicate 
the scope of changes to users. Wrong choice = confusing release notes.

Recommendation: {{Based on commit types, suggest version bump}}

Completeness: Note: options differ in kind (version semantics), not coverage.

Pros / cons:
A) Patch bump ({{CURRENT}}.{{CURRENT}}.{{CURRENT+1}}) (recommended if only fixes)
  ✅ Appropriate for bug fixes and minor improvements
  ✅ Signals backward compatibility
  ❌ Might understate significant fixes

B) Minor bump ({{CURRENT}}.{{CURRENT+1}}.0) (recommended if new features)
  ✅ Appropriate for new features
  ✅ Signals backward compatible additions
  ❌ Resets patch number to 0

C) Major bump ({{CURRENT+1}}.0.0) (only if breaking changes)
  ✅ Appropriate for breaking changes
  ✅ Clear signal to users about incompatibility
  ❌ Should only be used when truly breaking

D) Custom version (let me specify)
  ✅ Full control over version number
  ❌ Need to manually specify

Net: Version bump communicates the scope of changes to users and package managers.
```

### Step 5: Generate CHANGELOG entry

```bash
_VERSION="{{VERSION_FROM_DECISION}}"
_DATE=$(date +%Y-%m-%d)

cat > /tmp/changelog-entry.md <<EOF
## [$_VERSION] - $_DATE

### Added
$(grep "^feat" /tmp/changelog-commits.txt | sed 's/^feat[^:]*: /- /' || echo "- No new features")

### Fixed
$(grep "^fix" /tmp/changelog-commits.txt | sed 's/^fix[^:]*: /- /' || echo "- No bug fixes")

### Changed
$(grep "^refactor\|^perf" /tmp/changelog-commits.txt | sed 's/^[^:]*: /- /' || true)

### Documentation
$(grep "^docs" /tmp/changelog-commits.txt | sed 's/^docs[^:]*: /- /' || true)

### Internal
$(grep "^chore\|^test\|^build\|^ci" /tmp/changelog-commits.txt | sed 's/^[^:]*: /- /' || true)

EOF
```

### Step 6: Update or create CHANGELOG.md

If CHANGELOG.md exists, prepend the new entry after the header:

```bash
if [ -f CHANGELOG.md ]; then
  # Read existing file
  _HEADER=$(sed -n '1,/^## \[/p' CHANGELOG.md | sed '$d')
  _EXISTING=$(sed -n '/^## \[/,$p' CHANGELOG.md)
  
  # Write new file
  cat > CHANGELOG.md.new <<EOF
$_HEADER

$(cat /tmp/changelog-entry.md)

$_EXISTING
EOF
  
  mv CHANGELOG.md.new CHANGELOG.md
  echo "Updated CHANGELOG.md with version $_VERSION"
else
  # Create new CHANGELOG.md
  cat > CHANGELOG.md <<EOF
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

$(cat /tmp/changelog-entry.md)
EOF
  
  echo "Created CHANGELOG.md with version $_VERSION"
fi
```

### Step 7: Stage for commit

```bash
git add CHANGELOG.md
echo "CHANGELOG.md staged for commit"
```

### Step 8: Cleanup

```bash
rm -f /tmp/changelog-commits.txt /tmp/changelog-other.txt /tmp/changelog-entry.md
```

## Output

- Updated CHANGELOG.md in project root
- File staged for next commit
- Version $_VERSION entry added

## Notes

- **Conventional commits:** This skill works best when commits follow the format `type(scope): message`
- **Commit types recognized:**
  - `feat:` → Added section
  - `fix:` → Fixed section
  - `refactor:`, `perf:` → Changed section
  - `docs:` → Documentation section
  - `chore:`, `test:`, `build:`, `ci:` → Internal section
- **Non-conventional commits:** Grouped under "Other changes"
- **Git tags:** Uses git tags to determine what's new; if no tags exist, includes all commits

## Integration

This skill is auto-invoked by `/checkpoint --ship` but can also be run standalone.

## Example Output

```markdown
## [1.2.0] - 2026-06-17

### Added
- Add PostgreSQL persistence layer
- Add user authentication flow
- Add email verification

### Fixed
- Fix race condition in task processor
- Fix memory leak in event handler

### Changed
- Improve query performance by 40%

### Internal
- Update dependencies
- Add integration tests
```
