# 7. Acceptance Testing

## Core claim

Requirements communication between business and programmers is systematically error-prone. **The only reliable fix: automated acceptance tests written collaboratively, that formally define "done."**

## The observer effect on requirements — "premature precision" and "late ambiguity"

- **Premature precision:** both business (wanting exact scope before committing) and developers (wanting exact scope before estimating) chase a precision that isn't actually achievable — a spec looks different on paper than running in a system, and seeing it running changes what the business realizes they actually want.
- **The fix:** defer precision as long as possible — flesh out a requirement right before you build it, not far in advance.
- **The cost of deferring:** "late ambiguity" — disagreements get papered over with vague wording instead of resolved. Tom DeMarco: *"An ambiguity in a requirements document represents an argument amongst the stakeholders."*
- **Worked example of contextual ambiguity:** a stakeholder says "back up the log files daily," a developer hears "save last night's log," the customer meant "keep every log file forever" — nobody was lying, everyone assumed shared context that didn't exist. This kind of gap is invisible until it causes real damage.

## Acceptance tests = the actual definition of "done"

Professional developers reject soft distinctions like "done" vs. "done-done." **Done means done: all code written, all tests pass, QA and stakeholders have accepted** — and the way to make that objective rather than a matter of opinion is to drive requirements all the way down to **automated acceptance tests** written collaboratively by developers, testers, and stakeholders.

**Worked example** (the log-backup ambiguity, redone correctly): a three-way conversation (business stakeholder, developer, tester) forces out exactly what "backup" means (a permanent archive, not a temp copy), what it should be named (`old_inactive_logs`, chosen to be self-documenting), and produces an explicit given/when/then test spec before any code is written.

## Who writes them, and when

- Ideally stakeholders + QA collaborate, developers review for consistency. In practice, business analysts often write the "happy path" (business-value scenarios), **QA writes the "unhappy path"** (edge cases, exceptions — because finding what can go wrong is QA's actual job).
- If a developer must write the tests, **it should not be the same developer who implements the feature** (avoids testing your own assumptions back at yourself).
- Timing follows "late precision": tests should be ready a few days before implementation, not far in advance. In an iteration/sprint: first tests ready day 1, all ready by the iteration's midpoint (past that, developers or additional BA/QA capacity should help catch up).

## Negotiating a bad test — don't be passive-aggressive about it

Test authors make mistakes too. If a test as written is wrong, overcomplicated, or based on a bad assumption, **it's the developer's job to push back and negotiate a better one** — not to shrug and implement exactly what a flawed test says just to avoid the conversation. Worked example: negotiating a vague "finishes in 2 seconds" latency requirement into a real, statistically defined test (a Z-score threshold) that's both technically honest and still readable by the non-statistician who has to sign off on it.

## Acceptance tests vs. unit tests — not redundant

| | Unit tests | Acceptance tests |
|---|---|---|
| Written by/for | Programmers, for programmers | Business, for business (even if a developer writes them) |
| Audience | Programmers | Business + programmers |
| Entry point | Deep — individual classes/methods | Shallow — API or UI level |
| Primary purpose | **Document** the lowest-level design (being executable/verifying is a secondary bonus) | **Document** system behavior from the business's point of view |

Both are documents first, tests second — the fact that they also verify behavior automatically is "wildly useful" but not their core purpose.

## Testing GUIs — treat the GUI as an API

GUIs are aesthetically volatile (people constantly want to tweak layout/fonts/flow), which makes naive GUI-level acceptance tests fragile — a layout change breaks hundreds of tests. Fix, via the **Single Responsibility Principle**: separate what changes for aesthetic reasons from what stays stable underneath.

- Select elements by stable ID/name, never by screen position.
- **Better still: test business rules through the same API the GUI itself calls**, bypassing the GUI entirely for anything that isn't specifically testing the GUI's own behavior.
- Keep true GUI-level tests to a minimum — decouple business rules from the GUI (stub them out) when a test genuinely needs to exercise GUI behavior specifically.

## Continuous Integration — "stop the presses"

Run all unit + acceptance tests multiple times a day, triggered by source control commits, results emailed to the whole team. **A broken CI build is an emergency** — the whole team stops and fixes it, full stop. The book cites a real failure case: a team got "too busy" to fix broken tests, pulled them from the build to silence the noise, forgot to restore them, and shipped a real defect straight to an angry customer as a result.

## Build your new habit

- **WHEN THIS HAPPENS...** A requirement is being described in prose, or a written acceptance test looks wrong/awkward/incomplete once you start implementing it.
- **INSTEAD OF...** Assuming shared understanding without checking, or silently implementing a test you believe is flawed just to avoid the conversation.
- **I WILL...** Drive the requirement to a concrete, automated given/when/then test collaboratively, and negotiate any test I believe is wrong rather than build to a spec I don't trust.
