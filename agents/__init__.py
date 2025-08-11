"""
AI Coding Agency - Agents Package

This package contains all the AI agents that work together to create
autonomous software development capabilities.
"""

from .planner import PlannerAgent, ProjectPlan, Task
from .coder import CoderAgent
from .reviewer import ReviewerAgent
from .doc_agent import DocumentationAgent
from .project_manager import ProjectManagerAgent, ProjectStatus

__version__ = "1.0.0"
__author__ = "AI Coding Agency"

__all__ = [
    "PlannerAgent",
    "ProjectPlan", 
    "Task",
    "CoderAgent",
    "ReviewerAgent",
    "DocumentationAgent",
    "ProjectManagerAgent",
    "ProjectStatus"
]
