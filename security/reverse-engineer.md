---
name: reverse-engineer
description: Expert reverse engineering and binary analysis — disassembly, decompilation, static binary methodology (ELF, Mach-O, PE, JVM, .NET, Python bytecode), protocol extraction and vulnerability research across IDA Pro, Ghidra, radare2, x64dbg, angr and modern RE toolchains. Use for executable/library analysis, undocumented software or protocol comprehension, CTF challenges, security research, static-binary-only analysis without execution, or troubleshooting/fixing behavior only visible in compiled code. Triggers: reverse engineer, RE, disassembly, decompilation, binary analysis, static analysis, extract binary intelligence, ELF, Mach-O, PE, JVM bytecode, .NET assembly, protocol extraction, undocumented API, malware analysis, vulnerability research, IDA, Ghidra, radare2, angr.
metadata:
  source: https://github.com/majiayu000/claude-skill-registry (skills/security/reverse-engineer)
  license: MIT
  installed: 2026-09-14
  installed_by: skill-discovery (Talos + fleet capability request)
---

<!-- Vendored from https://github.com/majiayu000/claude-skill-registry (skills/security/reverse-engineer) (MIT). Body preserved verbatim; frontmatter description
     rewritten with fleet-wide trigger vocabulary so all agents auto-discover it. -->
     Merged with binary-analysis-greenfield (static methodology for compiled artifacts without execution).

# Static Binary Analysis Methodology

Extract behavioral intelligence from compiled artifacts when source code is unavailable. Static analysis only — the binary is never executed.

## When This Mode Applies

Binary analysis activates when:
- The target is a compiled artifact with no source code available
- Discovery identifies compiled binaries at the target path
- Other modes discover compiled artifacts during analysis (e.g., a bundled native binary inside an npm package)

## Binary Type Taxonomy

| Artifact Type | Format | Survey Tools | Decompiler | Decompilation Quality | Default Confidence |
|--------------|--------|-------------|------------|----------------------|-------------------|
| Native binaries | ELF, Mach-O, PE | `file`, `readelf`/`otool`/`objdump`, `nm`, `strings` | Ghidra, radare2 (disassembly only) | N/A (no source recovery) | `assumed` |
| JVM bytecode | `.class`, `.jar`, `.war` | `jar tf`, `javap -public`, manifest extraction | CFR, Procyon, FernFlower | Very high | `inferred` |
| .NET assemblies | `.dll`, `.exe` (managed) | `dotnet ildasm`, type enumeration, attributes | ILSpy (`ilspycmd`) | Very high | `inferred` |
| Python bytecode | `.pyc`, `.pyo` | Magic number inspection, `strings` | uncompyle6, decompyle3, pycdc | Very high | `inferred` |
| Electron apps | `.asar` bundles | `npx asar extract`, `package.json` | N/A (lossless source recovery) | Lossless | `inferred` |
| WebAssembly | `.wasm` | `wasm-tools print`, export/import enumeration | `wasm2wat` (text format only) | Limited | `assumed` |

### Step 1: Survey First

Always start with lightweight binary surveying. The survey:
- Identifies the binary type and selects the right tool chain
- Extracts everything accessible through lightweight tools (strings, symbols, metadata)
- Determines which modules warrant the cost of deep analysis
- Attempts decompilation for managed code

### Step 2: Strings Are Gold

Embedded strings are the highest-value, lowest-effort source of behavioral intelligence. They provide direct evidence:
- **Error messages** reveal validation rules, failure modes, and error handling
- **URLs and endpoints** reveal API surface and external dependencies
- **Configuration keys** reveal tunable parameters
- **Regex patterns** reveal input validation rules

Extract strings early. Categorize them. Cross-reference during deep analysis.

### Step 3: Managed Code Gets Decompiled

JVM, .NET, Python, and Electron artifacts preserve enough metadata for high-quality decompilation. When decompilation succeeds, use source code analysis on the decompiled result.

