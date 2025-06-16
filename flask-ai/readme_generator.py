import os
from dotenv import load_dotenv
load_dotenv()
import json
import re
from typing import Dict, List, Any
import google.generativeai as genai

class ReadmeGenerator:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        print("Loaded GEMINI_API_KEY:", api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_readme(self, github_url) -> str:
        from github_parser import GitHubParser
        parser = GitHubParser(github_url)
        repo_data = parser.get_repo_data()
        return self.generate_readme_content(repo_data)

    def analyze_repo_structure(self, repo_data: Dict) -> Dict[str, Any]:
        files = repo_data.get('files', {})
        categorized = {
            'config_files': [],
            'main_files': [],
            'frontend_files': [],
            'backend_files': [],
            'test_files': [],
            'documentation': [],
            'assets': []
        }
        patterns = {
            'config_files': [
                r'package\.json$', r'requirements\.txt$', r'Dockerfile$',
                r'docker-compose\.yml$', r'\.env$', r'config\.(js|json|py)$',
                r'vite\.config\.js$', r'eslint\.config\.js$'
            ],
            'main_files': [
                r'main\.(py|js|ts)$', r'app\.(py|js|ts)$', r'index\.(py|js|ts|html)$',
                r'server\.(py|js|ts)$'
            ],
            'frontend_files': [
                r'\.(jsx?|tsx?|vue|svelte)$', r'\.(css|scss|sass|less)$',
                r'\.(html|htm)$'
            ],
            'backend_files': [
                r'\.(py|java|php|rb|go|rs)$', r'routes/.*\.(js|ts|py)$',
                r'models/.*\.(js|ts|py)$', r'controllers/.*\.(js|ts|py)$'
            ],
            'test_files': [
                r'test.*\.(py|js|ts)$', r'.*test\.(py|js|ts)$',
                r'spec/.*\.(py|js|ts)$', r'.*spec\.(py|js|ts)$'
            ],
            'documentation': [
                r'README\.md$', r'CHANGELOG\.md$', r'CONTRIBUTING\.md$',
                r'LICENSE$', r'\.md$'
            ],
            'assets': [
                r'\.(png|jpg|jpeg|gif|svg|ico)$', r'\.(pdf|doc|docx)$'
            ]
        }
        for file_path, file_info in files.items():
            if file_info.get('type') == 'file':
                for category, category_patterns in patterns.items():
                    if any(re.search(pattern, file_path, re.IGNORECASE) for pattern in category_patterns):
                        categorized[category].append(file_path)
                        break
        return categorized

    def extract_dependencies(self, files: Dict) -> Dict[str, List[str]]:
        dependencies = {'npm': [], 'pip': [], 'other': []}
        package_json_files = [f for f in files.keys() if f.endswith('package.json')]
        for file_path in package_json_files:
            try:
                content = files[file_path].get('content', '')
                if content:
                    package_data = json.loads(content)
                    deps = package_data.get('dependencies', {})
                    dev_deps = package_data.get('devDependencies', {})
                    dependencies['npm'].extend(list(deps.keys()) + list(dev_deps.keys()))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        req_files = [f for f in files.keys() if f.endswith('requirements.txt')]
        for file_path in req_files:
            try:
                content = files[file_path].get('content', '')
                if content:
                    deps = [line.split('==')[0].split('>=')[0].split('<=')[0]
                           for line in content.split('\n') if line.strip() and not line.startswith('#')]
                    dependencies['pip'].extend(deps)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        return dependencies

    def generate_readme_content(self, repo_data: Dict) -> str:
        categorized_files = self.analyze_repo_structure(repo_data)
        dependencies = self.extract_dependencies(repo_data['files'])
        context = {
            'repo_name': repo_data.get('name', 'Unknown'),
            'description': repo_data.get('description', ''),
            'language': repo_data.get('language', 'Multiple'),
            'file_structure': categorized_files,
            'dependencies': dependencies,
            'file_count': len(repo_data.get('files', {})),
            'key_files': self._get_key_file_contents(repo_data['files'], categorized_files)
        }
        prompt = self._create_readme_prompt(context)
        try:
            response = self.model.generate_content(prompt)
            print("Gemini AI response (first 500 chars):", response.text[:500])
            return response.text
        except Exception as e:
            print("Gemini AI error:", e)
            return self._generate_fallback_readme(context)

    def _get_key_file_contents(self, files: Dict, categorized: Dict) -> Dict:
        key_contents = {}
        for file_path in categorized['main_files'][:3]:
            if file_path in files:
                content = files[file_path].get('content', '')
                if len(content) < 5000:
                    key_contents[file_path] = content[:2000]
        for file_path in categorized['config_files'][:2]:
            if file_path in files:
                content = files[file_path].get('content', '')
                if len(content) < 2000:
                    key_contents[file_path] = content
        return key_contents

    def _create_readme_prompt(self, context: Dict) -> str:
        file_structure = "\n".join([
            f"**{category.replace('_', ' ').title()}:** {', '.join(files[:5])}" +
            (f" (+{len(files)-5} more)" if len(files) > 5 else "")
            for category, files in context['file_structure'].items() if files
        ])
        dependencies_info = "\n".join([
            f"**{dep_type.upper()}:** {', '.join(deps[:10])}" +
            (f" (+{len(deps)-10} more)" if len(deps) > 10 else "")
            for dep_type, deps in context['dependencies'].items() if deps
        ])
        key_files_info = "\n".join([
            f"**{file_path}:**\n```\n{content[:500]}...\n```"
            for file_path, content in context['key_files'].items()
        ])
        prompt = f"""
Generate a comprehensive and professional README.md for a GitHub repository with the following information:

**File Structure:**
{file_structure}

**Dependencies:**
{dependencies_info}

**Key File Contents:**
{key_files_info}

Please generate a README.md that includes:
1. A compelling project title and description
2. Features list based on the code analysis
3. Installation instructions based on the dependencies
4. Usage examples
5. Project structure explanation
6. Technology stack
7. Contributing guidelines
8. License information

Make it professional, engaging, and developer-friendly. Use proper markdown formatting with emojis, badges, and clear sections. Infer the project's purpose and functionality from the code structure and dependencies.
"""
        return prompt
    
    def _generate_fallback_readme(self, context: Dict) -> str:
        """Generate a basic README if AI fails"""
        
        # Determine project type based on files
        project_type = "Application"
        if any('react' in dep.lower() for deps in context['dependencies'].values() for dep in deps):
            project_type = "React Application"
        elif any('flask' in dep.lower() for deps in context['dependencies'].values() for dep in deps):
            project_type = "Flask Application"
        elif any('express' in dep.lower() for deps in context['dependencies'].values() for dep in deps):
            project_type = "Express.js Application"
        
        readme_content = f"""# {context['repo_name']}

## 📝 Description
{context['description'] or f"A {project_type} built with {context['language']}"}

## 🚀 Features
- Modern {context['language']} application
- Well-structured codebase with {context['file_count']} files
- Professional development setup

## 🛠️ Installation

### Prerequisites
- Node.js (if using npm dependencies)
- Python (if using pip dependencies)

### Setup
1. Clone the repository
```bash
git clone <repository-url>
cd {context['repo_name']}
```

2. Install dependencies
"""
        
        if context['dependencies']['npm']:
            readme_content += """
```bash
npm install
```
"""
        
        if context['dependencies']['pip']:
            readme_content += """
```bash
pip install -r requirements.txt
```
"""
        
        readme_content += """
## 📁 Project Structure
```
"""
        
        for category, files in context['file_structure'].items():
            if files:
                readme_content += f"{category.replace('_', ' ').title()}: {len(files)} files\n"
        
        readme_content += """```

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License.
"""
        
        return readme_content
