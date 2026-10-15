---
name: mcp-bench
description: USB hardware discovery for AI tools via the `bench` MCP server (22 tools). Identifies connected USB devices, finds serial ports, recognizes maker boards (Arduino, ESP32, Raspberry Pi Pico), monitors hub topology, manages device tags, performs firmware flashing, and provides HID/serial communication. Use whenever a task needs to discover hardware, check USB device status, control maker boards, or debug connectivity issues.
---

# Bench USB Hardware MCP

The `bench` MCP server (proxy name `bench`, Swift binary at `/Users/charlieseay/Projects/bench/.build/release/Bench`) provides comprehensive USB device discovery, control, and communication. The binary is a native macOS app using IOKit for hardware introspection. All tools are confirmed live against source at `/Users/charlieseay/Projects/bench/Sources/BenchCore/USBExplorerCore.swift:3-425` (tool definitions, 22 tools total).

**No auth required** — this is local system hardware access via IOKit, no network or credentials needed.

## Quick patterns before calling any tool

**Device identification**: Most tools accept an `identifier` parameter that can be:
- Device **serial number** (if present)
- **Location ID** (format: `0x02100000`)
- **Device name** (as shown in `list_usb_devices`)

The tool will try all three; it's most reliable to first call `list_usb_devices` to get the exact name/serial, then use that.

**Defaults and validation**:
- Serial communication defaults to **115200 baud, 8 data bits, 1 stop bit, no parity** if not specified
- Firmware flashing **requires `confirm=true`** to prevent accidental destruction
- HID send operations **require `confirm=true`** for the same reason
- Port reset **requires `confirm=true`** (interrupts active transfers)

**When no USB devices are present**: Tools return "No USB devices found" or "No devices of type X found" — this is expected and not an error. Tools gracefully handle empty device lists.

## Tool catalog (22 tools, verified live 2026-10-01 against source)

### Discovery & Enumeration

**`ping`** — Check if Bench is running and IOKit is available. Returns status, version, macOS version, and IOKit availability (always call first to verify server health).
- No parameters
- Returns JSON: `{"status":"ok", "server":"Bench", "version":"0.2.0", "macos_version":"...", "iokit_available":true/false}`

**`list_usb_devices`** — List all connected USB devices with full details.
- `device_type` (string, optional): Filter by type. Valid: `storage`, `audio`, `hub`, `input`, `video`, `serial`, `microcontroller`, or `all` (default)
- `include_internal` (boolean, optional): Include Apple internal devices like Bluetooth controller, camera (default: false)
- Returns formatted text with vendor, type, speed, location, serial, mount point, capacity (if storage), and known-device identification

**`get_device_info`** — Get detailed information about a specific USB device.
- `identifier` (string, required): Serial number, location ID, or device name
- Returns: Full device details including USB class codes, protocol, bus power, removable status, filesystem type, BSD name
- Errors if device not found

**`identify_device`** — Identify a connected USB device and provide context.
- `identifier` (string, required): Serial number, location ID, or device name
- If in known database (Arduino, Raspberry Pi, ESP32, etc.), returns: vendor, category, human-readable name, and notes
- If not known, returns: vendor ID, product ID, USB class/subclass/protocol for reference
- Useful for disambiguating microcontroller variants

### Navigation & Status

**`list_serial_ports`** — Enumerate all serial ports on the system with matched USB device info.
- `device_type` (string, optional): Filter by `usb`, `bluetooth`, `built_in`, or `all` (default)
- Returns: Port path (e.g., `/dev/cu.usbserial-2120`), device category, and associated USB device name if matched
- Essential before calling `serial_open` to find the right port path

**`hub_topology`** — Display the USB hub topology tree showing device hierarchy.
- `include_internal` (boolean, optional): Show Apple internal hubs and devices (default: false)
- Returns: ASCII tree with each device showing vendor, product ID, speed, and power draw
- Useful for understanding which devices are on which hub/port and detecting cascading hub issues

**`power_info`** — Report USB power draw and capabilities.
- `identifier` (string, optional): Device serial, location ID, or name. If omitted, shows power summary for all devices
- Returns: Bus power available (mA), current draw per device, self-powered vs bus-powered classification, hub power budgets, charging type detection (if applicable)
- Critical for diagnosing power-related device failures

**`monitor_events`** — Monitor USB connect/disconnect events (polling-based).
- `clear` (boolean, optional): Clear the event log and re-snapshot current state (default: false)
- First call snapshots current state; subsequent calls report changes since last check
- Maintains circular buffer of last 50 events
- Useful for watching devices connect/disconnect during firmware flashing or board resets

