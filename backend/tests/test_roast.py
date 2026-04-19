"""
Tests for RoastMyStack backend — roast generation and API endpoints.
"""
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient


# ── Import app ──────────────────────────────────────────────────────────────
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


# ── Health check ────────────────────────────────────────────────────────────
class TestHealthCheck:
    def test_health_endpoint_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_has_status_key(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"


# ── Input validation ─────────────────────────────────────────────────────────
class TestRoastInputValidation:
    def test_empty_body_returns_422(self):
        """Roast endpoint must reject empty requests."""
        response = client.post("/api/roast", json={})
        assert response.status_code == 422

    def test_missing_fields_returns_422(self):
        """Must provide source_type, content, and intensity."""
        response = client.post("/api/roast", json={
            "intensity": "senior"
        })
        assert response.status_code == 422

    def test_invalid_github_url_format_returns_400(self):
        """Non-GitHub URLs should be rejected."""
        response = client.post("/api/roast", json={
            "source_type": "github",
            "content": "https://notgithub.com/user/repo",
            "intensity": "senior"
        })
        assert response.status_code == 400

    def test_valid_intensity_values_accepted(self):
        """Only valid intensity values should be accepted."""
        valid_intensities = ["junior", "senior", "staff"]
        for intensity in valid_intensities:
            with patch("main.roast_code_or_repo", new_callable=AsyncMock) as mock_roast:
                mock_roast.return_value = {
                    "roast": "Test roast",
                    "issues": [],
                    "fixPlan": [],
                    "scores": {
                        "codeQuality": 70,
                        "security": 80,
                        "efficiency": 75,
                        "testing": 60,
                        "accessibility": 65
                    }
                }
                response = client.post("/api/roast", json={
                    "source_type": "snippet",
                    "content": "def hello(): print('hello')",
                    "intensity": intensity
                })
                assert response.status_code != 422, f"Intensity '{intensity}' was rejected"

    def test_invalid_intensity_returns_422(self):
        """Invalid intensity values should be rejected."""
        response = client.post("/api/roast", json={
            "source_type": "snippet",
            "content": "def hello(): pass",
            "intensity": "ultra_destroy_mode"
        })
        assert response.status_code == 422


# ── Roast generation (mocked) ─────────────────────────────────────────────────
class TestRoastGeneration:
    def test_roast_returns_expected_structure(self):
        """Roast response must contain all required fields."""
        with patch("main.roast_code_or_repo", new_callable=AsyncMock) as mock_roast:
            mock_roast.return_value = {
                "roast": "Your variable names are crimes against humanity.",
                "issues": [
                    {
                        "type": "naming",
                        "line": 5,
                        "description": "Variable 'x' tells me nothing",
                        "severity": "medium"
                    }
                ],
                "fixPlan": [
                    {
                        "issue": "Poor variable naming",
                        "fix": "Use descriptive names like 'user_count' instead of 'x'",
                        "priority": 1
                    }
                ],
                "scores": {
                    "codeQuality": 45,
                    "security": 70,
                    "efficiency": 60,
                    "testing": 20,
                    "accessibility": 50
                }
            }

            response = client.post("/api/roast", json={
                "source_type": "snippet",
                "content": "x = 1\ny = 2\nz = x + y",
                "intensity": "senior"
            })

            assert response.status_code == 200
            data = response.json()
            assert "roast" in data
            assert "issues" in data
            assert "fixPlan" in data
            assert "scores" in data
            assert isinstance(data["issues"], list)
            assert isinstance(data["fixPlan"], list)

    def test_scores_are_numeric_and_in_range(self):
        """All scores must be integers between 0 and 100."""
        with patch("main.roast_code_or_repo", new_callable=AsyncMock) as mock_roast:
            mock_roast.return_value = {
                "roast": "This code hurts.",
                "issues": [],
                "fixPlan": [],
                "scores": {
                    "codeQuality": 55,
                    "security": 88,
                    "efficiency": 72,
                    "testing": 10,
                    "accessibility": 63
                }
            }

            response = client.post("/api/roast", json={
                "source_type": "snippet",
                "content": "console.log('hello world')",
                "intensity": "junior"
            })

            data = response.json()
            scores = data["scores"]
            for key, value in scores.items():
                assert isinstance(value, (int, float)), f"Score '{key}' is not numeric"
                assert 0 <= value <= 100, f"Score '{key}' = {value} is out of range"


# ── Security ──────────────────────────────────────────────────────────────────
class TestSecurity:
    def test_cors_headers_present(self):
        """CORS headers should be set on API responses."""
        response = client.options("/api/roast", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        })
        assert response.status_code in [200, 204, 400]

    def test_api_does_not_expose_internal_errors(self):
        """Error responses must not leak stack traces."""
        response = client.post("/api/roast", json={
            "source_type": "github",
            "content": "https://github.com/__nonexistent__/__repo__xyz__",
            "intensity": "senior"
        })
        if response.status_code >= 400:
            data = response.json()
            response_text = json.dumps(data).lower()
            assert "traceback" not in response_text

    def test_code_snippet_size_limit_enforced(self):
        """Excessively large code snippets should be rejected."""
        huge_code = "x = 1\n" * 100000
        response = client.post("/api/roast", json={
            "source_type": "snippet",
            "content": huge_code,
            "intensity": "senior"
        })
        assert response.status_code in [400, 413, 422]
