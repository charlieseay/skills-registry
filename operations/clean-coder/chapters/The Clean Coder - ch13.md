# 13. Teams and Projects

## "There is no such thing as half a person"

A common but broken pattern (the book's specific examples: banks and insurance companies): small projects staffed by people splitting time — 50%, sometimes 25% — across multiple projects, each with its own project manager, analyst, and testers. **This isn't a team, it's what came "out of a Waring blender."** Fractional attention across mismatched projects prevents the relationships and shared context a real team needs.

## The gelled team

Teams take real time to gel — the book's estimate is six months to a year — as members learn each other's quirks, strengths, and weaknesses. Once gelled, a team develops a kind of emergent capability: "they anticipate each other, cover for each other, support each other, and demand the best from each other."

- **Ideal size: ~12** (workable range 3-20).
- **Composition:** roughly a 2:1 ratio of programmers to testers+analysts (e.g., 7 programmers, 2 testers, 2 analysts, 1 project manager for a 12-person team).
- **Analysts vs. testers, restated from ch. 7:** both write acceptance tests, but analysts focus on business value (happy path), testers focus on correctness (failure/boundary cases) — same distinction as the specifier/characterizer split in ch. 8.
- **The coach/master role:** an optional part-time role, held by a team member, whose job is defending the team's process and disciplines — acting as "the team conscience when the team is tempted to go off-process because of schedule pressure."

## Which comes first, the team or the project?

**The book's strong recommendation: form persistent teams first, then allocate projects to them — not the reverse.** Banks/insurance companies that assemble a fresh team around each new project prevent gelling entirely, since individuals rotate through too briefly and too fractionally to ever really learn each other.

## Managing multiple projects with one gelled team — velocity

- **Velocity** = amount of work (measured in points, a complexity unit) a team completes per fixed period. It's statistical — expect real week-to-week variance (the book's example: 38, 42, 25 points across three weeks) that averages out over time.
- With a known average velocity, management can explicitly split a team's capacity across concurrent projects (e.g., 50 total points split 15/15/20 across three projects) — and just as importantly, **can reallocate that split on short notice** in a real emergency ("put 100% on Project B for three weeks") in a way that's essentially impossible for project-dedicated teams that would need to be dissolved and reformed.

## The project owner's dilemma

The honest tradeoff: a dedicated team gives its project owner *security* (guaranteed capacity, since reforming teams is expensive and disruptive). A shared, gelled team gives the *business* flexibility to reprioritize on a whim, at the cost of that same security for individual project owners. **The book states its preference plainly: flexibility for the business should win** — the business shouldn't have its hands tied by the artificial cost of dissolving/reforming teams, and it's the project owner's job to make the case for their project's priority, not to lock down dedicated headcount as insurance.

## Build your new habit

- **WHEN THIS HAPPENS...** You're deciding how to staff a new project, or a team is fractured across too many concurrent commitments.
- **INSTEAD OF...** Assembling a fresh team per project or splitting individuals thinly across unrelated projects with different stakeholders.
- **I WILL...** Advocate for allocating projects to an existing, gelled team (or building toward one) rather than assembling ad hoc teams around each new piece of work.
