# Seaynic Labs Skills Registry

**Shared infrastructure for all agents** — Claude Code, nvidia-agent, AIDER-GEM, Helmsman, autonomous loops.

## Directory Structure

| Category | Count | Purpose |
|----------|-------|---------|
| `creative/` | 10 | Logo generation, color palettes, icon sets, illustrations, frontend design |
| `development/` | 13 | Code review, debugging, deployment, testing, diagramming |
| `research/` | 3 | Research, brainstorming, UI/UX design |
| `operations/` | 12 | Audits, runbooks, decision records, meeting notes, quarterly reviews |
| `writing/` | 5 | Changelogs, documentation, coaching notes, PDF export |

**Total:** 43 skills

## Access Patterns

### Claude Code
Skills auto-loaded from symlink at `~/.claude/commands-shared/`:
```bash
ln -s /Volumes/data/skills ~/.claude/commands-shared
```

### Python Agents (nvidia-agent, scripts)
```python
from pathlib import Path
import glob

SKILLS_PATH = "/Volumes/data/skills"

# Find skill by name
skill_files = glob.glob(f"{SKILLS_PATH}/**/{skill_name}.md", recursive=True)
content = Path(skill_files[0]).read_text()
```

### Node.js Agents (Helmsman, Bosun, B3CK)
```javascript
const fs = require('fs');
const glob = require('glob');

const SKILLS_PATH = '/Volumes/data/skills';

// Find skill by name
const matches = glob.sync(`${SKILLS_PATH}/**/${skillName}.md`);
const content = fs.readFileSync(matches[0], 'utf-8');
```

### REST API (helmsman-db)
```bash
# Get skill content
curl -s "http://localhost:5682/skills/logo-gen/content"

# List all skills
curl -s "http://localhost:5682/skills/list"

# Register new skill
curl -X POST "http://localhost:5682/skills/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "skill-name", "file_path": "/Volumes/data/skills/...", ...}'
```

### Remote Access (Talos on Hetzner)
```bash
# Git sync (cron hourly)
git clone https://github.com/charlieseay/skills-registry.git /opt/skills
0 * * * * cd /opt/skills && git pull origin main
```

## Skill Frontmatter Standard

Every skill file MUST include YAML frontmatter for auto-discovery:

```yaml
---
name: skill-name
category: creative|development|research|operations|writing
description: "One-sentence what it does"
tags: [relevant, keywords]
triggers:
  patterns:
    - "user phrase that triggers this skill"
    - "another trigger phrase"
  contexts:
    - "domain area"
    - "project phase"
  anti_patterns:
    - "phrase that looks similar but WRONG skill"
success_indicators:
  - "Output artifact created"
  - "Validation passed"
when_to_use: "Detailed guidance on when to invoke"
when_NOT_to_use: "Anti-cases to prevent misuse"
avg_completion_time_mins: 5
agents_supported: ["claude-code", "nvidia-agent", "helmsman"]
---

# Skill Title

[skill instructions here]
```

## Syncing to helmsman.db

Skills must be registered in `helmsman.db` for auto-discovery:

```bash
# Auto-sync all skills
python3 /path/to/sync_skills_to_helmsman.py

# This runs automatically:
# - Daily at 3:00 AM (cron)
# - After git push (post-commit hook)
# - On demand when adding new skills
```

## Adding a New Skill

1. **Create skill file:**
   ```bash
   cat > /Volumes/data/skills/development/my-skill.md << 'EOF'
   ---
   name: my-skill
   description: "What this skill does"
   triggers:
     patterns: ["trigger phrase"]
   ---
   
   # My Skill
   [instructions]
   EOF
   ```

2. **Register in helmsman.db:**
   ```bash
   python3 /path/to/sync_skills_to_helmsman.py
   ```

3. **Verify:**
   ```bash
   curl -s "http://localhost:5682/skills/my-skill"
   ```

4. **Commit:**
   ```bash
   cd /Volumes/data/skills
   git add .
   git commit -m "Add my-skill"
   git push
   ```

## Skill Discovery Flow

```
Agent receives task
  ↓
1. Query helmsman.db: "What skills match this task?"
   └─> Semantic search via open-notebook
   └─> Metadata from helmsman.db
  ↓
2. Filter by confidence threshold (>= 0.7)
  ↓
3. Load skill content from /Volumes/data/skills/
  ↓
4. Execute skill instructions
  ↓
5. Log outcome to helmsman.db
   └─> Learning layer improves future discovery
```

## Analytics

**Most-used skills:**
```sql
SELECT * FROM skill_usage_leaderboard LIMIT 10;
```

**Success rate by skill:**
```sql
SELECT * FROM skill_success_rate ORDER BY success_rate_pct DESC;
```

**Stale skills (never used or 30+ days):**
```sql
SELECT * FROM stale_skills;
```

## Backup & Versioning

- **Git:** Versioned at `https://github.com/charlieseay/skills-registry`
- **Backup:** Daily Restic snapshots (included in `/Volumes/data/` backup)
- **Rollback:** `git checkout <commit-hash>` to restore previous version

## References

- `Standards/Skill Auto-Discovery Protocol.md` — Full specification
- `Standards/Agent Execution Protocol.md` — Pre-flight skill discovery
- `memory/reference_open_notebook_kb.md` — Semantic search architecture

---

**Last Updated:** 2026-08-19  
**Maintainer:** charlie@seayniclabs.com
