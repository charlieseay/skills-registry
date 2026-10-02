---
name: clean-coder
description: "Extracted from Robert C. Martin's 'The Clean Coder: A Code of Conduct for Professional Programmers' (2011). A code of professional conduct for software developers covering commitment language, saying no/yes honestly, TDD, acceptance testing, estimation as probability, handling pressure, collaboration, team structure, and mentoring/apprenticeship. Use when the user wants to negotiate a deadline, give an honest estimate, decide whether to cut corners under pressure, structure a team, or think through what professional conduct looks like for a developer."
---

# The Clean Coder — A Code of Conduct for Professional Programmers

## Philosophy

**Professionalism = taking responsibility.** The book's single throughline: a nonprofessional lets their employer absorb the cost of their mistakes; a professional owns the mistake and its consequences. Every chapter is really an application of this one idea to a different situation — saying no, saying yes, testing, estimating, handling pressure, collaborating, mentoring.

**"First, do no harm"** (borrowed deliberately from the Hippocratic oath) — to function (bugs) and to structure (rigidity, messes). Both are addressed by the same discipline: automated tests you actually trust, run constantly.

## The 14 chapters

| # | Chapter | Core idea | File |
|---|---|---|---|
| 1 | Professionalism | Taking responsibility; do no harm; the 60-hour work-ethic rule; kata as deliberate practice | [chapters/The Clean Coder - ch01.md](chapters/The%20Clean%20Coder%20-%20ch01.md) |
| 2 | Saying No | Adversarial roles are healthy; "there is no trying"; the real cost of always saying yes | [chapters/The Clean Coder - ch02.md](chapters/The%20Clean%20Coder%20-%20ch02.md) |
| 3 | Saying Yes | A language of commitment: "I will X by Y"; telltale non-commitment phrases | [chapters/The Clean Coder - ch03.md](chapters/The%20Clean%20Coder%20-%20ch03.md) |
| 4 | Coding | Preparedness, the Zone, writer's block, debugging, being late honestly, false delivery | [chapters/The Clean Coder - ch04.md](chapters/The%20Clean%20Coder%20-%20ch04.md) |
| 5 | Test Driven Development | The Three Laws of TDD; certainty, courage, documentation, design as benefits | [chapters/The Clean Coder - ch05.md](chapters/The%20Clean%20Coder%20-%20ch05.md) |
| 6 | Practicing | Kata, wasa, randori — deliberate practice outside of performance | [chapters/The Clean Coder - ch06.md](chapters/The%20Clean%20Coder%20-%20ch06.md) |
| 7 | Acceptance Testing | Premature precision vs. late ambiguity; acceptance tests as the real definition of "done" | [chapters/The Clean Coder - ch07.md](chapters/The%20Clean%20Coder%20-%20ch07.md) |
| 8 | Testing Strategies | The Test Automation Pyramid — unit/component/integration/system/exploratory | [chapters/The Clean Coder - ch08.md](chapters/The%20Clean%20Coder%20-%20ch08.md) |
| 9 | Time Management | Meeting discipline, focus-manna, Pomodoro, priority inversion, blind alleys, messes | [chapters/The Clean Coder - ch09.md](chapters/The%20Clean%20Coder%20-%20ch09.md) |
| 10 | Estimation | Estimate ≠ commitment; PERT trivariate estimation; Wideband Delphi variants | [chapters/The Clean Coder - ch10.md](chapters/The%20Clean%20Coder%20-%20ch10.md) |
| 11 | Pressure | Calm under pressure; crisis discipline as a self-test; rely on discipline, not panic | [chapters/The Clean Coder - ch11.md](chapters/The%20Clean%20Coder%20-%20ch11.md) |
| 12 | Collaboration | Collective code ownership; pairing as default, not emergency-only | [chapters/The Clean Coder - ch12.md](chapters/The%20Clean%20Coder%20-%20ch12.md) |
| 13 | Teams and Projects | Gelled teams; allocate projects to teams, not teams to projects; velocity | [chapters/The Clean Coder - ch13.md](chapters/The%20Clean%20Coder%20-%20ch13.md) |
| 14 | Mentoring, Apprenticeship, Craftsmanship | Apprentice → Journeyman → Master; craftsmanship as an observed meme, not an argued one | [chapters/The Clean Coder - ch14.md](chapters/The%20Clean%20Coder%20-%20ch14.md) |

## The book's throughline in one page

1. **Commitment language matters.** "I will X by Y" is a commitment. "I'll try" is not — it's either a hidden lie or a hidden admission you were holding back effort. Estimates are guesses (a probability distribution); commitments are promises. Never let the two blur.
2. **Saying no is professional, not insubordinate.** Managers doing their job push for aggressive dates; developers doing their job push back with real numbers. Confrontation avoided isn't harmony — it's often one side quietly failing their role.
3. **Tests are the mechanism that makes everything else possible.** TDD (unit level) + acceptance tests (business level) + the full pyramid (component/integration/system/exploratory) are what let you say "QA should find nothing," stay honest about "done," and have the *courage* to keep code clean without fear.
4. **Under pressure, do MORE of your discipline, not less.** "Crisis discipline" is the book's test for whether you actually believe in a practice: do you follow it when it's hardest, or only when it's convenient?
5. **Professionalism is social, not just technical.** Saying no/yes honestly, pairing, collective ownership, gelled teams, and mentoring apprentices are all professional obligations — not optional extras layered on top of "real" (technical) work.

## Supporting frameworks

- [glossary.md](glossary.md) — named concepts (Three Laws of TDD, PERT, Test Automation Pyramid, focus-manna, the Drama-free negotiation model, apprentice/journeyman/master, etc.)
- [patterns.md](patterns.md) — situational playbook: what to do when pushed to "just try," when a test looks wrong, when you're under real deadline pressure, when a design starts turning into a mess
- [cheatsheet.md](cheatsheet.md) — one-page quick reference
- [chapters/appendix-tooling.md](chapters/appendix-tooling.md) — condensed note on the book's (dated) tooling appendix

## Source

Robert C. Martin ("Uncle Bob"), *The Clean Coder: A Code of Conduct for Professional Programmers* (Prentice Hall, 2011). ISBN 978-0-13-708107-3.
