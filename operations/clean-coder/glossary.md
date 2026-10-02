# Glossary — The Clean Coder

**Blind alley** — a technical dead end you've wandered into. The Rule of Holes: "when you're in one, stop digging." The real skill isn't avoiding them (unavoidable) but recognizing and reversing quickly, before becoming too vested to turn back.

**Boy Scout Rule** — "always check in a module cleaner than when you checked it out." Constant, small, opportunistic improvement instead of scheduled "cleanup" phases.

**Crisis discipline (self-test)** — observing whether you keep your normal disciplines (TDD, clean code, pairing) during an actual crisis, as a test of whether you genuinely believe in them or only practice them when convenient.

**Focus-manna** — an informal name for concentration as a finite, decaying, rechargeable resource. Sleep is the strongest lever; meetings, worry, and forced work when it's depleted all waste it.

**Gelled team** — a team that has worked together long enough (the book estimates 6 months to a year) to anticipate, cover for, and demand the best from each other. The book's central staffing principle: allocate projects to gelled teams, don't form fresh teams around each project.

**Language of commitment** — "I will [X] by [date]" — first-person, factual, binary. Contrasted with non-commitment language ("need/should," "hope/wish," "let's" without "I").

**Messes** — worse than blind alleys because they let you keep moving forward while quietly destroying productivity. The inflection point is the moment you realize the design was wrong; going back is never cheaper than it is right then.

**PERT (trivariate estimation)** — Optimistic/Nominal/Pessimistic estimate → μ = (O+4N+P)/6, σ = (P−O)/6. For sequences: μ sums, σ root-sum-squares.

**Priority inversion** — raising a lower-priority task's apparent urgency to avoid a harder, higher-priority one. Named explicitly as self-deception, and preparation for a future justification.

**QA should find nothing** — the standing goal (never fully achieved, always aimed at): code should be verified by the developer before QA ever sees it; every QA-found bug is a process failure, not an acceptable cost of doing business.

**Test Automation Pyramid** — layered test strategy: Unit (~100%, programmers/programmers) → Component (~50%, business rules) → Integration (~20%, choreography between components) → System (~10%, whole-system wiring) → Exploratory (~5%, manual, unscripted).

**The Three Laws of TDD** — (1) no production code without a failing unit test first, (2) no more test than enough to fail, (3) no more production code than enough to pass. Locks you into a ~30-second red/green cycle.

**Trying (the trap)** — "I'll try" implies a hidden reserve of effort and a new plan to unlock it; without both, it's a disguised, unaccountable promise. "There is no trying."

**Wideband Delphi** — group estimation via iterated private-then-simultaneous reveal (Flying Fingers, Planning Poker, Affinity Estimation are variants), converging on consensus without anchoring bias.

**Apprentice → Journeyman → Master** — the book's proposed career structure, modeled on medicine's internship/residency/fellowship. Apprentices have no autonomy and pair intensively; journeymen gain autonomy as supervision loosens; masters lead architecture/design across multiple systems.

**Craftsmanship (as a meme)** — the mindset of a craftsman, explicitly framed as un-arguable — spread only by being observed in a role model, not persuaded via data or case studies.
