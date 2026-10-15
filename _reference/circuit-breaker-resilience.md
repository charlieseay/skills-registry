# Circuit Breaker & Resilience Patterns — Unified Decorator Approach

**Category:** error-handling  
**Priority:** HIGH  
**Created:** 2026-08-20  
**Status:** active  
**Confidence triggers:** circuit breaker, retry logic, API failures, external API, resilience, timeout, rate limiting, error handling

---

## When to Use This Skill

Use this skill when:
- Integrating with external APIs (Anthropic, OpenAI, Slack, GitHub, any HTTP service)
- Fixing external API failure cascades
- Adding retry logic to unstable services
- Implementing rate limiting for APIs
- Working on connector code (Sonique, helmsman, n8n webhooks)

**Anti-patterns this skill prevents:**
- Sonique connector crashes on network errors (lesson: ConnectorErrorHandler gap)
- Helmsman API calls failing without retry
- Infinite retry loops without backoff
- No circuit breaker → failed service keeps getting hammered

---

## The Solution

###Source: [pyresilience](https://github.com/AhsanSheraz/pyresilience) (Python) + [resilience-typescript](https://github.com/humppa123/resilience-typescript) (TypeScript)

**Key insight:** ONE decorator provides retry + circuit breaker + timeout + rate limiting + fallback + caching.

### Python Implementation (pyresilience)

#### Installation

```bash
pip install pyresilience
```

#### Basic Usage

```python
from pyresilience import resilient

@resilient(retry=3, circuit_breaker=True, timeout=10)
async def call_external_api():
    response = await http_client.get("https://api.example.com/data")
    return response.json()
```

**What this does:**
- ✅ Retries up to 3 times on failure
- ✅ Opens circuit breaker after 5 consecutive failures (stops calling dead service)
- ✅ Times out after 10 seconds
- ✅ Works with both sync and async functions

#### Advanced: Native Rate Limiting

```python
from pyresilience import resilient

# For Anthropic API
@resilient(
    retry=3,
    circuit_breaker=True,
    timeout=30,
    rate_limit="anthropic"  # ← Handles Anthropic rate limits automatically
)
async def call_claude_api(prompt: str):
    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# For OpenAI API
@resilient(retry=5, circuit_breaker=True, rate_limit="openai")
async def call_gpt_api(prompt: str):
    ...

# For GitHub API
@resilient(retry=3, circuit_breaker=True, rate_limit="github")
async def fetch_github_pr(repo: str, pr_num: int):
    ...

# For Stripe API
@resilient(retry=3, circuit_breaker=True, rate_limit="stripe")
async def create_stripe_charge(amount: int):
    ...
```

**Supported APIs:** OpenAI, Anthropic, Stripe, GitHub, and custom rate limits.

#### Full Feature Set

```python
from pyresilience import resilient

@resilient(
    retry=5,                    # Retry up to 5 times
    circuit_breaker=True,       # Enable circuit breaker
    timeout=30,                 # 30-second timeout
    fallback=default_response,  # Fallback function if all retries fail
    bulkhead=10,                # Max 10 concurrent calls
    rate_limit="anthropic",     # Anthropic rate limiting
    cache=True                  # Cache successful responses
)
async def robust_api_call():
    ...
```

---

### TypeScript Implementation (resilience-typescript)

#### Installation

```bash
npm install resilience-typescript
```

#### Basic Usage

```typescript
import { Resilient } from 'resilience-typescript';

const client = new Resilient({
  retry: { maxAttempts: 3, backoff: 'exponential' },
  circuitBreaker: { failureThreshold: 5, timeout: 60000 },
  timeout: 10000
});

async function callExternalAPI() {
  return client.execute(async () => {
    const response = await fetch('https://api.example.com/data');
    return response.json();
  });
}
```

#### For HTTP Calls (Axios-based)

```typescript
import { ResilientAxios } from 'resilience-typescript';

const axios = new ResilientAxios({
  baseURL: 'https://api.example.com',
  retry: { maxAttempts: 5 },
  circuitBreaker: { enabled: true },
  timeout: 30000
});

// All axios calls now have resilience built-in
const data = await axios.get('/users/123');
```

---

## Integration Examples

### Sonique Connectors (Swift → Python Bridge)

**Problem:** ConnectorErrorHandler gap — no retry, no circuit breaker, crashes on network errors.

**Fix:**