### Device Management

**`tag_device`** — Set, get, list, or remove persistent user-defined aliases (tags) for USB devices.
- `action` (string, required): `set`, `get`, `list`, or `remove`
- `identifier` (string, conditional): Required for set, get, remove
- `tag` (string, conditional): Required for set — the alias to assign
- Tags are stored locally and survive reconnections
- Useful for giving devices human-readable names like "Primary_ESP32" or "Test_Arduino"

**`eject_device`** — Safely unmount and eject a removable USB storage device.
- `identifier` (string, required): Serial, location ID, volume name, or mount point
- `force` (boolean, optional): Force eject even if volumes are in use (default: false)
- Returns: Success or error message with detailed reason if eject fails
- Only works on storage devices; validates device type before attempting eject

**`port_reset`** — Reset a USB port to recover a frozen or unresponsive device.
- `identifier` (string, required): Serial, location ID, or name
- `confirm` (boolean, required): Must be true to proceed
- Simulates unplug/replug via IOKit re-enumeration
- Only works on external/removable devices
- **Warning**: Interrupts active transfers; can cause data loss if device has open files

### Diagnostics & Info

**`diagnose_device`** — Query macOS system logs and IOKit for USB errors related to a specific device.
- `identifier` (string, required): Serial, location ID, or name
- `timeframe` (string, optional): Search depth: `1h`, `6h`, or `24h` (default: 1h)
- Returns: Error count, error types, and recent log entries
- Useful for debugging intermittent USB disconnects or protocol errors

**`device_descriptors`** — Read full USB descriptor chain for a device.
- `identifier` (string, required): Serial, location ID, or name
- Returns: Device descriptor, configuration descriptors, interface descriptors, endpoint descriptors with class codes, transfer types, max packet sizes
- Deep technical diagnostic; used when you need raw USB protocol information

**`snapshot_state`** — Capture and compare USB device state snapshots.
- `action` (string, required): `capture`, `list`, `compare`, or `delete`
- `name` (string, optional): Snapshot name to save/load/delete. If omitted for capture, auto-generates timestamp-based name
- `compare_to` (string, optional): For compare action, name of second snapshot to compare against. If omitted, compares to current live state
- Useful for detecting what changed between two moments (e.g., before/after a firmware flash attempt)

### Firmware & Microcontroller

**`chip_detect`** — Detect the exact chip type of a connected microcontroller via esptool.
- `identifier` (string, required): Serial, location ID, or name
- `port` (string, optional): Serial port override (auto-detected from device if not specified)
- Returns: Chip type, revision, features, crystal frequency, MAC address
- Resolves ambiguous USB identifications (e.g., ESP32-S2 vs S3 when both use PID 0x1001)
- **Requires esptool installed** on the system

**`flash_firmware`** — Flash firmware to a USB device (destructive operation).
- `identifier` (string, required): Serial, location ID, or name
- `firmware_path` (string, required): Path to firmware file (.bin, .hex, .uf2, .elf)
- `tool` (string, optional): Override auto-detection: `esptool`, `dfu-util`, `avrdude`, or `uf2`
- `port` (string, optional): Serial port override (auto-detected if not specified)
- `baud` (integer, optional): Baud rate for serial flashing (varies by tool)
- `confirm` (boolean, required): Must be true to proceed
- Supported platforms: **ESP32 (esptool)**, **STM32 (dfu-util)**, **Arduino AVR (avrdude)**, **RP2040 (UF2 copy)**
- **Shows the exact command before executing** — review carefully before confirming
- **Requires matching flasher tool installed** (esptool, dfu-util, avrdude, or UF2 support)
- **WARNING**: Flashing erases the device's program memory; incorrect firmware can brick the board

### HID (Human Interface Device)

**`hid_send`** — Interact with USB HID devices (Human Interface Devices).
- `identifier` (string, required): Serial, location ID, or name
- `action` (string, required): `send_report`, `get_report`, or `list_reports`
- `report_type` (string, optional): `output` or `feature` (default: output for send, feature for get)
- `report_id` (integer, optional): Report ID (default: 0)
- `data` (string, optional): Hex string of bytes to send, e.g., `0x01 0xFF 0x00` or `01ff00` (required for send_report)
- `confirm` (boolean, optional): Required for send_report to confirm you're sending data to a device
- Useful for: Stream Deck key presses, macro pad programming, custom HID device control
- Displays available report descriptors with max payload sizes if `list_reports` is called

