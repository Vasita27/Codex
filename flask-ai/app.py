from flask import Flask, request, jsonify
from flask_cors import CORS
from github_parser import parse_github_repo, get_github_branches
from embedding_store import embed_and_search
from readme_generator import ReadmeGenerator
import os
import logging
from urllib.parse import urlparse
import io
from flask import send_file
from file_summarizer import summarize_repo_as_string



try:
    from dotenv import load_dotenv
    load_dotenv('../server/.env')
except ImportError:
    pass  # dotenv is optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
readme_gen = ReadmeGenerator()
CORS(app)  # Enable CORS for all routes

# Add request logging
@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.path} - Body: {request.get_json(silent=True) or {}}")

@app.route('/api/branches', methods=['POST'])
def get_branches():
    try:
        data = request.get_json()
        if not data or 'repoUrl' not in data:
            return jsonify({"error": "Missing required field: repoUrl"}), 400
        
        repo_url = data['repoUrl']
        logger.info(f"Fetching branches for repo: {repo_url}")
        
        # Validate GitHub URL
        try:
            parsed_url = urlparse(repo_url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                return jsonify({"error": "Invalid repository URL"}), 400
                
            if 'github.com' not in parsed_url.netloc:
                return jsonify({"error": "Only GitHub repositories are supported"}), 400
        except Exception as e:
            return jsonify({"error": f"Invalid repository URL: {str(e)}"}), 400
        
        branches = get_github_branches(repo_url)
        if not branches:
            return jsonify({"error": "No branches found or error fetching branches"}), 404
            
        return jsonify({"branches": branches})
        
    except Exception as e:
        logger.error(f"Error fetching branches: {str(e)}")
        return jsonify({"error": f"Failed to fetch branches: {str(e)}"}), 500

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        if not data or 'repoUrl' not in data or 'question' not in data or 'branch' not in data:
            return jsonify({"error": "Missing required fields: repoUrl, question, and branch are required"}), 400
        
        repo_url = data['repoUrl']
        question = data['question']
        branch = data.get('branch', 'main')
        
        logger.info(f"Processing request for repo: {repo_url}, branch: {branch}, question: {question}")
        
        # Parse the GitHub repository
        logger.info("Parsing GitHub repository...")
        chunks = parse_github_repo(repo_url, branch)
        
        if not chunks:
            return jsonify({"error": "No code chunks found in the repository"}), 404
        
        # Get the answer
        logger.info("Generating answer...")
        answer = embed_and_search(chunks, question)
        
        return jsonify({"answer": answer})
        
    except Exception as e:
        logger.error(f"Error in /ask endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Service is running"})

@app.route('/api/readme-gen/generate', methods=['POST'])
def generate_readme():
    try:
        data = request.json
        github_url = data.get('githubUrl')
        
        if not github_url:
            return jsonify({
                "success": False,
                "error": "GitHub URL is required"
            }), 400
        
        # Generate README using the ReadmeGenerator
        readme_content = readme_gen.generate_readme(github_url)
        
        if readme_content.startswith("Error generating README:"):
            return jsonify({
                "success": False,
                "error": readme_content
            }), 500
        
        return jsonify({
            "success": True,
            "data": {
                "readme_content": readme_content
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500
@app.route('/api/file-summary/generate', methods=['POST'])
def generate_file_summary():
    try:
        data = request.json
        github_url = data.get('githubUrl')

        if not github_url:
            return jsonify({
                "success": False,
                "error": "GitHub URL is required"
            }), 400

        summary_content = summarize_repo_as_string(github_url)

        if not summary_content:
            return jsonify({
                "success": False,
                "error": "No summary was generated."
            }), 500

        return jsonify({
            "success": True,
            "data": {
                "summary_content": summary_content
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


if __name__ == '__main__':
    app.run(port=5001)
    # Check for required environment variables
    required_vars = ['GITHUB_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    # Install required packages if not already installed
    try:
        from github import Github as PyGithub
    except ImportError:
        print("Installing PyGithub...")
        import subprocess
        subprocess.check_call(["pip", "install", "PyGithub"])
        print("PyGithub installed successfully")
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        exit(1)
    
    logger.info("Starting Flask server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
