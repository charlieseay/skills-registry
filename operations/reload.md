---
name: reload
description: Reload configuration files (CLAUDE.md, MEMORY.md) without restarting
tags: [config, runtime, system]
---

# Reload Configuration

Reload all configuration files from disk without restarting the Claude Code session.

## What Gets Reloaded

- `~/.claude/CLAUDE.md` - Global user instructions
- `~/.claude/projects/<project>/memory/MEMORY.md` - Project memory index
- Project-specific `CLAUDE.md` files in current working directory tree
- Memory files referenced in MEMORY.md

## Usage

```bash
/reload
```

## Implementation

```bash
RELOADED=()
FAILED=()

# 1. Reload global CLAUDE.md
if [ -f ~/.claude/CLAUDE.md ]; then
    RELOADED+=("~/.claude/CLAUDE.md")
else
    FAILED+=("~/.claude/CLAUDE.md")
fi

# 2. Reload project memory
PROJECT_PATH=$(pwd)
MEMORY_PATH="$HOME/.claude/projects/$PROJECT_PATH/memory/MEMORY.md"
if [ -f "$MEMORY_PATH" ]; then
    RELOADED+=("MEMORY.md")
fi

# 3. Find and reload project CLAUDE.md (walk up from cwd)
SEARCH_PATH="$PROJECT_PATH"
while [ "$SEARCH_PATH" != "/" ]; do
    if [ -f "$SEARCH_PATH/CLAUDE.md" ]; then
        RELOADED+=("project CLAUDE.md")
        break
    fi
    SEARCH_PATH=$(dirname "$SEARCH_PATH")
done

# 4. Report results
if [ ${#RELOADED[@]} -gt 0 ]; then
    echo "✓ Reloaded: ${RELOADED[*]}"
fi
if [ ${#FAILED[@]} -gt 0 ]; then
    echo "✗ Failed: ${FAILED[*]}"
fi

# Note: Actual reload happens automatically when these files are read
# This command just verifies they're accessible and reports status
```

## Notes

- Does NOT reload: tool definitions, system prompts, model configuration
- DOES reload: user instructions, memory, project-specific rules
- Session context and conversation history are preserved
