#!/usr/bin/env python3
"""
GitHub Integration System for AI Coding Agency
Creates separate repositories for each project
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import base64

try:
    from github import Github, GithubException
    from github.Repository import Repository
    from github.Issue import Issue
    from github.Label import Label
    from github.Milestone import Milestone
    from github.Project import Project
    from github.ProjectColumn import ProjectColumn
    from github.ProjectCard import ProjectCard
    from github.Branch import Branch
    from github.ContentFile import ContentFile
except ImportError:
    print("PyGithub not installed. Install with: pip install PyGithub")
    Github = None

class GitHubProjectManager:
    """Manages GitHub repositories and project boards for AI Coding Agency"""
    
    def __init__(self, token: str = None, org_name: str = None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.org_name = org_name or os.environ.get('GITHUB_ORG')
        
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN environment variable.")
        
        # Initialize GitHub client
        self.github = Github(self.token)
        self.user = self.github.get_user()
        
        # Use organization if specified, otherwise use user account
        if self.org_name:
            try:
                self.org = self.github.get_organization(self.org_name)
                self.repo_owner = self.org
                print(f"✅ Using GitHub organization: {self.org_name}")
            except GithubException:
                print(f"⚠️  Organization {self.org_name} not found, using user account")
                self.org = None
                self.repo_owner = self.user
        else:
            self.org = None
            self.repo_owner = self.user
        
        # Cache for labels and project boards
        self._labels_cache = {}
        self._project_boards_cache = {}
    
    def create_project_repository(self, project_name: str, description: str, is_private: bool = True, 
                                template_repo: str = None) -> Dict[str, Any]:
        """Create a new repository for a specific project"""
        try:
            # Clean project name for repo
            repo_name = self._clean_repo_name(project_name)
            
            # Check if repo already exists
            try:
                existing_repo = self.repo_owner.get_repo(repo_name)
                print(f"⚠️  Repository {repo_name} already exists, using existing one")
                return self._get_repo_info(existing_repo)
            except GithubException:
                pass
            
            print(f"🚀 Creating new repository: {repo_name}")
            
            # Create new repo
            if self.org:
                repo = self.org.create_repo(
                    name=repo_name,
                    description=description,
                    private=is_private,
                    auto_init=True,
                    gitignore_template="Python",
                    license_template="mit"
                )
            else:
                repo = self.user.create_repo(
                    name=repo_name,
                    description=description,
                    private=is_private,
                    auto_init=True,
                    gitignore_template="Python",
                    license_template="mit"
                )
            
            # Set up project structure
            self._setup_project_repo_structure(repo, project_name, description)
            
            # Create project board
            project_board = self._create_project_board(repo)
            
            # Create initial issues for project phases
            self._create_project_phase_issues(repo, project_board)
            
            print(f"✅ Repository created successfully: {repo.html_url}")
            
            return {
                'repo_name': repo.full_name,
                'repo_url': repo.html_url,
                'clone_url': repo.clone_url,
                'ssh_url': repo.ssh_url,
                'private': repo.private,
                'project_board_url': project_board.html_url if project_board else None
            }
            
        except GithubException as e:
            print(f"Error creating project repository: {e}")
            return None
    
    def _clean_repo_name(self, project_name: str) -> str:
        """Clean project name to valid repository name"""
        # Remove special characters, replace spaces with hyphens
        cleaned = ''.join(c for c in project_name if c.isalnum() or c in ' -_')
        cleaned = cleaned.replace(' ', '-').replace('_', '-')
        cleaned = cleaned.lower()
        
        # Ensure it starts with a letter
        if cleaned and not cleaned[0].isalpha():
            cleaned = 'proj-' + cleaned
        
        # Add timestamp to ensure uniqueness
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        return f"{cleaned}-{timestamp}"
    
    def _setup_project_repo_structure(self, repo: Repository, project_name: str, description: str):
        """Set up initial repository structure with README and project files"""
        try:
            # Create comprehensive README
            readme_content = f"""# {project_name}

{description}

## 🚀 Project Overview

This project was created by **AI Coding Agency** - an autonomous development system powered by local LLM models.

## 📋 Project Status

- [ ] Project Planning
- [ ] Implementation
- [ ] Testing & Review
- [ ] Documentation
- [ ] Project Complete

## 🏗️ Architecture

*Architecture details will be added during development*

