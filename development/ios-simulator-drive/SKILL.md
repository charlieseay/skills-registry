---
name: ios-simulator-drive
description: "Launch and drive a native iOS/iPadOS app in the Simulator for real, interactive verification — boot, install, launch, screenshot, and reliable tap/type input. Use whenever you need to prove a SwiftUI/UIKit change actually works on-device rather than just compiling and passing unit tests: reading source and passing `xcodebuild test` does not catch first-launch black screens, blocked onboarding gates, missing progression, or any other interaction-shaped bug. Triggers on: run the iOS app, test in the simulator, drive the app, verify on-device, screenshot the app, click through the app, tap through onboarding, walk through the flow."
metadata:
  version: "1.0.0"
  non-tool-specific: true
---

# Driving a native iOS app in the Simulator

Any agent — Claude, Gemini, aider, a human — hits the same wall here: `xcrun
simctl` can boot, install, launch, and screenshot an app, but it has **no
native tap or type primitive**. Reaching for `osascript`/`System Events`
clicks or a coordinate-tapping tool (`cliclick`) feels obvious and **does not
reliably work** — System Events `click at` requires accessibility grants that
are not given by default, and even when granted, text fields frequently do
not receive focus from a synthetic click. This was tried and re-tried across
multiple approaches in a real session (2026-09-22, Enchapter/StoryChat) and
never got text into a UITextField. Do not repeat that loop — use one of the
two reliable paths below.

## Step 0 — boot, install, launch, screenshot (always works, no input yet)

```bash
# Find a simulator (any recent iPhone)
xcrun simctl list devices | grep -i "iPhone" | grep -v unavailable

# Boot it (idempotent — errors if already booted, that's fine)
xcrun simctl boot <DEVICE_UDID>
open -a Simulator   # brings the window up

# Build for simulator (adjust scheme/project)
xcodebuild -scheme <SCHEME> -project <PROJECT>.xcodeproj \
  -destination 'generic/platform=iOS Simulator' -configuration Debug build

# Find the .app bundle xcodebuild just produced
APP_PATH=$(find ~/Library/Developer/Xcode/DerivedData -maxdepth 1 -iname "<SCHEME>-*" | head -1)/Build/Products/Debug-iphonesimulator/<SCHEME>.app

# Install + launch
xcrun simctl install <DEVICE_UDID> "$APP_PATH"
BUNDLE_ID=$(/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "$APP_PATH/Info.plist")
xcrun simctl launch <DEVICE_UDID> "$BUNDLE_ID"

# Screenshot at any point
xcrun simctl io <DEVICE_UDID> screenshot /tmp/screenshot.png
```

This much is solid and needs no third-party tooling. If the flow you're
verifying needs zero user input (e.g. does the app crash on launch, does a
background task complete, does a specific screen render at all), stop here —
you're done.

## Step 1 — you need to tap or type: pick ONE reliable path

**Do not fall back to `osascript`/`cliclick` coordinate-tapping.** It is not
reliable input and wastes time discovering that. Pick one of these instead,
in order of preference:

### Path A — idb (Facebook's simulator automation CLI) — fastest, if available

```bash
brew tap facebook/fb   # third-party tap — ask the user before trusting it
                        # if this is the first time on this machine
brew install facebook/fb/idb-companion
pip3 install fb-idb

idb_companion --udid <DEVICE_UDID> &
idb tap <X> <Y>                      # coordinates in POINTS, not pixels —
                                       # screenshot is in pixels at @2x/@3x,
                                       # divide by the scale factor first
idb text "hello world"                # types into whatever has focus
idb key-sequence RETURN
```

`idb` reliably focuses text fields and types into them — this is the gap
`osascript` cannot cross. The `brew tap facebook/fb` step adds an untrusted
third-party formula; flag this to the user before running it rather than
tapping silently, per normal supply-chain caution.

### Path B — XCUITest (Apple's own automation, no third-party trust needed)

When `idb` isn't available or the user doesn't want a third-party tap
trusted, write a throwaway XCUITest instead — this is the actually-supported
Apple mechanism for driving simulator UI, and every iOS project already has
the toolchain for it.

```swift
// Add to <Target>UITests/ (or a scratch test file), run once, then delete
import XCTest

final class DriveOnceUITests: XCTestCase {
    func testDriveApp() throws {
        let app = XCUIApplication()
        app.launch()

        // Answer a math-gate style field
        app.textFields["Answer"].tap()
        app.textFields["Answer"].typeText("35")
        app.buttons["Continue"].tap()

        // Navigate tabs, take a screenshot at any point
        app.tabBars.buttons["Toybox"].tap()
        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
```

```bash
xcodebuild test -scheme <SCHEME> -project <PROJECT>.xcodeproj \
  -destination 'platform=iOS Simulator,name=<DEVICE_NAME>' \
  -only-testing:<Target>UITests/DriveOnceUITests
```

Screenshots attached via `XCTAttachment` land in the test result bundle
(`.xcresult`) — extract with:

```bash
xcrun xcresulttool get --path <result>.xcresult --format json | \
  jq -r '.. | objects | select(.type?.name == "ActionTestAttachment") | .filename._value' 
```

This is slower to set up per-session than `idb`, but requires nothing beyond
Xcode, uses element identifiers (`accessibilityIdentifier`) instead of raw
coordinates so it survives layout changes, and matches how the app's own
`<Target>UITests` target (if one exists) already tests interaction.

## What this replaces

The failed approach from the 2026-09-22 session, for reference — do not
repeat it:

```bash
# DOES NOT RELIABLY WORK — text fields do not receive focus from this
osascript -e "tell application \"System Events\" to click at {$X, $Y}"
cliclick c:$X,$Y
cliclick t:"some text"
```

If you find yourself computing screen-coordinate-from-screenshot-pixel scale
factors by hand and it still isn't typing into a field, stop — you're in the
dead end this skill exists to route around. Switch to Path A or B above.

## When code-level verification is enough instead

Not every change needs simulator driving. If the change is provably correct
from source + a passing build + passing unit tests (e.g. a pure color/value
change, a background-thread refactor with no new control flow), say so
explicitly and skip this skill — driving the simulator is for changes whose
correctness genuinely depends on interaction or timing that tests can't see
(first-launch behavior, navigation flows, gated onboarding, anything a human
tester would need to tap through to judge).
