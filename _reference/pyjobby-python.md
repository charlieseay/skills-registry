# pyjobby — Python PostgreSQL Job Queue

**Category:** task-queue  
**Priority:** HIGH  
**Created:** 2026-08-20  
**Language:** Python  
**Confidence triggers:** Python task queue, job queue, background jobs, PostgreSQL, nvidia-agent, worker

**Source:** [mattsta/pyjobby](https://github.com/mattsta/pyjobby)

## When to Use

Use for Python services (nvidia-agent, aider-svc, helmsman workers) that need job queues.

## Quick Start

```bash
pip install pyjobby
```

```python
from pyjobby import JobQueue

queue = JobQueue("postgresql://user:pass@localhost/db")

# Enqueue job
queue.enqueue("send_email", to="user@example.com", subject="Hello")

# Process jobs
@queue.worker("send_email")
def send_email(to, subject):
    print(f"Sending {subject} to {to}")

queue.start()
```

## Features

- Retry with exponential backoff
- Job priorities
- Scheduled jobs
- Dead letter queue

**Complements:** `task-deduplication.md` (SQL pattern) — pyjobby is Python implementation  
**Use case:** nvidia-agent background tasks, helmsman workers
