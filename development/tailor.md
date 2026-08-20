Tailor a resume to match a specific job description using AI keyword optimization.

## Usage
- `/tailor` — prompts for the job description text
- `/tailor <job description text or URL>` — analyzes the provided JD directly

## How It Works

1. Read the master resume data from `~/Projects/[your-site]/src/data/resume.json`
2. Read the resume page template from `~/Projects/[your-site]/src/pages/resume.astro`
3. Analyze the job description to extract:
   - Required technical skills (exact phrases)
   - Preferred/nice-to-have skills
   - Key responsibilities and action verbs
   - Industry-specific terminology
4. Tailor the resume by:
   - Rewriting the professional summary for this specific role (2-3 sentences max)
   - Reordering experience bullets so the most relevant are first
   - Rephrasing bullets to mirror the JD's exact terminology (e.g., if JD says "CI/CD pipelines", match that phrasing)
   - Highlighting quantified achievements relevant to this role
   - Being strategically vague where it sells the idea without overcommitting
   - **Cutting** bullets that aren't relevant to this specific role — less is more
5. Apply brevity rules (see below)
6. Generate the tailored output

## Brevity Rules — Keep It Lean

The tailored resume must read like a **one-page document** when printed to PDF. Recruiters skim — every word must earn its place.

- **Bullets**: One line each, two at most. Lead with a strong verb + quantified result. Cut filler words.
  - BAD: "Led enterprise endpoint management modernization: architected and migrated Microsoft Intune deployment at healthcare scale across a 70,000+ user environment, building on prior platform experience with JAMF, MobileIron, and Workspace ONE"
  - GOOD: "Architected Microsoft Intune migration across 70,000+ endpoint environment at healthcare scale"
- **Don't repeat the sidebar**: If a skill (JAMF, MobileIron, etc.) is listed in the Skills section, don't also name-drop it in bullets unless it adds context a keyword alone can't convey
- **Summary**: 2-3 punchy sentences. No preamble, no "with over two decades" padding — let the dates speak for themselves
- **Max bullets per role**: 4 for current role, 3 for previous roles, 1-2 for older roles
- **Cut entire roles** if they add nothing for this JD (e.g., Early Career can be dropped entirely if irrelevant)
- **Skill groups**: Max 5 groups, max 6 items per group. Remove anything irrelevant to the JD.

## Critical Rules — NO LYING

- **NEVER fabricate** experience, companies, metrics, certifications, or skills that aren't in the master resume data
- **NEVER invent** job titles, dates, or project names
- You CAN rephrase, reorder, and emphasize existing content
- You CAN be strategically vague (e.g., "enterprise-scale infrastructure supporting 70,000+ users" without naming the company)
- You CAN mirror the JD's exact terminology IF the candidate genuinely has that skill
- You MUST flag any required skills the candidate genuinely lacks — list them at the end as "Gaps to address"
- The facts must be **truthful** — vague is OK, false is not

## Output

1. Save the tailored resume data as `~/Projects/[your-site]/src/data/resume-tailored.json`
2. Create a tailored resume page at `~/Projects/[your-site]/src/pages/resume-tailored.astro` using the same sidebar layout as `resume.astro` but importing from `resume-tailored.json`
3. Run `cd ~/Projects/[your-site] && npm run build`
4. Print the URL: `/resume-tailored`
5. Report:
   - **Match score**: rough percentage of JD requirements covered by existing experience
   - **Keywords added**: terms from the JD that were woven into the resume
   - **Gaps**: required skills or experience the candidate genuinely doesn't have
   - **Changes made**: summary of what was reordered, rephrased, or emphasized

## Notes
- The tailored page is temporary — it's not committed to git and can be overwritten on each run
- The master `resume.json` is NEVER modified — only the tailored copy changes
- The tailored page uses the same sidebar layout (Layout 2) as the main resume
- After reviewing, the user can print to PDF from the browser

ARGUMENTS: $ARGUMENTS

## Lessons

- **2026-06-16** — `voice-needs-fast-llm-not-nvidia-first`: Latency-sensitive callers (voice assistants) must route to a FAST provider (ask_llm groq/cerebras) and bound the call with a timeout, NOT the NVIDIA-first ask_helmsman chain which can take 20-30s when NVIDIA stalls. _(context: SoniqueBar handleConversation shelled to ask_helmsman -> 20s hang. Switched to ask_llm --lane fast + timeout 12 -> 0.5s.)_ [src: session/2026-06-16-sonique]
