# 14. Mentoring, Apprenticeship, and Craftsmanship

## The problem: CS degrees don't reliably produce professionals

The chapter opens with a real (if extreme) anecdote — a CS master's candidate interviewing for an internship who says "I don't really write code" and had taken zero programming courses. Less extreme versions of this gap are common. Observation: the CS graduates who *aren't* disappointing almost all "taught themselves to program before they entered university and continued to teach themselves despite university." University CS can be excellent, but it doesn't reliably prepare graduates for what they'll actually meet in industry — no field's schooling maps perfectly onto its job, but software's gap is treated here as unusually wide.

## Two personal stories about being mentored

1. **The Digi-Comp I (age 12)** — a $1 mail-order manual on boolean algebra, written by strangers he'd never meet, taught him to program a plastic 3-bit finite-state-machine toy. First working program: a formative, life-shaping moment.
2. **The ECP-18 minicomputer (age 15)** — learned an entire machine's instruction set purely by silently *watching* technicians mutter to themselves while operating the front panel, then experimenting alone (learned the hard way that his programs "worked" only because he happened to zero-pad them in a way that accidentally matched the HALT instruction).

**Point of both stories: neither was conventional mentoring** — one was a well-written document from anonymous authors, the other was passive observation of people actively trying to ignore him. Both produced "profound and foundational" knowledge anyway. Mentoring can take many shapes; what matters is that *some* transfer of tacit knowledge happens.

## Hard knocks — the cost of *not* having a real mentor

Ties back to the ch. 12 firing story (missed a demo deadline, showed up late, got fired at 24) — the author's own conclusion: **"there has to be a better way."** He wishes he'd had "someone to teach me the in's and out's... someone to act as a role model and teach me appropriate values and reflexes. A sensei. A master. A mentor" instead of learning entirely by trial, error, and a termination letter.

## Apprenticeship — modeled explicitly on medicine

The chapter's central proposal is a three-tier career structure, borrowed from how medicine trains doctors (internship → residency → fellowship, roughly equal parts classroom and supervised clinical practice):

| Tier | Profile | Autonomy |
|---|---|---|
| **Apprentice / Intern** | Fresh graduate. No autonomy. | Assists journeymen; does not take independent tasks. Intense pair-programming — this is where disciplines and values get built. ~1 year. |
| **Journeyman** | Trained, competent, energetic. Typically knows one language/system/platform well, ~5 years average experience. | Closely supervised early on (code scrutinized), gaining autonomy over time until supervision becomes peer review. Journeymen are the actual teachers of apprentices — they assign reading/exercises, teach TDD/refactoring/estimation, review progress. |
| **Master** | 10+ years, led multiple significant projects, worked across multiple languages/systems, can design/architect/code at a high level. Has often turned down or fled from pure management roles. | Given technical responsibility for a project; the reference archetype given is "Scotty" (Star Trek). |

**Promotion path:** after ~1 year, journeymen who are willing to accept an apprentice recommend them upward; masters interview and review the apprentice's actual work before conferring journeyman status. Deliberately not automatic or time-based alone.

**Explicit challenge to the industry:** "It's insane" that companies hire graduates straight out of school and hand them critical systems with no structured technical supervision — a level of care the book says even painters, plumbers, electricians, and short-order cooks get more of. The stakes argument: software runs cars' engines/brakes, bank balances, bills, payments — high-consequence infrastructure deserves at least the apprenticeship rigor of lower-stakes trades.

**What's different from today's actual practice:** most companies *do* have informal supervision chains (grad → team lead → project lead), but it's rarely *technical* supervision — promotions happen "because that's just what you do with programmers," not through deliberate technical teaching, review, and mentorship.

## Craftsmanship — a meme, not a set of facts

**Craftsmanship = the mindset held by craftsmen: values, disciplines, techniques, attitudes.** The chapter's claim about how it spreads is unusual and important: **it cannot be argued into someone.** "You can't convince people to be craftsmen... Arguments are ineffective. Data is inconsequential. Case studies mean nothing." Acceptance of the mindset is closer to an emotional/observational process than a rational one — it's caught by observing it in someone else, not taught via persuasion.

**Practical implication:** the way to spread craftsmanship is to *become* visibly a craftsman yourself and let it be observed — "you act as a role model... then just let the meme do the rest of the work." Not a lecture strategy — a demonstration strategy.

## Build your new habit

- **WHEN THIS HAPPENS...** A junior developer joins your team, or you're deciding how to level up your own skills.
- **INSTEAD OF...** Assuming a CS degree alone means someone is ready for independent, unsupervised work, or trying to argue someone into caring about craft.
- **I WILL...** Treat early career stages as genuinely supervised apprenticeship (close review, real pairing, not just nominal oversight), and model the discipline I want others to adopt rather than just describing it.
