# pg-boss — Node.js PostgreSQL Job Queue

**Category:** task-queue  
**Priority:** HIGH  
**Created:** 2026-08-20  
**Language:** Node.js/TypeScript  
**Confidence triggers:** Node.js task queue, job queue, background jobs, PostgreSQL queue, n8n, Helmsman

**Source:** [timgit/pg-boss](https://github.com/timgit/pg-boss) — 2.1K stars

## When to Use

Use for Node.js/TypeScript services that need reliable background job processing:
- n8n workflow automation
- Helmsman task orchestration (currently Python, but if we port to Node)
- Any Express/Fastify/Hono backend

## Quick Start

```bash
npm install pg-boss
```

```javascript
const PgBoss = require('pg-boss');
const boss = new PgBoss('postgres://user:pass@host/database');

await boss.start();

// Send job
const jobId = await boss.send('send-email', {
  to: 'user@example.com',
  subject: 'Hello'
});

// Process jobs
await boss.work('send-email', async (job) => {
  console.log(`Sending email to ${job.data.to}`);
  // Your logic here
});
```

## Key Features

- **Exactly-once delivery** via PostgreSQL SKIP LOCKED
- **Deduplication** via singleton jobs
- **Retry with exponential backoff**
- **Scheduled jobs** (cron-like)
- **Job expiration and archiving**
- **Priority queues**

## Deduplication Pattern

```javascript
// Only allow one job per unique key
await boss.send('process-user', { userId: 123 }, {
  singletonKey: `user-${userId}`  // Dedup key
});
```

**Complements:** `task-deduplication.md` (SQL pattern) — pg-boss is the Node.js implementation

**Use case:** Helmsman Node.js worker, n8n background jobs
