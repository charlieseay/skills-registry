---
name: mcp-ollama
description: Manage and query Ollama local LLMs via the `ollama` MCP server (list/pull/run models, chat completions, model info). Use when you need to check what models are available locally, run inference on local models for testing, manage model lifecycle (pull/delete/copy), or verify Ollama is running and responding.
---

# Ollama MCP Server

The `ollama` MCP server (proxy name `ollama`, Node.js wrapper at `/Users/charlieseay/Projects/ollama-mcp-server/build/index.js`) is a **thin stdio-to-HTTP forwarder** into Ollama's native REST API at `http://localhost:11434` (configurable via `OLLAMA_HOST` env var; MCP config sets `http://localhost:11434`). Every tool maps directly to Ollama's `/api/` endpoints — the MCP adds only error formatting and zod schema validation.

**Auth note:** No auth required — Ollama's default config has no auth. The MCP assumes `OLLAMA_HOST=http://localhost:11434` which is the Ollama default. If Ollama isn't running, all tool calls return `Error: connect ECONNREFUSED 127.0.0.1:11434` or similar.

**Relationship to Claude/inference routing:**
- This MCP is for **managing and testing** Ollama models directly
- **Actual inference** through Ollama (e.g., in n8n workflows or agent_routing.py) uses the REST API directly, not this MCP
- Use this MCP to verify a model is available before asking an agent to use it, to pull new models, or to debug why a model isn't running

## The one critical gotcha: tools return raw JSON, not plain text

Unlike most MCPs (ha, vault) that return human-readable text, **ollama MCP tools return raw JSON** from the Ollama API:

- `list` returns full model metadata (name, size, model hash, modified time, etc.) — not a simple list
- `show` returns full model config (parameters, template, license, etc.)
- `chat_completion` returns OpenAI-compatible JSON (id, object, created, choices[], finish_reason)
- `run` returns the response text, but wrapped in JSON

**Practical implication:** When you call an ollama tool, parse the JSON response yourself. The text content of the MCP result will be a JSON dump, not formatted prose. This is correct behavior — Ollama's API speaks JSON natively.

## Tool catalog (10 tools, confirmed live 2026-10-01 against /Users/charlieseay/Projects/ollama-mcp-server/src/index.ts:21-195)

**Model lifecycle:**
- `list()` — list all models available locally
  - No args
  - Returns full Ollama response: `{"models": [{name, model, ..., size, digest, ...}]}`
  - Each model object includes: name, model (same as name), size in bytes, digest, modified_at, quant_level
  - If no models: `{"models": []}` (empty, not an error)
  - Use this to check what's available before calling `run` or `chat_completion`

- `pull(name)` — download a model from a registry (typically Ollama.ai)
  - `name` is the model identifier, e.g., "llama2", "neural-chat:latest", "mistral"
  - Returns streaming response: `{"status": "pulling manifest", "digest": "...", "total": ..., "completed": ...}` (multiple JSON objects, one per progress update)
  - This is a **long-running operation** — timeout should be generous (minutes for large models)
  - If model already exists locally, pull updates it if a newer version exists on the registry
  - Returns error if registry is unreachable or model name doesn't exist

- `push(name)` — push a model to a registry (requires Ollama.ai account and explicit push setup)
  - `name` is the model identifier to push
  - Rarely used; included for completeness
  - Returns status/progress JSON like pull

- `cp(source, destination)` — copy a local model to a new name
  - `source` and `destination` are model names, e.g., cp(source="llama2", destination="llama2-custom")
  - Useful for creating variants without re-downloading
  - Returns error if source doesn't exist

- `rm(name)` — delete a model from local storage
  - `name` is the model identifier to delete
  - Frees disk space (models can be several GB each)
  - Returns error if model doesn't exist

**Model inspection:**
- `show(name)` — get full metadata/config for a model
  - `name` is the model identifier
  - Returns full Ollama response: `{"modelfile": "FROM ...", "parameters": "...", "template": "...", "details": {...}, "license": "..."}`
  - Includes the original Modelfile (if known), quantization level, families, parameter count, etc.
  - Returns error if model doesn't exist locally

- `create(name, from)` — create a model from a base model via "remote only" method
  - `name` is new model name, `from` is base model to build from
  - **Important:** "remote only supports 'from'" means no Modelfile support via MCP
  - Useful for quick derivations without downloading from registry
  - Returns error if base model doesn't exist

