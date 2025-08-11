#!/usr/bin/env python3
"""
Tests for the AI Coding Agency system
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the parent directory to the path so we can import agents
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Now import from agents package
from agents.project_manager import ProjectManagerAgent
from agents.planner import PlannerAgent, ProjectPlan, Task
from agents.coder import CoderAgent
from agents.doc_agent import DocumentationAgent

class TestPlannerAgent:
    """Test the Planner Agent functionality"""
    
    def test_planner_initialization(self):
        """Test planner agent can be initialized"""
        planner = PlannerAgent()
        assert planner is not None
        assert hasattr(planner, 'model')
        assert hasattr(planner, 'ollama_cli')
    
    def test_task_creation(self):
        """Test task dataclass creation"""
        task = Task(
            id=1,
            title="Test Task",
            description="A test task",
            agent="coder",
            priority="high",
            estimated_hours=2.0,
            dependencies=[],
            acceptance_criteria=["Task completed"]
        )
        
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.agent == "coder"
        assert task.priority == "high"
        assert task.estimated_hours == 2.0
    
    def test_project_plan_creation(self):
        """Test project plan dataclass creation"""
        tasks = [
            Task(
                id=1,
                title="Setup",
                description="Project setup",
                agent="planner",
                priority="high",
                estimated_hours=1.0,
                dependencies=[],
                acceptance_criteria=["Setup complete"]
            )
        ]
        
        plan = ProjectPlan(
            project_name="Test Project",
            description="A test project",
            tasks=tasks,
            timeline_days=1,
            total_estimated_hours=1.0,
            architecture_decisions=["Use Python"],
            tech_stack={"language": "Python"}
        )
        
        assert plan.project_name == "Test Project"
        assert len(plan.tasks) == 1
        assert plan.timeline_days == 1
        assert plan.total_estimated_hours == 1.0

class TestCoderAgent:
    """Test the Coder Agent functionality"""
    
    def test_coder_initialization(self):
        """Test coder agent can be initialized"""
        with tempfile.TemporaryDirectory() as temp_dir:
            coder = CoderAgent(project_path=temp_dir)
            assert coder is not None
            assert hasattr(coder, 'model')
            assert hasattr(coder, 'project_path')
            assert hasattr(coder, 'available_tools')
    
    def test_tool_discovery(self):
        """Test that tools are properly discovered"""
        with tempfile.TemporaryDirectory() as temp_dir:
            coder = CoderAgent(project_path=temp_dir)
            
            # Check that expected tools are available
            assert 'file_system' in coder.available_tools
            assert 'git' in coder.available_tools
            assert 'testing' in coder.available_tools
            assert 'linting' in coder.available_tools
    
    def test_file_operations(self):
        """Test file system operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            coder = CoderAgent(project_path=temp_dir)
            
            # Test directory creation
            result = coder.use_tool('file_system', 'create_directory', 'test_dir')
            assert result is True
            
            # Test file writing
            result = coder.use_tool('file_system', 'write_file', 'test_dir/test.txt', 'Hello World')
            assert result is True
            
            # Test file reading
            content = coder.use_tool('file_system', 'read_file', 'test_dir/test.txt')
            assert content == 'Hello World'
            
            # Test directory listing
            files = coder.use_tool('file_system', 'list_directory', 'test_dir')
            assert 'test.txt' in files

class TestDocumentationAgent:
    """Test the Documentation Agent functionality"""
    
    def test_doc_agent_initialization(self):
        """Test documentation agent can be initialized"""
        with tempfile.TemporaryDirectory() as temp_dir:
            doc_agent = DocumentationAgent(project_path=temp_dir)
            assert doc_agent is not None
            assert hasattr(doc_agent, 'model')
            assert hasattr(doc_agent, 'project_path')
    
    def test_project_analysis(self):
        """Test project analysis functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            doc_agent = DocumentationAgent(project_path=temp_dir)
            
            # Create a mock requirements.txt
            (Path(temp_dir) / 'requirements.txt').write_text('flask\nrequests')
            
            # Analyze the project
            info = doc_agent._analyze_project()
            assert info['type'] == 'Python'
            assert 'Python' in info['languages']
            assert 'flask' in info['dependencies']

class TestProjectManagerAgent:
    """Test the Project Manager Agent functionality"""
    
    def test_project_manager_initialization(self):
        """Test project manager can be initialized"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectManagerAgent(project_path=temp_dir)
            assert pm is not None
            assert hasattr(pm, 'planner')
            assert hasattr(pm, 'coder')
            assert hasattr(pm, 'reviewer')
            assert hasattr(pm, 'doc_agent')
    
    def test_project_creation(self):
        """Test project creation functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectManagerAgent(project_path=temp_dir)
            
            # Create a simple project
            project_id = pm.create_project(
                title="Test Project",
                requirements="Create a simple hello world application"
            )
            
            assert project_id is not None
            assert project_id in pm.active_projects
            assert project_id in pm.project_plans
            
            # Check project status
            status = pm.get_project_status(project_id)
            assert status.name == "Test Project"
            assert status.status == "planning"
    
    def test_project_listing(self):
        """Test project listing functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectManagerAgent(project_path=temp_dir)
            
            # Create a project
            project_id = pm.create_project(
                title="Test Project",
                requirements="Simple test"
            )
            
            # List projects
            projects = pm.list_projects()
            assert len(projects) == 1
            assert projects[0]['project_id'] == project_id
            assert projects[0]['name'] == "Test Project"

def test_system_integration():
    """Test that all components work together"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize all agents
        pm = ProjectManagerAgent(project_path=temp_dir)
        
        # Create a project
        project_id = pm.create_project(
            title="Integration Test",
            requirements="Test the complete system"
        )
        
        # Verify project was created
        assert project_id in pm.active_projects
        
        # Check that all agents are properly initialized
        assert pm.planner is not None
        assert pm.coder is not None
        assert pm.reviewer is not None
        assert pm.doc_agent is not None
        
        # Verify project plan was created
        assert project_id in pm.project_plans
        plan = pm.project_plans[project_id]
        assert len(plan.tasks) > 0

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
