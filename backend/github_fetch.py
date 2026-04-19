import os
import httpx
import asyncio
from urllib.parse import urlparse

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Valid code file extensions for analysis
VALID_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html",
    ".css", ".java", ".go", ".rs", ".cpp", ".c",
    ".rb", ".json", ".md"
}

# Paths to skip when scanning repositories
SKIP_PATTERNS = [
    "node_modules/", ".git/", "venv/", ".venv/",
    "__pycache__/", "dist/", "build/", ".next/"
]

# Binary / non-code file extensions to exclude
NON_CODE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot",
    ".mp4", ".mp3", ".wav", ".avi",
    ".zip", ".tar", ".gz", ".rar",
    ".pdf", ".doc", ".docx",
    ".sqlite", ".db", ".pkl", ".bin", ".exe", ".dll",
    ".pyc", ".pyo", ".so", ".o"
}


def parse_github_url(url: str) -> tuple[str, str]:
    """
    Parse a GitHub URL and return (owner, repo).
    Raises ValueError for non-GitHub or malformed URLs.
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")

    url = url.strip().rstrip("/")

    from urllib.parse import urlparse
    import re
    
    parsed = urlparse(url)
    if parsed.netloc != "github.com" and not parsed.netloc.endswith(".github.com"):
        raise ValueError(f"Invalid GitHub URL: {url}. Must be a github.com URL.")
    
    path = parsed.path.strip("/")
    parts = path.split("/")

    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Invalid GitHub URL: {url}. Must be in format https://github.com/owner/repo")

    owner = parts[0]
    repo = parts[1]

    return owner, repo


def is_code_file(filename: str) -> bool:
    """Check if a file is a source code file based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in NON_CODE_EXTENSIONS:
        return False
    if ext in VALID_EXTENSIONS:
        return True
    return False


def should_skip_path(path: str) -> bool:
    """Check if a file path should be skipped during repo scanning."""
    for pattern in SKIP_PATTERNS:
        if pattern in path:
            return True
    return False

async def fetch_github_repo(repo_url: str) -> str:
    """
    Fetches the content of a GitHub repository given its URL.
    Returns a concatenated string of the contents of relevant files.
    """
    parsed = urlparse(repo_url)
    if parsed.netloc != "github.com" and not parsed.netloc.endswith(".github.com"):
        raise ValueError("Invalid GitHub URL. Must be from github.com")
    
    path_parts = parsed.path.strip('/').split('/')
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub URL. Must contain owner and repo.")
    
    owner = path_parts[-2]
    repo = path_parts[-1]
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN and GITHUB_TOKEN != "Skip":
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    async with httpx.AsyncClient() as client:
        # First get the default branch
        repo_info_url = f"https://api.github.com/repos/{owner}/{repo}"
        repo_response = await client.get(repo_info_url, headers=headers)
        if repo_response.status_code != 200:
            raise ValueError(f"Failed to fetch repository information: {repo_response.text}")
        
        repo_data = repo_response.json()
        default_branch = repo_data.get("default_branch", "main")

        # Get the tree recursively
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        tree_response = await client.get(tree_url, headers=headers)
        if tree_response.status_code != 200:
            raise ValueError(f"Failed to fetch repository tree: {tree_response.text}")
        
        tree_data = tree_response.json()
        
        file_contents = []
        valid_extensions = {
            ".py", ".js", ".jsx", ".ts", ".tsx", ".html", 
            ".css", ".java", ".go", ".rs", ".cpp", ".c", 
            ".rb", ".json", ".md"
        }
        
        # Filter files
        files_to_fetch = []
        for item in tree_data.get("tree", []):
            if item["type"] == "blob":
                path = item["path"]
                ext = os.path.splitext(path)[1].lower()
                # Exclude package-lock.json and other large generated files
                if ext in valid_extensions and "package-lock" not in path and "yarn.lock" not in path and "node_modules" not in path:
                    files_to_fetch.append(item)
                    
        # To avoid being rate limited heavily, let's limit the number of files we process for roasting
        # We can sort by size or just take the first N relevant files
        files_to_fetch = files_to_fetch[:40] 

        # Fetch contents
        async def fetch_file(item):
            file_url = item["url"] # gives base64 encoded content
            resp = await client.get(file_url, headers=headers)
            if resp.status_code == 200:
                import base64
                data = resp.json()
                try:
                    content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                    return f"--- FILE: {item['path']} ---\n{content}\n"
                except Exception:
                    return ""
            return ""

        results = await asyncio.gather(*(fetch_file(item) for item in files_to_fetch))
        
        final_code = "\n".join(filter(None, results))
        
        # Limit to 100k characters for Gemini context (Gemini 2.5 Pro can handle much more, up to 2M tokens, but we keep it reasonable)
        if len(final_code) > 200000:
            final_code = final_code[:200000] + "\n... [TRUNCATED] ..."

        return final_code

fetch_github_code = fetch_github_repo