```python
# File: sonique_bridge/connectors.py
from pyresilience import resilient

class HelmsmanConnector:
    @resilient(retry=3, circuit_breaker=True, timeout=10)
    async def create_task(self, task_data: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:5682/tasks",
                json=task_data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    @resilient(retry=5, circuit_breaker=True, timeout=5)
    async def health_check(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:5682/health") as response:
                return response.status == 200
```

### Helmsman-db REST Client

```python
# File: helmsman-db/client.py
from pyresilience import resilient
import httpx

class HelmsmanClient:
    def __init__(self, base_url: str = "http://localhost:5682"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    @resilient(
        retry=3,
        circuit_breaker=True,
        timeout=10,
        fallback=lambda: {"status": "unavailable"}
    )
    async def get_tasks(self, status: str = "pending", owner: str = None):
        params = {"status": status}
        if owner:
            params["owner"] = owner
        
        response = await self.client.get(f"{self.base_url}/tasks", params=params)
        response.raise_for_status()
        return response.json()
    
    @resilient(retry=5, circuit_breaker=True, timeout=15)
    async def post_task(self, task_data: dict):
        response = await self.client.post(
            f"{self.base_url}/tasks",
            json=task_data
        )
        response.raise_for_status()
        return response.json()
```

### n8n Webhook Calls (TypeScript)

```typescript
// File: n8n/nodes/HooksCharlieSaysCom/GenericFunctions.ts
import { Resilient } from 'resilience-typescript';

const resilientClient = new Resilient({
  retry: { maxAttempts: 3, backoff: 'exponential' },
  circuitBreaker: { failureThreshold: 5, timeout: 60000 },
  timeout: 30000
});

export async function helmsmanApiRequest(
  method: string,
  endpoint: string,
  body?: object
) {
  return resilientClient.execute(async () => {
    const response = await fetch(`http://localhost:5682${endpoint}`, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  });
}
```

### Bridge Dashboard (Frontend API Calls)

```typescript
// File: bridge/src/lib/api.ts
import { Resilient } from 'resilience-typescript';

const api = new Resilient({
  retry: { maxAttempts: 2, backoff: 'exponential' },
  circuitBreaker: { failureThreshold: 3, timeout: 30000 },
  timeout: 10000,
  fallback: () => ({ error: 'Service unavailable', cached: true })
});

export async function fetchTasks() {
  return api.execute(async () => {
    const response = await fetch('/api/tasks');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  });
}

export async function fetchMetrics() {
  return api.execute(async () => {
    const response = await fetch('/api/metrics');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  });
}
```

---

## Circuit Breaker States

### State Machine

```
CLOSED (normal) → requests pass through
    ↓ (failure threshold exceeded)
OPEN (broken) → requests fail immediately, service not called
    ↓ (timeout expires)
HALF-OPEN (testing) → limited requests allowed
    ↓ (success) → back to CLOSED
    ↓ (failure) → back to OPEN
```

### Monitoring Circuit State

```python
from pyresilience import get_circuit_state

# Check if circuit is open for a specific function
state = get_circuit_state('call_external_api')
print(f"Circuit state: {state}")  # CLOSED, OPEN, or HALF_OPEN

# Manually reset circuit
from pyresilience import reset_circuit
reset_circuit('call_external_api')
```

---

## Retry Strategies

### Exponential Backoff (Default)

```python
@resilient(retry=5)  # 1s, 2s, 4s, 8s, 16s delays
async def api_call():
    ...
```

### Linear Backoff

```python
@resilient(retry=5, backoff='linear')  # 1s, 2s, 3s, 4s, 5s
async def api_call():
    ...
```

### Custom Backoff

```python
@resilient(retry=5, backoff_factor=3)  # 3s, 9s, 27s, 81s, 243s
async def api_call():
    ...
```

### Jitter (Prevents Thundering Herd)

```python
@resilient(retry=5, jitter=True)  # Adds randomness to backoff times
async def api_call():
    ...
```

---

## Error Handling Patterns

### Fallback Functions

```python
def cached_response():
    return {"data": [], "cached": True, "timestamp": time.time()}

@resilient(retry=3, fallback=cached_response)
async def fetch_live_data():
    # If all retries fail, fallback is called
    response = await http_client.get("/api/live")
    return response.json()
```

### Selective Retry (Only Retry Specific Errors)

```python
from pyresilience import resilient, RetryPolicy

@resilient(
    retry=RetryPolicy(
        max_attempts=5,
        retry_on=[ConnectionError, TimeoutError],  # Only retry these
        dont_retry_on=[ValueError]  # Never retry these
    )
)
async def smart_retry_api():
    ...
