---
name: office-hours
description: YC Office Hours — six forcing questions before building anything
---

# Office Hours — Product Thinking Framework

Runs six forcing questions that expose demand reality, status quo, desperate specificity, narrowest wedge, observation, and future-fit. Prevents building the wrong thing by challenging premises before code is written.

## When to invoke

- User has a product idea ("I want to build X")
- Asked "is this worth building?"
- Before starting any new project or major feature
- When exploring concepts before any code is written
- **Proactively suggest** when user describes a new product idea

## Six Forcing Questions

### Q1: Demand Reality — Who is desperate for this right now?

Not "who might want this" but who is **actively suffering** from the problem today?

- What are they doing right now to solve it?
- How much does the current workaround cost them (time/money/pain)?
- Have you talked to 3+ people who said "I would pay for this today"?

**Red flags:**
- "Everyone could use this" (too broad, no desperation)
- "There's nothing like this" (might mean no demand)
- "It would be nice to have" (nice ≠ desperate)

### Q2: Status Quo — What exists today, and why isn't it enough?

- What do people use now?
- What's broken about the current solution?
- Why haven't incumbents fixed it?
- What makes you think you can do better?

**Red flags:**
- "Nobody is doing this" (research harder)
- "The UX is bad" (rarely enough to win)
- "It's expensive" (can you really undercut them?)

### Q3: Desperate Specificity — Describe one real user's exact workflow

Not personas. Not segments. **One real person.**

- Walk me through their Tuesday
- What specific task triggers the pain?
- What do they do immediately after?
- What tool/system do they use right before and right after?

**Red flags:**
- Generic descriptions ("busy professionals")
- Multiple use cases ("it could be used for X or Y or Z")
- Abstract pain ("inefficiency", "lack of visibility")

### Q4: Narrowest Wedge — What's the smallest thing that solves the core problem?

Not MVP. Not v1. The **absolute minimum** that delivers value.

- What can you build in 1 week that one person would pay for?
- What features can you cut and still solve the problem?
- What's the one workflow that must work perfectly?

**Red flags:**
- "We need X and Y and Z to launch" (too broad)
- "It's not useful until we have all these features" (start smaller)
- Platform thinking ("we're building infrastructure for...")

### Q5: Observation — What have you seen that others haven't?

What insight or trend makes this possible **now**?

- Technology shift (AI, cost drop, new capability)
- Regulatory change
- Behavior change in users
- Market gap created by something else

**Red flags:**
- "This has always been a problem" (why now?)
- "Technology is ready" (has been for years)
- No insight, just execution

### Q6: Future-Fit — Where does this go in 3 years?

If this works, what's the bigger vision?

- Does it grow in users or revenue per user?
- Does it expand to adjacent markets?
- What's the moat if this takes off?
- Can you describe the $10M/year version?

**Red flags:**
- "We'll figure that out later" (no vision)
- "We'll pivot based on traction" (aimless)
- Can't articulate growth path

## Output

After working through all six questions, write a design doc to `Projects/<project>/<project> Office Hours YYYY-MM-DD.md`:

```markdown
---
tags: [decision, product, office-hours]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---

# <Project> Office Hours — YYYY-MM-DD

## Idea

{{One paragraph: what you want to build}}

## Six Forcing Questions

### Q1: Demand Reality
{{Who is desperate, what they do now, proof of desperation}}

### Q2: Status Quo
{{What exists, why it's broken, why incumbents haven't fixed it}}

### Q3: Desperate Specificity
{{One real user's exact workflow, specific task, specific pain}}

### Q4: Narrowest Wedge
{{Smallest thing that solves core problem, 1-week build, must-have workflow}}

### Q5: Observation
{{Insight/trend that makes this possible now}}

### Q6: Future-Fit
{{3-year vision, growth path, moat}}

## Recommendation

{{Build it / Don't build it / Build this instead}}

**Because:** {{One-line reason}}

## Next Actions

- [ ] Talk to 3 more users (if validation needed)
- [ ] Build narrowest wedge in 1 week (if green-lit)
- [ ] Write tech spec (if moving forward)
- [ ] Register decision in `Projects/<project>/Decisions/`

## References

- Related ideas: {{Links to other notes}}
- Market research: {{Links to competitor analysis}}
```

## Integration

- Outputs to vault `Projects/<project>/` directory
- Links to related decision records
- Can trigger `/plan-ceo-review` if moving forward with build
- Auto-creates project folder if it doesn't exist

## Example

```
User: "I want to build a daily briefing app for my calendar"

Claude: Let's run through office hours. 

Q1: Demand Reality — Who is desperate for this right now?

[works through all 6 questions with user]

Result: "You said 'daily briefing app' but what you described is a personal 
chief of staff AI. The briefing is just one output. The real problem is 
context switching across 3 calendars with stale information."

Recommendation: Build the narrowest wedge — a single-calendar briefing that 
works perfectly for one workflow (morning prep). Learn from real usage before 
building the 3-calendar sync layer.
```

## Notes

- **Don't skip questions** — all six matter, order matters
- **Challenge assumptions** — push back on vague answers
- **Demand proof** — "have you talked to users?" is a yes/no question
- **Be honest** — if the idea doesn't pass, say so
- **Save the output** — this becomes reference for later decisions
