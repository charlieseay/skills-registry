---
name: writing-rules
description: Enforce Charlie's voice and writing standards on all public-facing documents
trigger: auto
---

# Writing Rules - Seaynic Labs Voice

**Mandatory for:** Any document that faces customers, users, or the public.

**Applies to:**
- Product documentation (READMEs, guides, PDFs)
- Marketing copy (landing pages, product descriptions)
- Blog posts, articles, tutorials
- Email templates, support docs
- GitHub repo READMEs
- Gumroad product listings
- Any content that represents Seaynic Labs

**Does NOT apply to:**
- Internal notes, vault documentation
- Git commit messages
- Code comments (those follow code style)
- API responses (those follow API contract)

---

## The Rules

### 1. Concrete, Not Abstract

❌ **Bad:** "This tool helps you work more efficiently"  
✅ **Good:** "This tool converts 500-line configs into 12-line YAML"

**Rule:** Every claim must be specific and measurable.

### 2. Specific, Not Generic

❌ **Bad:** "Easy to use"  
✅ **Good:** "Run `pytest` - no config file needed"

**Rule:** Name the file, the command, the exact step.

### 3. Active Voice

❌ **Bad:** "This guide is designed to cover testing patterns"  
✅ **Good:** "This guide covers 5 testing patterns you'll use daily"

**Rule:** Subject acts on object. Eliminate passive constructions.

### 4. No Question Openers

❌ **Bad:** "Want to test your Python code faster?"  
✅ **Good:** "Five pytest patterns that cut test runtime in half"

**Rule:** Never open with "Want to...?" "Need to...?" "Looking for...?"

### 5. No Most/Many/Some

❌ **Bad:** "Most developers find this useful"  
✅ **Good:** "47% of pytest users skip async testing"

**Rule:** Use exact numbers, "all", "zero", or named sets. Never vague quantifiers.

### 6. First Body Sentence Must Be Concrete

❌ **Bad:** "Testing is an important part of software development"  
✅ **Good:** "Run `pytest tests/` to execute all tests in the project"

**Rule:** First sentence after heading = concrete, topic-specific, zero fluff.

### 7. No Marketing Fluff

❌ **Bad:** "Revolutionary approach to testing"  
✅ **Good:** "Fixtures reduce test setup from 8 lines to 2"

**Rule:** Every claim must be verifiable. No superlatives without proof.

### 8. No Apologies or Hedging

❌ **Bad:** "This might help you understand fixtures"  
✅ **Good:** "Fixtures isolate test setup from test logic"

**Rule:** Confident, definitive statements. No "might", "perhaps", "hopefully".

### 9. Assume Competence

❌ **Bad:** "Don't worry, this is easy once you understand it"  
✅ **Good:** "Create a fixture by decorating a function with `@pytest.fixture`"

**Rule:** Reader is capable. Just needs the map, not reassurance.

### 10. Short Paragraphs

❌ **Bad:** 8-line paragraph explaining one concept  
✅ **Good:** 2-3 line paragraphs, each making one point

**Rule:** One idea per paragraph. White space is clarity.

---

## Tone Checklist

**You are:** A confident operator sharing the map  
**You are NOT:** A teacher, evangelist, or salesperson

**Write like:**
- You've done this 100 times
- The reader can handle it
- Time is valuable (theirs and yours)
- Precision matters

**Don't write like:**
- You're trying to convince someone
- You're selling them on an idea
- You're worried they won't understand
- You need to build excitement

---

## Before Publishing: Self-Check

Run this checklist on EVERY public document:

1. ✅ First sentence is concrete and specific?
2. ✅ No question openers?
3. ✅ No "most/many/some"?
4. ✅ Active voice throughout?
5. ✅ Every claim is measurable?
6. ✅ No marketing fluff or superlatives?
7. ✅ No apologies or hedging?
8. ✅ Assumes reader competence?
9. ✅ Short paragraphs (2-3 lines)?
10. ✅ Seaynic Labs branded? (if applicable)

**If ANY box is unchecked:** Rewrite before publishing.

---

## Skill Usage

This skill is **automatically invoked** by the `check-writing-rules` hook when you:
- Write a README
- Generate PDF documentation
- Create marketing copy
- Draft email templates
- Build product listings

**Manual invocation:**
```
/writing-rules <file-path>
```

The skill will:
1. Read the file
2. Check against all 10 rules
3. Report violations with line numbers
4. Suggest rewrites for each violation
5. BLOCK publishing if violations exist

---

## Examples

### Before (Generic AI Slop)

> **Python Testing Starter Kit**
>
> Are you looking to improve your testing workflow? This comprehensive guide will help you understand the most important testing patterns that many developers use. Testing is a critical part of software development, and this starter kit is designed to make it easier for you to get started.
>
> You'll learn about fixtures, which are a powerful feature that can help you write better tests. We'll also cover parametrization, mocking, and async testing. By the end, you should have a good understanding of how to write effective tests.

**Violations:**
- ❌ Question opener
- ❌ "most important" (vague)
- ❌ "many developers" (vague)
- ❌ "designed to make it easier" (passive + fluff)
- ❌ "should have a good understanding" (hedging)
- ❌ Abstract first sentence
- ❌ Long paragraphs

### After (Charlie's Voice)

> **Python Testing Starter Kit**
>
> Five runnable pytest templates covering fixtures, parametrization, mocking, async testing, and data factories. Drop these files into your project's `tests/` directory — pytest discovers them automatically, no config needed.
>
> Each template is 15-40 lines. Copy the pattern you need, adapt it to your code, run `pytest`. The 14-page guide explains when to use each pattern and what to avoid.
>
> Requires: `pip install pytest pytest-asyncio`

**Why it works:**
- ✅ Concrete first sentence (5 templates, named topics)
- ✅ Specific instructions ("drop into tests/")
- ✅ Active voice throughout
- ✅ No questions, no hedging, no fluff
- ✅ Assumes competence ("adapt it to your code")
- ✅ Short paragraphs (2-3 lines each)

---

## Enforcement

**This skill is MANDATORY for all public-facing content.**

If the hook detects violations:
1. Publishing is **BLOCKED**
2. Violations are **reported with line numbers**
3. Rewrites are **suggested**
4. Document must be **fixed before proceeding**

No exceptions. No "good enough". Either it follows the rules or it doesn't publish.
