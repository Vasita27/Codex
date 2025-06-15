from llama_index.readers.github import GithubRepositoryReader
from llama_index.readers.github import GithubClient
import requests
from urllib.parse import urlparse
import base64

def parse_github_repo(repo_url):
    # Extract owner and repo name
    owner, repo = repo_url.strip('/').split('/')[-2:]

    # GitHub personal access token
    github_token = "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"
    github_client = GithubClient(github_token)

    reader = GithubRepositoryReader(
        github_client=github_client,
        owner=owner,
        repo=repo,
        filter_directories=(
            # Exclude common irrelevant folders
            [".vscode", "__pycache__", "node_modules", ".github", "dist", "build", "coverage"],
            GithubRepositoryReader.FilterType.EXCLUDE,
        ),
        filter_file_extensions=(
            # Exclude non-code files (keep only relevant ones)
            [".md", ".json", ".lock", ".log", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".svg"],
            GithubRepositoryReader.FilterType.EXCLUDE,
        ),
    )

    # Load repo contents
    docs = reader.load_data(branch="main")  # or "master" if that’s the default

    return docs

class GitHubParser:
    """
    Advanced parser for extracting metadata, file tree, and raw contents
    independently of llama_index.
    """
    def __init__(self, github_url):
        self.github_url = github_url
        self.owner, self.repo = self._parse_github_url(github_url)
        self.api_base = f"https://api.github.com/repos/{self.owner}/{self.repo}"

    def _parse_github_url(self, url):
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL")
        return path_parts[0], path_parts[1]

    def get_repo_data(self):
        repo_resp = requests.get(self.api_base)
        if repo_resp.status_code != 200:
            raise Exception(f"Could not fetch repo metadata: {repo_resp.text}")
        repo_json = repo_resp.json()

        branch = repo_json.get("default_branch", "main")
        tree_url = f"{self.api_base}/git/trees/{branch}?recursive=1"
        tree_resp = requests.get(tree_url)
        if tree_resp.status_code != 200:
            raise Exception(f"Could not fetch repo tree: {tree_resp.text}")
        tree_json = tree_resp.json()
        files = {}
        for item in tree_json.get("tree", []):
            if item["type"] == "blob":
                file_path = item["path"]
                content = ""
                if any(file_path.endswith(ext) for ext in [
                    ".js", ".py", ".json", ".md", ".txt", ".ts",
                    ".jsx", ".tsx", ".css", ".html", ".yml", ".yaml"
                ]):
                    file_url = f"{self.api_base}/contents/{file_path}"
                    file_resp = requests.get(file_url)
                    if file_resp.status_code == 200:
                        content_json = file_resp.json()
                        if content_json.get("encoding") == "base64":
                            try:
                                raw = base64.b64decode(content_json["content"])
                                content = raw.decode("utf-8")[:20000]
                            except Exception:
                                content = ""
                files[file_path] = {
                    "type": "file",
                    "content": content
                }
        return {
            "name": repo_json.get("name"),
            "description": repo_json.get("description"),
            "language": repo_json.get("language"),
            "stars": repo_json.get("stargazers_count"),
            "created_at": repo_json.get("created_at"),
            "files": files
        }

    def get_all_chunks(self, max_chunk_size=1000):
        """
        Returns a list of dicts:
        [{"text": ..., "file_path": ...}, ...]
        Splits files longer than max_chunk_size.
        """
        repo_data = self.get_repo_data()
        chunks = []
        for file_path, fdict in repo_data["files"].items():
            content = fdict["content"]
            if not content: continue
            # For markdown and small files, one chunk
            if file_path.endswith(('.md', '.txt', '.json', '.yml', '.yaml')):
                chunks.append({"text": content, "file_path": file_path})
            else:
                # Code: split by double-newline or max_chunk_size
                code_chunks = [c for c in content.split('\n\n') if c.strip()]
                for c in code_chunks:
                    if len(c) > max_chunk_size:
                        # further split
                        for i in range(0, len(c), max_chunk_size):
                            chunks.append({"text": c[i:i+max_chunk_size], "file_path": file_path})
                    else:
                        chunks.append({"text": c, "file_path": file_path})
        return chunks

    def get_file_list(self):
        repo_data = self.get_repo_data()
        return list(repo_data["files"].keys())

    def get_readme_content(self):
        repo_data = self.get_repo_data()
        for file_path, fdict in repo_data["files"].items():
            if file_path.lower().startswith("readme"):
                return fdict["content"]
        return ""
