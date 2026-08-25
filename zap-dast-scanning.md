# ZAP DAST — Dynamic Application Security Testing

**Category:** security  
**Priority:** HIGH  
**Created:** 2026-08-20  
**Confidence triggers:** DAST, dynamic scanning, web application security, OWASP ZAP, runtime vulnerabilities

**Source:** [zaproxy/action-baseline](https://github.com/zaproxy/action-baseline)

## What DAST Catches (That SAST Can't)

- XSS in rendered output
- CSRF protection failures
- Authentication bypass
- Session management issues
- Actual runtime configuration issues

**Example from our stack:** StdOut health endpoint returning 401 when marked public

## Quick Start

```bash
# Install
docker pull zaproxy/zap-stable

# Baseline scan (passive)
docker run -t zaproxy/zap-stable zap-baseline.py \
  -t https://bridge.seaynicroute.com
```

## GitHub Actions

```yaml
- name: ZAP Baseline Scan
  uses: zaproxy/action-baseline@v0.15.0
  with:
    target: 'https://staging.example.com'
    rules_file_name: '.zap/rules.tsv'
    fail_action: true
```

## False Positive Management

```tsv
# .zap/rules.tsv
10049  IGNORE  # Storable and Cacheable Content (expected)
10055  WARN    # CSP Header Not Set
10096  FAIL    # Timestamp Disclosure
```

**Use cases:**
- Bridge dashboard pre-production
- StdOut before public launch
- Hone.academy continuous scanning
- Enchapter API endpoints

**Complements:** Semgrep (SAST) + ZAP (DAST) = static + runtime coverage