### Step 4: Native Binaries Get Deep Disassembly

For native code (ELF, Mach-O, PE) where decompilation is unreliable:
1. Select target functions based on surveyor recommendations
2. Disassemble with Ghidra (headless) or radare2
3. Trace control flow and express as behavioral decision trees
4. Map data structures from memory access patterns
5. Identify algorithms from instruction patterns and constants

### Step 5: Document Gaps Explicitly

Binary analysis frequently produces incomplete pictures. Include a "Gaps in Analysis" section listing what could NOT be determined and why.

## Tool Reference — Native Binaries (ELF)

```bash
file target.bin                        # Magic-based type identification
readelf -h target.bin                  # ELF header
readelf -S target.bin                  # Section headers
nm target.bin                          # Symbol table
strings -a -n 4 target.bin            # ASCII strings
objdump -d --section=.text target.bin  # Disassemble text section
```

## Tool Reference — Native Binaries (Mach-O)

```bash
otool -h target.bin                    # Mach-O header
otool -l target.bin                    # Load commands
otool -L target.bin                    # Linked libraries
```

## Tool Reference — Disassemblers

```bash
# Ghidra headless mode
$GHIDRA_HOME/support/analyzeHeadless /tmp/ghidra-project project-name \
  -import target.bin -postScript ExportDisassembly.java

# radare2: function disassembly
r2 -q -c 'aaa; pdf @ sym.main' target.bin

# radare2: function list
r2 -q -c 'aaa; afl' target.bin
```

## Tool Reference — JVM

```bash
jar tf target.jar                      # List contents
java -jar cfr.jar target.jar --outputdir decompiled/  # Decompile
```

## Tool Reference — .NET

```bash
dotnet ildasm target.dll               # Type/method listing
ilspycmd target.dll -o decompiled/     # Decompile to C#
```

## Tool Reference — Electron/ASAR

```bash
npx asar list app.asar                 # List contents
npx asar extract app.asar extracted/   # Extract (lossless)
```

---

# Common RE scripting environments
- IDAPython (IDA Pro scripting)
- Ghidra scripting (Java/Python via Jython)
- r2pipe (radare2 Python API)
- pwntools (CTF/exploitation toolkit)
- capstone (disassembly framework)
- keystone (assembly framework)
- unicorn (CPU emulator framework)
- angr (symbolic execution)
- Triton (dynamic binary analysis)
```

## Tooling: REA MCP

REA (Reverse Engineer Anything) is an MCP server with 207 tools for static analysis of JavaScript/Electron apps, native binaries, web bundles, WASM, APKs, and firmware without execution. Use it when you need:

- **Lossless source recovery from bundled JavaScript apps** (`.asar`, bundled Electron, web bundles)
- **Binary metadata extraction** (strings, symbols, headers) without decompilers
- **Managed code decompilation** (JVM, .NET, Python bytecode)
- **Version comparison and source-to-bundle integrity verification**
- **Web dependency graphs** from captured network bundles
- **WASM interface inspection** and export enumeration

See `/Volumes/data/skills/infrastructure/mcp-rea/SKILL.md` for full tool list, provider requirements, and common analysis patterns.

## Use this skill when

- Working on common re scripting environments tasks or workflows
- Needing guidance, best practices, or checklists for common re scripting environments
- Performing static-only analysis of binaries, Electron apps, or web bundles (REA MCP is available)

## Do not use this skill when

- The task is unrelated to reverse engineering or binary analysis
- You need a different domain or tool outside this scope

## Instructions

- Clarify goals, constraints, and required inputs.
- Apply relevant best practices and validate outcomes.
- Provide actionable steps and verification.
- If detailed examples are required, open `resources/implementation-playbook.md`.

## Analysis Methodology

### Phase 1: Reconnaissance
1. **File identification**: Determine file type, architecture, compiler
2. **Metadata extraction**: Strings, imports, exports, resources
3. **Packer detection**: Identify packers, protectors, obfuscators
4. **Initial triage**: Assess complexity, identify interesting regions

### Phase 2: Static Analysis
1. **Load into disassembler**: Configure analysis options appropriately
2. **Identify entry points**: Main function, exported functions, callbacks
3. **Map program structure**: Functions, basic blocks, control flow
4. **Annotate code**: Rename functions, define structures, add comments
5. **Cross-reference analysis**: Track data and code references

### Phase 3: Dynamic Analysis
1. **Environment setup**: Isolated VM, network monitoring, API hooks
2. **Breakpoint strategy**: Entry points, API calls, interesting addresses
3. **Trace execution**: Record program behavior, API calls, memory access
4. **Input manipulation**: Test different inputs, observe behavior changes

### Phase 4: Documentation
1. **Function documentation**: Purpose, parameters, return values
2. **Data structure documentation**: Layouts, field meanings
3. **Algorithm documentation**: Pseudocode, flowcharts
4. **Findings summary**: Key discoveries, vulnerabilities, behaviors

## Response Approach

When assisting with reverse engineering tasks:

1. **Clarify scope**: Ensure the analysis is for authorized purposes
2. **Understand objectives**: What specific information is needed?
3. **Recommend tools**: Suggest appropriate tools for the task
4. **Provide methodology**: Step-by-step analysis approach
5. **Explain findings**: Clear explanations with supporting evidence
6. **Document patterns**: Note interesting code patterns, techniques

## Code Pattern Recognition

### Common Patterns
```c
// String obfuscation (XOR)
for (int i = 0; i < len; i++)
    str[i] ^= key;

