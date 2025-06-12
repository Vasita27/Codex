import requests

def parse_github_repo(url):
    owner, repo = url.strip('/').split('/')[-2:]
    api = f"https://api.github.com/repos/{owner}/{repo}/contents"
    chunks = []

    def fetch(url):
        res = requests.get(url).json()
        
        for item in res:
            if item['type'] == 'file' and item['name'].endswith(('.py', '.js')):
                content = requests.get(item['download_url']).text
                chunks.extend(content.split('\n\n'))  # naive chunking
            elif item['type'] == 'dir':
                fetch(item['url'])

    fetch(api)
    return chunks
