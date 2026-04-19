import os
import pytest

@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """
    Ensure tests never hit real external APIs.
    Sets TESTING=true so the app knows it's in test mode.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real")
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("FIREBASE_SERVICE_ACCOUNT_JSON", "{}")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
