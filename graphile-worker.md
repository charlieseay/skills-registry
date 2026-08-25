# graphile-worker — High-Performance Node.js PostgreSQL Queue

**Category:** task-queue  
**Priority:** MEDIUM  
**Created:** 2026-08-20  
**Language:** Node.js/TypeScript  
**Confidence triggers:** Graphile, worker queue, job queue, PostgreSQL, Node.js

**Source:** [graphile/worker](https://github.com/graphile/worker) — 2K stars

## Advantages Over pg-boss

- **Admin UI** for monitoring jobs
- **Cron jobs** built-in
- **Graceful shutdown** handling
- **Dead-worker recovery**

## Quick Start

```bash
npm install graphile-worker
```

```javascript
const { run, quickAddJob } = require("graphile-worker");

const runner = await run({
  connectionString: "postgres://...",
  taskList: {
    hello: async (payload) => {
      console.log(`Hello, ${payload.name}!`);
    }
  }
});

// Add job
await quickAddJob({ name: "world" }, "hello");
```

## Use Case

When you need pg-boss features PLUS:
- Admin UI for non-technical monitoring
- Cron scheduling
- Better TypeScript support

**Complements:** `pg-boss-nodejs.md` (simpler alternative)
