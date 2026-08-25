# Schemathesis — API Contract Fuzzing

**Category:** security  
**Priority:** MEDIUM  
**Created:** 2026-08-20  
**Confidence triggers:** API fuzzing, contract testing, Schemathesis, OpenAPI, REST API security

**Source:** [schemathesis/schemathesis](https://github.com/schemathesis/schemathesis)

## What It Does

Generates property-based positive and negative HTTP payloads to find:
- Unhandled 500 errors
- Response schema mismatches
- Data leakage in error messages
- Edge cases you didn't write tests for

## Works With or Without OpenAPI

```bash
# With OpenAPI spec
schemathesis run https://api.example.com/openapi.json

# Without spec (black-box)
schemathesis run https://api.example.com --base-url /api
```

## Quick Start

```bash
pip install schemathesis

# Fuzz VoiceBox API (has OpenAPI spec)
schemathesis run ~/Projects/voicebox/docs/openapi.json \
  --checks all \
  --base-url http://localhost:8080
```

## GitHub Actions

```yaml
- name: API Fuzzing
  uses: schemathesis/action@v3
  with:
    schema: 'http://localhost:8080/openapi.json'
    checks: 'all'
    args: '--stateful=links --generation-maximize'
```

## Current Use Cases

- **VoiceBox:** Has OpenAPI spec → fuzz immediately
- **Jackel:** FastAPI auto-generates spec → fuzz
- **Helmsman REST API:** Black-box fuzz or write spec
- **Enchapter API:** Black-box fuzz

**Gap closed:** API edge case testing (found 2 HIGH + 6 MEDIUM in Enchapter via manual audit)

**Complements:** ZAP (web app) + Schemathesis (API) = full dynamic coverage
