# Task Deduplication — PostgreSQL SELECT FOR UPDATE SKIP LOCKED Pattern

**Category:** task-queue  
**Priority:** CRITICAL  
**Created:** 2026-08-20  
**Status:** active  
**Confidence triggers:** task queue, duplicate tasks, race conditions, PostgreSQL task management, helmsman, worker dispatch

---

## When to Use This Skill

Use this skill when:
- Implementing or fixing task queue deduplication
- Working on helmsman-db task management
- Debugging duplicate task spawn issues
- Adding task queue features to any PostgreSQL-backed system
- Researching task deduplication patterns

**Anti-patterns this skill prevents:**
- 20+ duplicate "Restart Talos agent" tasks (diagnostics KB)
- Meta-tasks investigating meta-tasks (lesson: assayer-qa-sweep)
- Race conditions in worker task claiming
- Duplicate spawns for same fingerprint (bosun-proactive-audit)

---

## The Pattern

### Problem Solved
**Without deduplication:** Multiple agents can create identical tasks for the same issue, or multiple workers can claim the same task simultaneously.

**Source:** [alekso/postgress_queue](https://github.com/alekso/postgress_queue) — High-performance priority task queue built on PostgreSQL

### Core Implementation

#### 1. Schema: Add Deduplication Key

```sql
-- Add to tasks table
ALTER TABLE tasks 
ADD COLUMN deduplication_key TEXT UNIQUE;

-- Create unique constraint
CREATE UNIQUE INDEX idx_tasks_dedup 
ON tasks(deduplication_key) 
WHERE status IN ('pending', 'assigned', 'in_progress');
```

**Why:** Unique constraint + partial index ensures only ONE task per deduplication_key can be pending/active at a time.

#### 2. Task Creation with Deduplication

```python
# INSERT with conflict handling
INSERT INTO tasks (brief, owner, deduplication_key, status, created_at)
VALUES (%s, %s, %s, 'pending', NOW())
ON CONFLICT (deduplication_key) DO NOTHING;
```

**Result:** Duplicate tasks are silently rejected at the database level — zero code logic needed.

#### 3. Atomic Task Claiming (SELECT FOR UPDATE SKIP LOCKED)

```python
# Worker claims next task atomically
SELECT * FROM tasks 
WHERE status = 'pending' 
  AND owner = %s
ORDER BY priority DESC, created_at ASC
LIMIT 1
FOR UPDATE SKIP LOCKED;

# Update to claimed
UPDATE tasks 
SET status = 'assigned', claimed_at = NOW(), worker_id = %s
WHERE id = %s;
```

**Why this works:**
- `FOR UPDATE` locks the row
- `SKIP LOCKED` skips rows already locked by other workers
- No race conditions — multiple workers never claim the same task

### 4. Deduplication Key Generation

```python
def generate_dedup_key(task_data: dict) -> str:
    """Generate stable deduplication key from task semantics."""
    
    # Option 1: Fingerprint-based (for infrastructure issues)
    if 'fingerprint' in task_data:
        return f"fingerprint:{task_data['fingerprint']}"
    
    # Option 2: Content hash (for generic tasks)
    content = f"{task_data['owner']}:{task_data['task']}:{task_data.get('target', '')}"
    return f"hash:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
    
    # Option 3: Explicit key (for known duplicates)
    if task_data.get('dedup_key'):
        return task_data['dedup_key']
    
    # Option 4: None (allow duplicates)
    return None
```

**Examples:**
- `fingerprint:talos_agent_down:23.88.112.70` — Infrastructure issues
- `hash:abc123def456` — Generic task content hash
- `user_action:approve_task_1234` — Explicit business logic key

---

## Integration Steps

### For helmsman-db (Current System)

**Step 1: Schema Migration**

```sql
-- File: migrations/0025_add_deduplication_key.sql
ALTER TABLE tasks ADD COLUMN deduplication_key TEXT;
CREATE UNIQUE INDEX idx_tasks_dedup ON tasks(deduplication_key) 
WHERE status IN ('pending', 'assigned', 'in_progress');
```

**Step 2: Update POST /tasks Endpoint**

```python
# Before (no dedup):
cursor.execute(
    "INSERT INTO tasks (brief, owner, effort, status) VALUES (?, ?, ?, ?)",
    (brief, owner, effort, 'pending')
)

# After (with dedup):
dedup_key = generate_dedup_key(request_data)
cursor.execute(
    """
    INSERT INTO tasks (brief, owner, effort, status, deduplication_key) 
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT (deduplication_key) DO NOTHING
    RETURNING id
    """,
    (brief, owner, effort, 'pending', dedup_key)
)
result = cursor.fetchone()
if not result:
    return {"status": "duplicate", "message": "Task already exists"}, 200
```

**Step 3: Update Worker Dispatcher**

```python
# Before (race-prone):
SELECT * FROM tasks WHERE status='pending' AND owner='CLAUDE'

# After (atomic claiming):
SELECT * FROM tasks 
WHERE status='pending' AND owner=%s
ORDER BY priority DESC, created_at ASC
LIMIT 1
FOR UPDATE SKIP LOCKED;
```

**Step 4: Update bosun-proactive-audit (Duplicate Source)**

```python
# Before (always creates task):
def create_remediation_task(fingerprint, issue):
    task = {
        "brief": generate_brief(issue),
        "owner": "CHARLIE"
    }
    post_task(task)

# After (with dedup):
def create_remediation_task(fingerprint, issue):
    task = {
        "brief": generate_brief(issue),
        "owner": "CHARLIE",
        "deduplication_key": f"fingerprint:{fingerprint}"  # ← KEY FIX
    }
    response = post_task(task)
    if response.status == "duplicate":
        logger.info(f"Task for {fingerprint} already exists, skipping")
```

---

## Retry Pattern with Deduplication

```python
# Failed tasks with exponential backoff
UPDATE tasks 
SET 
  status = 'pending',
  retry_count = retry_count + 1,
  next_retry_at = NOW() + INTERVAL '1 minute' * POW(2, retry_count),
  deduplication_key = NULL  -- Allow retry as new task
WHERE id = %s;
```

**Why NULL the dedup key:** Failed tasks that retry should be treated as new attempts (different dedup key or NULL).

---

## Monitoring & Metrics

```sql
-- Check for duplicate attempts (blocked by constraint)
SELECT deduplication_key, COUNT(*) as attempt_count
FROM task_creation_log  -- Requires audit log table
GROUP BY deduplication_key
HAVING COUNT(*) > 1
ORDER BY attempt_count DESC;

-- Active dedup keys
SELECT deduplication_key, status, created_at
FROM tasks
WHERE deduplication_key IS NOT NULL
  AND status IN ('pending', 'assigned', 'in_progress');
```

---

## References

- **Source repo:** [alekso/postgress_queue](https://github.com/alekso/postgress_queue)
- **PostgreSQL SKIP LOCKED docs:** https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE
- **Other proven implementations:**
  - [timgit/pg-boss](https://github.com/timgit/pg-boss) — Node.js, 2.1K stars
  - [graphile/worker](https://github.com/graphile/worker) — Node.js, 2K stars, has job keys
  - [btubbs/pgq](https://github.com/btubbs/pgq) — Go, supports exponential backoff

---

## Lessons Learned

### From Diagnostics KB

**Lesson ID:** lesson_2026-07-31 — Duplicate task spawn + silent no-op dispatch

**Problem:** bosun-proactive-audit re-detected down state on every sweep, spawned 9 duplicate "Restart Talos agent on Hetzner" tasks with no dedup check.

**Fix:** This skill. Add `deduplication_key: f"fingerprint:{fingerprint}"` to all bosun task creation calls.

**Lesson ID:** lesson_2026-07-30 — Meta-task investigating meta-task

**Problem:** assayer-qa-sweep spawned #1015376 ("Investigate high retry count for #1015348") investigating a task that was itself investigating another task — infinite meta-task recursion.

**Fix:** Dedup key prevents re-spawning investigation tasks for same target.

---

## Success Criteria

After implementing this skill:

✅ Zero duplicate task spawns for same `deduplication_key`  
✅ bosun-proactive-audit creates at most 1 task per fingerprint  
✅ Worker dispatchers never claim same task twice  
✅ Task queue monitoring shows dedup effectiveness  
✅ All 20+ duplicate spawn lessons from diagnostics KB are resolved

---

## Anti-Patterns to Avoid

❌ **Dedup key too broad** — `"restart_service"` catches ALL service restarts, not just duplicates  
❌ **Dedup key too narrow** — Including timestamp makes every task unique  
❌ **Never NULLing dedup key** — Failed tasks can never retry  
❌ **Forgetting partial index** — Completed tasks block new tasks with same key  
❌ **Client-side dedup** — Race conditions between check and insert  

✅ **Use database constraint** — Atomic, no race conditions  
✅ **Semantic dedup keys** — Based on what makes tasks equivalent  
✅ **Partial index** — Only enforce uniqueness for active statuses  
✅ **NULL for retries** — Allow failed tasks to re-enter queue  

---

## Quick Start Checklist

- [ ] Add `deduplication_key TEXT` column to tasks table
- [ ] Create unique partial index on pending/assigned/in_progress
- [ ] Update POST /tasks with `ON CONFLICT DO NOTHING`
- [ ] Add `generate_dedup_key()` function to codebase
- [ ] Update all task creation calls to pass dedup key
- [ ] Update worker dispatcher to use `SKIP LOCKED`
- [ ] Test: Try creating duplicate task, verify constraint blocks it
- [ ] Monitor: Query dedup metrics weekly

---

**Last Updated:** 2026-08-20  
**Maintained by:** Auto-discovery system  
**Confidence score:** 0.95 for "task queue", "duplicate tasks", "PostgreSQL"
