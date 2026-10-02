# Cheatsheet — The Clean Coder

## The Three Laws of TDD
1. No production code without a failing unit test first.
2. No more test than enough to fail (not compiling counts as failing).
3. No more production code than enough to pass the current failing test.

## Language of commitment
```
COMMITMENT:  "I will [X] by [date]."          <- factual, binary, first-person
NOT:         "I need to..." / "I hope to..." / "Let's..." (no "I")
NOT:         "I'll try" -- implies hidden reserve + a new plan; if you don't have both, it's a disguised non-commitment.
```

## PERT estimation
```
μ (expected) = (O + 4N + P) / 6
σ (uncertainty) = (P − O) / 6

Sequence: μ_seq = Σμ_task     σ_seq = √(Σσ_task²)
```
O and P should each have <1% real chance of occurring alone.

## The Test Automation Pyramid (bottom → top, coverage decreasing)
```
Unit (~100%, programmers)
  → Component (~50%, business rules, QA+Business)
    → Integration (~20%, choreography, architects)
      → System (~10%, whole-system wiring)
        → Exploratory (~5%, manual, unscripted)
```

## Do No Harm
- **To function:** you must know your code works — test it, automate the tests, drive toward (never quite reach) 100% coverage.
- **To structure:** the Boy Scout Rule — always leave code cleaner than you found it. Merciless, continuous refactoring, not scheduled cleanup.

## Under pressure — MORE discipline, not less
```
Don't panic. Don't rush. Communicate early (no surprises).
Rely on discipline HARDER than usual. Get help — pair.
```

## Crisis discipline self-test
"Do I follow this practice even when it's hardest?" If you drop it under pressure, you don't actually believe in it.

## Career ladder (ch. 14)
```
Apprentice (0 autonomy, intense pairing, ~1yr)
  → Journeyman (~5yr avg, growing autonomy, teaches apprentices)
    → Master (10+yr, architecture/leadership, "Scotty")
```

## Quick diagnostic

| Situation | Move |
|---|---|
| Asked for a hard date you're unsure of | State real uncertainty, don't soft-yes |
| Pushed to "try" for less time | Recognize it as an implied commitment |
| Pressured to cut testing/refactoring to go faster | Refuse — shortcuts make you slower, not faster |
| A test looks wrong once you implement it | Negotiate a better one, don't silently comply |
| You're going to be late | Report best/nominal/worst dates now, don't hope |
| A design is turning into a mess | Recognize the inflection point — go back now, it's cheapest today |
| Real deadline pressure has arrived | Slow down, communicate, double down on discipline, pair |
