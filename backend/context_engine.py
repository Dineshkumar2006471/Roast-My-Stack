"""
Context Engine — RoastMyStack Smart Assistant Layer

This module implements the logical decision-making that makes RoastMyStack
a dynamic assistant rather than a static analysis tool. All decisions are
based on detected user context: language, complexity, intensity level.

Challenge Vertical: Developer Tools
Persona: The Relentless Senior Engineer
"""

import re
from dataclasses import dataclass
from enum import Enum


class Intensity(str, Enum):
    JUNIOR = "junior"
    SENIOR = "senior"
    STAFF = "staff"


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    UNKNOWN = "unknown"


@dataclass
class CodeContext:
    """
    Represents the full user context detected from a code submission.
    This drives all downstream assistant decisions.
    """
    language: Language
    complexity_score: int          # 0-100: cyclomatic complexity proxy
    line_count: int
    has_functions: bool
    has_classes: bool
    has_imports: bool
    detected_frameworks: list[str]
    security_indicators: list[str] # patterns that suggest security review needed
    intensity: Intensity


# ── Language detection ────────────────────────────────────────────────────────

LANGUAGE_PATTERNS = {
    Language.PYTHON: [
        r"def\s+\w+\s*\(", r"import\s+\w+", r"from\s+\w+\s+import",
        r"class\s+\w+[\s\(:]", r"if\s+__name__\s*==\s*['\"]__main__['\"]"
    ],
    Language.TYPESCRIPT: [
        r":\s*(string|number|boolean|void|any|unknown)\b",
        r"interface\s+\w+", r"type\s+\w+\s*=", r"<\w+>"
    ],
    Language.JAVASCRIPT: [
        r"const\s+\w+\s*=", r"let\s+\w+\s*=", r"var\s+\w+\s*=",
        r"function\s+\w+\s*\(", r"=>\s*[{\w]", r"require\s*\("
    ],
    Language.GO: [
        r"func\s+\w+\s*\(", r"package\s+\w+", r"import\s+\(",
        r":=", r"fmt\."
    ],
}

