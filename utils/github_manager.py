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
import requests

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

class GitHubGraphQLManager:
    """Handles GitHub GraphQL API for Projects (beta) board automation."""
    def __init__(self, token: str):
        self.token = token
        self.endpoint = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

    def run_query(self, query: str, variables: dict = None):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        response = requests.post(self.endpoint, json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"GraphQL query failed: {response.status_code} {response.text}")
        data = response.json()
        # Allow partial data responses (e.g., querying both user and organization)
        if data.get("errors") and not data.get("data"):
            raise Exception(f"GraphQL error: {data['errors']}")
        return data.get("data", {})

    def get_viewer_id(self):
        query = """
        query { viewer { id login } }
        """
        return self.run_query(query)["viewer"]

    def create_project(self, owner_id: str, name: str, body: str = ""):
        query = """
        mutation($ownerId:ID!, $name:String!) {
          createProjectV2(input: {ownerId: $ownerId, title: $name}) {
            projectV2 { id title url }
          }
        }
        """
        variables = {"ownerId": owner_id, "name": name}
        return self.run_query(query, variables)["createProjectV2"]["projectV2"]

    def get_owner_id_by_login(self, login: str) -> dict:
        """Resolve a login to either a User or Organization node id.
        Returns dict { 'id': str, 'type': 'USER'|'ORG' }
        """
        # Try user first
        user_q = """
        query($login:String!) { user(login:$login) { id login } }
        """
        data = self.run_query(user_q, {"login": login})
        if data and data.get("user"):
            return {"id": data["user"]["id"], "type": "USER"}
        # Then org
        org_q = """
        query($login:String!) { organization(login:$login) { id login } }
        """
        data = self.run_query(org_q, {"login": login})
        if data and data.get("organization"):
            return {"id": data["organization"]["id"], "type": "ORG"}
        raise Exception(f"Could not resolve login '{login}' to a user or organization")

    def get_issue_node_id(self, owner: str, repo: str, issue_number: int) -> Optional[str]:
        query = """
        query($owner:String!, $repo:String!, $num:Int!) {
          repository(owner:$owner, name:$repo) {
            issue(number:$num) { id }
          }
        }
        """
        data = self.run_query(query, {"owner": owner, "repo": repo, "num": issue_number})
        node = (((data or {}).get("repository") or {}).get("issue") or {})
        return node.get("id") if node else None

    def add_field(self, project_id: str, name: str, data_type: str = "TEXT"):
        query = """
        mutation($projectId:ID!, $name:String!, $dataType:ProjectV2FieldType!) {
          addProjectV2Field(input: {projectId: $projectId, name: $name, dataType: $dataType}) {
            projectV2Field { id name dataType }
          }
        }
        """
        variables = {"projectId": project_id, "name": name, "dataType": data_type}
        return self.run_query(query, variables)["addProjectV2Field"]["projectV2Field"]

    def add_item(self, project_id: str, content_id: str):
        query = """
        mutation($projectId:ID!, $contentId:ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }
        """
        variables = {"projectId": project_id, "contentId": content_id}
        return self.run_query(query, variables)["addProjectV2ItemById"]["item"]

    def get_project_fields(self, project_id: str) -> dict:
        query = """
        query($projectId:ID!) {
          node(id:$projectId) {
            ... on ProjectV2 {
              fields(first: 50) {
                nodes {
                  __typename
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options { id name }
                  }
                  ... on ProjectV2FieldCommon { id name }
                }
              }
            }
          }
        }
        """
        data = self.run_query(query, {"projectId": project_id})
        return (((data or {}).get("node") or {}).get("fields") or {}).get("nodes", [])

    def create_single_select_option(self, project_id: str, field_id: str, name: str, color: str = "GRAY") -> dict:
        query = """
        mutation($projectId:ID!, $fieldId:ID!, $name:String!, $color:ProjectV2SingleSelectFieldOptionColor!) {
          createProjectV2SingleSelectFieldOption(input:{projectId:$projectId, fieldId:$fieldId, name:$name, color:$color}) {
            projectV2SingleSelectFieldOption { id name }
          }
        }
        """
        variables = {"projectId": project_id, "fieldId": field_id, "name": name, "color": color}
        return self.run_query(query, variables)["createProjectV2SingleSelectFieldOption"]["projectV2SingleSelectFieldOption"]

    def set_item_single_select(self, project_id: str, item_id: str, field_id: str, option_id: str) -> bool:
        query = """
        mutation($projectId:ID!, $itemId:ID!, $fieldId:ID!, $optionId:String!) {
          updateProjectV2ItemFieldValue(input:{
            projectId:$projectId,
            itemId:$itemId,
            fieldId:$fieldId,
            value:{ singleSelectOptionId:$optionId }
          }) { projectV2Item { id } }
        }
        """
        variables = {"projectId": project_id, "itemId": item_id, "fieldId": field_id, "optionId": option_id}
        _ = self.run_query(query, variables)
        return True

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
        """Create a new repository for a specific project, and a new Projects (beta) board via GraphQL."""
        try:
            # Clean project name for repo
            repo_name = self._clean_repo_name(project_name)
            
            # Truncate description to 350 characters (GitHub API limit)
            safe_description = (description or "")[:350]
            
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
                    description=safe_description,
                    private=is_private,
                    auto_init=True,
                    gitignore_template="Python",
                    license_template="mit"
                )
            else:
                repo = self.user.create_repo(
                    name=repo_name,
                    description=safe_description,
                    private=is_private,
                    auto_init=True,
                    gitignore_template="Python",
                    license_template="mit"
                )
            
            # Set up project structure
            self._setup_project_repo_structure(repo, project_name, description)

            # --- New: Create Projects (beta) board via GraphQL ---
            graphql_manager = GitHubGraphQLManager(self.token)
            # Determine correct owner login (org if available, otherwise user)
            owner_login = getattr(self.repo_owner, 'login', None) or (self.org_name if self.org_name else self.user.login)
            try:
                owner_info = graphql_manager.get_owner_id_by_login(owner_login)
                owner_id = owner_info["id"]
                project_board = graphql_manager.create_project(owner_id, f"{project_name} Development Board")
                project_board_url = project_board["url"] if project_board else None
                project_board_id = project_board["id"] if project_board else None
                if project_board_url:
                    print(f"  ✅ Created Projects (beta) board: {project_board_url}")
                else:
                    print("  ⚠️  Created Projects (beta) board but no URL returned")
            except Exception as e:
                project_board_url = None
                project_board_id = None
                print(f"  ⚠️  Could not create Projects (beta) board: {e}")
            # Ensure a Status single-select field exists with options mapped to labels
            status_field_id = None
            status_options_by_name = {}
            if project_board_id:
                try:
                    fields = graphql_manager.get_project_fields(project_board_id)
                    for f in fields:
                        if f.get('__typename') == 'ProjectV2SingleSelectField' and f.get('name') == 'Status':
                            status_field_id = f['id']
                            for opt in (f.get('options') or []):
                                status_options_by_name[opt['name']] = opt['id']
                            break
                    if not status_field_id:
                        created = graphql_manager.add_field(project_board_id, 'Status', 'SINGLE_SELECT')
                        status_field_id = created['id']
                        status_options_by_name = {}
                    desired = [
                        ('Planning', 'GRAY'),
                        ('In Progress', 'BLUE'),
                        ('Review', 'YELLOW'),
                        ('Testing', 'PURPLE'),
                        ('Completed', 'GREEN'),
                        ('Failed', 'RED')
                    ]
                    for name, color in desired:
                        if name not in status_options_by_name:
                            opt = graphql_manager.create_single_select_option(project_board_id, status_field_id, name, color)
                            status_options_by_name[name] = opt['id']
                except Exception as e:
                    print(f"  ⚠️  Could not ensure Status field/options: {e}")
            # --- End new GraphQL logic ---

            # Create initial issues for project phases and add to project board
            created_issues = []
            phases = [
                {
                    'title': '🚀 Project Setup Complete',
                    'body': 'Repository and project structure have been initialized.',
                    'labels': ['phase:setup', 'status:completed'],
                },
                {
                    'title': '📋 Requirements Analysis',
                    'body': 'Analyze project requirements and create detailed specifications.',
                    'labels': ['phase:planning', 'status:planning'],
                },
                {
                    'title': '🏗️ Architecture Design',
                    'body': 'Design system architecture and technical specifications.',
                    'labels': ['phase:planning', 'status:planning'],
                },
                {
                    'title': '💻 Core Implementation',
                    'body': 'Implement core functionality and features.',
                    'labels': ['phase:implementation', 'status:planning'],
                },
                {
                    'title': '🧪 Testing & Quality',
                    'body': 'Run comprehensive tests and quality checks.',
                    'labels': ['phase:testing', 'status:planning'],
                },
                {
                    'title': '📚 Documentation',
                    'body': 'Generate comprehensive project documentation.',
                    'labels': ['phase:documentation', 'status:planning'],
                }
            ]
            self._ensure_phase_labels(repo)
            for phase in phases:
                try:
                    issue = repo.create_issue(
                        title=phase['title'],
                        body=phase['body'],
                        labels=phase['labels']
                    )
                    print(f"  ✅ Created issue: {phase['title']}")
                    created_issues.append(issue)
                    # Add to Projects (beta) board via GraphQL
                    if project_board_id:
                        try:
                            # Prefer node_id if available; otherwise resolve via GraphQL
                            content_node_id = getattr(issue, 'node_id', None)
                            if not content_node_id:
                                content_node_id = graphql_manager.get_issue_node_id(repo.owner.login, repo.name, issue.number)
                            item_node = None
                            if content_node_id:
                                item_node = graphql_manager.add_item(project_board_id, content_node_id)
                            # Set Status single-select from labels
                            if item_node and status_field_id:
                                labels = [l.name for l in issue.labels]
                                status_name = 'Planning'
                                if 'status:completed' in labels:
                                    status_name = 'Completed'
                                elif 'status:in-progress' in labels:
                                    status_name = 'In Progress'
                                elif 'status:review' in labels:
                                    status_name = 'Review'
                                elif 'status:testing' in labels:
                                    status_name = 'Testing'
                                elif 'status:failed' in labels:
                                    status_name = 'Failed'
                                option_id = status_options_by_name.get(status_name)
                                if option_id:
                                    try:
                                        graphql_manager.set_item_single_select(project_board_id, item_node['id'], status_field_id, option_id)
                                    except Exception as se:
                                        print(f"    ⚠️  Could not set Status for '{phase['title']}': {se}")
                            else:
                                raise Exception("Could not resolve issue node id")
                            print(f"    ➕ Added issue '{phase['title']}' to project board")
                        except Exception as e:
                            print(f"    ⚠️  Could not add issue '{phase['title']}' to project board: {e}")
                except GithubException as e:
                    print(f"  ⚠️  Could not create issue {phase['title']}: {e}")

            print(f"✅ Repository created successfully: {repo.html_url}")
            return {
                'repo_name': repo.full_name,
                'repo_url': repo.html_url,
                'clone_url': repo.clone_url,
                'ssh_url': repo.ssh_url,
                'private': repo.private,
                'project_board_url': project_board_url
            }
        except GithubException as e:
            print(f"Error creating project repository: {e}")
            return None
        except Exception as e:
            # Do not fail the entire repo creation if project board failed
            print(f"Error (GraphQL) creating project board: {e}")
            try:
                return {
                    'repo_name': repo.full_name,
                    'repo_url': repo.html_url,
                    'clone_url': repo.clone_url,
                    'ssh_url': repo.ssh_url,
                    'private': repo.private,
                    'project_board_url': None
                }
            except Exception:
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
    
    def _create_or_update_file(self, repo: Repository, path: str, content: str, message: str) -> str:
        """Create a file if missing, otherwise update it; returns 'created' or 'updated'"""
        try:
            existing = repo.get_contents(path, ref='main')
            # If content is identical, do nothing
            try:
                existing_content = existing.decoded_content.decode('utf-8') if hasattr(existing, 'decoded_content') else ''
            except Exception:
                existing_content = ''
            if existing_content == content:
                return 'skipped'
            repo.update_file(path=path, message=message, content=content, sha=existing.sha, branch='main')
            return 'updated'
        except GithubException as ge:
            # If not found, create it
            if getattr(ge, 'status', None) == 404 or 'Not Found' in str(ge):
                repo.create_file(path=path, message=message, content=content, branch='main')
                return 'created'
            # Re-raise other errors
            raise

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
            
            # Create initial files (create or update to avoid 422 errors)
            files_to_create = [
                ('README.md', readme_content, 'Add or update README.md'),
                ('PROJECT_STRUCTURE.md', structure_content, 'Add or update PROJECT_STRUCTURE.md'),
                ('requirements.txt', requirements_content, 'Add or update requirements.txt'),
                ('.gitignore', gitignore_content, 'Add or update .gitignore'),
                ('src/__init__.py', '# Source package\n', 'Add or update src/__init__.py'),
                ('tests/__init__.py', '# Tests package\n', 'Add or update tests/__init__.py'),
                ('docs/README.md', '# Documentation\n\nDocumentation will be generated here.\n', 'Add or update docs/README.md'),
            ]
            
            for file_path, content, message in files_to_create:
                try:
                    result = self._create_or_update_file(repo, file_path, content, message)
                    if result == 'created':
                        print(f"  ✅ Created {file_path}")
                    elif result == 'updated':
                        print(f"  🔄 Updated {file_path}")
                    else:
                        print(f"  ⏭️  Skipped {file_path} (no changes)")
                except GithubException as e:
                    print(f"  ⚠️  Could not write {file_path}: {e}")
            
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

# Usage notes:
# - To use the new Projects (beta) automation, you must generate a GitHub PAT with the following scopes:
#   - repo (for private repos)
#   - project (for project management)
#   - read:org (if using organization projects)
# - The GraphQL API is required for all new project board automation.
# - See https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects
