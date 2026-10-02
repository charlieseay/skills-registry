#!/usr/bin/env python3
"""
Writing Rules Checker - Enforces Seaynic Labs voice standards

Usage:
    check.py <file-path>

Exits with:
    0 = all rules passed
    1 = violations found (blocks publishing)
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

class Violation:
    def __init__(self, rule: str, line_num: int, line: str, suggestion: str):
        self.rule = rule
        self.line_num = line_num
        self.line = line
        self.suggestion = suggestion

def check_question_openers(lines: List[str]) -> List[Violation]:
    """Rule 4: No question openers"""
    violations = []
    question_patterns = [
        r'^#+\s+(Want to|Need to|Looking for|Wondering|Are you)',
        r'^(Want to|Need to|Looking for|Wondering|Are you)',
    ]

    for i, line in enumerate(lines, 1):
        for pattern in question_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(Violation(
                    rule="No Question Openers",
                    line_num=i,
                    line=line.strip(),
                    suggestion="Rewrite as a statement. Start with what it does, not a question."
                ))

    return violations

def check_vague_quantifiers(lines: List[str]) -> List[Violation]:
    """Rule 5: No most/many/some"""
    violations = []
    vague_words = r'\b(most|many|some|several|various|numerous|a lot of)\b'

    for i, line in enumerate(lines, 1):
        if re.search(vague_words, line, re.IGNORECASE):
            violations.append(Violation(
                rule="No Vague Quantifiers",
                line_num=i,
                line=line.strip(),
                suggestion="Replace with exact number, 'all', 'zero', or named set."
            ))

    return violations

def check_passive_voice(lines: List[str]) -> List[Violation]:
    """Rule 3: Active voice"""
    violations = []
    passive_patterns = [
        r'\bis designed to\b',
        r'\bcan be used\b',
        r'\bwill be\b',
        r'\bare created\b',
        r'\bis recommended\b',
        r'\bshould be\b',
    ]

    for i, line in enumerate(lines, 1):
        for pattern in passive_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(Violation(
                    rule="Active Voice Required",
                    line_num=i,
                    line=line.strip(),
                    suggestion="Rewrite in active voice. Subject acts on object."
                ))

    return violations

def check_hedging(lines: List[str]) -> List[Violation]:
    """Rule 8: No hedging"""
    violations = []
    hedge_words = r'\b(might|perhaps|maybe|hopefully|should|could|would seem|appears to)\b'

    for i, line in enumerate(lines, 1):
        if re.search(hedge_words, line, re.IGNORECASE):
            violations.append(Violation(
                rule="No Hedging",
                line_num=i,
                line=line.strip(),
                suggestion="Use definitive statements. Remove hedging words."
            ))

    return violations

def check_marketing_fluff(lines: List[str]) -> List[Violation]:
    """Rule 7: No marketing fluff"""
    violations = []
    fluff_patterns = [
        r'\b(revolutionary|groundbreaking|amazing|incredible|fantastic|awesome)\b',
        r'\b(game-changing|cutting-edge|state-of-the-art|best-in-class)\b',
        r'\b(powerful|robust|comprehensive|innovative)\b',
    ]

    for i, line in enumerate(lines, 1):
        for pattern in fluff_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(Violation(
                    rule="No Marketing Fluff",
                    line_num=i,
                    line=line.strip(),
                    suggestion="Replace with measurable claim or specific feature."
                ))

    return violations

def check_first_sentence(lines: List[str]) -> List[Violation]:
    """Rule 6: First body sentence must be concrete"""
    violations = []

    # Find first heading and first sentence after it
    in_frontmatter = False
    past_heading = False

    for i, line in enumerate(lines, 1):
        # Skip frontmatter
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue

        # Find first heading
        if line.startswith('#') and not past_heading:
            past_heading = True
            continue

        # Check first sentence after heading
        if past_heading and line.strip() and not line.startswith('#'):
            # Abstract openers to avoid
            abstract_openers = [
                r'^(This|It|Testing|Documentation|The following)',
                r'is (a|an|the) (important|critical|essential|key)',
                r'(helps|allows|enables) you',
            ]

            for pattern in abstract_openers:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(Violation(
                        rule="First Sentence Must Be Concrete",
                        line_num=i,
                        line=line.strip(),
                        suggestion="Start with specific action, number, or named thing. No abstract setup."
                    ))
            break

    return violations

def check_file(file_path: Path) -> Tuple[bool, List[Violation]]:
    """Check a file against all writing rules"""

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False, []

    lines = file_path.read_text().splitlines()

    violations = []
    violations.extend(check_question_openers(lines))
    violations.extend(check_vague_quantifiers(lines))
    violations.extend(check_passive_voice(lines))
    violations.extend(check_hedging(lines))
    violations.extend(check_marketing_fluff(lines))
    violations.extend(check_first_sentence(lines))

    return len(violations) == 0, violations

def main():
    if len(sys.argv) != 2:
        print("Usage: check.py <file-path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    print(f"🔍 Checking writing rules: {file_path.name}")
    print()

    passed, violations = check_file(file_path)

    if passed:
        print("✅ All writing rules passed")
        print()
        print("Document follows Seaynic Labs voice standards.")
        sys.exit(0)

    else:
        print(f"❌ {len(violations)} violation(s) found")
        print()

        for v in violations:
            print(f"Line {v.line_num}: {v.rule}")
            print(f"  > {v.line}")
            print(f"  ↳ {v.suggestion}")
            print()

        print("⛔ BLOCKED: Fix violations before publishing")
        sys.exit(1)

if __name__ == '__main__':
    main()
