# Trivy Container Security — CVE Scanning

**Category:** security  
**Priority:** HIGH  
**Created:** 2026-08-20  
**Confidence triggers:** container security, CVE, vulnerability scanning, Docker security, image scanning

**Source:** [aquasecurity/trivy](https://github.com/aquasecurity/trivy) — 24K stars

## What It Does

Scans Docker images, filesystems, and IaC for CVEs and misconfigurations. OWASP compliance built-in.

## Quick Start

```bash
# Install
brew install aquasecurity/trivy/trivy

# Scan Docker image
trivy image myimage:latest

# Scan filesystem
trivy fs /path/to/project

# OWASP compliance scan
trivy image --compliance @compliance/owasp-top10-2021 myimage:latest
```

## GitHub Actions

```yaml
# .github/workflows/trivy.yml
- name: Run Trivy Container Scan
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'image'
    image-ref: 'myimage:latest'
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'HIGH,CRITICAL'
```

## Pre-Push Hook

```bash
# Scan before pushing image
docker build -t myimage:latest .
trivy image myimage:latest --severity HIGH,CRITICAL --exit-code 1
docker push myimage:latest  # Only pushes if no HIGH/CRITICAL CVEs
```

## Integration Pattern

```yaml
# docker-compose.yml
services:
  myservice:
    image: myimage:latest
    # Add to CI: trivy image myimage:latest before deploy
```

**Gap closed:** No container CVE scanning (Docker standards gap)

**Complements:** gitleaks (secrets) + semgrep (SAST) + trivy (container CVEs) = defense in depth

**References:** [aquasecurity/trivy-action](https://github.com/aquasecurity/trivy-action)
