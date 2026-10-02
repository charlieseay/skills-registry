# Writing Rules - Quick Reference

**USE THIS BEFORE WRITING ANY PUBLIC-FACING DOCUMENT**

## The 10 Rules

| Rule | Bad | Good |
|------|-----|------|
| **1. Concrete** | "Helps you work efficiently" | "Converts 500-line configs into 12-line YAML" |
| **2. Specific** | "Easy to use" | "Run `pytest` - no config needed" |
| **3. Active Voice** | "This is designed to cover..." | "This covers..." |
| **4. No Questions** | "Want to test faster?" | "Five patterns that cut test runtime in half" |
| **5. No Vague Quantifiers** | "Most developers" | "47% of pytest users" OR "All fixtures" |
| **6. First Sentence Concrete** | "Testing is important" | "Run `pytest tests/` to execute all tests" |
| **7. No Marketing Fluff** | "Revolutionary approach" | "Fixtures reduce setup from 8 lines to 2" |
| **8. No Hedging** | "This might help..." | "This reduces memory usage by 40%" |
| **9. Assume Competence** | "Don't worry, it's easy" | "Create a fixture with `@pytest.fixture`" |
| **10. Short Paragraphs** | 8-line paragraph | 2-3 line paragraphs |

## Auto-Checker

```bash
# Check any file
/writing-rules path/to/file.md

# Or run directly
python3 ~/.claude/skills/writing-rules/check.py path/to/file.md
```

**Exit codes:**
- `0` = Passed (publish allowed)
- `1` = Violations found (publishing blocked)

## Tone

**Write like:** A confident operator sharing the map  
**Don't write like:** A teacher, evangelist, or salesperson

## When It Runs

**Automatically on:**
- README files
- docs/ directories
- guides/ directories
- public/ directories
- products/ directories
- Gumroad listings

**Blocked if violations found** - no exceptions.
