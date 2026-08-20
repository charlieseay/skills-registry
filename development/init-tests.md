---
name: init-tests
description: Bootstrap test framework for a project (detects language, scaffolds tests)
---

# Test Framework Bootstrap

Auto-scaffolds a test framework for projects that don't have one. Detects project type, installs appropriate test runner, creates test directory, adds sample test.

## When to invoke

- New project with no tests
- User says "set up testing" or "add tests"
- Before first `/checkpoint --ship` if no test framework exists
- **Proactively suggest** after implementing first feature with no tests

## Workflow

### Step 1: Detect project type

```bash
_PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$_PROJECT_ROOT"

# Check for language/framework indicators
if [ -f "package.json" ]; then
  _LANG="javascript"
  _FRAMEWORK=$(node -e "const pkg=require('./package.json'); console.log(pkg.dependencies?.astro ? 'astro' : pkg.dependencies?.next ? 'next' : pkg.dependencies?.react ? 'react' : pkg.dependencies?.vue ? 'vue' : pkg.dependencies?.svelte ? 'svelte' : 'node')" 2>/dev/null || echo "node")
elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  _LANG="python"
  _FRAMEWORK="python"
elif [ -f "go.mod" ]; then
  _LANG="go"
  _FRAMEWORK="go"
elif [ -f "*.xcodeproj" ] || [ -f "*.xcworkspace" ]; then
  _LANG="swift"
  _FRAMEWORK="swift"
elif [ -f "Cargo.toml" ]; then
  _LANG="rust"
  _FRAMEWORK="rust"
else
  _LANG="unknown"
  _FRAMEWORK="unknown"
fi

echo "Detected: $_LANG / $_FRAMEWORK"
```

### Step 2: Choose test framework

| Language/Framework | Test Runner | Install Command |
|-------------------|-------------|-----------------|
| JavaScript/Node | Vitest | `npm install -D vitest` |
| Astro | Vitest | `npm install -D vitest` |
| Next.js | Jest | `npm install -D jest @testing-library/react @testing-library/jest-dom` |
| React | Vitest | `npm install -D vitest @testing-library/react` |
| Vue | Vitest | `npm install -D vitest @vue/test-utils` |
| Svelte | Vitest | `npm install -D vitest @testing-library/svelte` |
| Python | pytest | `pip install pytest pytest-cov` |
| Go | testing | Built-in, no install needed |
| Swift/iOS | XCTest | Built-in Xcode framework |
| Rust | cargo test | Built-in, no install needed |

### Step 3: Install test runner

```bash
case "$_FRAMEWORK" in
  astro|node|react|vue|svelte)
    npm install -D vitest
    ;;
  next)
    npm install -D jest @testing-library/react @testing-library/jest-dom
    ;;
  python)
    if [ -f "pyproject.toml" ]; then
      # Use uv if available, otherwise pip
      if command -v uv >/dev/null 2>&1; then
        uv add --dev pytest pytest-cov
      else
        pip install pytest pytest-cov
      fi
    else
      pip install pytest pytest-cov
    fi
    ;;
  go|swift|rust)
    echo "Using built-in test framework"
    ;;
  *)
    echo "Unknown framework, cannot auto-install"
    exit 1
    ;;
esac
```

### Step 4: Create test directory

```bash
case "$_LANG" in
  javascript)
    mkdir -p tests
    _TEST_DIR="tests"
    ;;
  python)
    mkdir -p tests
    touch tests/__init__.py
    _TEST_DIR="tests"
    ;;
  go)
    # Go tests live alongside source
    _TEST_DIR="."
    ;;
  swift)
    # XCTest target in Xcode
    echo "Create test target in Xcode: File → New → Target → Unit Testing Bundle"
    _TEST_DIR="<ProjectName>Tests"
    ;;
  rust)
    mkdir -p tests
    _TEST_DIR="tests"
    ;;
esac

echo "Test directory: $_TEST_DIR"
```

### Step 5: Add sample test

Create a simple smoke test to verify the framework works:

**JavaScript (Vitest):**
```javascript
// tests/smoke.test.js
import { describe, it, expect } from 'vitest'

describe('Smoke test', () => {
  it('should pass', () => {
    expect(true).toBe(true)
  })
})
```

**Python (pytest):**
```python
# tests/test_smoke.py
def test_smoke():
    assert True
```

**Go:**
```go
// smoke_test.go
package main

import "testing"

func TestSmoke(t *testing.T) {
	if !true {
		t.Error("Smoke test failed")
	}
}
```

**Swift (XCTest):**
```swift
// SmokeTests.swift
import XCTest

class SmokeTests: XCTestCase {
    func testSmoke() {
        XCTAssertTrue(true)
    }
}
```

**Rust:**
```rust
// tests/smoke.rs
#[test]
fn test_smoke() {
    assert!(true);
}
```

### Step 6: Update project config

Add test script to package.json / pyproject.toml / etc.:

**JavaScript (package.json):**
```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

**Python (pyproject.toml):**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "--cov=. --cov-report=term-missing"
```

**Go (run with `go test ./...`):**
No config needed.

**Rust (Cargo.toml):**
```toml
[[test]]
name = "integration"
path = "tests/smoke.rs"
```

### Step 7: Run smoke test

```bash
case "$_FRAMEWORK" in
  astro|node|react|vue|svelte|next)
    npm test
    ;;
  python)
    pytest
    ;;
  go)
    go test ./...
    ;;
  swift)
    xcodebuild test -scheme <ProjectName> -destination 'platform=iOS Simulator,name=iPhone 15'
    ;;
  rust)
    cargo test
    ;;
esac
```

If smoke test passes, framework is working.

### Step 8: Document in project note

Update `Projects/<project>/<project>.md` with testing setup:

```markdown
## Testing

**Framework:** <test-runner>
**Run tests:** <command>
**Coverage:** <command>

**Test directory:** `<path>`

**Sample test:** `<path-to-smoke-test>`
```

## Output

- Test framework installed
- Test directory created
- Sample test added
- Project config updated
- Tests passing
- Documentation updated

Report:
```
✅ Test framework initialized: <framework>
✅ Test directory: <path>
✅ Sample test: <smoke-test-path>
✅ Smoke test: PASSED
✅ Run tests with: <command>
```

## Skip Conditions

- Tests already exist (`tests/` dir or `*_test.go` files)
- Project type cannot be detected
- User declines auto-setup

## Integration

- Auto-suggested after first feature implementation with no tests
- Can be manually invoked with `/init-tests`
- Outputs documented in project note
- Smoke test verifies framework works

## Notes

- **Defaults to modern frameworks** (Vitest over Jest for JS)
- **Minimal setup** — just enough to start testing
- **Smoke test proves it works** — user sees green test immediately
- **Framework-specific** — respects each language's conventions
