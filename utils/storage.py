#!/usr/bin/env python3
"""
Simple persistent storage for AI Coding Agency projects
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import shutil

class ProjectStorage:
    """Simple file-based storage for projects"""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.storage_dir / "projects").mkdir(exist_ok=True)
        (self.storage_dir / "backups").mkdir(exist_ok=True)
    
    def save_project(self, project_id: str, project_data: Dict[str, Any]) -> bool:
        """Save project data to file"""
        try:
            project_file = self.storage_dir / "projects" / f"{project_id}.json"
            
            # Add metadata
            project_data['_metadata'] = {
                'saved_at': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Save to file
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error saving project {project_id}: {e}")
            return False
    
    def load_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Load project data from file"""
        try:
            project_file = self.storage_dir / "projects" / f"{project_id}.json"
            
            if not project_file.exists():
                return None
            
            with open(project_file, 'r') as f:
                data = json.load(f)
            
            # Remove metadata
            if '_metadata' in data:
                del data['_metadata']
            
            return data
            
        except Exception as e:
            print(f"Error loading project {project_id}: {e}")
            return None
    
    def list_projects(self) -> list:
        """List all saved projects"""
        projects = []
        projects_dir = self.storage_dir / "projects"
        
        if not projects_dir.exists():
            return projects
        
        for project_file in projects_dir.glob("*.json"):
            try:
                with open(project_file, 'r') as f:
                    data = json.load(f)
                
                # Extract basic info
                project_info = {
                    'id': project_file.stem,
                    'name': data.get('name', 'Unknown'),
                    'status': data.get('status', 'unknown'),
                    'saved_at': data.get('_metadata', {}).get('saved_at', 'Unknown')
                }
                projects.append(project_info)
                
            except Exception as e:
                print(f"Error reading project file {project_file}: {e}")
        
        return projects
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        try:
            project_file = self.storage_dir / "projects" / f"{project_id}.json"
            
            if project_file.exists():
                # Create backup before deleting
                backup_file = self.storage_dir / "backups" / f"{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(project_file, backup_file)
                
                # Delete original
                project_file.unlink()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting project {project_id}: {e}")
            return False
    
    def backup_all_projects(self) -> str:
        """Create a backup of all projects"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.storage_dir / "backups" / f"full_backup_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            projects_dir = self.storage_dir / "projects"
            if projects_dir.exists():
                shutil.copytree(projects_dir, backup_dir / "projects", dirs_exist_ok=True)
            
            return str(backup_dir)
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return ""
    
    def restore_project(self, project_id: str, backup_file: str) -> bool:
        """Restore a project from backup"""
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                print(f"Backup file not found: {backup_file}")
                return False
            
            # Load backup data
            with open(backup_path, 'r') as f:
                data = json.load(f)
            
            # Save as current project
            return self.save_project(project_id, data)
            
        except Exception as e:
            print(f"Error restoring project {project_id}: {e}")
            return False
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage statistics"""
        projects_dir = self.storage_dir / "projects"
        backups_dir = self.storage_dir / "backups"
        
        project_count = len(list(projects_dir.glob("*.json"))) if projects_dir.exists() else 0
        backup_count = len(list(backups_dir.glob("*.json"))) if backups_dir.exists() else 0
        
        total_size = 0
        if projects_dir.exists():
            for file_path in projects_dir.glob("*.json"):
                total_size += file_path.stat().st_size
        
        return {
            'total_projects': project_count,
            'total_backups': backup_count,
            'total_size_bytes': total_size,
            'storage_directory': str(self.storage_dir),
            'last_updated': datetime.now().isoformat()
        }

# Global storage instance
storage = ProjectStorage()

def save_project(project_id: str, project_data: Dict[str, Any]) -> bool:
    """Convenience function to save project"""
    return storage.save_project(project_id, project_data)

def load_project(project_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to load project"""
    return storage.load_project(project_id)

def list_saved_projects() -> list:
    """Convenience function to list projects"""
    return storage.list_projects()