## 🧪 Testing

*Test instructions will be added during development*

## 📚 Documentation

*Documentation will be generated during development*

## 🔧 Development

### Prerequisites

- Python 3.8+
- Required dependencies (see requirements.txt)

### Setup

```bash
# Clone the repository
git clone {repo.clone_url}

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Generated by AI Coding Agency on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # Create project structure file
            structure_content = f"""# Project Structure

This file tracks the development structure of {project_name}.

## 📁 Directory Structure

```
{project_name}/
├── src/                    # Source code
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

## 🔄 Development Phases

### Phase 1: Planning ✅
- [x] Repository created
- [x] Initial structure setup
- [ ] Requirements analysis
- [ ] Architecture design

### Phase 2: Implementation
- [ ] Core functionality
- [ ] Feature development
- [ ] Code generation

### Phase 3: Testing & Review
- [ ] Unit tests
- [ ] Integration tests
- [ ] Code review
- [ ] Quality checks

### Phase 4: Documentation
- [ ] API documentation
- [ ] User guides
- [ ] Developer documentation

### Phase 5: Completion
- [ ] Final testing
- [ ] Documentation review
- [ ] Project packaging
- [ ] Deployment preparation

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # Create requirements.txt template
            requirements_content = """# Project Dependencies

# Core dependencies
# Add your project-specific dependencies here

# Development dependencies
pytest>=7.4.0
black>=23.0.0
ruff>=0.1.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.2.0
"""
            
            # Create .gitignore
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment variables
.env
.env.local

# Coverage
.coverage
htmlcov/

