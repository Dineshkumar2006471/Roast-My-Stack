"""
Tests for GitHub repository fetching utilities.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGitHubURLParsing:
    def test_standard_repo_url(self):
        from github_fetch import parse_github_url
        owner, repo = parse_github_url("https://github.com/user/my-project")
        assert owner == "user"
        assert repo == "my-project"

    def test_repo_with_dots_in_name(self):
        from github_fetch import parse_github_url
        owner, repo = parse_github_url("https://github.com/vercel/next.js")
        assert repo == "next.js"

    def test_non_github_domain_rejected(self):
        from github_fetch import parse_github_url
        with pytest.raises(ValueError):
            parse_github_url("https://bitbucket.org/user/repo")


class TestCodeFiltering:
    def test_filters_non_code_files(self):
        from github_fetch import is_code_file
        assert is_code_file("main.py") is True
        assert is_code_file("index.ts") is True
        assert is_code_file("styles.css") is True
        assert is_code_file("logo.png") is False
        assert is_code_file("data.sqlite") is False
        assert is_code_file("model.pkl") is False

    def test_filters_node_modules_paths(self):
        from github_fetch import should_skip_path
        assert should_skip_path("node_modules/express/index.js") is True
        assert should_skip_path("src/components/Button.tsx") is False
        assert should_skip_path(".git/config") is True
        assert should_skip_path("venv/lib/python3.12/site.py") is True
