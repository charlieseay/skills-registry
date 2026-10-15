---
name: mcp-stem
description: Control Apple Music via the `stem` MCP server (search catalog, playback control, queue management, playlist operations). Use whenever a task needs to search for songs/albums/artists, control what's playing, check the queue, or manage playlists in Apple Music.
---

# Apple Music MCP (stem)

The `stem` MCP server (proxy name `stem`, binary at `/Users/charlieseay/Projects/stem/.build/release/Stem`) is a Swift-based wrapper around Apple's **native MusicKit framework**. Every tool uses MusicKit's official APIs — not scripting, not AppleScript, not a web scraper. This means tools require:

1. **Active Apple Music subscription** for playback (`play_pause`, `skip_next`, `play_song`, `set_queue`, media control). Catalog search works without a subscription.
2. **Music.app running** or at least not in a state that prevents playback. If playback fails, the error message will say so explicitly.
3. **Proper authorization** granted via `stem setup` run at least once (this prompts for MusicKit access via System Settings → Privacy & Security → Media & Apple Music).

**Auth note:** Authorization is stored locally via MusicKit's own credential cache. The `stem` binary reads it automatically; no agent action needed. The authorization grants the mac's logged-in user access only.

## The one critical gotcha: catalog vs. playback permissions are separate

**Search/catalog (always works if Music.app can run):**
- `search_catalog` — searches the Apple Music catalog
- `get_song_details`, `get_album_details` — fetch catalog metadata
- `get_recently_played` — reads your play history

**Playback (requires active subscription AND Music.app running):**
- `play_pause`, `skip_next`, `skip_previous`, `play_song`, `set_queue` — all require a subscription
- If called without a subscription, they return a hard error: `"Playback requires an active Apple Music subscription."` This is not a tool miscall — it's a real MusicKit limitation. Catalog search still works; playback is blocked.
- If Music.app hangs or is closed, playback calls may timeout or fail silently. Best practice: always check `get_now_playing` first to confirm the player is responsive.

## Tool catalog (15 tools, confirmed live 2026-10-01 against /Users/charlieseay/Projects/stem/Sources/Sound/main.swift:99-185)

**Catalog search (no subscription required):**
- `search_catalog(query, type="song", limit=10)` — search the Apple Music catalog
  - `type` enum: "song", "album", "artist" (defaults to "song")
  - `limit` clamped to 1-25 (default 10)
  - Returns formatted results with IDs: `[song_id] Title by Artist — Album` for songs
  - Returns empty result string if no matches found (not an error)

- `get_song_details(id)` — fetch full metadata for a catalog song by its Apple Music ID
  - Returns: title, artist, album, duration (min:sec), genre, release date, disc number, track number
  - Returns error if ID not found in catalog

- `get_album_details(id)` — fetch full album metadata including track listing
  - Returns: album title, artist, release date, genre, track count
  - Includes full track listing with IDs and durations for each track
  - Returns error if ID not found

- `get_recently_played(limit=10)` — fetch your recently played tracks
  - Requires subscription (reads from your play history)
  - `limit` clamped to 1-25 (default 10)
  - Returns: "1. Track by Artist — Album", "2. ...", etc.

**Playback control (subscription + Music.app required):**
- `play_pause()` — toggle play/pause
  - No args. Returns "Playing." or "Paused." on success
  - If nothing is queued, returns error: `"Nothing in the playback queue. Try playing a specific song first."`

- `skip_next()` — skip to next track
  - Calls `skipToNextEntry()` then returns the new now-playing via `get_now_playing()`
  - If queue is empty, returns error

- `skip_previous()` — go back to previous track
  - Calls `skipToPreviousEntry()` then returns the new now-playing
  - If at start of queue, behavior depends on MusicKit (typically restarts current track)

- `get_now_playing()` — query what's currently playing
  - No args. Returns "Playing: Title by Artist — Album" or "Paused: ..."
  - If nothing is queued: `"Nothing is currently playing."` (not an error)
  - Use this to check player state before attempting playback control

- `play_song(id)` — play a specific catalog song by ID
  - Sets queue to just this song and starts playback
  - Returns `"Now playing: Title by Artist"` on success
  - Requires subscription; returns error if none active

