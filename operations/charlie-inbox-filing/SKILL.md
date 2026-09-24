---
name: "charlie-inbox-filing"
description: "How to put something in front of Charlie for review or a decision, and how to read back what he chose. Covers the three real shapes his unified Inbox (Bridge -> My Week) understands: a decision (approve/reject/write-in), a product ready for review (built, QA passed, needs his eyes on the actual deliverable), and a strategy idea (pick one of several options). Use this BEFORE filing a pending_decisions row, a strategy item, or assuming a finished product will surface for review automatically -- getting the shape wrong means Charlie either never sees it, or sees a duplicate of something that already shows up on its own. Any agent (TALOS, BOSUN, B3CK, CLAUDE, or a human writing a brief for one of them) should read this before writing to helmsman's /decisions, /strategy, or a product's STATUS.json expecting it to appear for review."
category: "operations"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["talos-brief-authoring", "digital-product-quality-bar"]
---

# Charlie Inbox Filing

## Why this exists

Charlie used to have three separate places to check for things needing his
attention: a flat decision list (`/my-tasks`), a strategy-review page
(`/strategy`), and a Digital Products tab buried under Talos where reviewing
a product meant expanding a card, finding the right phase, copying a
filesystem path, and pasting it into Finder. As of 2026-09-24 all three are
one screen: **Bridge -> My Week**, a split-pane queue (left: list, right:
live preview + action bar). If you file something in a shape this queue
doesn't recognize, or duplicate something it already picks up on its own,
Charlie either doesn't see it or sees it twice.

**The Inbox has three item kinds. Know which one you're filing.**

## Kind 1 — Decision (a one-off question needing an answer)

Use this for anything that genuinely has no other home: an approval that
isn't tied to a product, an escalation, a question only Charlie can answer,
a routine daily/weekly check-in.

```bash
curl -s -X POST "http://localhost:5682/decisions" -H 'Content-Type: application/json' -d '{
  "type": "approval",
  "source": "<your-agent-name>",
  "title": "<short, specific headline>",
  "body": "WHY: <why this exists>\n\nDO: <what Charlie should actually do>\n\nPROVE: <exact file paths / URLs / commands backing the claim>\n\nCONTEXT: <anything else load-bearing>",
  "actions_json": "[{\"label\":\"<primary action>\",\"action\":\"<action_id>\"},{\"label\":\"Reject\",\"action\":\"reject\"}]"
}'
```

The WHY/DO/PROVE/CONTEXT structure isn't cosmetic — it's what renders in the
detail pane. A `body` without it just shows as one undifferentiated block of
text and is much harder to act on fast.

**Do NOT use a decision to review a specific already-built product** — see
Kind 2. A decision manually describing "product #X is ready, go check
`~/Projects/talos-tools/digital-products/product-X/phase-3/`" is the exact
duplicate-effort pattern this Inbox replaced. If the product is real,
finished, and QA-passed, it will appear under the Products filter on its own
(see Kind 2) — filing a decision for it just makes Charlie see the same
thing twice, once in each shape (this happened twice on 2026-09-24, both
had to be manually resolved as superseded once the real bug blocking the
product from surfacing was found and fixed).

Reading the answer back (for automated dispatch, not a human checking):

```bash
curl -s "http://localhost:5682/decisions/<id>"
# status: "open" | "resolved"
# resolved_action: the action id Charlie picked
# resolved_note: any free-text he added
```

## Kind 2 — Product ready for review (built, QA passed, needs his eyes on the real deliverable)

**You do not file anything for this.** A product surfaces automatically in
the Inbox's Products filter the moment it is genuinely done. The Inbox
queries `GET /api/talos/products` and includes any product where
`ready_for_review === true && published === false`.

What actually makes a product `ready_for_review`:

