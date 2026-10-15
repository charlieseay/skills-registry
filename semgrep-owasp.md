# Semgrep OWASP Scanning — Automated SAST

**Category:** security  
**Priority:** HIGH  
**Created:** 2026-08-20  
**Confidence triggers:** OWASP, SAST, code scanning, security audit, static analysis, vulnerability

**Source:** [semgrep/semgrep](https://github.com/semgrep/semgrep) — 10K stars

## What It Does

Automated Static Application Security Testing (SAST) with OWASP Top 10 rulesets. Maps findings directly to OWASP categories.

## Quick Start

```bash
# Install
pip install semgrep

# Scan with OWASP rulesets
semgrep scan --config p/owasp-top-ten \
              --config p/cwe-top-25 \
              --config p/r2c-security-audit
```

## GitHub Actions

```yaml
# .github/workflows/semgrep.yml
name: Semgrep OWASP SAST
on: [pull_request]

jobs:
  semgrep-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/owasp-top-ten
            p/cwe-top-25
            p/r2c-security-audit
        env:
          SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
```

## Custom Rules

```yaml
# .semgrep/rules.yml
rules:
  - id: hardcoded-secret
    pattern: |
      password = "..."
    message: Hardcoded password detected
    severity: ERROR
    languages: [python, javascript, typescript]
```

**Complements:** gitleaks (secrets) + Semgrep (code patterns) = comprehensive security

**Gap closed:** Manual OWASP compliance audits (19 findings in Hone, manual review)

**References:** [semgrep/semgrep-rules](https://github.com/semgrep/semgrep-rules)
