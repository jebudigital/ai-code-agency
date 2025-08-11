import os
import json
import time
import zipfile
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Use absolute imports instead of relative imports
from agents.planner import PlannerAgent, ProjectPlan, Task
from agents.coder import CoderAgent
from agents.reviewer import ReviewerAgent
from agents.doc_agent import DocumentationAgent

# Import GitHub integration
try:
    from utils.github_manager import GitHubProjectManager
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("Warning: GitHub integration not available. Install PyGithub: pip install PyGithub")

@dataclass
class ProjectStatus:
    project_id: str
    name: str
    status: str  # planning, in_progress, testing, documentation, completed, failed
    progress_percentage: float
    current_task: Optional[str]
    completed_tasks: List[int]
    failed_tasks: List[int]
    start_time: datetime
    estimated_completion: datetime
    actual_completion: Optional[datetime]
    errors: List[str]
    warnings: List[str]
    # GitHub integration fields
    github_repo_name: Optional[str] = None
    github_repo_url: Optional[str] = None
    github_clone_url: Optional[str] = None
    github_project_board_url: Optional[str] = None

class ProjectManagerAgent:
    def __init__(self, project_path: str = None, model: str = None, use_github: bool = True, 
                 github_org: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.model = model or os.environ.get('OLLAMA_MODEL', 'phind-codellama:34b-v2')
        self.use_github = use_github and GITHUB_AVAILABLE
        self.github_org = github_org or os.environ.get('GITHUB_ORG')
        
        # Initialize all agents
        self.planner = PlannerAgent(model=self.model)
        self.coder = CoderAgent(model=self.model, project_path=str(self.project_path))
        self.reviewer = ReviewerAgent()
        self.doc_agent = DocumentationAgent(model=self.model, project_path=str(self.project_path))
        
        # Initialize GitHub manager if available
        self.github_manager = None
        if self.use_github:
            try:
                self.github_manager = GitHubProjectManager(org_name=self.github_org)
                print("✅ GitHub integration enabled")
                if self.github_org:
                    print(f"   Using organization: {self.github_org}")
                else:
                    print("   Using user account")
            except Exception as e:
                print(f"⚠️  GitHub integration failed: {e}")
                self.use_github = False
        
        # Project tracking
        self.active_projects: Dict[str, ProjectStatus] = {}
        self.project_plans: Dict[str, ProjectPlan] = {}
        
    def create_project(self, title: str, requirements: str, project_id: str = None, 
                      is_private: bool = True) -> str:
        """Create a new project and return project ID"""
        if not project_id:
            project_id = f"proj_{int(time.time())}"
        
        # Create project plan
        project_plan = self.planner.plan(title, requirements)
        self.project_plans[project_id] = project_plan
        
        # Initialize project status
        project_status = ProjectStatus(
            project_id=project_id,
            name=title,
            status="planning",
            progress_percentage=0.0,
            current_task="Project planning completed",
            completed_tasks=[],
            failed_tasks=[],
            start_time=datetime.now(),
            estimated_completion=datetime.now() + timedelta(days=project_plan.timeline_days),
            actual_completion=None,
            errors=[],
            warnings=[]
        )
        
        # Create GitHub repository if enabled
        if self.use_github and self.github_manager:
            try:
                print("🚀 Creating GitHub repository...")
                github_repo = self.github_manager.create_project_repository(
                    title, requirements, is_private
                )
                
                if github_repo:
                    project_status.github_repo_name = github_repo['repo_name']
                    project_status.github_repo_url = github_repo['repo_url']
                    project_status.github_clone_url = github_repo['clone_url']
                    project_status.github_project_board_url = github_repo['project_board_url']
                    
                    print(f"✅ GitHub repository created: {github_repo['repo_url']}")
                    if github_repo['project_board_url']:
                        print(f"   Project Board: {github_repo['project_board_url']}")
                    
                else:
                    error_msg = "Failed to create GitHub repository"
                    project_status.errors.append(error_msg)
                    print(f"❌ {error_msg}")
                    
            except Exception as e:
                error_msg = f"GitHub integration failed: {e}"
                project_status.errors.append(error_msg)
                print(f"⚠️  {error_msg}")
        
        self.active_projects[project_id] = project_status
        
        print(f"Project '{title}' created with ID: {project_id}")
        print(f"Estimated timeline: {project_plan.timeline_days} days")
        print(f"Total estimated hours: {project_plan.total_estimated_hours}")
        
        if project_status.github_repo_url:
            print(f"🔗 GitHub Repository: {project_status.github_repo_url}")
            print(f"📋 Project Board: {project_status.github_project_board_url}")
        
        return project_id
    
    def execute_project(self, project_id: str) -> bool:
        """Execute a complete project from start to finish"""
        if project_id not in self.active_projects:
            raise ValueError(f"Project {project_id} not found")
        
        project_status = self.active_projects[project_id]
        project_plan = self.project_plans[project_id]
        
        print(f"Starting execution of project: {project_status.name}")
        
        try:
            # Phase 1: Project Setup
            self._update_status(project_id, "in_progress", "Setting up project structure")
            if not self._setup_project_structure(project_id):
                raise Exception("Failed to setup project structure")
            
            # Phase 2: Implementation
            self._update_status(project_id, "in_progress", "Implementing core functionality")
            if not self._implement_project(project_id):
                raise Exception("Failed to implement project")
            
            # Phase 3: Testing and Review
            self._update_status(project_id, "testing", "Running tests and quality checks")
            if not self._test_and_review_project(project_id):
                raise Exception("Failed testing and review phase")
            
            # Phase 4: Documentation
            self._update_status(project_id, "documentation", "Generating documentation")
            if not self._generate_documentation(project_id):
                raise Exception("Failed to generate documentation")
            
            # Phase 5: Finalize
            self._update_status(project_id, "completed", "Project completed successfully")
            project_status.actual_completion = datetime.now()
            
            # Update GitHub project completion
            if self.use_github and self.github_manager and project_status.github_repo_name:
                try:
                    # Update the "Documentation" issue to completed
                    self.github_manager.update_project_issue(
                        project_status.github_repo_name,
                        "📚 Documentation",
                        "completed",
                        "Project documentation completed successfully"
                    )
                    
                    # Update the "Project Complete" issue
                    self.github_manager.update_project_issue(
                        project_status.github_repo_name,
                        "🚀 Project Setup Complete",
                        "completed",
                        "Project completed successfully by AI Coding Agency"
                    )
                    
                    print("✅ GitHub project status updated")
                    
                except Exception as e:
                    print(f"⚠️  Failed to update GitHub project status: {e}")
            
            print(f"Project {project_id} completed successfully!")
            return True
            
        except Exception as e:
            error_msg = f"Project execution failed: {str(e)}"
            self._update_status(project_id, "failed", error_msg)
            project_status.errors.append(error_msg)
            print(f"Project {project_id} failed: {error_msg}")
            return False
    
    def _setup_project_structure(self, project_id: str) -> bool:
        """Setup project directory structure and initial files"""
        try:
            project_status = self.active_projects[project_id]
            project_plan = self.project_plans[project_id]
            
            # Create project structure based on plan
            structure = self.coder.generate_project_structure(project_plan.description)
            
            # Create directories
            for directory in structure.get('directories', []):
                dir_path = self.project_path / directory
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create files
            for file_info in structure.get('files', []):
                file_path = file_info.get('path', '')
                content = file_info.get('content', '')
                if file_path and content:
                    full_path = self.project_path / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.write_text(content)
            
            # Mark setup task as complete
            setup_task = next((task for task in project_plan.tasks if 'setup' in task.title.lower()), None)
            if setup_task:
                project_status.completed_tasks.append(setup_task.id)
                
                # Update GitHub issue if available
                if self.use_github and self.github_manager and project_status.github_repo_name:
                    try:
                        self.github_manager.update_project_issue(
                            project_status.github_repo_name,
                            "🚀 Project Setup Complete",
                            "completed",
                            "Project structure setup completed successfully"
                        )
                    except Exception as e:
                        print(f"⚠️  Could not update GitHub issue: {e}")
            
            self._update_progress(project_id)
            return True
            
        except Exception as e:
            self.active_projects[project_id].errors.append(f"Setup failed: {str(e)}")
            return False
    
    def _implement_project(self, project_id: str) -> bool:
        """Implement the core project functionality"""
        try:
            project_status = self.active_projects[project_id]
            project_plan = self.project_plans[project_id]
            
            # Get coding tasks
            coding_tasks = [task for task in project_plan.tasks if task.agent == 'coder']
            
            for task in coding_tasks:
                if self._can_execute_task(task, project_status.completed_tasks):
                    self._update_status(project_id, "in_progress", f"Implementing: {task.title}")
                    
                    # Update GitHub issue if available
                    if self.use_github and self.github_manager and project_status.github_repo_name:
                        try:
                            self.github_manager.update_project_issue(
                                project_status.github_repo_name,
                                "💻 Core Implementation",
                                "in-progress",
                                f"Starting implementation of: {task.title}"
                            )
                        except Exception as e:
                            print(f"⚠️  Could not update GitHub issue: {e}")
                    
                    # Generate code for the task
                    code = self.coder.implement_feature(task.description)
                    
                    # Write code to appropriate file
                    if self._write_task_code(task, code):
                        project_status.completed_tasks.append(task.id)
                        
                        # Update GitHub issue if available
                        if self.use_github and self.github_manager and project_status.github_repo_name:
                            try:
                                self.github_manager.update_project_issue(
                                    project_status.github_repo_name,
                                    "💻 Core Implementation",
                                    "completed",
                                    f"Implementation completed for: {task.title}"
                                )
                            except Exception as e:
                                print(f"⚠️  Could not update GitHub issue: {e}")
                        
                        self._update_progress(project_id)
                    else:
                        raise Exception(f"Failed to write code for task: {task.title}")
            
            return True
            
        except Exception as e:
            self.active_projects[project_id].errors.append(f"Implementation failed: {str(e)}")
            return False
    
    def _test_and_review_project(self, project_id: str) -> bool:
        """Run tests and quality checks"""
        try:
            project_status = self.active_projects[project_id]
            project_plan = self.project_plans[project_id]
            
            # Get review tasks
            review_tasks = [task for task in project_plan.tasks if task.agent == 'reviewer']
            
            for task in review_tasks:
                if self._can_execute_task(task, project_status.completed_tasks):
                    self._update_status(project_id, "testing", f"Reviewing: {task.title}")
                    
                    # Update GitHub issue if available
                    if self.use_github and self.github_manager and project_status.github_repo_name:
                        try:
                            self.github_manager.update_project_issue(
                                project_status.github_repo_name,
                                "🧪 Testing & Quality",
                                "in-progress",
                                f"Starting review of: {task.title}"
                            )
                        except Exception as e:
                            print(f"⚠️  Could not update GitHub issue: {e}")
                    
                    # Run tests
                    test_results = self.reviewer.lint_and_test()
                    
                    # Evaluate results
                    approved, notes = self.reviewer.evaluate(test_results)
                    
                    if approved:
                        project_status.completed_tasks.append(task.id)
                        
                        # Update GitHub issue if available
                        if self.use_github and self.github_manager and project_status.github_repo_name:
                            try:
                                self.github_manager.update_project_issue(
                                    project_status.github_repo_name,
                                    "🧪 Testing & Quality",
                                    "completed",
                                    f"Review completed successfully for: {task.title}"
                                )
                            except Exception as e:
                                print(f"⚠️  Could not update GitHub issue: {e}")
                        
                        self._update_progress(project_id)
                    else:
                        # Try to fix issues
                        if self._fix_code_issues(project_id, notes):
                            project_status.completed_tasks.append(task.id)
                            
                            # Update GitHub issue if available
                            if self.use_github and self.github_manager and project_status.github_repo_name:
                                try:
                                    self.github_manager.update_project_issue(
                                        project_status.github_repo_name,
                                        "🧪 Testing & Quality",
                                        "completed",
                                        f"Review completed after fixing issues for: {task.title}"
                                    )
                                except Exception as e:
                                    print(f"⚠️  Could not update GitHub issue: {e}")
                            
                            self._update_progress(project_id)
                        else:
                            raise Exception(f"Failed to fix code issues: {notes}")
            
            return True
            
        except Exception as e:
            self.active_projects[project_id].errors.append(f"Testing failed: {str(e)}")
            return False
    
    def _generate_documentation(self, project_id: str) -> bool:
        """Generate project documentation"""
        try:
            project_status = self.active_projects[project_id]
            project_plan = self.project_plans[project_id]
            
            # Get documentation tasks
            doc_tasks = [task for task in project_plan.tasks if task.agent == 'doc_agent']
            
            for task in doc_tasks:
                if self._can_execute_task(task, project_status.completed_tasks):
                    self._update_status(project_id, "documentation", f"Generating: {task.title}")
                    
                    # Update GitHub issue if available
                    if self.use_github and self.github_manager and project_status.github_repo_name:
                        try:
                            self.github_manager.update_project_issue(
                                project_status.github_repo_name,
                                "📚 Documentation",
                                "in-progress",
                                f"Starting documentation generation for: {task.title}"
                            )
                        except Exception as e:
                            print(f"⚠️  Could not update GitHub issue: {e}")
                    
                    # Generate documentation package
                    if self.doc_agent.generate_project_package():
                        project_status.completed_tasks.append(task.id)
                        
                        # Update GitHub issue if available
                        if self.use_github and self.github_manager and project_status.github_repo_name:
                            try:
                                self.github_manager.update_project_issue(
                                    project_status.github_repo_name,
                                    "📚 Documentation",
                                    "completed",
                                    f"Documentation completed for: {task.title}"
                                )
                            except Exception as e:
                                print(f"⚠️  Could not update GitHub issue: {e}")
                        
                        self._update_progress(project_id)
                    else:
                        raise Exception(f"Failed to generate documentation for task: {task.title}")
            
            return True
            
        except Exception as e:
            self.active_projects[project_id].errors.append(f"Documentation failed: {str(e)}")
            return False
    
    def _can_execute_task(self, task: Task, completed_tasks: List[int]) -> bool:
        """Check if a task can be executed (dependencies satisfied)"""
        return all(dep in completed_tasks for dep in task.dependencies)
    
    def _write_task_code(self, task: Task, code: str) -> bool:
        """Write generated code to appropriate file"""
        try:
            # Determine file path based on task
            if 'test' in task.title.lower():
                file_path = f"tests/test_{task.id}.py"
            elif 'main' in task.title.lower():
                file_path = "src/main.py"
            else:
                file_path = f"src/{task.title.lower().replace(' ', '_')}.py"
            
            return self.coder.use_tool('file_system', 'write_file', file_path, code)
            
        except Exception as e:
            print(f"Error writing task code: {e}")
            return False
    
    def _fix_code_issues(self, project_id: str, issues: List[str]) -> bool:
        """Attempt to fix code issues automatically"""
        try:
            # This is a simplified fix - in practice, you'd want more sophisticated issue resolution
            for issue in issues:
                if 'ruff' in issue.lower():
                    # Run ruff auto-fix
                    ruff_result = self.coder.use_tool('linting', 'ruff_check', '.')
                    if not ruff_result.get('success', False):
                        return False
                elif 'test' in issue.lower():
                    # Run tests to see current status
                    test_result = self.coder.use_tool('testing', 'run_tests', '.')
                    if not test_result.get('success', False):
                        return False
            
            return True
            
        except Exception as e:
            print(f"Error fixing code issues: {e}")
            return False
    
    def _update_status(self, project_id: str, status: str, current_task: str):
        """Update project status"""
        if project_id in self.active_projects:
            self.active_projects[project_id].status = status
            self.active_projects[project_id].current_task = current_task
    
    def _update_progress(self, project_id: str):
        """Update project progress percentage"""
        if project_id in self.active_projects and project_id in self.project_plans:
            project_status = self.active_projects[project_id]
            project_plan = self.project_plans[project_id]
            
            total_tasks = len(project_plan.tasks)
            completed_tasks = len(project_status.completed_tasks)
            
            if total_tasks > 0:
                project_status.progress_percentage = (completed_tasks / total_tasks) * 100
    
    def get_project_status(self, project_id: str) -> Optional[ProjectStatus]:
        """Get current status of a project"""
        return self.active_projects.get(project_id)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects with their status"""
        projects = []
        for project_id, status in self.active_projects.items():
            project_info = asdict(status)
            if project_id in self.project_plans:
                project_info['plan'] = {
                    'timeline_days': self.project_plans[project_id].timeline_days,
                    'total_estimated_hours': self.project_plans[project_id].total_estimated_hours
                }
            projects.append(project_info)
        return projects
    
    def get_github_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project status from GitHub if available"""
        if not self.use_github or not self.github_manager:
            return None
        
        project_status = self.active_projects.get(project_id)
        if not project_status or not project_status.github_repo_name:
            return None
        
        try:
            return self.github_manager.get_project_status(project_status.github_repo_name)
        except Exception as e:
            print(f"Error getting GitHub project status: {e}")
            return None
    
    def list_github_projects(self) -> List[Dict[str, Any]]:
        """List all GitHub project repositories"""
        if not self.use_github or not self.github_manager:
            return []
        
        try:
            return self.github_manager.list_project_repositories()
        except Exception as e:
            print(f"Error listing GitHub projects: {e}")
            return []
    
    def package_project(self, project_id: str, output_path: str = None) -> str:
        """Package completed project for distribution"""
        if project_id not in self.active_projects:
            raise ValueError(f"Project {project_id} not found")
        
        project_status = self.active_projects[project_id]
        if project_status.status != "completed":
            raise ValueError(f"Project {project_id} is not completed")
        
        if not output_path:
            output_path = f"{project_id}_package.zip"
        
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all project files
                for root, dirs, files in os.walk(self.project_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.project_path)
                        
                        # Skip certain files/directories
                        if any(skip in str(arcname) for skip in ['.git', '__pycache__', '.venv', 'venv']):
                            continue
                        
                        zipf.write(file_path, arcname)
            
            print(f"Project packaged successfully: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to package project: {str(e)}")
    
    def cleanup_project(self, project_id: str) -> bool:
        """Clean up project resources"""
        try:
            if project_id in self.active_projects:
                del self.active_projects[project_id]
            if project_id in self.project_plans:
                del self.project_plans[project_id]
            
            print(f"Project {project_id} cleaned up successfully")
            return True
            
        except Exception as e:
            print(f"Error cleaning up project {project_id}: {e}")
            return False