**Inference:**
- `run(name, prompt, images=[], temperature=0.7, think=false)` — run a model on a prompt (non-streaming)
  - `name` is the model identifier, e.g., "llama2", "neural-chat"
  - `prompt` is the user input text
  - `images` optional array of local file paths (for vision/multimodal models like llava)
  - `temperature` optional 0-2 (lower = more deterministic, default per model)
  - `think` optional boolean (enables extended thinking on models that support it)
  - Returns the full response text in one JSON object: `{"content": [{"type": "text", "text": "response..."}]}`
  - **Long-running:** models can take seconds to minutes; no timeout is set, so be patient
  - If model not found: returns error immediately
  - If model is not running, Ollama starts it automatically (cold start)

- `chat_completion(model, messages, temperature=0.7, think=false)` — OpenAI-compatible chat API
  - `model` is model identifier
  - `messages` is array of `{role, content, images?}` where role is "system", "user", or "assistant"
  - `temperature` and `think` same as `run`
  - Each message can optionally include `images` array for vision models
  - Returns OpenAI-compatible response: `{"id": "chatcmpl-...", "object": "chat.completion", "created": timestamp, "model": name, "choices": [{message: {...}, finish_reason: "stop"}]}`
  - Identical to `run` but structured for multi-turn conversation; prefer this for chat workflows

## Known Ollama environment facts (confirmed 2026-10-01)

- Ollama API endpoint: `http://localhost:11434` (set in MCP config env var)
- No authentication required (Ollama default)
- Models stored locally at `~/.ollama/models/` (or wherever `OLLAMA_MODELS` env var points)
- Ollama daemon must be running for any MCP call to work (`ollama serve` or system service)
- Common models available on Ollama.ai registry: llama2, mistral, neural-chat, codellama, orca, etc.

## Real error modes confirmed by reading source (2026-10-01)

**No model name provided** (index.ts doesn't validate, Ollama API rejects):
```
Error: {"status":400,"message":"model required"}
```

**Model doesn't exist** (index.ts:45):
When calling `show(name)` with non-existent model, Ollama returns 404:
```
Error: response status is 404
```

**Connection refused** (index.ts:14):
If Ollama isn't running at the configured OLLAMA_HOST:
```
Error: connect ECONNREFUSED 127.0.0.1:11434
```
This is **not** a tool miscall — Ollama simply isn't reachable. Start the Ollama daemon and retry.

**Image path not found** (for run/chat_completion with images):
Ollama silently ignores missing image files (doesn't error). The model is run, but the image isn't passed. If you reference an image and it's not found, the model won't see it — this is silent, not an error.

**Model is downloading/not ready** (from pull/create):
If you call `run` while the model is still being pulled, Ollama queues the run and starts it once available. This can make the call appear to hang (model is auto-starting). No explicit error is returned — the tool just takes longer.

## Gotchas and design tradeoffs

**Streaming responses are buffered** — Ollama's `pull` and `push` endpoints stream progress, but the MCP buffers the entire response before returning. This means large model downloads appear to hang until complete, then return all progress at once. No way to stream progress in real-time via this MCP.

**Images are file paths, not embedded** — for vision models, you must pass local file paths, not base64/URLs. If an image is on a remote server, you must download it first.

**No explicit model lifecycle hooks** — there's no "unload model" or "pause model" tool. Models stay in VRAM until you restart Ollama or manually send an `DELETE /api/generate` request to Ollama's API directly.

**temperature and think are optional** — if not provided, Ollama uses its default (typically 0.7 for temperature, false for think). Not all models support extended thinking (`think` parameter); models that don't support it silently ignore it.

**Response format is always JSON** — no plain-text mode. Even `run()` which returns a simple response wraps it in MCP content format, which the proxy then wraps in more JSON. Be ready to parse.

## Quick verification pattern for this skill

```bash
# Test that Ollama is reachable
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list","arguments":{}}}' | \
  timeout 5 /opt/homebrew/bin/node /Users/charlieseay/Projects/ollama-mcp-server/build/index.js 2>/dev/null | \
  grep -q '"models"' && echo "PASS: Ollama reachable" || echo "FAIL: Ollama not responding"

# Test that a model is available (e.g. llama2)
# This requires that at least one model has been pulled previously
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list","arguments":{}}}' | \
  timeout 5 /opt/homebrew/bin/node /Users/charlieseay/Projects/ollama-mcp-server/build/index.js 2>/dev/null | \
  grep -q '"name"' && echo "PASS: Models exist locally" || echo "FAIL: No models found"
```

If these fail:
- Check that Ollama daemon is running: `curl -s http://localhost:11434/api/tags` should respond with `{"models":[...]}`
- Check that the Node.js wrapper exists at `/Users/charlieseay/Projects/ollama-mcp-server/build/index.js`
- Check that OLLAMA_HOST env var is set correctly (should be `http://localhost:11434` by default)
