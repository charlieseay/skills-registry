---
name: mcp-home-assistant
description: Control and query Charlie's Home Assistant smart home via the `ha` MCP server (natural-language entity targeting, media playback, lights, todo lists, live state). Use this whenever a task needs to turn devices on/off, check what's currently happening in the house, control media players, manage a to-do list in HA, or needs real entity/area/floor names before calling an action tool. Also use when debugging a "device not found" or MatchFailedError from an HA action call.
---

# Home Assistant MCP

The `ha` MCP server (proxy name `ha`, bridged via
`/Volumes/data/containers/n8n-control/state/helmsman-state/ha_mcp_bridge.py`)
is a thin stdio-to-HTTP forwarder straight into Home Assistant's own **native**
MCP integration at `http://192.168.68.90:8123/api/mcp`. The bridge does
nothing but add the bearer token and forward JSON-RPC — every real behavior,
tool, and quirk documented here comes from HA itself, not the bridge. If HA's
MCP integration changes, this skill goes stale; re-run the discovery call
below to check.

**Auth note:** the token lives at
`/Volumes/data/containers/n8n-control/state/helmsman-state/ha_token` (183
bytes, a long-lived access token) — never print it, never put it in a
brief/task text. The bridge reads it itself; agents never need to see it.

## The one thing to internalize before calling any action tool

**Every targeting parameter (`name`, `area`, `floor`, `domain`,
`device_class`) is fuzzy natural-language matching against HA's entity
registry, not an entity_id.** `HassTurnOn({"name": "Carter's Echo"})` matches
by display name and resolves internally to `media_player.carter_s_echo` — you
never pass the entity_id directly. This is friendly but means a near-miss
spelling or a renamed device returns a hard, explicit failure rather than a
silent no-op. Confirmed live (2026-10-01):

```json
// HassTurnOn({"name": "Nonexistent Device XYZ123"})
{"isError": true, "content": [{"text": "Error calling tool: <MatchFailedError
  result=MatchTargetsResult(is_match=False,
  no_match_reason=<MatchFailedReason.NAME: 1>, ...)>"}]}
```

**Fix when you hit this**: call `GetLiveContext` first (see below) to get the
exact `names:` string HA actually has registered, then retry with that exact
string. Don't guess at a device name from memory or from a vault note — HA's
own registry is the only ground truth, and names drift (devices get renamed,
added, removed) independent of any note documenting them.

## Discovery first, action second

**Always call `GetLiveContext` (no arguments) before any targeted action** if
you don't already know the exact registered name from a call earlier in the
same task. It returns a flat list of every entity: `names`, `domain`, `state`,
and (when set) `areas`. This is the fastest way to find the real name, confirm
an entity exists, or check current state before deciding to flip it.

```json
{"name": "GetLiveContext", "arguments": {}}
```

Returns text like:
```
- names: Carter's Echo
  domain: media_player
  state: paused
  attributes:
    volume_level: 1.0
    media_title: Body [Explicit]
```

Use `GetDateTime` the same way for the current date/time — don't assume the
agent's own clock matches the house's timezone/DST state.

## Tool catalog (20 tools, confirmed live 2026-10-01)

Query `tools/list` yourself if this skill feels stale — HA's MCP integration
can gain/lose tools on a Home Assistant version bump, and this list is a
snapshot, not a contract.

**Power/state:**
- `HassTurnOn` — turns on/opens/presses/**locks**. The description itself
  says locks resolve to a "lock" action under this verb, which reads
  backwards in English — remember "on" = locked for a lock entity.
- `HassTurnOff` — turns off/closes/**unlocks**. Same inversion for locks.

**Media (all take `name`/`area`/`floor`/`domain`, domain enum is
`media_player`):**
- `HassMediaUnpause`, `HassMediaPause`, `HassMediaNext`, `HassMediaPrevious`
- `HassSetVolume` (absolute percentage), `HassSetVolumeRelative` (nudge
  up/down — use this for "turn it up a bit" phrasing, HassSetVolume for "set
  it to 40%")
- `HassMediaPlayerMute` / `HassMediaPlayerUnmute`
- `HassMediaSearchAndPlay` — searches and plays the FIRST result; if the
  house has ambiguous media libraries across players, confirm the target
  player with `name`/`area` rather than relying on this to guess right.

**Lights:**
- `HassLightSet` — brightness percentage and/or color in one call. Prefer
  this over separate on/off + brightness calls when both are needed.

**Lists (HA's own `todo` entities — "Chores" is a real one, confirmed live,
currently showing `state: '0'` meaning 0 open items):**
- `HassListAddItem`, `HassListCompleteItem`, `HassListRemoveItem`
- `todo_get_items` — query what's actually on a list before adding, to avoid
  creating a duplicate entry with slightly different wording.

**Misc:**
- `HassCancelAllTimers` (optionally scoped to an `area`)
- `HassBroadcast` — plays a TTS message through the house's speakers.
- `GetDateTime`, `GetLiveContext` — read-only, see above.

**Notably absent** (as of the 2026-10-01 snapshot — don't assume these exist
without re-checking `tools/list`): no climate/thermostat tool, no
scene-activation tool, no direct automation-trigger tool, no camera-snapshot
tool. If a task needs one of these, it is NOT currently exposed through this
MCP — check `tools/list` live before telling Charlie it's impossible, in case
HA's integration has added it since this was written.

## Known environment facts (from MEMORY.md, cross-check before relying on these)

- HA runs at `homeassistant.local:8123` (internally `192.168.68.90:8123` per
  the bridge's hardcoded URL — these should be the same box; if DNS and IP
  disagree, trust the IP, since that's what the MCP bridge actually dials).
- Aqara devices are on Matter; Sengled bulbs are NOT integrated as of the last
  MEMORY.md update — don't assume a Sengled bulb will resolve via
  `GetLiveContext`.

## Quick verification pattern for this skill itself

```bash
TOKEN=$(cat /Volumes/data/containers/n8n-control/state/helmsman-state/ha_token)
curl -s -m 10 -X POST -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  http://192.168.68.90:8123/api/mcp
```
If this returns fewer/more/different tools than the 20 listed above, HA's
integration has changed — update this file before trusting the tool
descriptions above for anything novel.
