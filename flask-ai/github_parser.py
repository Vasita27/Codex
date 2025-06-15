import os
from llama_index.readers.github import GithubRepositoryReader
from llama_index.readers.github import GithubClient
from github import Github as PyGithub
from typing import List, Dict, Any

def get_github_branches(repo_url: str) -> List[Dict[str, str]]:
    """Fetch all branches for a GitHub repository."""
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        g = PyGithub(github_token)
        
        # Extract owner and repo name from URL
        parts = repo_url.strip('/').split('/')
        owner = parts[-2]
        repo_name = parts[-1]
        
        # Get the repository
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        # Get all branches
        branches = []
        for branch in repo.get_branches():
            branches.append({
                'name': branch.name,
                'commit_sha': branch.commit.sha[:7],
                'protected': branch.protected
            })
            
        return branches
    except Exception as e:
        print(f"Error fetching branches: {str(e)}")
        return []

def parse_github_repo(repo_url: str, branch: str = "main") -> Any:
    """Parse a GitHub repository from the given URL and branch."""
    try:
        # Extract owner and repo name
        parts = repo_url.strip('/').split('/')
        owner = parts[-2]
        repo = parts[-1]

        # GitHub personal access token
        github_token = os.getenv("GITHUB_TOKEN")
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

        # Load repo contents from the specified branch
        print(f"Loading repository data from branch: {branch}")
        docs = reader.load_data(branch=branch)
        return docs
    except Exception as e:
        print(f"Error parsing repository: {str(e)}")
        raise