SECURITY_PATTERNS = [
    (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password detected"),
    (r"api_key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key detected"),
    (r"secret\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret detected"),
    (r"SELECT.*\+.*\+", "Potential SQL injection via string concatenation"),
    (r"exec\s*\(", "Dynamic code execution — review carefully"),
    (r"eval\s*\(", "eval() usage — serious security risk"),
    (r"subprocess\.call\(['\"].*shell\s*=\s*True", "Shell injection risk"),
    (r"os\.system\s*\(", "OS command execution — injection risk"),
    (r"http://(?!localhost)", "Insecure HTTP endpoint (should be HTTPS)"),
]

FRAMEWORK_PATTERNS = {
    "react": [r"import React", r"from 'react'", r"from \"react\""],
    "fastapi": [r"from fastapi", r"@app\.(get|post|put|delete)"],
    "django": [r"from django", r"INSTALLED_APPS", r"urlpatterns"],
    "express": [r"require\('express'\)", r"app\.use\(", r"app\.listen\("],
    "nextjs": [r"from 'next/", r"getServerSideProps", r"getStaticProps"],
    "flask": [r"from flask import", r"@app\.route"],
    "sqlalchemy": [r"from sqlalchemy", r"Base\.metadata"],
}


def detect_language(code: str) -> Language:
    """
    Decision: What language is this code?
    Uses pattern matching — no user declaration required.
    TypeScript check runs before JavaScript (TS is a superset).
    """
    scores = {}
    for lang, patterns in LANGUAGE_PATTERNS.items():
        score = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        scores[lang] = score

    if scores.get(Language.TYPESCRIPT, 0) > 0:
        return Language.TYPESCRIPT

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else Language.UNKNOWN


def calculate_complexity_score(code: str) -> int:
    """
    Decision: How complex is this code?
    Proxy for cyclomatic complexity using structural pattern counts.
    Score 0-100. Drives analysis depth.
    """
    indicators = [
        r"\bif\b", r"\belif\b", r"\belse\b", r"\bfor\b", r"\bwhile\b",
        r"\btry\b", r"\bcatch\b", r"\bexcept\b", r"\bswitch\b", r"\bcase\b",
        r"&&", r"\|\|", r"\?", r"async\s+def", r"await\s",
    ]

    lines = code.count("\n") + 1
    branch_count = sum(
        len(re.findall(p, code, re.IGNORECASE)) for p in indicators
    )

    # Normalize: high branch count + high line count = high complexity
    line_factor = min(lines / 500, 1.0)
    branch_factor = min(branch_count / 50, 1.0)
    raw = (line_factor * 40) + (branch_factor * 60)

    return int(raw)


def detect_security_indicators(code: str) -> list[str]:
    """
    Decision: Does this code need extra security scrutiny?
    Returns list of specific security concerns found.
    """
    found = []
    for pattern, message in SECURITY_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            found.append(message)
    return found


def detect_frameworks(code: str) -> list[str]:
    """
    Decision: What frameworks is this code using?
    Used to apply framework-specific best practice rules.
    """
    found = []
    for framework, patterns in FRAMEWORK_PATTERNS.items():
        if any(re.search(p, code, re.IGNORECASE) for p in patterns):
            found.append(framework)
    return found


def build_code_context(code: str, intensity: str) -> CodeContext:
    """
    Master context builder. Assembles all detected signals into
    a CodeContext object that drives every downstream decision.
    This is the core of the smart assistant layer.
    """
    return CodeContext(
        language=detect_language(code),
        complexity_score=calculate_complexity_score(code),
        line_count=code.count("\n") + 1,
        has_functions=bool(re.search(r"\bdef\b|\bfunction\b|\bfunc\b", code)),
        has_classes=bool(re.search(r"\bclass\b", code)),
        has_imports=bool(re.search(r"\bimport\b|\brequire\b", code)),
        detected_frameworks=detect_frameworks(code),
        security_indicators=detect_security_indicators(code),
        intensity=Intensity(intensity),
    )


# ── Rule selection based on context ──────────────────────────────────────────

LANGUAGE_RULES = {
    Language.PYTHON: [
        "Check for missing type hints on all public functions and methods",
        "Verify context managers (with statements) used for file and resource handling",
        "Check for bare except clauses that swallow errors silently",
        "Verify f-strings used over .format() and % formatting",
        "Check for mutable default arguments in function signatures",
        "Verify __init__ methods don't do heavy work",
        "Check for proper use of dataclasses vs plain dicts",
    ],
    Language.JAVASCRIPT: [
        "Check for == vs === comparisons throughout",
        "Verify all async functions have try/catch error handling",
        "Check for var usage — should use const or let",
        "Identify potential null/undefined access without optional chaining",
        "Check for console.log statements that should not be in production",
        "Verify event listeners are properly cleaned up",
    ],
    Language.TYPESCRIPT: [
        "Check for 'any' type usage — every 'any' is a type safety hole",
        "Verify strict null checks are respected in all branches",
        "Check for missing return type annotations on exported functions",
        "Identify improper use of type assertions (as X) over type guards",
        "Verify interfaces used for object shapes, types for unions/intersections",
    ],
    Language.GO: [
        "Check that all errors are handled — no bare _ for error returns",
        "Verify goroutines have proper cancellation via context",
        "Check for proper defer usage for cleanup",
        "Verify interfaces are small and focused",
    ],
    Language.UNKNOWN: [
        "Check naming conventions are consistent and descriptive",
        "Verify error handling exists for all failure paths",
        "Check for hardcoded values that should be constants or configs",
        "Verify code is modular — functions do one thing",
    ],
}

INTENSITY_FOCUS = {
    Intensity.JUNIOR: {
        "tone": "direct but educational — explain WHY each issue matters",
        "focus": "common beginner mistakes, naming, basic structure, obvious security issues",
        "depth": "line-level issues with before/after examples",
    },
    Intensity.SENIOR: {
        "tone": "blunt and professional — no hand-holding",
        "focus": "architectural decisions, production risks, maintainability at team scale",
        "depth": "systemic patterns — not just individual lines",
    },
    Intensity.STAFF: {
        "tone": "merciless and precise — consequences of shipping this",
        "focus": "scalability, security posture, tech debt cost, team cognitive load",
        "depth": "full architectural critique with long-term risk assessment",
    },
}


def build_analysis_prompt(context: CodeContext, code: str) -> str:
    """
    Decision: What exact prompt does this code get?
    Constructs a context-specific analysis prompt — not a generic one.
    Every submission gets a different prompt based on detected context.
    """
    lang_rules = LANGUAGE_RULES.get(context.language, LANGUAGE_RULES[Language.UNKNOWN])
    intensity_config = INTENSITY_FOCUS[context.intensity]

    # Adapt rule depth to complexity
    if context.complexity_score > 70:
        active_rules = lang_rules
    elif context.complexity_score > 40:
        active_rules = lang_rules[:5]
    else:
        active_rules = lang_rules[:3]

    # Add security rules if indicators found
    security_section = ""
    if context.security_indicators:
        security_section = f"""
SECURITY ALERT — These specific issues were pre-detected in this submission:
{chr(10).join(f"  - {s}" for s in context.security_indicators)}
Address each one explicitly in the security section of your analysis.
"""

    framework_section = ""
    if context.detected_frameworks:
        framework_section = f"""
Detected frameworks: {', '.join(context.detected_frameworks)}
Apply framework-specific best practices in your analysis.
"""

    return f"""You are The Relentless Senior Engineer — a smart assistant that adapts 
its code review based on the specific context of each submission.

SUBMISSION CONTEXT (auto-detected):
- Language: {context.language.value}
- Complexity score: {context.complexity_score}/100
- Lines of code: {context.line_count}
- Has classes: {context.has_classes}
- Has functions: {context.has_functions}
{framework_section}
REVIEW MODE: {context.intensity.value.upper()}
Tone: {intensity_config['tone']}
Focus areas: {intensity_config['focus']}
Analysis depth: {intensity_config['depth']}

LANGUAGE-SPECIFIC RULES TO APPLY:
{chr(10).join(f"  {i+1}. {r}" for i, r in enumerate(active_rules))}
{security_section}
Analyze the following code and respond ONLY with this exact JSON structure.
No preamble. No explanation outside the JSON. Valid JSON only.

{{
  "roast": "string — brutal honest opening assessment (150-300 words, adapted to intensity mode)",
  "issues": [
    {{
      "type": "string (security|naming|structure|performance|testing|error_handling|style)",
      "line": "number or null",
      "description": "string — specific issue description",
      "severity": "critical|high|medium|low",
      "language_specific": "boolean — is this a {context.language.value}-specific issue"
    }}
  ],
  "fixPlan": [
    {{
      "issue": "string — the issue being fixed",
      "fix": "string — exact, actionable fix instruction",
      "code_example": "string or null — before/after code if applicable",
      "priority": "number — 1 is highest priority"
    }}
  ],
  "scores": {{
    "codeQuality": "number 0-100",
    "security": "number 0-100",
    "efficiency": "number 0-100",
    "testing": "number 0-100",
    "accessibility": "number 0-100"
  }},
  "context_summary": {{
    "language_detected": "{context.language.value}",
    "complexity": "{context.complexity_score}",
    "review_mode": "{context.intensity.value}",
    "frameworks": {context.detected_frameworks},
    "security_pre_detected": {len(context.security_indicators) > 0}
  }}
}}

CODE TO ANALYZE:
{code[:12000]}"""
