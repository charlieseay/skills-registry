---
name: mcp-rea
description: |
  REA (Reverse Engineer Anything) MCP server for static and dynamic application analysis without execution. Use this skill when:
  - Analyzing JavaScript/Electron applications for undocumented APIs, architecture, and data flows
  - Extracting strings, symbols, and metadata from compiled binaries (ELF, Mach-O, PE, JVM, .NET, Python bytecode)
  - Comparing application versions, source-to-bundle integrity, or exported interfaces
  - Reconstructing web applications from captured network bundles
  - Examining WASM modules, Android APKs, iOS apps, or firmware artifacts
  - Reverse engineering software you own or are authorized to examine (lawful use only)
  - Any request like "reverse engineer", "analyze app", "extract schema", "decompile", "static analysis"
  keywords: [reverse-engineering, static-analysis, binary-analysis, javascript, electron, decompilation, WASM, APK]
---

# REA MCP Server — Reverse Engineer Anything

Static and dynamic application analysis for understanding undocumented software, extracting schemas, comparing versions, and reverse engineering.

## When to Use

REA is a 207-tool MCP server for analyzing applications without executing them. Use it when:

- **JavaScript/Electron apps**: Extract export shapes, dependency graphs, and architecture from bundled source
- **Native binaries**: Survey ELF/Mach-O/PE/JVM/.NET binaries for strings, symbols, functions, and metadata
- **Web bundles**: Capture and analyze page dependencies, imports, and critical paths from browser network traces
- **Version comparison**: Diff two application versions to identify API changes, interface shifts, or behavior divergence
- **Mobile apps**: Analyze Android APKs, iOS .ipa archives, or firmware blobs
- **WASM modules**: Inspect WebAssembly exports, memory layouts, and function signatures
- **Protocol extraction**: Pull URLs, endpoints, configuration keys, and error messages from application strings
- **Source-to-bundle verification**: Compare committed source against published artifacts for integrity and divergence

## How It Works

```
Input: Application artifact (JS, binary, ASAR, APK, .ipa, firmware, WASM)
  ↓
Survey: Identify type, extract lightweight metadata (strings, symbols, headers)
  ↓
Analyze: Deep dive (decompilation for managed code, graph reconstruction for JS, etc.)
  ↓
Output: JSON Evidence bundle with findings, extraction, and comparison results
```

## Key Capabilities

| Category | Tools | When to Use |
|----------|-------|------------|
| **JavaScript/Electron** | analyze-javascript-application, compare-javascript-export-shapes, compare-application-versions | Understand bundled app structure, APIs, and changes |
| **Native Binaries** | analyze (ELF/Mach-O/PE), address-to-file-offset, annotate-native-function | Extract symbols, strings, function annotations from compiled code |
| **Web Bundles** | analyze-web-bundle, capture-web-screenshot, compare-web-captures | Analyze dependency graphs and UI from network traces |
| **Mobile/Firmware** | collect-adb-bugreport, capture-process, compare-process-captures | Extract traces, logs, and runtime state |
| **WASM** | compare-wasm-interfaces | Inspect WebAssembly module boundaries and exports |
| **Evidence** | build-reconstruction-obligation-ledger, compare | Generate audit trails and deterministic comparison reports |

## Provider Requirements

REA works **without external providers** for:
- JavaScript/Electron static analysis (lossless source recovery from bundled apps)
- Web bundle analysis (network captures and DOM introspection)
- WASM inspection (text format only)
- Metadata extraction from binaries (strings, symbols, headers)
- ELF/Mach-O/PE basic surveying (readelf, otool, objdump equivalents)

**Optional providers for deeper analysis:**
- **Ghidra** (JDK required): Free, open-source decompiler for ELF/Mach-O/PE/MIPS/PPC binaries. Install: `brew tap NationalSecurityAgency/ghidra && brew install ghidra` or download from NSA repo
- **radare2**: Lightweight disassembler and binary analysis platform
- **IDA Pro / Hopper / JEB**: Commercial reverse engineering suites (REA detects and uses if installed)
- **rizin**: Cutter GUI or CLI for decompilation and annotation
- **Browser/ADB/LLDB**: For live process analysis and network capture

Current status (this Mac): **No reverse engineering providers installed.** Static JS/Electron, web bundles, WASM, and strings-based analysis work. For native binary decompilation, install Ghidra (free, requires JDK which is present).

## Common Commands

### Analyze a JavaScript/Electron app
```bash
rea analyze-javascript-application /path/to/app.asar
```
Returns: Export graph, dependency tree, potential entry points.

### Extract strings from a binary
```bash
rea analyze /path/to/binary | grep -E "string|url|endpoint"
```
Returns: Embedded URLs, API keys, error messages, configuration keys.

### Compare two app versions
```bash
rea compare-application-versions path1.asar path2.asar
```
Returns: Diff of exports, dependencies, and API surface changes.

### Analyze a web page bundle
```bash
# Requires a running browser with Chrome DevTools Protocol
rea analyze-web-bundle http://localhost:9222 <targetId>
```
Returns: Script graph, imports, critical dependencies, DOM structure.

### Verify source-to-bundle integrity
```bash
rea compare-source-to-bundle source/ app.asar
```
Returns: Divergence report (stripped files, obfuscation, version drift).

## Pitfalls & Tips

1. **Codesigned binaries**: macOS apps signed by Apple often have runtime code patching and integrity checks that cause analysis mismatches. Use `--integrity-policy record-and-continue` to analyze despite codesign drift, or get a fresh unsigned copy.

2. **Bundled native modules**: Electron apps with `.node` binaries inside `.asar` require native binary analysis for those modules. REA handles the extraction; Ghidra or radare2 is needed for the `.node` decompilation.

3. **Obfuscated JavaScript**: Minified/uglified code will still decompile but variable names are lost. Source maps (if bundled) help. Use `--fetch-source-maps` for web captures.

4. **Evidence bundles are deterministic**: REA outputs match input artifacts byte-for-byte. Rerun the same analysis twice and get identical JSON hashes — useful for CI/CD and audit trails.

5. **Lawful use only**: REA is a neutral analysis tool. Only analyze software you own, have authorization to examine (e.g., from vendor source), or have legal justification to reverse engineer (e.g., security research, interoperability, scholarship). Violating software licensing or DMCA restrictions is illegal.

## MCP Registration

REA is registered as an MCP server for:
- **Claude Code** (~/.claude.json)
- **Cursor** (~/.cursor/mcp.json)

Access is automatic through the `rea` tools in the MCP tool manifest once the server connects.

## Tooling: REA MCP

REA integrates with the **reverse-engineer skill** for methodology and provider configuration. See `/Volumes/data/skills/security/reverse-engineer.md` for static binary analysis workflows.
