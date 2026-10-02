# 10. Estimation

## The central distinction: commitment vs. estimate

- **A commitment** is something you must achieve — full stop. Missing a commitment "is an act of dishonesty only slightly less onerous than an overt lie." Professionals don't make one unless they're certain they can hit it.
- **An estimate is a guess.** No promise implied. Missing one is not dishonorable — the whole reason to estimate is that you *don't* know how long something will take.

Most developers are bad estimators not for lack of skill, but because **an estimate is not a single number — it's a probability distribution**, and treating "three days" as a commitment rather than a distribution's peak is where the trouble starts. A worked dialogue shows a developer's honest "three days" unpacking, under gentle questioning, into "50-60% likely at 3, could be 5-6, 95% confident under 6, worst case 10-11 if everything goes wrong" — a real shape, not a point estimate.

### The "try" trap, reprised from Chapter 2
When a manager asks "can you try to make it six days?", agreeing to "try" is — by the same logic as Chapter 2 — **an implicit commitment to six days**, with all the overtime/weekend/vacation-skipping that implies. Professionals decline the implied commitment and instead keep communicating the real distribution.

## PERT — turning a guess into a real distribution

Three numbers (trivariate estimation), each with <1% chance of actually occurring on their own:
- **O (Optimistic)** — everything goes right.
- **N (Nominal)** — the single most likely duration (the tallest bar on the distribution).
- **P (Pessimistic)** — everything short of catastrophe goes wrong.

Formulas:
```
μ (expected duration) = (O + 4N + P) / 6
σ (standard deviation, i.e. uncertainty)  = (P − O) / 6
```

**For a sequence of tasks:**
```
μ_sequence = Σ μ_task                      (just add the expected durations)
σ_sequence = √(Σ σ_task²)                  (root-sum-square the standard deviations)
```

Worked example in the book: three tasks with nominal estimates 3, 1.5, 6.25 (summing to only ~10.75 days) actually produce a combined expected duration of **14 days**, with a real chance of 17 or even 20 — because uncertainty compounds across a sequence in a way flat nominal-sum estimates hide entirely. This is offered as the mechanism behind the extremely common real-world pattern of "optimistically estimated projects taking 3-5x longer than hoped."

## Getting a group estimate — Wideband Delphi and its variants

The core idea across all variants: **iterate discussion + private simultaneous reveal until the group converges**, so nobody anchors on someone else's number before forming their own.

- **Flying Fingers** — discuss a task, everyone hides hands under the table, moderator counts down, all hands appear at once showing 0-5 fingers. Close-enough convergence (a mix of 3s and 4s) is fine; a lone outlier (one 1 among a sea of 4s) means more discussion is needed.
- **Planning Poker** — same mechanic with a dealt hand of numbered cards instead of fingers (0/1/3/5/10 is the author's preferred minimal deck), revealed simultaneously.
- **Affinity Estimation** — tasks on cards, spread out; team silently sorts them left-to-right (smaller→larger) relative to each other with no talking, any card moved repeatedly gets flagged for discussion once sorting settles. Final step: draw bucket-size dividing lines (often a Fibonacci-like scale: 1, 2, 3, 5, 8).
- All variants can be run twice — once for optimistic, once for pessimistic — to feed the same PERT math above.

## The Law of Large Numbers, applied to estimation

Breaking a large task into many smaller independently-estimated tasks tends to produce a *more accurate* sum than one estimate of the whole — because errors in the small tasks partially cancel out. The book is candid that this isn't a clean guarantee (estimation errors skew toward underestimation, not symmetric over/under), but decomposing large tasks is still worthwhile: it surfaces surprises and improves understanding even where the error-cancellation is imperfect.

## Build your new habit

- **WHEN THIS HAPPENS...** You're asked "how long will this take?"
- **INSTEAD OF...** Giving a single number as if it were a promise, or agreeing to "try" for a tighter date.
- **I WILL...** Communicate a real distribution (optimistic/nominal/pessimistic, or at least a stated confidence level) instead of a bare number, and be explicit about whether I'm giving an estimate (a guess) or a commitment (a promise) — never let the two blur into each other.
