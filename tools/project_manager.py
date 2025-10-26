#!/usr/bin/env python3
"""
Project Manager
Handles project switching and context management
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from config_manager import get_config

class ProjectManager:
    """Manage multiple projects and their contexts"""
    
    def __init__(self):
        """Initialize project manager"""
        self.config = get_config()
        self.workspace_root = Path(self.config.workspace_root)
        self.projects_file = self.workspace_root / "projects_index.json"
        self.session_file = self.workspace_root / "session_context.json"
        self.contexts_dir = self.workspace_root / "project_contexts"
        
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get list of all projects"""
        
        with open(self.projects_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('projects', [])
    
    def get_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get specific project by name"""
        
        projects = self.get_all_projects()
        
        for project in projects:
            if project['name'] == project_name:
                return project
        
        return None
    
    def get_current_project(self) -> Optional[str]:
        """Get currently active project"""
        
        if not self.session_file.exists():
            return None
        
        with open(self.session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
        
        return session.get('current_project')
    
    def switch_project(self, project_name: str) -> Dict[str, Any]:
        """
        Switch to different project
        
        Args:
            project_name: Name of project to switch to
            
        Returns:
            Result dict with project info
        """
        
        # Verify project exists
        project = self.get_project(project_name)
        
        if not project:
            return {
                "success": False,
                "error": f"Project '{project_name}' not found"
            }
        
        # Update session
        if self.session_file.exists():
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
        else:
            session = {
                "conversation_history": [],
                "total_tokens_used": 0
            }
        
        old_project = session.get('current_project')
        session['current_project'] = project_name
        session['last_updated'] = datetime.now().isoformat()
        session['last_switch'] = {
            "from": old_project,
            "to": project_name,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        
        # Load project context
        context = self.load_project_context(project_name)
        
        return {
            "success": True,
            "project": project,
            "context": context,
            "previous_project": old_project
        }
    
    def load_project_context(self, project_name: str) -> Dict[str, Any]:
        """Load project context from file"""
        
        context_file = self.contexts_dir / f"{project_name}_context.json"
        
        if not context_file.exists():
            return {
                "project_name": project_name,
                "description": "",
                "key_files": [],
                "recent_changes": [],
                "notes": []
            }
        
        with open(context_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_project_context(
        self,
        project_name: str,
        context: Dict[str, Any]
    ):
        """Save project context to file"""
        
        context_file = self.contexts_dir / f"{project_name}_context.json"
        context['last_updated'] = datetime.now().isoformat()
        
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)
    
    def update_project_context(
        self,
        project_name: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update specific fields in project context
        
        Args:
            project_name: Project name
            updates: Dict with fields to update
            
        Returns:
            Updated context
        """
        
        context = self.load_project_context(project_name)
        context.update(updates)
        self.save_project_context(project_name, context)
        
        return context
    
    def add_recent_change(
        self,
        project_name: str,
        change_description: str,
        max_changes: int = 10
    ):
        """Add change to recent changes list"""
        
        context = self.load_project_context(project_name)
        
        recent_changes = context.get('recent_changes', [])
        recent_changes.insert(0, {
            "description": change_description,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last N changes
        context['recent_changes'] = recent_changes[:max_changes]
        
        self.save_project_context(project_name, context)
    
    def add_note(
        self,
        project_name: str,
        note: str
    ):
        """Add note to project context"""
        
        context = self.load_project_context(project_name)
        
        notes = context.get('notes', [])
        notes.append({
            "note": note,
            "timestamp": datetime.now().isoformat()
        })
        
        context['notes'] = notes
        self.save_project_context(project_name, context)
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Get statistics about all projects"""
        
        projects = self.get_all_projects()
        current = self.get_current_project()
        
        stats = {
            "total_projects": len(projects),
            "active_projects": len([p for p in projects if p['status'] == 'active']),
            "current_project": current,
            "projects_by_language": {}
        }
        
        # Count by language
        for project in projects:
            lang = project.get('language', 'unknown')
            stats['projects_by_language'][lang] = stats['projects_by_language'].get(lang, 0) + 1
        
        return stats


if __name__ == "__main__":
    # Test project manager
    print("Testing Project Manager...")
    print("=" * 60)
    
    try:
        pm = ProjectManager()
        
        # Test 1: Get all projects
        print("\n1. All projects:")
        projects = pm.get_all_projects()
        print(f"   Total: {len(projects)} projects")
        for proj in projects:
            print(f"   - {proj['name']}")
        
        # Test 2: Get current project
        print("\n2. Current project:")
        current = pm.get_current_project()
        print(f"   Active: {current or 'None'}")
        
        # Test 3: Switch project
        print("\n3. Switch to uae-legal-agent:")
        result = pm.switch_project("uae-legal-agent")
        if result['success']:
            print(f"   ✅ Switched to: {result['project']['name']}")
            print(f"   Previous: {result['previous_project']}")
        else:
            print(f"   ❌ Failed: {result['error']}")
        
        # Test 4: Load context
        print("\n4. Project context:")
        context = pm.load_project_context("uae-legal-agent")
        print(f"   Description: {context.get('description') or 'N/A'}")
        print(f"   Key files: {len(context.get('key_files', []))}")
        print(f"   Recent changes: {len(context.get('recent_changes', []))}")
        
        # Test 5: Stats
        print("\n5. Project statistics:")
        stats = pm.get_project_stats()
        print(f"   Total projects: {stats['total_projects']}")
        print(f"   Active projects: {stats['active_projects']}")
        print(f"   By language: {stats['projects_by_language']}")
        
        print("\n" + "=" * 60)
        print("✅ Project Manager test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")