**Queue management (subscription required):**
- `get_queue()` — list current playback queue
  - No args. Returns queue as "▶ 1. Title by Artist", "  2. ...", etc.
  - "▶" marks currently playing track; spaces mark queued-up tracks
  - If queue empty: `"Queue is empty."`

- `set_queue(ids: [song_ids])` — replace queue with specific songs and start playing
  - `ids` is an array of Apple Music catalog song IDs
  - Fetches all songs by ID, builds a queue, and plays the first
  - Returns error if none of the IDs match real songs in catalog
  - Requires subscription

**Playlist operations (subscription required, uses REST API fallback for macOS CLI compatibility):**
- `get_library_playlists(limit=25)` — list your Apple Music library playlists
  - `limit` clamped to 1-100 (default 25)
  - Returns: `[playlist_id] Playlist Name` for each
  - Playlist IDs look like `p.XXXXXXXXX` (alphanumeric + dots)
  - Note: uses REST API fallback because MusicLibraryRequest returns empty on macOS CLI — this is a MusicKit quirk, not a tool bug

- `create_playlist(name, description=None)` — create a new playlist in your library
  - `name` required, `description` optional
  - Returns: `"Created playlist: Name [ID: p.XXXXXXXXX]"`
  - Also uses REST API (macOS CLI incompatibility with MusicLibraryRequest)

- `add_to_playlist(playlist_id, song_ids: [ids])` — add songs to an existing playlist
  - `playlist_id` from `get_library_playlists()`
  - `song_ids` is an array of catalog song IDs
  - Returns: `"Added N songs to playlist p.XXXXXXXXX."`
  - Playlist ID validation: must be alphanumeric + dots only (rejects other formats)
  - Note: also uses REST API directly instead of MusicLibraryRequest (same macOS CLI issue)

**Utility:**
- `ping()` — check if stem is running and Music.app authorization is granted
  - No args. Returns a text message confirming setup status
  - Use this to verify the MCP is alive before attempting real operations

## Known environment facts (confirmed 2026-10-01)

- Binary at `/Users/charlieseay/Projects/stem/.build/release/Stem` (rebuilt recently, working)
- Requires Music.app available (macOS only, not iOS)
- Uses Apple's official MusicKit framework, not a third-party API
- Playback is tied to the local machine's Music.app player — no remote/headless mode
- Playlist IDs from REST API look like `p.XXXXX` (alphanumeric with dots)
- Song/album/artist IDs are typically long alphanumeric strings (e.g., `123456789012345678`)

## Real error modes confirmed by reading source (2026-10-01)

**When subscription is missing** (from main.swift:617-619):
```swift
if message.contains("subscription") || message.contains("not subscribed") || message.contains("offer") {
    return "Playback requires an active Apple Music subscription. Catalog search and library access still work without one."
}
```
Return playback tools return this exact message, not a generic error.

**When queue is empty** (main.swift:621-623):
```swift
if message.contains("queue") || message.contains("empty") {
    return "Nothing in the playback queue. Try playing a specific song first."
}
```
This is returned by `play_pause()`, `skip_next()`, and similar when queue is empty.

**When searching returns no results** (main.swift:237-239):
Catalog search returns NOT an error, but a text result: `"No results found for 'query'"`
This is intentional (no-results is not an exceptional case), so don't treat it as a tool failure.

**When an ID doesn't exist in catalog** (main.swift:252-253, 287-288):
`get_song_details()` and `get_album_details()` return an error string: `"No song found with ID: xyz"` or `"No album found with ID: xyz"`

## Quick verification pattern for this skill

```bash
# Test that the binary is alive and responds to ping
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"ping","arguments":{}}}' | \
  timeout 5 /Users/charlieseay/Projects/stem/.build/release/Stem 2>/dev/null | \
  grep -q "Sound" && echo "PASS: stem responds" || echo "FAIL: stem not responding"

# Test that Music.app authorization is in place (requires setup to have run)
# This cannot be tested remotely; setup must have been run at least once on the Mac
```

If the binary has moved, been rebuilt, or Music.app access has been revoked, the verification will fail. When working with stem:
- Assume Music.app access is in place if setup has been run in this session or recently
- If a playback call fails with a cryptic error, always check Music.app is running and the user has an active subscription
- Catalog search is always safe even if playback is broken — it doesn't require a subscription or an active player
