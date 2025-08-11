import os
import json
import subprocess
import shutil
import time
from typing import Dict, List, Any
from dataclasses import dataclass

# Import logging utilities
try:
    from utils.logger import get_logger, log_ollama_call, log_error
    logger = get_logger('planner')
except ImportError:
    # Fallback if logging not available
    logger = None
    def log_ollama_call(*args, **kwargs): pass
    def log_error(*args, **kwargs): pass

@dataclass
class Task:
    id: int
    title: str
    description: str
    agent: str
    priority: str
    estimated_hours: float
    dependencies: List[int]
    acceptance_criteria: List[str]

@dataclass
class ProjectPlan:
    project_name: str
    description: str
    tasks: List[Task]
    timeline_days: int
    total_estimated_hours: float
    architecture_decisions: List[str]
    tech_stack: Dict[str, str]

class PlannerAgent:
    def __init__(self, model: str = None):
        self.model = model or os.environ.get('OLLAMA_MODEL', 'phind-codellama:34b-v2')
        self.ollama_cli = shutil.which('ollama')
        self.ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        
        # Log initialization
        if logger:
            logger.info(f"PlannerAgent initialized with model: {self.model}")
        
    def _call_local_llm(self, prompt: str, max_tokens: int = 2048, timeout: int = 30) -> str:
        """Call local LLM via Ollama CLI or HTTP API with comprehensive logging"""
        start_time = time.time()
        
        # Try Ollama CLI first
        if self.ollama_cli:
            try:
                if logger:
                    logger.info(f"Attempting Ollama CLI call with model: {self.model}")
                
                result = subprocess.run(
                    [self.ollama_cli, 'run', self.model, '--', prompt],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout
                )
                
                duration = time.time() - start_time
                
                if result.returncode == 0 and result.stdout.strip():
                    response = result.stdout.strip()
                    log_ollama_call(
                        model=self.model,
                        prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                        response=response[:200] + "..." if len(response) > 200 else response,
                        duration=duration,
                        success=True
                    )
                    return response
                else:
                    error_msg = f"Ollama CLI failed with return code {result.returncode}: {result.stderr}"
                    log_ollama_call(
                        model=self.model,
                        prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                        duration=duration,
                        success=False,
                        error=error_msg
                    )
                    if logger:
                        logger.warning(f"Ollama CLI failed: {error_msg}")
                        
            except subprocess.TimeoutExpired:
                duration = time.time() - start_time
                error_msg = f"Ollama CLI timeout after {timeout} seconds"
                log_ollama_call(
                    model=self.model,
                    prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                    duration=duration,
                    success=False,
                    error=error_msg
                )
                if logger:
                    logger.error(f"Ollama CLI timeout: {error_msg}")
            except Exception as e:
                duration = time.time() - start_time
                error_msg = f"Ollama CLI exception: {str(e)}"
                log_ollama_call(
                    model=self.model,
                    prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                    duration=duration,
                    success=False,
                    error=error_msg
                )
                if logger:
                    logger.error(f"Ollama CLI exception: {error_msg}")
        
        # Fallback to HTTP API
        try:
            if logger:
                logger.info(f"Attempting Ollama HTTP API call with model: {self.model}")
            
            import requests
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            if response.ok:
                data = response.json()
                result_text = data.get('response', '')
                log_ollama_call(
                    model=self.model,
                    prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                    response=result_text[:200] + "..." if len(result_text) > 200 else result_text,
                    duration=duration,
                    success=True
                )
                return result_text
            else:
                error_msg = f"Ollama HTTP API failed with status {response.status_code}: {response.text}"
                log_ollama_call(
                    model=self.model,
                    prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                    duration=duration,
                    success=False,
                    error=error_msg
                )
                if logger:
                    logger.warning(f"Ollama HTTP API failed: {error_msg}")
                    
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            error_msg = f"Ollama HTTP API timeout after {timeout} seconds"
            log_ollama_call(
                model=self.model,
                prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                duration=duration,
                success=False,
                error=error_msg
            )
            if logger:
                logger.error(f"Ollama HTTP API timeout: {error_msg}")
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Ollama HTTP API exception: {str(e)}"
            log_ollama_call(
                model=self.model,
                prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
                duration=duration,
                success=False,
                error=error_msg
            )
            if logger:
                logger.error(f"Ollama HTTP API exception: {error_msg}")
        
        # Log total failure
        total_duration = time.time() - start_time
        log_ollama_call(
            model=self.model,
            prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
            duration=total_duration,
            success=False,
            error="All Ollama methods failed"
        )
        
        return ""

    def analyze_requirements(self, requirements_text: str) -> Dict[str, Any]:
        """Analyze functional requirements and extract key information"""
        if logger:
            logger.info("Starting requirements analysis")
        
        prompt = f"""
        Analyze the following functional requirements and extract key information:
        
        {requirements_text}
        
        Please provide a JSON response with:
        - project_type: The type of project (web app, API, CLI tool, etc.)
        - complexity_level: low/medium/high
        - estimated_duration_days: Estimated project duration
        - key_features: List of main features
        - tech_stack_recommendations: Recommended technologies
        - risk_factors: Potential risks and challenges
        """
        
        response = self._call_local_llm(prompt, timeout=45)  # Increased timeout
        
        try:
            # Try to extract JSON from response
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                result = json.loads(json_str)
                
                if logger:
                    logger.info(f"Requirements analysis successful: {result.get('project_type', 'unknown')}")
                
                return result
        except Exception as e:
            if logger:
                logger.warning(f"Failed to parse JSON response: {e}")
                log_error('planner', e, {'operation': 'analyze_requirements', 'response': response})
        
        # Fallback analysis
        fallback_result = {
            'project_type': 'web_application',
            'complexity_level': 'medium',
            'estimated_duration_days': 7,
            'key_features': ['Basic functionality'],
            'tech_stack_recommendations': ['Python', 'Flask', 'HTML/CSS'],
            'risk_factors': ['Requirements may need clarification', 'LLM response parsing failed']
        }
        
        if logger:
            logger.info("Using fallback requirements analysis")
        
        return fallback_result

    def create_task_breakdown(self, requirements_text: str) -> List[Task]:
        """Break down requirements into specific tasks"""
        if logger:
            logger.info("Starting task breakdown")
        
        analysis = self.analyze_requirements(requirements_text)
        
        prompt = f"""
        Based on this project analysis:
        {json.dumps(analysis, indent=2)}
        
        Create a detailed task breakdown. Return a JSON array of tasks with:
        - title: Task title
        - description: Detailed description
        - agent: Which agent should handle this (planner, coder, reviewer, doc_agent)
        - priority: high/medium/low
        - estimated_hours: Time estimate
        - dependencies: List of task IDs this depends on
        - acceptance_criteria: List of completion criteria
        
        Focus on creating actionable, specific tasks that can be assigned to agents.
        """
        
        response = self._call_local_llm(prompt, timeout=45)  # Increased timeout
        
        try:
            if '[' in response and ']' in response:
                start = response.find('[')
                end = response.rfind(']') + 1
                json_str = response[start:end]
                task_data = json.loads(json_str)
                
                tasks = []
                for i, task in enumerate(task_data):
                    tasks.append(Task(
                        id=i+1,
                        title=task.get('title', f'Task {i+1}'),
                        description=task.get('description', ''),
                        agent=task.get('agent', 'coder'),
                        priority=task.get('priority', 'medium'),
                        estimated_hours=task.get('estimated_hours', 2.0),
                        dependencies=task.get('dependencies', []),
                        acceptance_criteria=task.get('acceptance_criteria', [])
                    ))
                
                if logger:
                    logger.info(f"Task breakdown successful: {len(tasks)} tasks created")
                
                return tasks
        except Exception as e:
            if logger:
                logger.warning(f"Failed to parse task breakdown JSON: {e}")
                log_error('planner', e, {'operation': 'create_task_breakdown', 'response': response})
        
        # Fallback task breakdown
        if logger:
            logger.info("Using fallback task breakdown")
        
        return [
            Task(
                id=1,
                title="Project Setup and Architecture",
                description="Set up project structure and define architecture",
                agent="planner",
                priority="high",
                estimated_hours=4.0,
                dependencies=[],
                acceptance_criteria=["Project structure defined", "Architecture documented"]
            ),
            Task(
                id=2,
                title="Core Implementation",
                description="Implement main functionality based on requirements",
                agent="coder",
                priority="high",
                estimated_hours=16.0,
                dependencies=[1],
                acceptance_criteria=["Core features working", "Basic tests passing"]
            ),
            Task(
                id=3,
                title="Testing and Quality Assurance",
                description="Comprehensive testing and code review",
                agent="reviewer",
                priority="medium",
                estimated_hours=8.0,
                dependencies=[2],
                acceptance_criteria=["All tests passing", "Code quality standards met"]
            ),
            Task(
                id=4,
                title="Documentation",
                description="Create comprehensive project documentation",
                agent="doc_agent",
                priority="medium",
                estimated_hours=6.0,
                dependencies=[3],
                acceptance_criteria=["README complete", "API docs generated", "Architecture diagrams"]
            )
        ]

    def plan(self, title: str, body: str) -> ProjectPlan:
        """Main planning method - creates comprehensive project plan"""
        if logger:
            logger.info(f"Starting project planning for: {title}")
        
        requirements = f"Title: {title}\n\n{body}"
        
        # Analyze requirements
        analysis = self.analyze_requirements(requirements)
        
        # Create task breakdown
        tasks = self.create_task_breakdown(requirements)
        
        # Calculate timeline and estimates
        total_hours = sum(task.estimated_hours for task in tasks)
        timeline_days = max(1, int(total_hours / 8))  # Assume 8 hours per day
        
        # Generate architecture decisions
        arch_prompt = f"""
        Based on the project requirements and analysis, suggest key architecture decisions:
        
        Project: {title}
        Analysis: {json.dumps(analysis, indent=2)}
        
        Provide 3-5 key architecture decisions that should be made.
        """
        
        arch_response = self._call_local_llm(arch_prompt, timeout=30)
        architecture_decisions = [line.strip() for line in arch_response.split('\n') if line.strip() and not line.startswith('#')]
        
        # Limit to 5 decisions
        architecture_decisions = architecture_decisions[:5]
        
        project_plan = ProjectPlan(
            project_name=title,
            description=body,
            tasks=tasks,
            timeline_days=timeline_days,
            total_estimated_hours=total_hours,
            architecture_decisions=architecture_decisions,
            tech_stack=analysis.get('tech_stack_recommendations', {})
        )
        
        if logger:
            logger.info(f"Project planning completed: {len(tasks)} tasks, {timeline_days} days, {total_hours} hours")
        
        return project_plan

    def get_project_status(self, project_plan: ProjectPlan, completed_tasks: List[int]) -> Dict[str, Any]:
        """Get current project status and progress"""
        total_tasks = len(project_plan.tasks)
        completed_count = len(completed_tasks)
        progress_percentage = (completed_count / total_tasks) * 100 if total_tasks > 0 else 0
        
        remaining_tasks = [task for task in project_plan.tasks if task.id not in completed_tasks]
        blocked_tasks = [task for task in remaining_tasks if any(dep not in completed_tasks for dep in task.dependencies)]
        
        return {
            'progress_percentage': progress_percentage,
            'completed_tasks': completed_count,
            'total_tasks': total_tasks,
            'remaining_tasks': len(remaining_tasks),
            'blocked_tasks': len(blocked_tasks),
            'estimated_completion_days': max(1, int(sum(task.estimated_hours for task in remaining_tasks) / 8))
        }
