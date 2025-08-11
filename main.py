#!/usr/bin/env python3
"""
AI Coding Agency - Main Application

This is the main entry point for the AI Coding Agency system.
It demonstrates the capabilities of the multi-agent system using local LLM models.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add the current directory to Python path so we can import agents
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import logging first
try:
    from utils.logger import get_logger, logger as main_logger
    logger = get_logger('main')
except ImportError:
    logger = None
    main_logger = None

# Now import from agents package
from agents.project_manager import ProjectManagerAgent
from agents.planner import PlannerAgent
from agents.coder import CoderAgent
from agents.reviewer import ReviewerAgent
from agents.doc_agent import DocumentationAgent

def check_ollama_setup():
    """Check if Ollama is properly set up"""
    if logger:
        logger.info("Checking Ollama setup")
    
    import shutil
    import requests
    
    # Check if ollama CLI is available
    ollama_cli = shutil.which('ollama')
    if not ollama_cli:
        error_msg = "Ollama CLI not found. Please install Ollama first."
        if logger:
            logger.error(error_msg)
        print("❌ Ollama CLI not found. Please install Ollama first.")
        print("   Visit: https://ollama.ai/")
        return False
    
    # Check if ollama service is running
    try:
        if logger:
            logger.info("Testing Ollama service connectivity")
        
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.ok:
            models = response.json().get('models', [])
            if models:
                if logger:
                    logger.info(f"Ollama is running with {len(models)} model(s)")
                print(f"✅ Ollama is running with {len(models)} model(s):")
                for model in models:
                    print(f"   - {model['name']} ({model['size']})")
                return True
            else:
                warning_msg = "Ollama is running but no models installed"
                if logger:
                    logger.warning(warning_msg)
                print("⚠️  Ollama is running but no models installed")
                print("   Run: ollama pull phind-codellama:34b-v2")
                return False
        else:
            error_msg = f"Ollama service not responding properly: {response.status_code}"
            if logger:
                logger.error(error_msg)
            print("❌ Ollama service is not responding properly.")
            return False
    except requests.exceptions.RequestException as e:
        error_msg = f"Cannot connect to Ollama service: {e}"
        if logger:
            logger.error(error_msg)
        print("❌ Cannot connect to Ollama service.")
        print("   Make sure Ollama is running: ollama serve")
        return False

def create_sample_project(project_manager: ProjectManagerAgent):
    """Create a sample project to demonstrate the system"""
    if logger:
        logger.info("Creating sample project")
    
    print("\n🚀 Creating a sample project to demonstrate the AI Coding Agency...")
    
    sample_requirements = """
    Create a simple task management API with the following features:
    
    1. REST API endpoints for CRUD operations on tasks
    2. Task properties: id, title, description, status, priority, due_date
    3. Status values: pending, in_progress, completed, cancelled
    4. Priority values: low, medium, high
    5. Data persistence using SQLite
    6. Input validation and error handling
    7. Unit tests with pytest
    8. API documentation with examples
    9. Docker containerization
    
    The API should be production-ready with proper error handling, logging, and security considerations.
    """
    
    try:
        project_id = project_manager.create_project(
            title="Task Management API",
            requirements=sample_requirements
        )
        
        if logger:
            logger.info(f"Sample project created successfully: {project_id}")
        
        print(f"\n📋 Sample project created with ID: {project_id}")
        print("   You can now run: python main.py --execute-project {project_id}")
        
        return project_id
        
    except Exception as e:
        error_msg = f"Failed to create sample project: {e}"
        if logger:
            logger.error(error_msg)
        print(f"❌ Failed to create sample project: {e}")
        return None

def execute_project(project_manager: ProjectManagerAgent, project_id: str):
    """Execute a specific project"""
    if logger:
        logger.info(f"Executing project: {project_id}")
    
    print(f"\n🔄 Executing project: {project_id}")
    
    try:
        success = project_manager.execute_project(project_id)
        
        if success:
            if logger:
                logger.info(f"Project {project_id} completed successfully")
            print(f"\n✅ Project {project_id} completed successfully!")
            
            # Package the project
            try:
                package_path = project_manager.package_project(project_id)
                print(f"📦 Project packaged as: {package_path}")
            except Exception as e:
                warning_msg = f"Failed to package project: {e}"
                if logger:
                    logger.warning(warning_msg)
                print(f"⚠️  Failed to package project: {e}")
        else:
            if logger:
                logger.warning(f"Project {project_id} failed to complete")
            print(f"\n❌ Project {project_id} failed to complete.")
            
            # Show project status
            status = project_manager.get_project_status(project_id)
            if status:
                print(f"   Status: {status.status}")
                print(f"   Current task: {status.current_task}")
                if status.errors:
                    print(f"   Errors: {status.errors}")
        
    except Exception as e:
        error_msg = f"Error executing project: {e}"
        if logger:
            logger.error(error_msg)
        print(f"❌ Error executing project: {e}")

def list_projects(project_manager: ProjectManagerAgent):
    """List all projects and their status"""
    if logger:
        logger.info("Listing all projects")
    
    projects = project_manager.list_projects()
    
    if not projects:
        print("📭 No projects found.")
        return
    
    print(f"\n📋 Found {len(projects)} project(s):")
    print("-" * 80)
    
    for project in projects:
        print(f"ID: {project['project_id']}")
        print(f"Name: {project['name']}")
        print(f"Status: {project['status']}")
        print(f"Progress: {project['progress_percentage']:.1f}%")
        print(f"Current Task: {project['current_task']}")
        
        if 'plan' in project:
            print(f"Timeline: {project['plan']['timeline_days']} days")
            print(f"Estimated Hours: {project['plan']['total_estimated_hours']}")
        
        if project['errors']:
            print(f"Errors: {', '.join(project['errors'])}")
        
        print("-" * 80)

def show_project_status(project_manager: ProjectManagerAgent, project_id: str):
    """Show detailed status of a specific project"""
    if logger:
        logger.info(f"Showing status for project: {project_id}")
    
    status = project_manager.get_project_status(project_id)
    
    if not status:
        print(f"❌ Project {project_id} not found.")
        return
    
    print(f"\n📊 Project Status: {status.name}")
    print("=" * 60)
    print(f"ID: {status.project_id}")
    print(f"Status: {status.status}")
    print(f"Progress: {status.progress_percentage:.1f}%")
    print(f"Current Task: {status.current_task}")
    print(f"Start Time: {status.start_time}")
    print(f"Estimated Completion: {status.estimated_completion}")
    
    if status.actual_completion:
        print(f"Actual Completion: {status.actual_completion}")
    
    print(f"Completed Tasks: {len(status.completed_tasks)}")
    print(f"Failed Tasks: {len(status.failed_tasks)}")
    
    if status.errors:
        print(f"Errors: {status.errors}")
    
    if status.warnings:
        print(f"Warnings: {status.warnings}")
    
    # Show GitHub integration info if available
    if hasattr(status, 'github_repo_url') and status.github_repo_url:
        print(f"\n🔗 GitHub Integration:")
        print(f"   Repository: {status.github_repo_url}")
        print(f"   Clone URL: {status.github_clone_url}")
        if status.github_project_board_url:
            print(f"   Project Board: {status.github_project_board_url}")
        
        # Get GitHub project status
        github_status = project_manager.get_github_project_status(project_id)
        if github_status:
            print(f"   GitHub Progress: {github_status.get('progress_percentage', 0):.1f}%")
            print(f"   Total Issues: {github_status.get('total_issues', 0)}")
            print(f"   Completed: {github_status.get('completed_issues', 0)}")
            print(f"   In Progress: {github_status.get('in_progress_issues', 0)}")
            print(f"   Failed: {github_status.get('failed_issues', 0)}")
            print(f"   Language: {github_status.get('language', 'Unknown')}")
            print(f"   Created: {github_status.get('created_at', 'Unknown')}")
        else:
            print(f"   ❌ No GitHub integration found for project {project_id}")

def interactive_mode(project_manager: ProjectManagerAgent):
    """Run in interactive mode"""
    if logger:
        logger.info("Starting interactive mode")
    
    print("\n🎯 AI Coding Agency - Interactive Mode")
    print("Type 'help' for available commands, 'quit' to exit.")
    
    while True:
        try:
            command = input("\n🤖 > ").strip().lower()
            
            if command in ['quit', 'exit', 'q']:
                if logger:
                    logger.info("User exited interactive mode")
                print("👋 Goodbye!")
                break
            elif command == 'help':
                print("""
