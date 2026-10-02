# Appendix A: Tooling (condensed — dated content)

The book's tooling appendix (source control, IDEs, issue tracking, CI, unit/component/integration testing tools, UML/MDA) is explicitly framed by the author as "my current personal toolkit... not a comprehensive review," written in 2011. Most of the concrete tool names (specific version control systems, specific IDEs of that era) are now dated and not durable knowledge worth extracting in detail. The load-bearing *principles* from this appendix, still relevant, are:

- **Prefer developer-written, developer-focused tools over "enterprise" tools sold to managers.** The stated reason: enterprise tools often lack the feature developers actually need most — speed.
- **If forced onto a slow/heavyweight "enterprise" system**, the book's workaround: use a fast open tool during active iteration work, and sync/check into the enterprise system only at iteration boundaries — satisfies the mandate without absorbing its cost during real work.
- The underlying stance carries forward the book's whole ethos: **tooling choices should serve the disciplines (fast feedback loops, TDD cycle time, continuous integration), not the other way around.**

For current, concrete tool recommendations, this appendix should not be treated as authoritative — the specific names are stale. The principle (favor speed and developer ergonomics; don't let heavyweight "enterprise" tooling slow the actual TDD/CI loop) is the durable takeaway.