### Serial Communication

**`serial_open`** — Open a serial connection to a port (e.g., `/dev/cu.usbserial-2120`).
- `port` (string, required): Serial port path (must be `/dev/cu.*` on macOS, not `/dev/tty.*`)
- `baud_rate` (integer, optional): Baud rate (default: 115200). Common: 300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400
- `data_bits` (integer, optional): 5, 6, 7, or 8 (default: 8)
- `stop_bits` (integer, optional): 1 or 2 (default: 1)
- `parity` (string, optional): `none`, `even`, or `odd` (default: none)
- Returns: Success or error message (e.g., "Port already open", "Invalid port path")
- Must be called before `serial_read`, `serial_write`, or `serial_monitor`

**`serial_read`** — Read available data from an open serial connection.
- `port` (string, required): Serial port path (must be opened with `serial_open` first)
- `timeout` (number, optional): Read timeout in seconds (default: 1.0, clamped to 0.1-30.0)
- Returns: Text data from the receive buffer, or error if port not open
- Waits up to timeout for data; returns immediately if data is available

**`serial_write`** — Write data or a command to an open serial connection.
- `port` (string, required): Serial port path (must be opened with `serial_open` first)
- `data` (string, required): Text string or hex bytes (e.g., `0x01 0xFF 0x00` or `01FF`)
- Text data is sent as UTF-8 with `\r\n` appended; hex bytes are sent as raw bytes
- Returns: Confirmation or error message

**`serial_close`** — Close an open serial connection and restore the port to its original state.
- `port` (string, required): Serial port path
- Returns: Success or error message (e.g., "Port not open")

**`serial_monitor`** — Read from a serial port for a specified duration and return all output.
- `port` (string, required): Serial port path (e.g., `/dev/cu.usbserial-2120`)
- `seconds` (number, optional): How long to monitor in seconds (default: 5.0, clamped to 0.5-30.0)
- `auto_open` (boolean, optional): Automatically open the port if not already open (default: false)
- `baud_rate` (integer, optional): Baud rate for auto_open (default: 115200)
- Returns: All output captured during the monitoring period
- Useful for: Capturing boot output, watching log streams, collecting device responses during initialization

## Known patterns and gotchas

**Serial port paths on macOS**: Use `/dev/cu.*` (call port) for communication, not `/dev/tty.*` (dial-in). The tools validate this and return explicit errors if you use the wrong prefix.

**No USB devices connected**: When no devices are present, `list_usb_devices` returns "No USB devices found." — this is not an error, and subsequent calls like `get_device_info` will also return device-not-found gracefully.

**Firmware flashing requires matching tools**: Each platform needs a specific flashing utility:
- **ESP32**: `esptool` (install via `pip install esptool`)
- **STM32**: `dfu-util` (install via Homebrew: `brew install dfu-util`)
- **Arduino AVR**: `avrdude` (install via Homebrew: `brew install avrdude`)
- **RP2040**: No tool needed; Bench copies to the UF2 mount point directly
If the tool is missing, the flash attempt fails with a clear error message naming the missing tool.

**Identifier matching is lenient**: Serial number, location ID (e.g., `0x02100000`), and device name all work. The tool tries all three; location ID is most reliable for repeated calls since serial numbers can vary or be absent.

**Monitor_events is polling-based**: It's not a live stream. Call it repeatedly to check for state changes since the last call; each call returns only what changed, up to 50 events.

**Tag persistence**: Tags are stored locally on the mac (exact file location not documented in source, but implied to survive reconnects). If you tag a device, that tag persists even after the device is unplugged and replugged.

**HID send is potentially destructive**: The tool asks for `confirm=true` because sending the wrong report to an HID device can cause unexpected behavior (e.g., sending button-press reports to a Stream Deck might trigger macros).

## Quick verification pattern for this skill

```bash
# Test that Bench is running and IOKit is available
/Users/charlieseay/Projects/bench/.build/release/Bench <<'EOF'
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"ping","arguments":{}}}
EOF

# Expected output includes: "status":"ok" and "iokit_available":true or false
```

If Bench doesn't respond or crashes:
- Check that the binary exists at `/Users/charlieseay/Projects/bench/.build/release/Bench`
- Run `file /Users/charlieseay/Projects/bench/.build/release/Bench` to verify it's a valid Mach-O arm64 binary
- Check macOS System Preferences → Security & Privacy for any restrictions (unlikely but possible)
- Note that IOKit access requires root on some older macOS versions; if `iokit_available` is false, many tools will fail
