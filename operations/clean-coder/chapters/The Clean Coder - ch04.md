# 4. Coding

## Preparedness — what coding actually demands

Four things must be juggled simultaneously for code to be right: (1) it must genuinely work and solve the real problem, (2) it must solve the *customer's* actual problem, not just their literal spec, (3) it must fit cleanly into the existing system without adding rigidity/fragility/opacity, (4) it must reveal its intent to other readers. This requires sustained concentration — and **if you cannot concentrate, don't code; you'll just have to redo it.**

### Three states to recognize and avoid coding in

- **3 AM code** — exhaustion masquerading as dedication. "Dedication and professionalism are more about discipline than hours." Bad decisions made while exhausted create technical debt that outlives the memory of why it was written that way.
- **Worry code** — a background emotional process (an argument, a sick child, a crisis) consumes the same mental resources coding needs. Solution: **partition time** — spend a dedicated block resolving or at least de-escalating the worry (a phone call, a check-in) rather than forcing code output through it.
- **The Zone / flow state** — feels hyper-productive but isn't reliably so; you lose the big picture and often have to revisit decisions made there. Antidotes: step away briefly, or **pair** — pairing makes the Zone nearly impossible to enter because it requires constant communication, which is presented as a *feature*, not a bug, of pairing.

## Music and interruptions

- Music's effect is personal — the author found it actively harmful to his own code quality (literally found song lyrics leaking into code comments); doesn't prescribe this as universal, but flags it as worth testing on yourself.
- Rudeness to interruptions often comes from resentment at being pulled from (or blocked from entering) the Zone. **Pairing and TDD both help**: a pair partner holds context during an interruption; a failing test itself holds your place so you can resume without having to reload the whole mental state.

## Writer's block

Sleep, worry, fear, and depression are the usual causes. **The most reliable fix found in the book: find a pair partner.** Sitting down with someone else reliably breaks the block — described as an almost physiological shift. Also: **creative input feeds creative output** — deliberately consuming other creative material (the author's specific fuel is science fiction; yours may differ) primes the pump.

## Debugging

- **Debugging time is coding time** — treat it as an expense to minimize, not an inevitable tax. The book's own claimed result: adopting TDD cut personal debugging time by roughly a factor of ten.
- The goal (an asymptote, like 100% test coverage) is to drive debugging time toward zero. "A software developer who creates many bugs is acting unprofessionally," same standard as a doctor who keeps reopening patients.

## Pacing yourself — a marathon, not a sprint

- **Know when to walk away.** Creativity and intelligence are fleeting states that vanish with fatigue; grinding on a stuck problem late at night mostly just makes you more tired without progress.
- Two specific, reported-effective disengagement rituals: **driving home** (occupies non-creative attention, frees the rest of the mind) and **the shower** (an inordinate number of problems reportedly solved there — proximity to focus can suppress the more lateral, creative part of the mind).

## Being late — the discipline of honest lateness

- You *will* be late sometimes. The failure mode isn't lateness — it's **hiding it until the last moment.**
- Track and report **three fact-based dates continuously: best case, nominal case, worst case.** Never let hope leak into the estimate. Update daily.
- **Hope is "the project killer."** If the nominal estimate doesn't meet a hard external deadline, say so loudly and early — don't let anyone, including yourself, "hope" the gap away.
- **Under pressure to rush:** hold your estimates. You cannot make yourself code faster by trying — attempting to rush produces a slower, messier result. The only real lever is reducing scope, not increasing speed.
- **Overtime**, when used, should meet three conditions: (1) you can personally afford it, (2) it's short-term (2-3 weeks max — beyond that it becomes counterproductive), (3) your manager has an articulated fallback plan if the overtime effort still fails. If your manager can't name the fallback plan, don't agree to the overtime.

## False delivery — the worst professional sin in this chapter

Saying you're "done" when you know you aren't — sometimes an outright lie, more often a **quietly rationalized redefinition of "done"** (the book cites a real client who defined done as merely "checked in," code not even required to compile). This is contagious: once one person loosens the definition, the team follows.

**The fix:** an *independent*, automated definition of done — acceptance tests written by business analysts/testers (FitNesse, Selenium, Cucumber, etc.) that must pass, understandable by non-engineers, run frequently. Done becomes externally verifiable, not self-declared.

## Help — giving and receiving

- Programming is too hard for any one person to do well alone — you WILL benefit from other perspectives. Sequestering yourself and refusing others' questions is framed as **a violation of professional ethics**, not just an interpersonal preference.
- It's fine to protect blocks of focus time (e.g., "no interruptions 10am-noon, open door 1-3pm") — the point is fairness and transparency about when you're available, not permanent unavailability.
- **When helping, commit real time** (the better part of an hour) rather than a rushed drive-by — you'll typically learn as much as you give.
- **When being helped, be gracious** — don't defend your turf, don't wave help away because you're "under the gun." Give it ~30 minutes; if it's not working, politely end it.
- **Ask for help early** — staying stuck when help is available is called out as unprofessional, not just inefficient.

## Build your new habit

- **WHEN THIS HAPPENS...** You're behind, or a manager pushes you to "just try" to hit an unrealistic date.
- **INSTEAD OF...** Hoping the gap closes itself, quietly redefining "done" to something smaller, or agreeing to open-ended overtime.
- **I WILL...** Report best/nominal/worst-case dates honestly and often, hold my estimate under pressure, and if overtime is genuinely warranted, bound it explicitly with a stated end date and a fallback plan.
