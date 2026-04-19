# Challenge Vertical: Developer Tools

## Selected Persona

**The Relentless Senior Engineer** — A smart, dynamic AI assistant that acts as
an always-available senior software engineer. It adapts its feedback style,
depth of analysis, and communication tone based on user context: the programming
language detected, the complexity of the submitted code, the experience level
selected by the user, and patterns found in the code itself.

## Problem Statement

Junior and mid-level developers lack access to consistent, honest, senior-level
code review. The feedback gap between what developers write and what production
code looks like is wide — and expensive. This assistant bridges that gap.

## How the Assistant Demonstrates Logical Decision Making

The assistant does not apply a single static analysis. It makes contextual
decisions at every step:

### Decision 1 — Input Type Detection
When a user submits input, the assistant first decides:
- Is this a GitHub URL or raw code?
- If GitHub URL: is it a single file or full repository?
- What language is this? (auto-detected, not user-declared)
- How large is the codebase? (determines analysis depth)

### Decision 2 — Experience Level Adaptation
Based on the user-selected intensity AND detected code complexity, the assistant
recalibrates:
- Junior mode: explains WHY each issue is a problem, uses analogies
- Senior mode: assumes context, focuses on architectural issues
- Staff mode: focuses on systemic patterns, scalability, maintainability at scale
The assistant does NOT simply change the tone — it changes WHAT it looks for.

### Decision 3 — Language-Specific Rule Application
The assistant applies language-appropriate heuristics:
- Python: checks for type hints, PEP 8, context managers, generator usage
- JavaScript/TypeScript: checks for async/await patterns, null safety, bundle impact
- Any language: checks security, naming, structure, test coverage signals

### Decision 4 — Severity-Based Fix Prioritization
The assistant ranks issues by real-world impact, not just code style:
- Critical: security vulnerabilities, data exposure, auth bypass risks
- High: crashes, race conditions, missing error handling
- Medium: performance bottlenecks, code smell, maintainability
- Low: style, naming, formatting

### Decision 5 — Adaptive Fix Plan Generation
The fix plan is not generic advice. It is generated from the specific issues
found in the specific code submitted, with concrete before/after examples
where the code is known.

## Vertical Alignment Statement

This solution is purpose-built for the Developer Tools vertical. It solves a
real, documented problem in the software development lifecycle — the absence
of accessible, on-demand, expert-level code review. The assistant is dynamic
because its analysis, tone, depth, and output adapt entirely to the context
of each submission. No two roasts are identical because no two codebases are.
