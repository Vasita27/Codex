from flask import Flask, request, jsonify
from flask_cors import CORS
from github_parser import parse_github_repo
from embedding_store import embed_and_search
from readme_generator import ReadmeGenerator
import os

app = Flask(__name__)
CORS(app)
readme_gen = ReadmeGenerator()

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    repo_url = data['repoUrl']
    question = data['question']

    chunks = parse_github_repo(repo_url)
    
    answer = embed_and_search(chunks, question)
    

    return jsonify({"answer": answer})

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

if __name__ == '__main__':
    app.run(port=5001)