```

---

## Rate Limiting

### Built-in Rate Limiters

```python
# Anthropic: 50 requests/minute
@resilient(rate_limit="anthropic")
async def call_claude():
    ...

# OpenAI: 60 requests/minute (free tier)
@resilient(rate_limit="openai")
async def call_gpt():
    ...

# Custom rate limit: 100 requests/minute
@resilient(rate_limit={"requests": 100, "period": 60})
async def custom_api():
    ...
```

### Token Bucket Algorithm

```python
from pyresilience import TokenBucket

bucket = TokenBucket(capacity=100, refill_rate=10)  # 10 tokens/second

@resilient(rate_limiter=bucket)
async def rate_limited_call():
    ...
```

---

## Bulkhead Pattern (Concurrency Limiting)

```python
@resilient(bulkhead=10)  # Max 10 concurrent calls
async def expensive_operation():
    # If 10 calls are already in progress, new calls wait or fail
    ...
```

**Use case:** Prevent resource exhaustion when calling expensive services.

---

## Caching

```python
@resilient(cache=True, cache_ttl=300)  # Cache for 5 minutes
async def fetch_rarely_changing_data():
    # Successful responses are cached
    # Subsequent calls within 5 minutes return cached value
    ...
```

---

## Complete Real-World Example

```python
from pyresilience import resilient
import httpx
import logging

logger = logging.getLogger(__name__)

class AnthropicClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={"x-api-key": api_key},
            timeout=60.0
        )
    
    def fallback_response(self):
        logger.warning("Using fallback response due to API failure")
        return {
            "content": [{"text": "Service temporarily unavailable"}],
            "cached": True
        }
    
    @resilient(
        retry=5,                     # Retry up to 5 times
        circuit_breaker=True,        # Enable circuit breaker
        timeout=30,                  # 30s timeout per attempt
        rate_limit="anthropic",      # Anthropic rate limiting
        fallback=fallback_response,  # Fallback on total failure
        cache=True,                  # Cache successful responses
        cache_ttl=300,               # 5-minute cache
        jitter=True                  # Add jitter to retries
    )
    async def create_message(self, prompt: str, model: str = "claude-sonnet-4-5"):
        response = await self.client.post(
            "https://api.anthropic.com/v1/messages",
            json={
                "model": model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        await self.client.aclose()
```

---

## Testing Resilience

### Simulate Failures

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_retry_on_failure():
    with patch('httpx.AsyncClient.get') as mock_get:
        # Fail 2 times, then succeed
        mock_get.side_effect = [
            httpx.ConnectError("Connection refused"),
            httpx.ConnectError("Connection refused"),
            httpx.Response(200, json={"status": "ok"})
        ]
        
        @resilient(retry=3)
        async def api_call():
            async with httpx.AsyncClient() as client:
                response = await client.get("http://api.test")
                response.raise_for_status()
                return response.json()
        
        result = await api_call()
        assert result == {"status": "ok"}
        assert mock_get.call_count == 3  # Verified retry happened
```

---

## Lessons Learned

**Lesson:** Sonique External API Error Handling Unverified (2026-06-26)

**Problem:** Four connectors (Slack, GitHub, Docker, Helmsman) made external API calls without error handling, retry logic, or graceful degradation. Network failures crashed the app.

**Fix:** This skill. Wrap all connector calls with `@resilient()` decorator.

**Impact:** Prevents app crashes, enables offline mode, reduces support burden.

---

## References

- **Python:** [pyresilience](https://github.com/AhsanSheraz/pyresilience)
- **TypeScript:** [resilience-typescript](https://github.com/humppa123/resilience-typescript)
- **Alternative (TS):** [carbonteq/resilience](https://github.com/carbonteq/resilience) (Polly-inspired)
- **Alternative (TS):** Cockatiel (similar feature set)

---

## Quick Start Checklist

- [ ] Install: `pip install pyresilience` (Python) or `npm install resilience-typescript` (TS)
- [ ] Identify all external API calls in codebase
- [ ] Wrap each with `@resilient()` decorator (Python) or `Resilient.execute()` (TS)
- [ ] Add circuit breaker + retry + timeout as minimum
- [ ] Add rate limiting for known APIs (Anthropic, OpenAI, GitHub, Stripe)
- [ ] Test failure scenarios (network down, timeout, 500 errors)
- [ ] Monitor circuit breaker states in production
- [ ] Add fallback functions for critical paths

---

**Last Updated:** 2026-08-20  
**Confidence score:** 0.95 for "circuit breaker", "API failures", "resilience", "retry"
