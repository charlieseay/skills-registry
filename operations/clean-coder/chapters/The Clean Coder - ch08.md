# 8. Testing Strategies

## QA is part of the team, not an adversary — two roles

1. **QA as Specifiers** — work *with* business to turn requirements into the automated acceptance tests that become the real spec (business writes happy-path, QA writes corner/boundary/unhappy-path — because thinking about what can go wrong is QA's actual skill).
2. **QA as Characterizers** — exploratory testing that reports back what the system *actually* does, without interpreting requirements. Two different jobs, not one.

**"QA should find nothing"** stays the north-star goal even though it's not always achieved — every time QA does find something, development should treat it as a signal to fix the *process* that let it through, not just the individual bug.

## The Test Automation Pyramid

A layered testing strategy, from broad/cheap/fast (bottom) to narrow/expensive/slow (top):

| Layer | Coverage | Written by | Purpose |
|---|---|---|---|
| **Unit tests** (XUnit) | ~100% (practically, high-90s) | Programmers, for programmers | Specify the lowest-level design; run in CI on every commit |
| **Component tests** (API) | ~50% | QA + Business, dev-assisted | Acceptance tests wrapping one component at a time — mostly happy-path + obvious edge cases; unhappy-path is unit tests' job |
| **Integration tests** (API) | ~20% | System architects/leads | "Choreography" tests — do groups of components communicate correctly? Not business-rule tests. Often too slow for every-commit CI; run nightly/weekly. |
| **System tests** (GUI) | ~10% | Architects/tech leads | Whole-system wiring correctness and throughput/performance — not correctness of underlying logic (already proven at lower layers) |
| **Exploratory** (manual) | ~5% | Humans, unscripted | Creative, unscripted probing for the unexpected — a written test plan for this layer defeats its own purpose. Sometimes run as team-wide "bug hunt" days. |

Each higher layer intentionally covers *less* of the system — the pyramid shape is the point: cheap, fast, comprehensive tests do the bulk of the work; expensive, slow, human-driven tests fill the remaining gap.

## Build your new habit

- **WHEN THIS HAPPENS...** You're designing a test strategy for a feature or system, or QA finds a bug.
- **INSTEAD OF...** Relying on one layer alone (e.g., only unit tests, or only manual QA) or treating a QA-found bug as just "one more bug to fix."
- **I WILL...** Match the test to the right layer of the pyramid (unit for logic, component for business rules, integration for wiring, system for end-to-end, exploratory for the unscriptable), and treat any QA-found defect as a prompt to improve the layer that should have caught it.
