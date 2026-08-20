---
description: Guided feature development with mandatory clarification gates
---

# Phased Feature

Structured 5-phase approach for implementing new features with comprehensive codebase understanding and architecture planning BEFORE writing code.

## When to Use

- Building new features
- Large refactoring projects
- Work requiring architectural decisions
- Complex integrations
- Any work where "just start coding" would cause rework

## Don't Use When

- Simple bug fixes
- Configuration tweaks
- Documentation-only updates
- Obvious one-file changes

## The 5 Phases

### Phase 1: Discovery

**Goal:** Clear understanding of what needs to be built

**Actions:**
1. Create todo list with all 5 phases
2. If feature request is unclear, ask:
   - What problem are they solving?
   - What should the feature do?
   - Any constraints or requirements?
3. Summarize understanding in 2-3 sentences
4. Get user confirmation before proceeding

**Output:** Written goal statement user has approved

---

### Phase 2: Codebase Exploration

**Goal:** Understand existing code patterns at both high and low levels

**CRITICAL:** Don't skip this. Understanding the codebase prevents building the wrong thing.

**Actions:**

1. Launch 2-3 parallel code-explorer agents (Sonnet or nvidia-agent), each targeting a different aspect:

   **Agent A: Similar Features**
   > Find features similar to [feature name] and trace through their implementation comprehensively. Return: architecture overview + list of 5-10 key files to read.

   **Agent B: Architecture & Abstractions**
   > Map the architecture and abstractions for [feature area], tracing through the code comprehensively. Return: high-level flow + component relationships + 5-10 key files.

   **Agent C: Patterns & Extension Points**
   > Identify UI patterns, testing approaches, and extension points relevant to [feature]. Return: current conventions + where this feature should integrate + 5-10 key files.

