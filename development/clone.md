Clone a GitHub repository into ~/Projects/ using the gh CLI.

## Usage
- `/clone owner/repo` — clones the repo into ~/Projects/repo
- `/clone owner/repo my-name` — clones into ~/Projects/my-name

## Steps

1. Parse the arguments: the first argument is the `owner/repo` (required), the second is an optional local directory name
2. Ensure `~/Projects/` exists: `mkdir -p ~/Projects`
3. Clone using gh: `gh repo clone <owner/repo> ~/Projects/<local-name>`
4. Report the clone location and the repo URL
5. If there is a README, read the first 30 lines and summarize what the project is

## Notes
- Default clone location is `~/Projects/` — always use this unless the user specifies otherwise
- Use `gh repo clone` (not `git clone`) so authentication is handled automatically
- If the clone fails because the directory already exists, tell the user and stop

## Lessons

- **2026-06-15** — `tts_streaming_failures_must_be_caught_at`: TTS streaming failures must be caught at arrayBuffer() to prevent service crashes. When upstream TTS providers (ElevenLabs, Kokoro) send incomplete responses with mismatched Content-Length, Node's undici throws ResponseContentLengthMismatchError inside await res.arrayBuffer(). Wrap all arrayBuffer() calls in try/catch, log with full context, capture to error tracking, return null to let caller retry. Never let streaming errors propagate uncaught. _(context: 2026-06-05 incident: Both Fly.io production and Mac Mini local enchapter-api crashed simultaneously at 3:05 AM when ElevenLabs sent incomplete audio responses. Both services remained down for 4 hours until manual restart.)_ [src: task-unknown]
- **2026-06-15** — `when_fighting_a_platform_sdk_api_repeate`: When fighting a platform/SDK API repeatedly (errors, hangs, weird behavior), STOP and fetch the official vendor docs (WebFetch on developer.apple.com etc.). Sonique 2026-06-11: echo + OSStatus-50 + 40s-delay + restart-storm all collapsed to one root cause once Apple audio docs were read (ONE shared AVAudioEngine for mic+speaker; persistent .playAndRecord/.voiceChat; voice processing for AEC/AGC). Reinventing VAD/gain/PCM that Apple ships wasted iterations. Same win repeated for iCloud (off-main container resolve, startDownloadingUbiquitousItem, NSFileCoordinator) and HIG (44pt targets, VoiceOver, Dynamic Type). [src: task-unknown]