1. Its directory must be discoverable: `product-item-<N>` or
   `product-item-<N>-<anything>` under
   `~/Projects/talos-tools/digital-products/`, or the legacy `product-<N>`
   form. (A descriptive suffix like `product-item-54-soccer-templates` is
   fine and common — just don't invent a THIRD naming shape.)
2. Its `STATUS.json` needs a `phases` object keyed by phase number, where
   `phases["4"].status` is `"complete"` or `"shipped"` (or an equivalent
   helmsman task for phase 4 exists and is shipped). **This is the one real
   trap**: several products on 2026-09-24 had their own STATUS.json saying
   `"all_phases_complete": true` and `"ready_for_review": true` as flat
   top-level fields, which is a completely different, unread shape — the
   Inbox's merge logic (`$lib/server/inbox.ts` -> `api/talos/products`)
   only reads the `phases` object form. Five real, finished products were
   invisible to review for this exact reason before it was caught and
   fixed. If you hand-write or hand-patch a product's STATUS.json outside
   the normal Talos phase pipeline, use this shape:
   ```json
   "phases": {
     "0": {"status": "complete"},
     "1": {"status": "complete"},
     "2": {"status": "complete"},
     "3": {"status": "complete"},
     "4": {"status": "complete"}
   }
   ```
3. It must not already be published (`published: false` — checked against
   `store.db`'s `published_listings` table first, falling back to
   `STATUS.json.platforms` only if no store.db record exists).

**The actual deliverable Charlie sees:** the Inbox looks in
`phase-3/customer-package/` (an unzipped mirror) first, and if that
directory doesn't exist, reads directly inside `phase-3/customer-package.zip`
(most products only ship the zip — this is the common case, not a fallback).
It picks the first PDF as the primary inline preview, falling back to the
first image, then any file. If your product's most important preview-worthy
file isn't a PDF or image at the top of that list, nothing forces you to
change anything — Charlie can still browse every file in the "Other files in
this phase" list — but know that a bundle of only fonts or Notion-hosted
templates (no local preview-able file) will correctly show "No deliverable
file recorded for this product yet," which is honest, not a bug to work
around.

**Approve / reject wiring**, if you're building UI or automation against
this rather than just making sure a product surfaces correctly:
- Approve: `POST /api/products/<num>/approve` — refuses unless
  `phase-4/qa-report.json` shows a clean PASS. Writes
  `phase-4/approval.json`.
- Reject: `POST /api/products/<num>/revise` with `{"notes": "<required, specific feedback>"}`
  — files a new `owner: TALOS` revision task with those notes as the brief.

## Kind 3 — Strategy idea (Charlie needs to pick a direction, not just approve/reject)

Use `POST /strategy` (via `helmsman-db`, or the Bridge passthrough at
`/api/strategy`) for an idea, a multi-option fork in the road, or an
escalation that isn't yet resolvable into a single approve/reject.

Real, live schema (verified 2026-09-24 — do not assume a different shape):

```json
{
  "title": "...",
  "type": "product" | "business" | "technical",
  "category": "idea" | "action" | "escalation" | "question",
  "description": "...",
  "context": "... (optional, shown as background)",
  "options": ["Option A text", "Option B text", "..."]
}
```

**`options` is an array of plain strings, not objects.** No `{id, text}`
shape, no numeric index wrapper — just the option text itself. This got
reimplemented wrong once already (2026-09-24) by an agent that assumed a
richer shape without checking the live data first; caught by diffing
against the old `/strategy` page's own working code before it shipped.

Only items with `status: "pending"` appear in the Inbox
(`GET /strategy?status=pending`). Once Charlie answers, `POST /strategy/<id>`
or the feedback endpoint below moves it to `approved`/`rejected`/`in-review`
and it drops out of the queue on its own — you don't need to clean it up.

**Reading the answer back:** a confirmed option or free-text note goes
through `POST /strategy/<id>/feedback` with `{"feedback": "<text>"}`, NOT a
plain `PATCH .../status`. This is the endpoint that actually dispatches
downstream work when the item's `category` is `"question"` — a plain status
flip records the answer but doesn't wake anything up. `PATCH /strategy/<id>`
with `{"status": "rejected"}` is correct for an outright reject; anything
that represents Charlie actually choosing something goes through
`/feedback`.

## Quick decision table

| What you have | File it as | Endpoint |
|---|---|---|
| A one-off approval/question with no product behind it | Decision | `POST /decisions` |
| A finished, QA-passed digital product | **Nothing** — it surfaces on its own if `phases.4` is set correctly | n/a (verify STATUS.json shape) |
| An idea, or a multi-option fork Charlie needs to pick from | Strategy item | `POST /strategy` |
| Charlie approving/rejecting a product | (handled by the Inbox UI) | `POST /api/products/<num>/approve` or `/revise` |
| Charlie picking a strategy option or answering a question | (handled by the Inbox UI) | `POST /api/strategy/<id>/feedback` |

## Before you file anything

Query the live shape, don't assume it from memory (including this skill's
own examples — schemas drift):

```bash
curl -s "http://localhost:5682/decisions" | python3 -m json.tool | head -40
curl -s "http://localhost:5682/strategy?status=pending" | python3 -m json.tool | head -40
curl -s "http://localhost:8117/api/talos/products" | python3 -c "
import json,sys
d = json.load(sys.stdin)
print(len(d), 'products,', sum(1 for p in d if p.get('ready_for_review')), 'ready for review')
"
```
