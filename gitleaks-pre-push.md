# Gitleaks Pre-Push — Automated Secret Scanning

**Category:** security  
**Priority:** MEDIUM  
**Created:** 2026-08-20  
**Confidence triggers:** gitleaks, secret scanning, pre-push, credentials, security

**Source:** [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) — 18K stars

## Setup

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.24.2
    hooks:
      - id: gitleaks
        stages: [pre-push]
        args: ["protect", "--staged", "--verbose"]
```

```bash
# Install
brew install pre-commit gitleaks
pre-commit install --hook-type pre-push
```

## False Positive Management

```toml
# .gitleaks.toml
[allowlists]
paths = [
  '''tests/fixtures/.*''',
  '''vendor/.*'''
]
regexes = [
  '''EXAMPLE[A-Za-z0-9+/=]{20,}'''
]
```

## CI/CD Integration

```yaml
# .github/workflows/gitleaks.yml
- uses: gitleaks/gitleaks-action@v3
  env:
    GITLEAKS_CONFIG: .gitleaks.toml
```

**Fixes:** Manual secret scanning, credential leaks

**References:** [gitleaks/gitleaks-action](https://github.com/gitleaks/gitleaks-action), [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog)
