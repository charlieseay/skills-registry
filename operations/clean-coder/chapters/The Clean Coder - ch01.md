# 1. Professionalism

## Core claim

Professionalism is **taking responsibility** — a badge of honor paired inseparably with accountability. Nonprofessionals let their employer clean up their mistakes; professionals clean up their own.

## First, Do No Harm (borrowed from the Hippocratic oath)

Two domains a developer can harm:

### Do No Harm to Function
- You are responsible for bugs even though 100% bug-free code is impossible. The lot of a professional is to be accountable for near-certain errors — your error rate should trend toward (never reach) zero.
- **"QA should find nothing."** Sending code to QA that you haven't verified yourself is unprofessional — it's not QA's job to catch your bugs, it's your job to know your code works before you ship it.
- **You must know it works** — the only way is to test it, and the only economical way to test *constantly* is to **automate the tests** (unit tests you can run on a moment's notice).
- **100% test coverage isn't a suggestion, it's a demand** — "every single line of code that you write should be tested. Period." (100% is an asymptote you approach, not a literal claim of perfection — the book's own FitNesse project runs ~90% measured coverage with 2000+ tests.)
- Hard-to-test code is code that was **designed** to be hard to test. Fix: write the tests first (TDD, covered in ch. 5).

### Do No Harm to Structure
- Delivering function at the expense of structure is a fool's errand — flexible structure is what makes future changes affordable, and the software industry's whole economic model assumes software is easy to change.
- **The Boy Scout Rule:** "Always check in a module cleaner than when you checked it out." Flex the code constantly — small, safe, opportunistic improvements every time you touch it. Called "merciless refactoring."
- Developers avoid changing code because they fear breaking it. They fear breaking it because they lack tests. It circles back to tests: with near-100% automated coverage, you are not afraid to change code — and *changing it often* is the proof you aren't afraid.

## Work Ethic — the 60-hour rule

- Your career is **your** responsibility, not your employer's. Training, conferences, books your employer provides are favors, not entitlements.
- You owe your employer ~40 hours/week. Plan on **60 hours/week total**: 40 for the employer, **20 for yourself** — reading, practicing, learning, on your own time, on your own topics. (168 hrs/week − 40 employer − 20 career − 56 sleep = 52 hours for everything else.)
- This is explicitly framed as burnout *prevention*, not burnout risk — the 20 hours should reinforce the passion that got you into the field in the first place, not extend work.

## Know Your Field — the minimum literacy list

- **Design patterns** — all 24 GOF patterns, working knowledge of POSA
- **Design principles** — the SOLID principles, component principles
- **Methods** — XP, Scrum, Lean, Kanban, Waterfall, Structured Analysis/Design
- **Disciplines** — TDD, OO design, Structured Programming, Continuous Integration, Pair Programming
- **Artifacts** — UML, DFDs, Structure Charts, Petri Nets, State Transition Diagrams/Tables, flow charts, decision tables

Old ideas rarely become irrelevant — the field's *tools* change fast, but the underlying disciplines (patterns, principles) have stayed valuable for 50 years. Santayana's curse: "Those who cannot remember the past are condemned to repeat it."

## Continuous Learning + Practice + Collaboration + Mentoring

- **Continuous learning:** architects who stop coding, programmers who stop learning new languages, developers who stop learning new disciplines — all become irrelevant. Would you see a doctor who doesn't read medical journals?
- **Practice ≠ performance.** Your day job is performance. Practice is deliberately exercising skills *outside* the job, for the sole purpose of sharpening them — analogous to a musician's scales and etudes. The book's recommended technique: **kata** — small, repeatable programming exercises (e.g., the Bowling Game, Prime Factors) done not to solve the problem (you already know how) but to train fingers and brain. Suggested cadence: ~10 minutes as a warm-up, ~10 minutes as a cool-down.
- **Collaboration** — pairing, group design, group planning: more gets done, faster, with fewer errors, plus everyone learns from everyone. (Balance with real alone-time — both matter.)
- **Mentoring** — "the best way to learn is to teach." Explaining forces you to actually understand.

## Build your new habit (New-Habit-Formula style, inferred from chapter content)

- **WHEN THIS HAPPENS...** You're about to ship code you haven't fully tested, or you're tempted to let QA "catch it."
- **INSTEAD OF...** Shipping and hoping, or treating bug-finding as QA's job.
- **I WILL...** Write the automated test first, run the full suite before shipping, and treat any QA-caught bug as a signal to fix the *process* that let it through, not just the bug.
