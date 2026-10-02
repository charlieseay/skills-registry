# 5. Test Driven Development

## "The jury is in" — TDD is presented as non-optional

The author's framing is deliberately strong: TDD is compared to hand-washing for surgeons — not something a professional should have to defend. The chain of logic: to be professional you must know your code works → to know that, you must test it on every change → to do that economically, you need automated unit tests with very high coverage → to get that reliably, you need TDD.

## The Three Laws of TDD

1. You are **not allowed** to write any production code until you've first written a **failing unit test**.
2. You are **not allowed** to write more of a unit test than is sufficient to fail — and not compiling counts as failing.
3. You are **not allowed** to write more production code than is sufficient to pass the currently failing test.

Followed strictly, this locks you into a cycle roughly **30 seconds long**: write a sliver of test → it fails to compile → write just enough production code to compile → write a bit more test → repeat. Test code and production code grow together, "like an antibody fits an antigen."

## The five claimed benefits

1. **Certainty** — a large, fast-running, trusted test suite means "if the tests pass, I'm nearly certain nothing broke." (The book's own project, FitNesse: ~64K LOC, ~2,200 unit tests covering 90%+, running in ~90 seconds — full QA is just "run the tests.")
2. **Lower defect injection rate** — cited industry reports (IBM, Microsoft, Sabre, Symantec) showing 2x-10x defect reduction from TDD adoption.
3. **Courage** — with a trusted suite, you lose the fear of touching bad code. Without tests, the instinct on seeing a mess is "I'm not touching it, if I break it, it becomes mine." With tests, you clean it on sight — "code becomes clay you can safely sculpt."
4. **Documentation** — unit tests are executable, unambiguous examples of exactly how every object is created and every function is meaningfully called. When evaluating a third-party framework, programmers go straight to code examples over prose docs because "the code will tell you the truth" — your own tests serve that same role for your own codebase.
5. **Design** — writing the test *first* forces you to isolate the code under test, which forces decoupling. Tests written *after* the code ("defense") are written by someone already vested in how the problem was solved and are structurally weaker than tests written *first* ("offense") — after-the-fact tests can't drive the same decoupling pressure.

## What TDD is NOT

Not a religion, not a magic formula. Writing tests first doesn't guarantee good code or good tests — you can still write both badly. There are rare, legitimate cases where following the three laws is impractical; **no professional should follow a discipline that does more harm than good in a given situation.**

## Build your new habit

- **WHEN THIS HAPPENS...** You're about to write production code for a new behavior.
- **INSTEAD OF...** Writing the implementation first and testing after (or not at all).
- **I WILL...** Write a failing unit test first, write only enough code to pass it, and repeat in a tight loop — treating the resulting suite as my real definition of "it works," not a bolt-on afterthought.
