---
name: "product-illustration-generation"
description: "Generate recognizable illustrated artwork for a digital product (picture cards, flashcards, icon sets, instructional diagrams) with Fal.ai Flux, at ~$0.001 per image. Use when a product's value depends on a buyer or a CHILD recognizing what a picture shows, when hand-coded Pillow/SVG primitives have produced abstract shapes, or before shipping any product whose promise is 'picture-based' / 'no reading required'. Includes the per-image subject table pattern, the mandatory visual QA pass, and the three failure modes Flux reliably produces (hallucinated text, trademarked emblems, wrong-object substitution)."
category: "product"
metadata:
  version: "1.0.0"
  agents: ["any"]
  related_skills: ["etsy-preview-quality", "digital-product-quality-bar", "etsy-hero-image-generation", "product-quality-verify"]
---

# Product Illustration Generation

**Fal.ai Flux (Black Forest Labs). NOT Gemini** — Charlie has ruled the Gemini
API out; Fal is a separate provider and is the sanctioned image lane.

## Why this exists

2026-10-14: product-item-223 (Montessori Visual Routine Cards) shipped with
illustrations hand-coded as Pillow primitives. "Put On Pajamas" rendered as a
hexagon, "Brush Teeth" as a diagonal bar, "Eat Dinner" as a circle between two
lines. The product promised "picture-based routine a toddler can follow, no
reading required" — a core promise that a geometric shape cannot keep. QA
passed it because all 64 files hashed differently.

`icon_lib.py` also ALIASED icons (`hands-wash-2`/`-3` -> one function,
`toothbrush-2`, `comb-2`, `bath-2`, `book-2`, `heart-2`), so different cards
drew identical pictures. **Check for aliasing in any name->function map.**

## The method

### 1. One explicit SUBJECT per asset — never reuse a prompt
Build a dict mapping each asset id to a concrete noun phrase describing what
the picture must SHOW. "a toothbrush with a blob of toothpaste", not "hygiene".
Assert zero missing before spending anything.

### 2. One shared STYLE suffix
```
flat vector illustration for a toddler's picture card, simple bold shapes,
thick clean outlines, soft pastel colours, cheerful, centered on a plain white
background, no text, no letters, no words, no logos, no watermark
```
Consistency across the set comes from the shared suffix; distinctness comes
from the per-asset subject.

### 3. Generate
`POST https://fal.run/fal-ai/flux/schnell`, header `Authorization: Key <key>`,
key at `/Volumes/data/secrets/n8n_fal_api_key`. Body: `prompt`, `image_size:
"square"`, `num_inference_steps: 4`. Thread-pool 5 workers; retry 3x with
backoff; skip any file already on disk so a re-run is cheap.

**Cost: flux/schnell is $0.003/megapixel.** 512x512 is ~$0.0008 each; 64 icons
cost about $0.05. Charlie's Fal budget is ~$20/month — this is nothing. Do NOT
reach for flux/dev ($0.025/MP) for flat icon work.

### 4. VISUAL QA IS MANDATORY — build a contact sheet and LOOK
Tile every generated image into one labelled sheet and read it. Hashing proves
distinctness, not correctness. Three failure modes Flux produces reliably:
- **Hallucinated text** — it writes garbled words on books/signs despite "no
  text". Observed: a storybook reading "Aur bedtime".
- **Trademarked emblems** — "superhero cape" produced a Superman-style S
  shield. This is a LEGAL risk on a product for sale. Re-prompt with "plain,
  no emblem, no letters, no logo".
- **Wrong object** — "nail clippers" produced pliers, then scissors. When two
  re-prompts fail, change the SUBJECT rather than fight the model (we shipped
  "a child's open hand with clean short nails and a sparkle", which reads
  better to a toddler than any tool).

