"""
Tests for the Context Engine — the smart assistant decision-making layer.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context_engine import (
    detect_language, calculate_complexity_score,
    detect_security_indicators, detect_frameworks,
    build_code_context, build_analysis_prompt,
    Language, Intensity
)


class TestLanguageDetection:
    def test_detects_python(self):
        code = "def hello(name: str) -> None:\n    print(f'Hello {name}')"
        assert detect_language(code) == Language.PYTHON

    def test_detects_typescript_over_javascript(self):
        code = "const greet = (name: string): void => { console.log(name) }"
        assert detect_language(code) == Language.TYPESCRIPT

    def test_detects_javascript(self):
        code = "const x = require('express')\napp.get('/', (req, res) => res.send('hi'))"
        assert detect_language(code) == Language.JAVASCRIPT

    def test_unknown_returns_unknown(self):
        code = "hello world this is not code"
        result = detect_language(code)
        assert result == Language.UNKNOWN


class TestComplexityScoring:
    def test_simple_code_scores_low(self):
        code = "x = 1\ny = 2\nprint(x + y)"
        score = calculate_complexity_score(code)
        assert score < 40

    def test_branchy_code_scores_higher(self):
        code = "\n".join([
            "if x:", "    if y:", "        for i in range(10):",
            "            try:", "                if a and b:",
            "                    while c:", "                        pass",
            "            except Exception:", "                pass"
        ] * 5)
        score = calculate_complexity_score(code)
        assert score > 40


class TestSecurityDetection:
    def test_detects_hardcoded_password(self):
        code = "password = 'supersecret123'"
        issues = detect_security_indicators(code)
        assert any("password" in i.lower() for i in issues)

    def test_detects_eval_usage(self):
        code = "result = eval(user_input)"
        issues = detect_security_indicators(code)
        assert any("eval" in i.lower() for i in issues)

    def test_clean_code_has_no_issues(self):
        code = "def add(a: int, b: int) -> int:\n    return a + b"
        issues = detect_security_indicators(code)
        assert len(issues) == 0


class TestContextBuilding:
    def test_builds_context_for_python_senior(self):
        code = "def process(data):\n    for item in data:\n        if item: print(item)"
        ctx = build_code_context(code, "senior")
        assert ctx.language == Language.PYTHON
        assert ctx.intensity == Intensity.SENIOR
        assert ctx.has_functions is True

    def test_complexity_score_in_range(self):
        code = "x = 1"
        ctx = build_code_context(code, "junior")
        assert 0 <= ctx.complexity_score <= 100


class TestPromptBuilding:
    def test_prompt_contains_language(self):
        code = "def hello(): pass"
        ctx = build_code_context(code, "senior")
        prompt = build_analysis_prompt(ctx, code)
        assert "python" in prompt.lower()

    def test_prompt_contains_intensity(self):
        code = "const x = 1"
        ctx = build_code_context(code, "staff")
        prompt = build_analysis_prompt(ctx, code)
        assert "staff" in prompt.lower()

    def test_prompt_includes_security_alert_when_needed(self):
        code = "password = 'hardcoded123'\nresult = eval(user_input)"
        ctx = build_code_context(code, "senior")
        prompt = build_analysis_prompt(ctx, code)
        assert "SECURITY ALERT" in prompt

    def test_prompt_does_not_include_security_alert_for_clean_code(self):
        code = "def add(a: int, b: int) -> int:\n    return a + b"
        ctx = build_code_context(code, "junior")
        prompt = build_analysis_prompt(ctx, code)
        assert "SECURITY ALERT" not in prompt