# Jupyter
.ipynb_checkpoints
"""
            
            # Create initial files
            files_to_create = [
                ('README.md', readme_content),
                ('PROJECT_STRUCTURE.md', structure_content),
                ('requirements.txt', requirements_content),
                ('.gitignore', gitignore_content),
                ('src/__init__.py', '# Source package\n'),
                ('tests/__init__.py', '# Tests package\n'),
                ('docs/README.md', '# Documentation\n\nDocumentation will be generated here.\n')
            ]
            
            for file_path, content in files_to_create:
                try:
                    # Create directory if needed
                    dir_path = os.path.dirname(file_path)
                    if dir_path and not os.path.exists(dir_path):
                        os.makedirs(dir_path, exist_ok=True)
                    
                    # Create file in repo
                    repo.create_file(
                        path=file_path,
                        message=f"Add {file_path}",
                        content=content,
                        branch='main'
                    )
                    print(f"  ✅ Created {file_path}")
                    
                except GithubException as e:
                    print(f"  ⚠️  Could not create {file_path}: {e}")
            
            # Create main branch protection if organization
            if self.org:
                try:
                    main_branch = repo.get_branch('main')
                    main_branch.edit_protection(
                        required_status_checks=None,
                        enforce_admins=False,
                        required_pull_request_reviews=None,
                        dismiss_stale_reviews=False,
                        required_approving_review_count=0,
                        required_commit_signature=False,
                        required_linear_history=False,
                        allow_force_pushes=False,
                        allow_deletions=False,
                        block_creations=False,
                        required_conversation_resolution=False
                    )
                    print("  ✅ Added branch protection to main")
                except GithubException as e:
                    print(f"  ⚠️  Could not add branch protection: {e}")
            
        except Exception as e:
            print(f"Error setting up repository structure: {e}")
    
    def _create_project_board(self, repo: Repository) -> Optional[Project]:
        """Create a project board for the repository"""
        try:
            # Create project board
            project_board = repo.create_project(
                name=f"📋 {repo.name} Development Board",
                body="Project management board for development phases"
            )
            
            # Create columns
            columns = [
                "📋 Planning",
                "🚀 In Progress", 
                "🔍 Review",
                "🧪 Testing",
                "✅ Completed",
                "❌ Failed"
            ]
            
            for column_name in columns:
                project_board.create_column(column_name)
            
            print(f"  ✅ Created project board with {len(columns)} columns")
            return project_board
            
        except GithubException as e:
            print(f"  ⚠️  Could not create project board: {e}")
            return None
    
    def _create_project_phase_issues(self, repo: Repository, project_board: Project):
        """Create initial issues for project phases"""
        try:
            phases = [
                {
                    'title': '🚀 Project Setup Complete',
                    'body': 'Repository and project structure have been initialized.',
                    'labels': ['phase:setup', 'status:completed'],
                    'column': '✅ Completed'
                },
                {
                    'title': '📋 Requirements Analysis',
                    'body': 'Analyze project requirements and create detailed specifications.',
                    'labels': ['phase:planning', 'status:planning'],
                    'column': '📋 Planning'
                },
                {
                    'title': '🏗️ Architecture Design',
                    'body': 'Design system architecture and technical specifications.',
                    'labels': ['phase:planning', 'status:planning'],
                    'column': '📋 Planning'
                },
                {
                    'title': '💻 Core Implementation',
                    'body': 'Implement core functionality and features.',
                    'labels': ['phase:implementation', 'status:planning'],
                    'column': '📋 Planning'
                },
                {
                    'title': '🧪 Testing & Quality',
                    'body': 'Run comprehensive tests and quality checks.',
                    'labels': ['phase:testing', 'status:planning'],
                    'column': '📋 Planning'
                },
                {
                    'title': '📚 Documentation',
                    'body': 'Generate comprehensive project documentation.',
                    'labels': ['phase:documentation', 'status:planning'],
                    'column': '📋 Planning'
                }
            ]
            
            # Create labels first
            self._ensure_phase_labels(repo)
            
            for phase in phases:
                try:
                    # Create issue
                    issue = repo.create_issue(
                        title=phase['title'],
                        body=phase['body'],
                        labels=phase['labels']
                    )
                    
                    # Add to project board
                    if project_board:
                        columns = project_board.get_columns()
                        for column in columns:
                            if phase['column'] in column.name:
                                column.create_card(content_id=issue.id, content_type="Issue")
                                break
                    
                    print(f"  ✅ Created issue: {phase['title']}")
                    
                except GithubException as e:
                    print(f"  ⚠️  Could not create issue {phase['title']}: {e}")
            
        except Exception as e:
            print(f"Error creating phase issues: {e}")
    
    def _ensure_phase_labels(self, repo: Repository):
        """Ensure phase and status labels exist"""
        labels_to_create = [
            # Phase labels
            {'name': 'phase:setup', 'color': '0e8a16', 'description': 'Project setup phase'},
            {'name': 'phase:planning', 'color': '1d76db', 'description': 'Planning phase'},
            {'name': 'phase:implementation', 'color': 'fbca04', 'description': 'Implementation phase'},
            {'name': 'phase:testing', 'color': '5319e7', 'description': 'Testing phase'},
            {'name': 'phase:documentation', 'color': 'd93f0b', 'description': 'Documentation phase'},
            
            # Status labels
            {'name': 'status:planning', 'color': 'fef2c0', 'description': 'Task is being planned'},
            {'name': 'status:in-progress', 'color': '1d76db', 'description': 'Task is in progress'},
            {'name': 'status:review', 'color': 'fbca04', 'description': 'Task is under review'},
            {'name': 'status:testing', 'color': '5319e7', 'description': 'Task is being tested'},
            {'name': 'status:completed', 'color': '0e8a16', 'description': 'Task is completed'},
            {'name': 'status:failed', 'color': 'b60205', 'description': 'Task failed'}
        ]
        
        for label_info in labels_to_create:
            try:
                repo.get_label(label_info['name'])
            except GithubException:
                repo.create_label(
                    name=label_info['name'],
                    color=label_info['color'],
                    description=label_info['description']
                )
    
    def _get_repo_info(self, repo: Repository) -> Dict[str, Any]:
        """Get repository information"""
        return {
            'repo_name': repo.full_name,
            'repo_url': repo.html_url,
            'clone_url': repo.clone_url,
            'ssh_url': repo.ssh_url,
            'private': repo.private,
            'created_at': repo.created_at.isoformat() if repo.created_at else None,
            'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
            'language': repo.language,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count
        }
    
    def get_project_status(self, repo_name: str) -> Dict[str, Any]:
        """Get project status from repository"""
        try:
            repo = self.repo_owner.get_repo(repo_name)
            
            # Get issues
            issues = repo.get_issues(state='all')
            
            total_issues = 0
            completed_issues = 0
            in_progress_issues = 0
            planning_issues = 0
            failed_issues = 0
            
            for issue in issues:
                total_issues += 1
                labels = [label.name for label in issue.labels]
                
                if 'status:completed' in labels:
                    completed_issues += 1
                elif 'status:in-progress' in labels or 'status:review' in labels or 'status:testing' in labels:
                    in_progress_issues += 1
                elif 'status:failed' in labels:
                    failed_issues += 0
                else:
                    planning_issues += 1
            
            progress_percentage = (completed_issues / total_issues * 100) if total_issues > 0 else 0
            
            return {
                'repo_name': repo.full_name,
                'repo_url': repo.html_url,
                'total_issues': total_issues,
                'completed_issues': completed_issues,
                'in_progress_issues': in_progress_issues,
                'planning_issues': planning_issues,
                'failed_issues': failed_issues,
                'progress_percentage': progress_percentage,
                'language': repo.language,
                'created_at': repo.created_at.isoformat() if repo.created_at else None,
                'updated_at': repo.updated_at.isoformat() if repo.updated_at else None
            }
            
        except GithubException as e:
            print(f"Error getting project status: {e}")
            return {}
    
    def list_project_repositories(self) -> List[Dict[str, Any]]:
        """List all project repositories"""
        try:
            repos = []
            
            if self.org:
                # Get organization repositories
                for repo in self.org.get_repos():
                    if repo.name.endswith(('-proj-', '-project-')) or 'ai-coding-agency' in repo.description.lower():
                        repos.append(self._get_repo_info(repo))
            else:
                # Get user repositories
                for repo in self.user.get_repos():
                    if repo.name.endswith(('-proj-', '-project-')) or 'ai-coding-agency' in repo.description.lower():
                        repos.append(self._get_repo_info(repo))
            
            return repos
            
        except GithubException as e:
            print(f"Error listing repositories: {e}")
            return []
    
    def update_project_issue(self, repo_name: str, issue_title: str, status: str, 
                            progress: str = None) -> bool:
        """Update project issue status"""
        try:
            repo = self.repo_owner.get_repo(repo_name)
            issues = repo.get_issues()
            
            # Find issue by title
            target_issue = None
            for issue in issues:
                if issue.title == issue_title:
                    target_issue = issue
                    break
            
            if not target_issue:
                print(f"Issue '{issue_title}' not found in {repo_name}")
                return False
            
            # Update status label
            current_labels = [label.name for label in target_issue.labels]
            
            # Remove old status labels
            status_labels = [label for label in current_labels if label.startswith('status:')]
            for status_label in status_labels:
                target_issue.remove_from_labels(status_label)
            
            # Add new status label
            new_status_label = f"status:{status}"
            target_issue.add_to_labels(new_status_label)
            
            # Add progress comment
            if progress:
                comment = f"""