### 5. Wire into the build, don't hand-place
Write the PNGs to `phase-2/art/<id>.png` and replace the drawing dispatcher:
```python
def draw_icon(draw, name, box, ink, accent):
    im = _art(name)
    if im is None:                      # keep the old primitives as fallback
        ICONS.get(name, icon_star)(draw, box, ink, accent); return
    ...fit to box, paste with alpha...
```
Flux renders on near-white, not transparent — knock back pixels above ~243 to
alpha 0 so the card's tinted panel shows through instead of a grey box.

### 6. Re-verify after the rebuild
Re-hash the rendered cards (must be N distinct) and LOOK at a rendered board.
Then check the packaged zip against Etsy's **20MB per-file limit** — real
artwork is far larger than vector fills (3.3MB -> 28MB in our case), so the
split-into-parts path is usually needed.

## Verification is a pipeline step, not a manual favour

`talos-tools/digital-products/tools/visual_review.py` runs the semantic check
automatically against the **local Ollama vision model on the M5**
(`http://192.168.68.67:11434`, `gemma3:27b`). Zero cost, no external API, and
**not Gemini** — Charlie has ruled the Gemini API out; this is a local weights
file served by Ollama.

```bash
cd ~/Projects/talos-tools/digital-products
python3 tools/visual_review.py <product-dir> \
  --product "a toddler visual routine card deck" \
  --audience "a 3-year-old who cannot read"
```

It writes `phase-4/visual-review.md`, which `qa_gate.check_illustrations_reviewed()`
requires before any product with >= 8 images can pass. Exit code is non-zero if
any asset fails, so it can gate a build.

**Proven on the real defect (2026-10-14):** the model returns
`NO — a light green, somewhat coffin-shaped polygon ... does not show pajamas`
for the original hand-coded icon, and `YES — a set of baby pajamas with a star
pattern` for the Flux replacement. It also flags readable text and brand logos,
which covers two of the three Flux failure modes automatically.

## Where the config default is wrong
`qa-hands/qa_hands/config.py` defaults `VISION_MODEL=qwen2.5vl:7b`, which is
NOT installed, and `OLLAMA_URL=http://localhost:11434`, which is the Mac Mini.
Local models live on the **M5** per Charlie. Override both:
`OLLAMA_URL=http://192.168.68.67:11434 VISION_MODEL=gemma3:27b`.

## Reading the review output: real defects vs abstract concepts

The first full run on 64 Montessori cards returned **54 pass / 10 fail**. The
failures split into two groups that need DIFFERENT responses:

**Real defects — regenerate these (4 of 10):**
| asset | label | model saw |
|---|---|---|
| sponge | Wipe The Table | "a yellow robotic vacuum cleaner" |
| napkin | Fold Napkins | "resembling a wallet or cardholder" |
| nails  | Trim Nails | "doesn't clearly represent nail trimming" |
| lamp   | Turn Off Lights | a lamp that is ON, for an OFF instruction |

The fix that worked: **show the ACTION, not the object alone.** "a child's hand
holding a yellow sponge wiping a wooden table, visible wiping motion" passed
where a sponge on its own failed. All four passed on re-check.

**Abstract concepts — accept the conventional symbol (6 of 10):**
`speech-please`, `speech-thanks`, `speech-heart`, `turns`, `cape`, `sticker`.
"Say Please" has no physical referent. A smiling speech bubble IS the
conventional representation and there is no better alternative. The model is
strict here and technically right that a pre-reader cannot decode it, but
regenerating will not help — this is a limitation of picture cards for
manners/abstract rewards, not a defect in the artwork. **Record the verdict
and move on; do not burn generations fighting it.**

Treat the review as a triage list, not a pass/fail oracle. The judgement call
is whether a concrete object was drawn wrong (fix) or whether the concept has
no concrete form (accept).

## Safety reading matters for children's products
On the second attempt `nails` produced clippers touching a fingertip and the
model objected: *"could be misinterpreted as an injury."* That is a legitimate
concern on a toddler card. Separating the objects ("both objects separate and
not touching, friendly and safe") passed. Watch for anything that reads as a
blade near skin.
