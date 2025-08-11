import os
import json
import subprocess
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

class DocumentationAgent:
    def __init__(self, model: str = None, project_path: str = None):
        self.model = model or os.environ.get('OLLAMA_MODEL', 'phind-codellama:34b-v2')
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.ollama_cli = shutil.which('ollama')
        self.ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        
    def _call_local_llm(self, prompt: str, max_tokens: int = 4096) -> str:
        """Call local LLM via Ollama for documentation generation"""
        enhanced_prompt = f"""
        You are an expert technical writer and software architect. Generate high-quality, comprehensive documentation.
        
        Requirements:
        - Use clear, professional language
        - Include practical examples where appropriate
        - Structure information logically
        - Use proper markdown formatting
        - Include code examples when relevant
        - Focus on being helpful and actionable
        
        {prompt}
        
        Provide only the documentation content, no explanations unless specifically requested.
        """
        
        # Try Ollama CLI first
        if self.ollama_cli:
            try:
                result = subprocess.run(
                    [self.ollama_cli, 'run', self.model, '--', enhanced_prompt],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except Exception as e:
                print(f"Ollama CLI failed: {e}")
        
        # Fallback to HTTP API
        try:
            import requests
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    'model': self.model,
                    'prompt': enhanced_prompt,
                    'stream': False
                },
                timeout=60
            )
            if response.ok:
                data = response.json()
                return data.get('response', '')
        except Exception as e:
            print(f"Ollama HTTP API failed: {e}")
        
        return ""

    def generate_readme(self, project_info: Dict[str, Any]) -> str:
        """Generate comprehensive README.md"""
        prompt = f"""
        Generate a professional README.md for this project:
        
        Project Information:
        {json.dumps(project_info, indent=2)}
        
        Include:
        - Project title and description
        - Features and capabilities
        - Installation instructions
        - Usage examples
        - API documentation (if applicable)
        - Contributing guidelines
        - License information
        - Badges and status indicators
        
        Use proper markdown formatting with headers, code blocks, and lists.
        """
        
        return self._call_local_llm(prompt)

    def generate_architecture_docs(self, project_structure: Dict[str, Any], code_files: List[str]) -> str:
        """Generate architecture documentation with Mermaid diagrams"""
        prompt = f"""
        Generate comprehensive architecture documentation for this project:
        
        Project Structure:
        {json.dumps(project_structure, indent=2)}
        
        Code Files:
        {json.dumps(code_files, indent=2)}
        
        Include:
        - System overview and high-level architecture
        - Component diagrams using Mermaid syntax
        - Data flow diagrams
        - Technology stack details
        - Design patterns used
        - Security considerations
        - Performance characteristics
        - Scalability aspects
        
        Use Mermaid diagrams for visual representation. Format as markdown.
        """
        
        return self._call_local_llm(prompt)

    def generate_api_docs(self, code_content: str, api_type: str = 'REST') -> str:
        """Generate API documentation from code"""
        prompt = f"""
        Generate {api_type} API documentation from this code:
        
        Code:
        {code_content}
        
        Include:
        - API endpoints and methods
        - Request/response schemas
        - Authentication requirements
        - Rate limiting information
        - Error codes and handling
        - Example requests and responses
        - SDK examples (if applicable)
        
        Format as markdown with proper code blocks and tables.
        """
        
        return self._call_local_llm(prompt)

    def generate_developer_guide(self, project_info: Dict[str, Any], setup_instructions: List[str]) -> str:
        """Generate comprehensive developer guide"""
        prompt = f"""
        Generate a developer guide for this project:
        
        Project Info:
        {json.dumps(project_info, indent=2)}
        
        Setup Instructions:
        {json.dumps(setup_instructions, indent=2)}
        
        Include:
        - Development environment setup
        - Code style guidelines
        - Testing procedures
        - Debugging tips
        - Common issues and solutions
        - Performance optimization
        - Security best practices
        - Deployment procedures
        
        Make it practical and actionable for developers.
        """
        
        return self._call_local_llm(prompt)

    def generate_runbook(self, project_info: Dict[str, Any], common_issues: List[str]) -> str:
        """Generate production runbook for incident handling"""
        prompt = f"""
        Generate a production runbook for this project:
        
        Project Info:
        {json.dumps(project_info, indent=2)}
        
        Common Issues:
        {json.dumps(common_issues, indent=2)}
        
        Include:
        - System architecture overview
        - Monitoring and alerting
        - Common incident scenarios
        - Troubleshooting procedures
        - Escalation procedures
        - Recovery procedures
        - Post-incident analysis
        - Preventive measures
        
        Focus on practical steps for on-call engineers.
        """
        
        return self._call_local_llm(prompt)

    def generate_changelog(self, version: str, changes: List[str], change_type: str = 'release') -> str:
        """Generate changelog entries"""
        prompt = f"""
        Generate a changelog entry for version {version} ({change_type}):
        
        Changes:
        {json.dumps(changes, indent=2)}
        
        Format as:
        - Version header with date
        - Categorized changes (Added, Changed, Fixed, Removed, etc.)
        - Breaking changes clearly marked
        - Migration notes if applicable
        - Contributors and acknowledgments
        
        Use proper markdown formatting and follow conventional changelog format.
        """
        
        return self._call_local_llm(prompt)

    def create_mermaid_diagram(self, diagram_type: str, description: str) -> str:
        """Generate Mermaid diagram code"""
        prompt = f"""
        Generate a Mermaid {diagram_type} diagram for:
        
        {description}
        
        Requirements:
        - Use proper Mermaid syntax
        - Make it clear and readable
        - Include appropriate styling
        - Use meaningful names and labels
        - Follow Mermaid best practices
        
        Return only the Mermaid code block, no explanations.
        """
        
        response = self._call_local_llm(prompt)
        
        # Ensure it's wrapped in mermaid code block
        if not response.startswith('```mermaid'):
            response = f"```mermaid\n{response}\n```"
        
        return response

    def update_documentation(self, existing_docs: str, changes: str) -> str:
        """Update existing documentation based on changes"""
        prompt = f"""
        Update this existing documentation based on the following changes:
        
        Existing Documentation:
        {existing_docs}
        
        Changes to Apply:
        {changes}
        
        Requirements:
        - Maintain existing structure and style
        - Update relevant sections
        - Add new sections if needed
        - Remove outdated information
        - Preserve formatting and links
        - Ensure consistency throughout
        
        Return the updated documentation.
        """
        
        return self._call_local_llm(prompt)

    def generate_project_package(self, docs_dir: str = 'docs') -> bool:
        """Package documentation for distribution"""
        try:
            docs_path = self.project_path / docs_dir
            
            # Create docs directory if it doesn't exist
            docs_path.mkdir(exist_ok=True)
            
            # Generate documentation files
            project_info = self._analyze_project()
            
            # README
            readme_content = self.generate_readme(project_info)
            (self.project_path / 'README.md').write_text(readme_content)
            
            # Architecture docs
            arch_content = self.generate_architecture_docs(project_info, [])
            (docs_path / 'ARCHITECTURE.md').write_text(arch_content)
            
            # Developer guide
            dev_guide = self.generate_developer_guide(project_info, [])
            (docs_path / 'DEVELOPER_GUIDE.md').write_text(dev_guide)
            
            # Runbook
            runbook = self.generate_runbook(project_info, [])
            (docs_path / 'RUNBOOK.md').write_text(runbook)
            
            # Create mkdocs.yml for HTML generation
            mkdocs_config = self._generate_mkdocs_config(project_info)
            (docs_path / 'mkdocs.yml').write_text(mkdocs_config)
            
            return True
            
        except Exception as e:
            print(f"Error generating documentation package: {e}")
            return False

    def _analyze_project(self) -> Dict[str, Any]:
        """Analyze project structure and extract information"""
        info = {
            'name': self.project_path.name,
            'type': 'unknown',
            'languages': [],
            'frameworks': [],
            'dependencies': []
        }
        
        # Check for common project files
        if (self.project_path / 'requirements.txt').exists():
            info['type'] = 'Python'
            info['languages'].append('Python')
            try:
                requirements = (self.project_path / 'requirements.txt').read_text()
                info['dependencies'] = [line.strip() for line in requirements.split('\n') 
                                      if line.strip() and not line.startswith('#')]
            except:
                pass
        
        if (self.project_path / 'package.json').exists():
            info['type'] = 'Node.js'
            info['languages'].append('JavaScript/TypeScript')
            try:
                import json
                package_data = json.loads((self.project_path / 'package.json').read_text())
                info['dependencies'] = list(package_data.get('dependencies', {}).keys())
                info['frameworks'] = [pkg for pkg in info['dependencies'] 
                                    if pkg in ['express', 'react', 'vue', 'angular', 'next']]
            except:
                pass
        
        if (self.project_path / 'Cargo.toml').exists():
            info['type'] = 'Rust'
            info['languages'].append('Rust')
        
        # Check source directories
        src_dirs = [d.name for d in self.project_path.iterdir() 
                   if d.is_dir() and d.name in ['src', 'app', 'lib', 'main']]
        info['source_directories'] = src_dirs
        
        return info

    def _generate_mkdocs_config(self, project_info: Dict[str, Any]) -> str:
        """Generate mkdocs.yml configuration"""
        return f"""site_name: {project_info['name']}
site_description: {project_info.get('description', 'Project Documentation')}
site_author: AI Coding Agency
repo_url: https://github.com/your-org/{project_info['name']}

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.highlight
    - search.share

nav:
  - Home: index.md
  - Architecture: ARCHITECTURE.md
  - Developer Guide: DEVELOPER_GUIDE.md
  - Runbook: RUNBOOK.md

plugins:
  - search
  - mermaid2

markdown_extensions:
  - mermaid2
  - pymdownx.superfences
  - pymdownx.highlight
  - pymdownx.snippets
  - pymdownx.arithmatex
  - admonition
  - codehilite
  - footnotes
  - meta
  - pymdownx.details
  - pymdownx.emoji
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.magiclink
  - pymdownx.mark
  - pymdownx.smartsymbols
  - pymdownx.snippets
  - pymdownx.superfences
  - pymdownx.tabbed
  - pymdownx.tasklist
  - pymdownx.tilde
  - toc:
      permalink: true
"""
