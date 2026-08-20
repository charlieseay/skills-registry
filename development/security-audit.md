---
name: security-audit
version: 1.0.0
description: Infrastructure-first security audit — secrets, dependencies, LLM boundaries
---

# Security Audit Framework

Runs comprehensive security audit covering: secrets archaeology (git history scan), dependency supply chain, LLM/AI trust boundaries, plus OWASP Top 10 checks.

Integrates with our existing `Standards/API Security Checklist.md` (12 required controls).

## When to invoke

- Before deploying any service
- Monthly security review
- After adding new dependencies
- When user says "security audit" or "check for vulnerabilities"
- **Proactively suggest** before creating a PR for deployment-related code

## Audit Scope

### 1. Secrets Archaeology

Scan git history for accidentally committed credentials:

```bash
# Patterns to search for
PATTERNS=(
  "api[_-]?key"
  "secret[_-]?key"
  "password"
  "token"
  "bearer"
  "aws[_-]?access"
  "private[_-]?key"
  "-----BEGIN"
  "sk-[a-zA-Z0-9]{20,}"  # OpenAI keys
  "ghp_[a-zA-Z0-9]{36}"  # GitHub tokens
  "AKIA[0-9A-Z]{16}"     # AWS keys
)

# Search all commits
for pattern in "${PATTERNS[@]}"; do
  git log --all --full-history -p -S "$pattern" --pretty=format:"%H %an %ad" | \
    grep -E "$pattern" | \
    while read -r line; do
      echo "⚠️  Potential secret found: $line"
    done
done
```

### 2. Dependency Supply Chain

**npm/Node.js:**
```bash
npm audit --json > /tmp/npm-audit.json
CRITICAL_COUNT=$(jq '.metadata.vulnerabilities.critical // 0' /tmp/npm-audit.json)
HIGH_COUNT=$(jq '.metadata.vulnerabilities.high // 0' /tmp/npm-audit.json)

if [ "$CRITICAL_COUNT" -gt 0 ] || [ "$HIGH_COUNT" -gt 0 ]; then
  echo "❌ Found $CRITICAL_COUNT critical, $HIGH_COUNT high vulnerabilities"
  jq '.vulnerabilities | to_entries[] | select(.value.severity == "critical" or .value.severity == "high") | {name: .key, severity: .value.severity, via: .value.via}' /tmp/npm-audit.json
fi
```

**Python:**
```bash
# Use pip-audit or safety
pip-audit --format json > /tmp/pip-audit.json 2>/dev/null || \
  safety check --json > /tmp/safety-check.json 2>/dev/null || \
  echo "⚠️  No Python vulnerability scanner found (install pip-audit or safety)"
```

**Docker base images:**
```bash
# Check for outdated base images in Dockerfiles
grep "^FROM" Dockerfile* 2>/dev/null | while read -r line; do
  image=$(echo "$line" | awk '{print $2}')
  echo "Checking: $image"
  
  # Get image age
  docker pull "$image" >/dev/null 2>&1
  age=$(docker inspect "$image" --format='{{.Created}}' 2>/dev/null || echo "unknown")
  echo "  Created: $age"
  
  # Check for known CVEs (requires docker scan or trivy)
  if command -v trivy >/dev/null 2>&1; then
    trivy image --severity HIGH,CRITICAL --format json "$image" > "/tmp/trivy-$(echo "$image" | tr '/:' '_').json"
  fi
done
```

### 3. LLM Trust Boundary Violations

Detect user input flowing into LLM prompts without sanitization:

```bash
# Search for prompt construction patterns
rg "prompt.*\+.*req\.(body|query|params)" --type ts --type js --type python || true
rg "f['\"].*{.*request\." --type python || true
rg "\`\$\{.*req\." --type ts --type js || true

# Check for direct user input in LLM calls
rg "claude\.|anthropic\.|openai\." --type ts --type js --type python | \
  grep -E "(req\.body|request\.json|params|query)" || true
```

**Specific checks:**
- [ ] User input sanitized before LLM prompts?
- [ ] System prompts separated from user content?
- [ ] Output validation (no code execution from LLM response)?
- [ ] Rate limiting on LLM endpoints?

### 4. SQL Safety

```bash
# Check for string concatenation in SQL
rg "SELECT.*\+.*" --type ts --type js --type python || true
rg "f['\"]SELECT.*{" --type python || true
rg "WHERE.*\+.*" --type ts --type js --type python || true

# Look for raw queries without parameterization
rg "\.raw\(|\.execute\(|db\.run\(" --type ts --type js --type python || true
```

### 5. OWASP Top 10 (2023)

Check against our `Standards/API Security Checklist.md`:

