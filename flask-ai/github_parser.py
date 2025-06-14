from llama_index.readers.github import GithubRepositoryReader
from llama_index.readers.github import GithubClient

def parse_github_repo(repo_url):
    # Extract owner and repo name
    owner, repo = repo_url.strip('/').split('/')[-2:]

    # GitHub personal access token
    github_token = ""
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
    docs = reader.load_data(branch="master")  # or "master" if that’s the default

    return docs