## Progress Update
**Status**: {status}
**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{progress}
                """
                target_issue.create_comment(comment)
            
            return True
            
        except GithubException as e:
            print(f"Error updating project issue: {e}")
            return False
    
    def delete_project_repository(self, repo_name: str, confirm: bool = False) -> bool:
        """Delete a project repository"""
        if not confirm:
            print(f"⚠️  This will permanently delete repository: {repo_name}")
            response = input("Type 'DELETE' to confirm: ")
            if response != 'DELETE':
                print("Deletion cancelled")
                return False
        
        try:
            repo = self.repo_owner.get_repo(repo_name)
            repo.delete()
            print(f"✅ Repository {repo_name} deleted successfully")
            return True
            
        except GithubException as e:
            print(f"Error deleting repository: {e}")
            return False

# Convenience functions
def create_project_repo(project_name: str, description: str, is_private: bool = True, 
                       org_name: str = None) -> Dict[str, Any]:
    """Create a new project repository"""
    try:
        manager = GitHubProjectManager(org_name=org_name)
        return manager.create_project_repository(project_name, description, is_private)
    except Exception as e:
        print(f"Error creating project repository: {e}")
        return None

def get_project_status(repo_name: str, org_name: str = None) -> Dict[str, Any]:
    """Get project status from repository"""
    try:
        manager = GitHubProjectManager(org_name=org_name)
        return manager.get_project_status(repo_name)
    except Exception as e:
        print(f"Error getting project status: {e}")
        return {}

def list_project_repos(org_name: str = None) -> List[Dict[str, Any]]:
    """List all project repositories"""
    try:
        manager = GitHubProjectManager(org_name=org_name)
        return manager.list_project_repositories()
    except Exception as e:
        print(f"Error listing project repositories: {e}")
        return []
