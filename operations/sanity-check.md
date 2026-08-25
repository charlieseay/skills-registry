---
description: Cross-model review of an agent's REASONING (not its code) — find the pattern behind repeated misdiagnoses
---

# Sanity Check

Have a different model family review **how you reasoned**, not what you built.
Established 2026-08-21 after a session that produced five misdiagnoses with one
shared root cause the agent could not see about itself.

Distinct from `parallel-review`, which reviews **code** for security,
performance and standards. This reviews **decision-making**: where you decided
you had enough evidence, and whether that was true.

## When to Use

- After a session with **2+ wrong diagnoses**, near-misses, or safety-guard blocks
- Before trusting a lesson you wrote **about yourself**
- When a fix took far more attempts than it should have
- Periodically — agents drift into habits that feel like competence
- After any near-miss on a destructive action

**Not for:** ordinary code review (use `parallel-review`), or single mistakes
with an obvious cause.

## How It Works

### 1. Assemble evidence, not narrative

Write a file containing the **actual tool-call sequences** — what you ran, in
order, and what came back. Include:

- Every failed hypothesis with the command that tested it
- The step where the answer was available but missed
- **Counter-examples**: cases in the same session that went right

Your summary of what happened is compromised — the failure was in judging when
you had enough evidence, so your account of that judgement is suspect. Ship raw
sequences.

The counter-examples matter most. Without them the reviewer can only describe
failure; with them it can identify what structurally differs.

### 2. Send to a different model family, framed adversarially

```
mcp__agy-bridge__adversarial_review  (Gemini)
cursor-agent -p "<prompt>" --output-format text   (Cursor, headless)
```

Prompt requirements — ask for the pattern, not a summary:

- "Do NOT summarize the file back to me"
- "What is the actual decision rule the agent uses? Not the one it claims —
  infer from behaviour"
- "Compare failures against counter-examples: what structurally differs?"
- "Is the agent's self-written lesson correct, or comforting? Test it against
  every case"
- "What single intervention prevents the most cases? 'Be more careful' is useless"
- "Say 'insufficient evidence' rather than inventing an answer"

### 3. Cross-check with a SECOND family — this is the step that matters

**Do not stop at one reviewer.** In the founding case, Gemini correctly found
the pattern and then overreached in its prescription ("confidence carries zero
signal — mandate falsification gates everywhere"). Cursor rejected that on
three grounds:

- N=4 in one session is anecdote, not a baseline
- The "confident and right" cases were only visible *because a guard fired* —
  selection bias, ignoring hundreds of unflagged correct actions
- Universal gates tax the 90% you get right to catch the 10% you don't

A single reviewer — especially an agreeable one — would have left that
overcorrection in the KB as doctrine.

Frame the second reviewer to **disagree**: give it the first verdict and the
same evidence, and ask it to find the overreach.

### 4. Write the lesson the reviewers support, not the one you drafted

In the founding case the agent's self-written lesson ("read the source first")
would have prevented **zero of five** cases. It described the counter-examples
and flattered the failures. Tombstone superseded lessons rather than deleting
them, so the flawed version cannot resurface.

## What This Found (2026-08-21)

Kept as a worked example — these are findings, not a template to match.

**Failure mode:** heuristic path tracing — take a scalar proxy (`wc -l`,
`head -1`, `updated_at`), build a narrative, follow one unverified branch.

**Success mode:** bounded exhaustive enumeration — a 6-case truth table before
changing a gate; all four failure paths traced; all 87 backups pairwise-diffed
against the aggregate "0 orphans" that was a false green light.

**The trigger is invokable deliberately:**
1. Truth-table gate — enumerate every input state before changing a conditional
2. Full branch trace — list every site producing an outcome before modifying one
3. Raw-diff requirement — aggregates are never proof for deletion or validation

**Surviving prescription:** state questions get state tools. Never infer live
system state from a file, a count, or a proxy timestamp. Gate on
**irreversibility**, not on felt confidence.

## Definition of Done

- [ ] Evidence file contains raw sequences, including counter-examples
- [ ] Reviewed by a model family different from the one under review
- [ ] Cross-checked by a **second** family, framed to disagree
- [ ] Disagreements resolved on merit, not by averaging
- [ ] Lessons in the KB match what the evidence supports
- [ ] Superseded lessons tombstoned, not deleted

## Related

- `parallel-review` — code review; use that for diffs
- Lesson: *Bounded exhaustive enumeration is the trigger for good diagnostic work*
- Lesson: *Confidence decouples from correctness when heuristics substitute for state queries*
- Lesson: *contract-exhaustion-not-keyword-matching*
- Lesson: *probe-runtime-state-not-static-proxies*