1. **Broken Access Control** — Check for authorization on all endpoints
2. **Cryptographic Failures** — Verify secrets not in plaintext
3. **Injection** — SQL/NoSQL/Command injection checks
4. **Insecure Design** — Review architecture for trust boundaries
5. **Security Misconfiguration** — Check for default configs, debug mode
6. **Vulnerable Components** — Dependency audit (covered above)
7. **Auth Failures** — Session management, MFA, password policies
8. **Data Integrity Failures** — Verify signed/encrypted data
9. **Logging Failures** — Security events logged?
10. **SSRF** — User-controlled URLs validated?

### 6. Environment Variable Leakage

```bash
# Check for .env files in git
git ls-files | grep -E "\.env$|\.env\." || true

# Check for hardcoded secrets in code
rg "process\.env\.[A-Z_]+.*=.*['\"]" --type ts --type js || true
rg "os\.environ\[['\"][A-Z_]+['\"]\].*=.*['\"]" --type python || true
```

### 7. CI/CD Pipeline Security

```bash
# Check for secrets in GitHub Actions
if [ -d ".github/workflows" ]; then
  rg "password|secret|token|key" .github/workflows/ | \
    grep -v "secrets\." || true
fi

# Check for privileged Docker commands
rg "docker.*--privileged" .github/workflows/ Dockerfile* || true
```

## Output Format

Write audit results to `Projects/<project>/Security Audit YYYY-MM-DD.md`:

```markdown
---
tags: [security, audit]
created: YYYY-MM-DD
status: active
---

# Security Audit — YYYY-MM-DD

## Executive Summary

- **Secrets archaeology:** X potential leaks found
- **Dependencies:** X critical, Y high vulnerabilities
- **LLM boundaries:** X violations detected
- **SQL safety:** X unsafe queries found
- **OWASP compliance:** X/10 controls passing
- **Overall risk:** LOW | MEDIUM | HIGH | CRITICAL

## Findings

### CRITICAL (fix immediately)

1. **[SEC-001] Hardcoded API key in git history**
   - Location: `commit abc123, src/config.ts:42`
   - Evidence: `API_KEY = "sk-abc123..."`
   - Impact: Full API access to attacker
   - Remediation: Rotate key, add to `.gitignore`, use secrets manager
   - Ref: Standards/API Security Checklist.md #2

2. ...

### HIGH (fix before deploy)

### MEDIUM (fix within 30 days)

### LOW (track for future fix)

## Trend Tracking

| Date | Critical | High | Medium | Low |
|------|----------|------|--------|-----|
| 2026-06-17 | 2 | 5 | 12 | 8 |
| 2026-05-17 | 3 | 7 | 15 | 10 |

**Direction:** ⬇️ Improving (2 fewer critical)

## Compliance Check

Against `Standards/API Security Checklist.md` (12 required controls):

- [x] 1. Input validation
- [x] 2. Authentication required
- [ ] 3. Authorization enforced (missing on 2 endpoints)
- [x] 4. Rate limiting
- ...

**Score:** 10/12 controls passing (83%)

## Next Actions

- [ ] Rotate leaked API key (SEC-001)
- [ ] Add missing authorization checks (SEC-002)
- [ ] Update dependency X to v2.0 (SEC-003)
- [ ] Schedule follow-up audit in 30 days
```

## Integration with helmsman.db

Register audit findings as tasks:

```bash
for finding in "${CRITICAL_FINDINGS[@]}"; do
  curl -X POST http://localhost:5682/tasks \
    -H "Content-Type: application/json" \
    -d "{
      \"task\": \"Fix security finding: $finding\",
      \"owner\": \"CHARLIE\",
      \"priority\": \"critical\",
      \"tags\": [\"security\", \"audit\"],
      \"context\": \"Security audit found: $finding\"
    }"
done
```

## Modes

**Daily mode (zero-noise):**
- 8/10 confidence gate
- Only show high-confidence findings
- Skip false-positive-prone checks
- ~5-10 min runtime

**Comprehensive mode (monthly deep scan):**
- 2/10 confidence bar
- All checks enabled
- Includes manual review prompts
- ~30-60 min runtime
- Generates full report for compliance

```bash
# Invoke daily mode
/security-audit

# Invoke comprehensive mode
/security-audit --comprehensive
```

## Benefits

✅ **Prevents secret leaks** — git history archaeology  
✅ **Dependency safety** — CVE scanning  
✅ **LLM-specific** — AI trust boundary checks  
✅ **Trend tracking** — see improvements over time  
✅ **Compliance ready** — maps to our API Security Checklist  
✅ **Automated remediation** — creates tasks for fixes  

## Notes

- **Run before every deploy** — gate in `/checkpoint --ship`
- **Monthly comprehensive audit** — schedule via cron
- **Integrate with CI** — fail build on critical findings
- **Track trends** — commit audit results to vault
