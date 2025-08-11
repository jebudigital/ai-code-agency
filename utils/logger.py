#!/usr/bin/env python3
"""
Comprehensive logging system for AI Coding Agency
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json
import traceback

class AICodingAgencyLogger:
    """Centralized logging system for AI Coding Agency"""
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create loggers for different components
        self.loggers = {}
        self.setup_loggers(log_level)
        
        # Performance tracking
        self.performance_log = []
        
    def setup_loggers(self, log_level: str):
        """Setup individual loggers for different components"""
        log_level_num = getattr(logging, log_level.upper(), logging.INFO)
        
        # Main application logger
        self.loggers['main'] = self._create_logger(
            'ai_coding_agency.main',
            self.log_dir / 'main.log',
            log_level_num
        )
        
        # Agent-specific loggers
        agent_loggers = [
            'planner', 'coder', 'reviewer', 'doc_agent', 'project_manager'
        ]
        
        for agent in agent_loggers:
            self.loggers[agent] = self._create_logger(
                f'ai_coding_agency.{agent}',
                self.log_dir / f'{agent}.log',
                log_level_num
            )
        
        # Performance logger
        self.loggers['performance'] = self._create_logger(
            'ai_coding_agency.performance',
            self.log_dir / 'performance.log',
            log_level_num
        )
        
        # Error logger
        self.loggers['errors'] = self._create_logger(
            'ai_coding_agency.errors',
            self.log_dir / 'errors.log',
            log_level_num
        )
        
        # Ollama interaction logger
        self.loggers['ollama'] = self._create_logger(
            'ai_coding_agency.ollama',
            self.log_dir / 'ollama.log',
            log_level_num
        )
    
    def _create_logger(self, name: str, log_file: Path, level: int) -> logging.Logger:
        """Create a logger with file and console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_agent_operation(self, agent: str, operation: str, details: Dict[str, Any] = None):
        """Log agent operations with details"""
        if agent in self.loggers:
            message = f"Operation: {operation}"
            if details:
                message += f" | Details: {json.dumps(details, indent=2)}"
            self.loggers[agent].info(message)
    
    def log_ollama_interaction(self, model: str, prompt: str, response: str = None, 
                              duration: float = None, success: bool = True, error: str = None):
        """Log Ollama interactions with performance metrics"""
        log_data = {
            'model': model,
            'prompt_length': len(prompt),
            'duration_seconds': duration,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if response:
            log_data['response_length'] = len(response)
        
        if error:
            log_data['error'] = error
        
        # Log to ollama logger
        self.loggers['ollama'].info(f"Ollama Interaction: {json.dumps(log_data)}")
        
        # Log performance metrics
        if duration:
            self.log_performance('ollama_interaction', duration, log_data)
    
    def log_performance(self, operation: str, duration: float, metadata: Dict[str, Any] = None):
        """Log performance metrics"""
        perf_data = {
            'operation': operation,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        if metadata:
            perf_data.update(metadata)
        
        self.loggers['performance'].info(f"Performance: {json.dumps(perf_data)}")
        self.performance_log.append(perf_data)
    
    def log_error(self, component: str, error: Exception, context: Dict[str, Any] = None):
        """Log errors with full context and stack trace"""
        error_data = {
            'component': component,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            error_data['context'] = context
        
        # Log to error logger
        self.loggers['errors'].error(f"Error in {component}: {json.dumps(error_data, indent=2)}")
        
        # Also log to component logger if available
        if component in self.loggers:
            self.loggers[component].error(f"Error: {str(error)}")
    
    def log_project_lifecycle(self, project_id: str, stage: str, details: Dict[str, Any] = None):
        """Log project lifecycle events"""
        lifecycle_data = {
            'project_id': project_id,
            'stage': stage,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            lifecycle_data.update(details)
        
        self.loggers['main'].info(f"Project Lifecycle: {json.dumps(lifecycle_data)}")
    
    def log_task_execution(self, project_id: str, task_id: int, task_title: str, 
                          agent: str, status: str, details: Dict[str, Any] = None):
        """Log task execution details"""
        task_data = {
            'project_id': project_id,
            'task_id': task_id,
            'task_title': task_title,
            'agent': agent,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        if details:
            task_data.update(details)
        
        self.loggers['main'].info(f"Task Execution: {json.dumps(task_data)}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        if not self.performance_log:
            return {}
        
        operations = {}
        for entry in self.performance_log:
            op = entry['operation']
            if op not in operations:
                operations[op] = []
            operations[op].append(entry['duration_seconds'])
        
        summary = {}
        for op, durations in operations.items():
            summary[op] = {
                'count': len(durations),
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'total_duration': sum(durations)
            }
        
        return summary
    
    def export_logs(self, output_file: str = None) -> str:
        """Export all logs to a single file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"logs/ai_coding_agency_logs_{timestamp}.txt"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write("AI Coding Agency - Complete Log Export\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            # Performance summary
            f.write("PERFORMANCE SUMMARY\n")
            f.write("-" * 20 + "\n")
            perf_summary = self.get_performance_summary()
            f.write(json.dumps(perf_summary, indent=2))
            f.write("\n\n")
            
            # Recent logs from each component
            for component, logger in self.loggers.items():
                f.write(f"{component.upper()} LOGS\n")
                f.write("-" * (len(component) + 6) + "\n")
                
                # Get recent log entries (last 100 lines)
                log_file = self.log_dir / f"{component}.log"
                if log_file.exists():
                    with open(log_file, 'r') as log_f:
                        lines = log_f.readlines()
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        f.writelines(recent_lines)
                f.write("\n")
        
        return str(output_path)

# Global logger instance
logger = AICodingAgencyLogger()

def get_logger(component: str = 'main') -> logging.Logger:
    """Get logger for a specific component"""
    return logger.loggers.get(component, logger.loggers['main'])

def log_ollama_call(model: str, prompt: str, response: str = None, 
                    duration: float = None, success: bool = True, error: str = None):
    """Convenience function for logging Ollama calls"""
    logger.log_ollama_interaction(model, prompt, response, duration, success, error)

def log_error(component: str, error: Exception, context: Dict[str, Any] = None):
    """Convenience function for logging errors"""
    logger.log_error(component, error, context)

def log_performance(operation: str, duration: float, metadata: Dict[str, Any] = None):
    """Convenience function for logging performance"""
    logger.log_performance(operation, metadata)
