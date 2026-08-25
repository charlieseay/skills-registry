# TruffleHog — Active Secret Verification

**Category:** security  
**Priority:** MEDIUM  
**Created:** 2026-08-20  
**Confidence triggers:** secret scanning, credential verification, TruffleHog, active verification, false positives

**Source:** [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) — 18K stars

## Advantage Over Gitleaks

**Gitleaks:** Pattern matching + entropy → HIGH false-positive rate  
**TruffleHog:** Pattern matching + **live API validation** → ZERO false positives

## How It Works

```bash
# Install
brew install trufflehog

# Scan with active verification
trufflehog git file://. --only-verified
```

**What "verified" means:**
- AWS keys → validated against STS API
- GitHub tokens → validated against GitHub API
- Stripe keys → validated against Stripe API
- Slack tokens → validated against Slack API

**Result:** Only reports secrets that actually work.

## Pre-Push Hook

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/trufflesecurity/trufflehog
  rev: v3.88.5
  hooks:
    - id: trufflehog
      stages: [pre-push]
      args: ["git", "file://.", "--since-commit", "HEAD~5", "--only-verified"]
```

**Use when:** Gitleaks false-positive rate becomes a problem

**Complements:** `gitleaks-pre-push.md` (faster, catches more patterns)