Available commands:
- help: Show this help message
- list: List all local projects
- list-github: List all GitHub project repositories
- create <title>: Create a new project
- execute <project_id>: Execute a project
- status <project_id>: Show project status
- package <project_id>: Package a completed project
- sample: Create a sample project
- logs: Show recent logs
- github-status <project_id>: Show GitHub project status
- github-projects: List all GitHub repositories
- quit: Exit the application
                """)
            elif command == 'list':
                list_projects(project_manager)
            elif command == 'list-github':
                github_projects = project_manager.list_github_projects()
                if github_projects:
                    print(f"\n🔗 GitHub Project Repositories ({len(github_projects)}):")
                    print("=" * 60)
                    for repo in github_projects:
                        print(f"📁 {repo['repo_name']}")
                        print(f"   URL: {repo['repo_url']}")
                        print(f"   Language: {repo.get('language', 'Unknown')}")
                        print(f"   Created: {repo.get('created_at', 'Unknown')}")
                        print(f"   Private: {'Yes' if repo['private'] else 'No'}")
                        print()
                else:
                    print("❌ No GitHub project repositories found")
            elif command.startswith('create '):
                title = command[7:].strip()
                if title:
                    requirements = input("Enter project requirements: ")
                    is_private = input("Make repository private? (y/n, default: y): ").lower() != 'n'
                    if logger:
                        logger.info(f"Creating project: {title}")
                    project_id = project_manager.create_project(title, requirements, is_private=is_private)
                    print(f"✅ Project created with ID: {project_id}")
                else:
                    print("❌ Please provide a project title.")
            elif command.startswith('execute '):
                project_id = command[8:].strip()
                if project_id:
                    execute_project(project_manager, project_id)
                else:
                    print("❌ Please provide a project ID.")
            elif command.startswith('status '):
                project_id = command[7:].strip()
                if project_id:
                    show_project_status(project_manager, project_id)
                else:
                    print("❌ Please provide a project ID.")
            elif command.startswith('package '):
                project_id = command[8:].strip()
                if project_id:
                    try:
                        package_path = project_manager.package_project(project_id)
                        print(f"✅ Project packaged as: {package_path}")
                    except Exception as e:
                        print(f"❌ Failed to package project: {e}")
                else:
                    print("❌ Please provide a project ID.")
            elif command == 'sample':
                create_sample_project(project_manager)
            elif command == 'logs':
                if main_logger:
                    try:
                        log_file = main_logger.export_logs()
                        print(f"📋 Logs exported to: {log_file}")
                    except Exception as e:
                        print(f"❌ Failed to export logs: {e}")
                else:
                    print("❌ Logging system not available")
            elif command.startswith('github-status '):
                project_id = command[15:].strip()
                if project_id:
                    github_status = project_manager.get_github_project_status(project_id)
                    if github_status:
                        print(f"\n🔗 GitHub Project Status for {project_id}:")
                        print("=" * 50)
                        print(f"Repository: {github_status.get('repo_name', 'Unknown')}")
                        print(f"Progress: {github_status.get('progress_percentage', 0):.1f}%")
                        print(f"Total Issues: {github_status.get('total_issues', 0)}")
                        print(f"Completed: {github_status.get('completed_issues', 0)}")
                        print(f"In Progress: {github_status.get('in_progress_issues', 0)}")
                        print(f"Planning: {github_status.get('planning_issues', 0)}")
                        print(f"Failed: {github_status.get('failed_issues', 0)}")
                        print(f"Language: {github_status.get('language', 'Unknown')}")
                        print(f"Created: {github_status.get('created_at', 'Unknown')}")
                    else:
                        print(f"❌ No GitHub integration found for project {project_id}")
                else:
                    print("❌ Please provide a project ID.")
            elif command == 'github-projects':
                github_projects = project_manager.list_github_projects()
                if github_projects:
                    print(f"\n🔗 GitHub Project Repositories ({len(github_projects)}):")
                    print("=" * 60)
                    for repo in github_projects:
                        print(f"📁 {repo['repo_name']}")
                        print(f"   URL: {repo['repo_url']}")
                        print(f"   Language: {repo.get('language', 'Unknown')}")
                        print(f"   Created: {repo.get('created_at', 'Unknown')}")
                        print(f"   Private: {'Yes' if repo['private'] else 'No'}")
                        print()
                else:
                    print("❌ No GitHub project repositories found")
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            if logger:
                logger.info("User interrupted interactive mode")
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            error_msg = f"Error in interactive mode: {e}"
            if logger:
                logger.error(error_msg)
            print(f"❌ Error: {e}")

def main():
    """Main application entry point"""
    if logger:
        logger.info("Starting AI Coding Agency application")
    
    parser = argparse.ArgumentParser(
        description="AI Coding Agency - Autonomous project development using local LLM models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --interactive                    # Run in interactive mode
  python main.py --create-sample                 # Create and execute sample project
  python main.py --execute-project proj_123      # Execute specific project
  python main.py --list-projects                 # List all local projects
  python main.py --list-github                   # List all GitHub repositories
  python main.py --status proj_123               # Show project status
  python main.py --github-status proj_123        # Show GitHub project status
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create and execute a sample project')
    parser.add_argument('--execute-project', metavar='PROJECT_ID',
                       help='Execute a specific project by ID')
    parser.add_argument('--list-projects', action='store_true',
                       help='List all local projects and their status')
    parser.add_argument('--list-github', action='store_true',
                       help='List all GitHub project repositories')
    parser.add_argument('--status', metavar='PROJECT_ID',
                       help='Show detailed status of a specific project')
    parser.add_argument('--package', metavar='PROJECT_ID',
                       help='Package a completed project for distribution')
    parser.add_argument('--github-status', metavar='PROJECT_ID',
                       help='Show GitHub project status')
    parser.add_argument('--project-path', metavar='PATH',
                       help='Path to project directory (default: current directory)')
    parser.add_argument('--model', metavar='MODEL',
                       help='Ollama model to use (default: phind-codellama:34b-v2)')
    parser.add_argument('--log-level', metavar='LEVEL', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    parser.add_argument('--no-github', action='store_true',
                       help='Disable GitHub integration')
    parser.add_argument('--github-org', metavar='ORG_NAME',
                       help='GitHub organization name (default: user account)')
    
    args = parser.parse_args()
    
    # Check Ollama setup
    if not check_ollama_setup():
        sys.exit(1)
    
    # Initialize project manager
    try:
        if logger:
            logger.info("Initializing Project Manager")
        
        project_manager = ProjectManagerAgent(
            project_path=args.project_path,
            model=args.model,
            use_github=not args.no_github,
            github_org=args.github_org
        )
        print("✅ AI Coding Agency initialized successfully!")
        
    except Exception as e:
        error_msg = f"Failed to initialize AI Coding Agency: {e}"
        if logger:
            logger.error(error_msg)
        print(f"❌ Failed to initialize AI Coding Agency: {e}")
        sys.exit(1)
    
    # Handle command line arguments
    if args.create_sample:
        project_id = create_sample_project(project_manager)
        if project_id:
            execute_project(project_manager, project_id)
    elif args.execute_project:
        execute_project(project_manager, args.execute_project)
    elif args.list_projects:
        list_projects(project_manager)
    elif args.list_github:
        github_projects = project_manager.list_github_projects()
        if github_projects:
            print(f"\n🔗 GitHub Project Repositories ({len(github_projects)}):")
            print("=" * 60)
            for repo in github_projects:
                print(f"📁 {repo['repo_name']}")
                print(f"   URL: {repo['repo_url']}")
                print(f"   Language: {repo.get('language', 'Unknown')}")
                print(f"   Created: {repo.get('created_at', 'Unknown')}")
                print(f"   Private: {'Yes' if repo['private'] else 'No'}")
                print()
        else:
            print("❌ No GitHub project repositories found")
    elif args.status:
        show_project_status(project_manager, args.status)
    elif args.github_status:
        github_status = project_manager.get_github_project_status(args.github_status)
        if github_status:
            print(f"🔗 GitHub Project Status for {args.github_status}:")
            print(json.dumps(github_status, indent=2))
        else:
            print(f"❌ No GitHub integration found for project {args.github_status}")
    elif args.package:
        try:
            package_path = project_manager.package_project(args.package)
            print(f"✅ Project packaged as: {package_path}")
        except Exception as e:
            print(f"❌ Failed to package project: {e}")
    elif args.interactive or not any([args.create_sample, args.execute_project, 
                                     args.list_projects, args.list_github, args.status, 
                                     args.package, args.github_status]):
        interactive_mode(project_manager)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