// Anti-debugging (IsDebuggerPresent)
if (IsDebuggerPresent())
    exit(1);

// API hashing (common in malware)
hash = 0;
while (*name)
    hash = ror(hash, 13) + *name++;

// Stack string construction
char s[8];
*(DWORD*)s = 0x6C6C6548;  // "Hell"
*(DWORD*)(s+4) = 0x6F;     // "o\0"
```

### Calling Conventions
- **x86 cdecl**: Args on stack, caller cleans
- **x86 stdcall**: Args on stack, callee cleans
- **x64 Windows**: RCX, RDX, R8, R9, then stack
- **x64 System V**: RDI, RSI, RDX, RCX, R8, R9, then stack
- **ARM**: R0-R3, then stack

## Security & Ethics

### Authorized Use Only
- Security research with proper authorization
- CTF competitions and educational challenges
- Malware analysis for defensive purposes
- Vulnerability disclosure through responsible channels
- Understanding software for interoperability

### Never Assist With
- Unauthorized access to systems
- Creating malware for malicious purposes
- Bypassing software licensing illegitimately
- Intellectual property theft
- Any illegal activities

## Example Interactions

### CTF Binary Challenge
```
User: "I have a CTF binary that asks for a password. How do I approach this?"

Response: Let me guide you through the analysis:

1. First, identify the binary type:
   $ file challenge
   $ checksec --file=challenge

2. Load in Ghidra/IDA and find main()

3. Look for:
   - String comparisons (strcmp, memcmp)
   - Crypto functions (xor loops, constants like 0x5A827999)
   - Input validation logic

4. Set breakpoints on comparison functions in GDB:
   $ gdb ./challenge
   (gdb) break strcmp
   (gdb) run

5. Examine memory at comparison point to see expected value
```

### Library Analysis
```
User: "I need to understand how this closed-source DLL handles authentication"

Response: For authorized analysis of the DLL:

1. Static analysis:
   - List exports: dumpbin /exports library.dll
   - Find auth-related functions by name patterns
   - Load in IDA/Ghidra, analyze exported functions

2. Dynamic analysis:
   - Hook API calls with Frida
   - Monitor network traffic
   - Trace function parameters

3. Documentation:
   - Document function signatures
   - Map data structures
   - Note any security considerations
```
