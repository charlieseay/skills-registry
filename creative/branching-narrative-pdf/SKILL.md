---
name: "branching-narrative-pdf"
description: "Blueprint for branching-narrative 'gamebook' PDFs (choose-your-own-adventure style, e.g. survival scenarios) for Etsy/Gumroad, built via HTML+Playwright rather than Canva. Documents a real, serious defect found and fixed in the first build: a CSS min-height taller than the printable page area silently split every logical page across two physical PDF pages, breaking the core 'turn to page N' mechanic for buyers. Use this whenever building a gamebook, choose-your-own-adventure PDF, or any other page-number-navigated print PDF via HTML/CSS/Playwright."
category: "creative"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["occasion-card-generation", "digital-product-quality-bar", "talos-product-launch-audit"]
---

# Branching Narrative PDF — Gamebook Pipeline

**Fleet-wide skill.** This is the shop's first plain-text/PDF-generation pipeline (distinct from the Canva-illustration pipeline used by `coloring-book-generation` and its sibling skills, and distinct from `notion-template-api-build`'s Notion-workspace API). Builds via HTML + Playwright's `page.pdf()`, reusing the rendering approach already proven in `occasion-card-generation`.

## Why this exists

On 2026-09-22, Charlie's brief was "a survival handbook that reads like a story or a game you have to learn as you progress through the challenges/story." Market research (two independent passes, both with real listing IDs) found: choose-your-own-adventure/gamebook PDFs are a real, proven niche (confirmed Etsy listings at $4.50 and $16.50, DriveThruRPG $5-12, itch.io community); survival-themed interactive fiction specifically is genuine white space with no commercial precedent found (only one free proof-of-concept, "Preppers: The Game" on itch.io). This justified a small, cheap validation bet rather than a big build — see product-item-178.

**The first build had a real, serious defect that a self-reported "verified, no broken links" claim did not catch.** The build agent's own verification checked that referenced page numbers existed *somewhere* in its internal data model, not that the *rendered PDF's physical pages* actually lined up with their printed page-number labels. The actual bug: the CSS gave `.page { min-height: 10in; }` inside an `@page { size: 8.5in 11in; margin: 0.75in; }` context. The printable content area per physical page is only 9.5in tall (11in − 0.75in top − 0.75in bottom), so `min-height: 10in` forced every logical page to overflow onto a second physical page. Combined with real 200-400 word scenario text, a heading, and a choices block, EVERY logical page spilled across two physical PDF pages — the page count came out at 33 physical pages for what should have been 17 (1 title + 16 numbered pages).

**Why this was dangerous, not just cosmetic:** the printed "Page 1" label landed on physical page 2 (mostly empty), while the actual scenario text and "Turn to page 3" / "Turn to page 4" choice instructions spilled onto physical page 3 — which had NO visible page-number label printed on it at all (the footer element got pushed onto the first physical page by `margin-top: auto`, leaving the overflow page unlabeled). A buyer reading "Page 1," reaching the bottom, and flipping to "page 3" as instructed would find no page labeled "3" anywhere near where they'd expect it, since every logical page was consuming roughly two physical pages. This is worse than shipping nothing — a customer experiencing this would reasonably conclude their PDF download was corrupted, not that the product itself was broken.

## The fix

Remove `min-height` from `.page` (and any other structural container competing for full-page height, e.g. `.title-page`) and let content size naturally — rely on `page-break-after: always` alone to force each logical page onto its own physical page. If a specific page's real content still doesn't fit within the actual printable height (page size minus `@page` margins) at the chosen font sizes/padding, the correct fix is trimming padding/margins or reducing font size for that content, never adding back a `min-height` that exceeds the printable area.

## The verification method that actually catches this — use it every time

Do NOT trust "the PDF looks fine" or an internal reference-count check. Extract the actual rendered PDF's text with page boundaries preserved and verify from the OUTPUT, not the source data model:

```bash
pdftotext -layout Your-Gamebook.pdf output.txt
```

```python
import re
text = open("output.txt").read()
pages = text.split("\f")  # \f is the form-feed pdftotext inserts between physical pages

print("Total physical PDF pages:", len(pages))
for i, p in enumerate(pages, start=1):
    m = re.search(r"Page (\d+)\s*\Z", p.rstrip())  # label sits at the end of the page, often with trailing whitespace
    label = m.group(1) if m else "NONE"
    refs = re.findall(r"Turn to page (\d+)", p)
    print(f"physical page {i}: label={label}, refs={refs}")
```

Checks that must all pass before shipping:
1. **Total physical page count matches the expected logical page count** (title page + N numbered pages). A mismatch (e.g. 33 physical pages for 16 logical pages) is the single fastest signal something is overflowing.
2. **Every physical page has exactly one page-number label**, in strictly increasing order, with no gaps and no unlabeled pages in between.
3. **Every "Turn to page N" reference is printed on the SAME physical page as its own page's label** — not spilling onto a second, unlabeled physical page. This is the check that actually catches the overflow bug; a page-count match alone (checked 1) can still hide a case where content shifted but totals coincidentally matched.
4. **Every "Turn to page N" target number actually appears as a real page label somewhere in the document** — no dangling references to a page number that doesn't exist.

A regex anchored on a clean standalone line (`^Page \d+\s*$`) can produce false "NONE" results if the label sits at the end of a paragraph's trailing whitespace on the same conceptual line rather than a clean standalone line after `.strip()` — anchor on `Page (\d+)\s*\Z` against the page's raw (non-stripped) text instead, or inspect a raw page's content directly if labels aren't matching as expected before concluding the fix failed.

## Content and structure guidance

- **Keep the first validation product genuinely small**: 5-7 major decision points, 12-18 total pages, 200-400 words per page. A branching structure's complexity explodes geometrically — a "50-path epic" is not a reasonable first bet for an unproven niche.
- **Use the classic page-number mechanic ("Turn to page N"), not clickable PDF links, for a first validation product.** Real clickable internal PDF links (`GoTo` actions via ReportLab's `canvas.bookmarkPage()`/`canvas.linkAbsolute()`, or equivalent) are technically real and well-documented, but Apple Preview has known quirks with named destinations specifically. Page-number instructions work in literally every PDF reader with zero technical risk — save clickable links for a later, higher-polish iteration if the category validates.
- **The narrative should carry genuinely useful content, not just be a game wrapper.** product-item-178's survival scenarios embedded real, accurate guidance (food safety windows, water storage, when to shelter vs. evacuate) inside the narrative choices — this is what separates a legitimate prepper-adjacent product from a novelty.
- **Multiple distinct endings matter for perceived replay value.** product-item-178 shipped 8 distinct endings from 5 decision points — a buyer re-reading with different choices should reach meaningfully different outcomes, not just cosmetic variations of the same ending.

## Reference implementation

Product-item-178 (2026-09-22): "Urban Survival: Apartment Power Outage." 16 numbered pages + title page, 5 decision points, 8 endings, single PDF (not per-page files, unlike the coloring-book category — a gamebook is one document a reader flips through). Built via Playwright HTML-to-PDF (`generate_gamebook.py`), $3.99, explicitly documented in its own STATUS.json as a cheap validation bet against genuine white space, not proven demand.

---

**This skill was authored 2026-09-22 after a real page-overflow defect was found (by extracting and manually mapping the rendered PDF's physical pages) in the first build, root-caused to a CSS `min-height` exceeding the printable page area, and fixed and re-verified using the pdftotext-based method documented above.**