2. **After agents return:** Read ALL files they identified (don't just read their summaries)

3. Present comprehensive summary of findings and patterns discovered

**Output:** 
- Understanding of existing architecture
- 10-20 key files read and understood
- Written summary of relevant patterns

---

### Phase 3: Clarifying Questions

**Goal:** Fill in ALL gaps and resolve ambiguities before designing

**CRITICAL:** This is the most important phase. DO NOT SKIP. This prevents "I assumed you wanted X but you meant Y" failures.

**Actions:**

1. Review codebase findings + original feature request
2. Identify ALL underspecified aspects:
   - Edge cases?
   - Error handling strategy?
   - Integration points?
   - Scope boundaries? (What's explicitly OUT of scope?)
   - Performance requirements?
   - Backward compatibility needs?
   - Design preferences? (UI/UX choices, API shape)
   - Security considerations?
   - Testing expectations?

3. **Present ALL questions to user in organized list**

4. **BLOCK until answers provided**

**If user says "whatever you think is best":**
- Provide your recommendation with reasoning
- Get explicit confirmation
- Don't assume approval

**Output:** 
- All ambiguities resolved
- Documented decisions
- User approval to proceed

---

### Phase 4: Architecture Design

**Goal:** Design multiple approaches, compare trade-offs, get user buy-in

**Actions:**

1. Launch 2-3 code-architect agents with different focuses:

   **Approach A: Minimal Changes**
   > Design implementation that makes the SMALLEST change possible. Maximum code reuse, minimum new abstractions. What's the simplest way to add this feature?

   **Approach B: Clean Architecture**
   > Design implementation optimizing for maintainability and elegant abstractions. What would this look like if we built it "the right way"?

   **Approach C: Pragmatic Balance**
   > Design implementation balancing speed and quality. Good enough for production but not over-engineered. What's the practical middle ground?

2. Review all approaches and form your opinion (consider: urgency, complexity, team context, is this a small fix or major feature?)

3. Present to user:
   - Brief summary of each approach (2-3 sentences each)
   - Trade-offs comparison table
   - **Your recommendation with clear reasoning**
   - Concrete implementation differences (what files change, what gets added)

4. **Ask user which approach they prefer**

**Output:**
- 3 architectural approaches documented
- Trade-offs clearly presented
- User-approved approach to implement

---

### Phase 5: Implementation

**Goal:** Build the feature following chosen architecture

**DO NOT START WITHOUT USER APPROVAL**

**Actions:**

1. Wait for explicit approval from Phase 4
2. Re-read all relevant files identified in Phase 2
3. Implement following chosen architecture from Phase 4
4. Follow codebase conventions strictly (spacing, naming, error handling, testing patterns)
5. Write clean, well-documented code
6. Update TodoWrite as you progress
7. Test as you build (don't wait until the end)

**Output:**
- Working feature
- Tests passing
- Documentation updated
- Changelog entry
- Git commit with clear message

---

## Progress Tracking

Use TodoWrite throughout:

```markdown
- [ ] Phase 1: Discovery
- [ ] Phase 2: Codebase Exploration
  - [ ] Agent A: Similar features
  - [ ] Agent B: Architecture
  - [ ] Agent C: Patterns
  - [ ] Read all identified files
- [ ] Phase 3: Clarification
  - [ ] Questions identified
  - [ ] Answers received
- [ ] Phase 4: Architecture
  - [ ] 3 approaches designed
  - [ ] User approval
- [ ] Phase 5: Implementation
  - [ ] Code written
  - [ ] Tests passing
  - [ ] Docs updated
```

Update after each phase completes.

---

## Usage

```bash
# Start phased feature development
/phased-feature [optional: brief feature description]

# Resume at specific phase (if interrupted)
/phased-feature --phase 3
```

---

## Why This Works

**Problem:** Jumping straight to implementation causes:
- Misunderstood requirements
- Inconsistent with existing patterns
- Architectural mismatch
- Rework when user says "not what I wanted"

**Solution:** Phased approach with gates:
- **Phase 2** ensures you understand the codebase
- **Phase 3** ensures you understand the requirement
- **Phase 4** ensures user agrees with the approach
- **Phase 5** executes with confidence

## Anti-Patterns (Reject These)

❌ "I'll just start coding and figure it out"
❌ Skipping codebase exploration because "it's just a small feature"
❌ Skipping clarification because "it seems obvious"
❌ Presenting one architecture as "the way" without alternatives
❌ Starting implementation before getting Phase 4 approval

## Example Run

```bash
User: "Add ability to export reports as PDF"

Phase 1: Discovery
✓ Confirmed: Reports page needs Export button → generates PDF → downloads to user

Phase 2: Exploration
✓ Found: Invoices already export to PDF using jsPDF library
✓ Found: Reports use same data table component as invoices
✓ Read: 12 key files (InvoiceExport.tsx, ReportTable.tsx, pdfGenerator.ts, ...)

Phase 3: Clarification
❓ Should PDF match printed layout or be custom designed?
❓ Include charts/graphs or just tables?
❓ Any branding requirements (logo, colors)?
→ Answers: Match printed layout, include charts, use company logo

Phase 4: Architecture
A: Minimal → Copy invoice PDF code, adapt for reports (fastest)
B: Clean → Abstract shared PDF generator, inject report-specific template (maintainable)
C: Pragmatic → Shared PDF utilities, report-specific implementation (balanced)

Recommendation: Approach C (shared utils, lets us customize reports differently than invoices later)
✓ User approved

Phase 5: Implementation
✓ Created src/utils/pdf.ts with shared helpers
✓ Created src/features/reports/exportPDF.ts with report logic
✓ Added Export button to ReportTable.tsx
✓ Tests passing
✓ Commit: Add PDF export to reports (#542)
```

---

## Integration with Brief Templates

When dispatching autonomous work, embed the phased approach in the brief:

```markdown
## Phased Approach

This task follows the 5-phase feature development pattern.

### Phase 2: Discovery
Dispatch 3 nvidia-agent tasks to explore:
- Similar features: [specific prompt]
- Architecture: [specific prompt]
- Patterns: [specific prompt]

### Phase 3: Clarification
Before proceeding to architecture, answer:
- [Question 1]
- [Question 2]
- [Question 3]

### Phase 4: Architecture
Present 3 approaches (minimal / clean / pragmatic) with trade-offs.
Recommend one. Get approval before Phase 5.

### Phase 5: Implementation
[Specific deliverables based on approved architecture]
```

## Lessons

- **2026-06-15** — `when_a_feature_call_fails_at_runtime__ve`: When a feature call fails at runtime, verify the backend endpoint actually exists before debugging the client. ls src/pages/api/<feature>/ and git log --name-only to confirm files were actually committed. [src: task-unknown]
- **2026-06-16** — `feature-starved-of-data-not-missing`: Before building a 'missing' feature, check if it already EXISTS but is starved of data or mis-wired. The bid-review and deliverable-review UIs both existed — they showed nothing because the board was empty (ssh bug) + a button was mis-wired. Verify the data path + wiring before writing new UI. _(context: Spent effort thinking bid/deliverable review needed building; both were fully built, just data-starved by the broken board + one mis-wired button.)_ [src: session/2026-06-16-meta]
