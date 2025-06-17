import os
import sys
import time
from dotenv import load_dotenv
from github_parser import GitHubParser  # Make sure this is in the same directory or PYTHONPATH
import google.generativeai as genai

# Load .env variables (for GEMINI_API_KEY)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment or .env file.")

# Configure Gemini API for 1.5 Flash model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def gemini_flash_summarize(text, file_path):
    """
    Summarize a file using Gemini 1.5 Flash.
    Handles 429 (rate limit) errors by waiting and retrying.
    """
    prompt = (
        f"You are a helpful AI code assistant. Summarize the following file for a developer. "
        f"Explain what the file does, its main features, and any important implementation details. "
        f"File: {file_path}\n\n"
        f"--- FILE CONTENT START ---\n"
        f"{text[:12000]}\n"
        f"--- FILE CONTENT END ---"
    )
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            summary = response.text.strip()
            return summary
        except Exception as e:
            err_msg = str(e)
            if '429' in err_msg or "quota" in err_msg.lower() or "rate limit" in err_msg.lower():
                wait_time = 60
                print(f"Rate limit hit while summarizing {file_path}, waiting {wait_time} seconds before retrying... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
                continue
            print(f"Error summarizing {file_path}: {e}")
            return text[:300]
    print(f"Failed to summarize {file_path} after {max_retries} attempts due to rate limits.")
    return text[:300]

def summarize_repo_as_string(repo_url):
    """
    Summarize all files in a repo and return the summary as a string.
    Shows progress like [11/20] Summarizing: <filename> ...
    """
    parser = GitHubParser(repo_url)
    repo_data = parser.get_repo_data()
    files = repo_data['files']

    summaries = []
    total = len(files)
    for i, (file_path, info) in enumerate(files.items(), 1):
        content = info.get('content', '')
        if not content.strip():
            continue
        print(f"[{i}/{total}] Summarizing: {file_path} ...")
        summary = gemini_flash_summarize(content, file_path)
        summaries.append(f"## {file_path}\n\n{summary}\n\n---\n")

    output = "# File-to-File Summaries (Gemini 1.5 Flash)\n\n" + "\n".join(summaries)
    return output

def main(repo_url):
    output = summarize_repo_as_string(repo_url)
    out_name = "repo_file_summaries_flash.md"
    with open(out_name, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"\nDone! Summaries written to {out_name}")
