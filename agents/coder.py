import os
import subprocess
import shutil
import requests
import json
import tempfile
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

OLLAMA_CLI = shutil.which('ollama')
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
OPENROUTER_KEY = os.environ.get('OPENROUTER_API_KEY', '')
GROQ_KEY = os.environ.get('GROQ_API_KEY', '')
FIREWORKS_KEY = os.environ.get('FIREWORKS_API_KEY', '')

class CoderAgent:
    def __init__(self, model: str = None, project_path: str = None):
        self.model = model or os.environ.get('OLLAMA_MODEL', 'phind-codellama:34b-v2')
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.ollama_cli = shutil.which('ollama')
        self.ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        
        # MCP-style tool access
        self.available_tools = self._discover_tools()
        
    def _discover_tools(self) -> Dict[str, Any]:
        """Discover available development tools and capabilities"""
        tools = {
            'file_system': {
                'read_file': self._read_file,
                'write_file': self._write_file,
                'list_directory': self._list_directory,
                'create_directory': self._create_directory
            },
            'git': {
                'status': self._git_status,
                'commit': self._git_commit,
                'branch': self._git_branch
            },
            'testing': {
                'run_tests': self._run_tests,
                'coverage': self._run_coverage
            },
            'linting': {
                'ruff_check': self._run_ruff,
                'black_format': self._run_black
            }
        }
        return tools
    
    def _call_local_llm(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.1) -> str:
        """Call local LLM via Ollama with enhanced prompting"""
        enhanced_prompt = f"""
        You are an expert software developer. Generate high-quality, production-ready code.
        
        Requirements:
        - Follow best practices and design patterns
        - Include proper error handling
        - Add comprehensive docstrings and comments
        - Ensure code is maintainable and readable
        - Follow language-specific conventions
        
        {prompt}
        
        Provide only the code implementation, no explanations unless specifically requested.
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
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    'model': self.model,
                    'prompt': enhanced_prompt,
                    'stream': False,
                    'options': {
                        'temperature': temperature,
                        'num_predict': max_tokens
                    }
                },
                timeout=60
            )
            if response.ok:
                data = response.json()
                return data.get('response', '')
        except Exception as e:
            print(f"Ollama HTTP API failed: {e}")
        
        return ""

    def generate_code(self, prompt: str, file_path: str = None, language: str = None) -> str:
        """Generate code with enhanced context awareness"""
        # Determine language from file path or prompt
        if not language and file_path:
            language = Path(file_path).suffix.lstrip('.')
        
        # Add language-specific context
        if language:
            prompt = f"Generate {language} code for: {prompt}"
        
        # Get project context
        project_context = self._get_project_context()
        if project_context:
            prompt = f"{prompt}\n\nProject Context:\n{project_context}"
        
        return self._call_local_llm(prompt)

    def generate_project_structure(self, requirements: str) -> Dict[str, Any]:
        """Generate complete project structure based on requirements"""
        prompt = f"""
        Based on these requirements, generate a complete project structure:
        
        {requirements}
        
        Return a JSON structure with:
        - directories: List of directory paths to create
        - files: List of files with their content and paths
        - dependencies: List of required packages/dependencies
        - setup_instructions: Commands to set up the project
        """
        
        response = self._call_local_llm(prompt)
        
        try:
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback structure
        return {
            'directories': ['src', 'tests', 'docs', 'config'],
            'files': [
                {'path': 'README.md', 'content': '# Project\n\nGenerated project'},
                {'path': 'requirements.txt', 'content': '# Dependencies'},
                {'path': 'src/__init__.py', 'content': ''}
            ],
            'dependencies': [],
            'setup_instructions': ['pip install -r requirements.txt']
        }

    def implement_feature(self, feature_description: str, existing_code: str = None) -> str:
        """Implement a specific feature with context awareness"""
        prompt = f"""
        Implement this feature: {feature_description}
        
        Requirements:
        - Follow existing code patterns if provided
        - Include proper error handling
        - Add unit tests
        - Follow best practices
        
        {f'Existing code context:\n{existing_code}' if existing_code else ''}
        """
        
        return self._call_local_llm(prompt)

    def generate_tests(self, code: str, test_framework: str = 'pytest') -> str:
        """Generate comprehensive tests for given code"""
        prompt = f"""
        Generate comprehensive {test_framework} tests for this code:
        
        {code}
        
        Requirements:
        - Test all functions and edge cases
        - Include positive and negative test cases
        - Mock external dependencies
        - Ensure high test coverage
        - Follow testing best practices
        """
        
        return self._call_local_llm(prompt)

    def refactor_code(self, code: str, improvements: str) -> str:
        """Refactor code based on specific improvements"""
        prompt = f"""
        Refactor this code with the following improvements: {improvements}
        
        Original code:
        {code}
        
        Requirements:
        - Maintain functionality
        - Improve readability and maintainability
        - Follow best practices
        - Add proper error handling if missing
        - Optimize performance where possible
        """
        
        return self._call_local_llm(prompt)

    # MCP-style tool methods
    def _read_file(self, file_path: str) -> str:
        """Read file content"""
        try:
            full_path = self.project_path / file_path
            return full_path.read_text()
        except Exception as e:
            return f"Error reading file: {e}"

    def _write_file(self, file_path: str, content: str) -> bool:
        """Write content to file"""
        try:
            full_path = self.project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False

    def _list_directory(self, dir_path: str = '.') -> List[str]:
        """List directory contents"""
        try:
            full_path = self.project_path / dir_path
            return [str(item.relative_to(self.project_path)) for item in full_path.iterdir()]
        except Exception as e:
            return [f"Error listing directory: {e}"]

    def _create_directory(self, dir_path: str) -> bool:
        """Create directory"""
        try:
            full_path = self.project_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory: {e}")
            return False

    def _git_status(self) -> str:
        """Get git status"""
        try:
            result = subprocess.run(['git', 'status'], cwd=self.project_path, 
                                  capture_output=True, text=True)
            return result.stdout
        except Exception:
            return "Git not available"

    def _git_commit(self, message: str) -> bool:
        """Commit changes"""
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.project_path, check=True)
            subprocess.run(['git', 'commit', '-m', message], cwd=self.project_path, check=True)
            return True
        except Exception as e:
            print(f"Git commit failed: {e}")
            return False

    def _git_branch(self, branch_name: str) -> bool:
        """Create and switch to branch"""
        try:
            subprocess.run(['git', 'checkout', '-b', branch_name], cwd=self.project_path, check=True)
            return True
        except Exception as e:
            print(f"Git branch creation failed: {e}")
            return False

    def _run_tests(self, test_path: str = '.') -> Dict[str, Any]:
        """Run tests and return results"""
        try:
            result = subprocess.run(['python', '-m', 'pytest', test_path], 
                                  cwd=self.project_path, capture_output=True, text=True)
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {'error': str(e), 'success': False}

    def _run_coverage(self, test_path: str = '.') -> Dict[str, Any]:
        """Run tests with coverage"""
        try:
            result = subprocess.run(['python', '-m', 'pytest', '--cov=src', test_path], 
                                  cwd=self.project_path, capture_output=True, text=True)
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {'error': str(e), 'success': False}

    def _run_ruff(self, path: str = '.') -> Dict[str, Any]:
        """Run ruff linter"""
        try:
            result = subprocess.run(['ruff', 'check', path], 
                                  cwd=self.project_path, capture_output=True, text=True)
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {'error': str(e), 'success': False}

    def _run_black(self, path: str = '.') -> Dict[str, Any]:
        """Run black formatter"""
        try:
            result = subprocess.run(['black', path], 
                                  cwd=self.project_path, capture_output=True, text=True)
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {'error': str(e), 'success': False}

    def _get_project_context(self) -> str:
        """Get context about the current project"""
        context_parts = []
        
        # Check for common project files
        if (self.project_path / 'requirements.txt').exists():
            context_parts.append("Python project with requirements.txt")
        
        if (self.project_path / 'package.json').exists():
            context_parts.append("Node.js project with package.json")
        
        if (self.project_path / 'Cargo.toml').exists():
            context_parts.append("Rust project with Cargo.toml")
        
        # Check project structure
        src_dirs = [d for d in self.project_path.iterdir() if d.is_dir() and d.name in ['src', 'app', 'lib']]
        if src_dirs:
            context_parts.append(f"Has source directories: {[d.name for d in src_dirs]}")
        
        return "; ".join(context_parts) if context_parts else "New project"

    def use_tool(self, tool_name: str, method: str, *args, **kwargs) -> Any:
        """Use MCP-style tools"""
        if tool_name in self.available_tools and method in self.available_tools[tool_name]:
            return self.available_tools[tool_name][method](*args, **kwargs)
        else:
            return f"Tool {tool_name}.{method} not available"
