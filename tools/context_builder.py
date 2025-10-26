#!/usr/bin/env python3
"""
Context Builder
Builds minimal context for Claude API calls to minimize token usage
Target: ~5k tokens instead of 40k chat initialization
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from config_manager import get_config

class ContextBuilder:
    """Build minimal context for API calls"""
    
    def __init__(self):
        """Initialize context builder"""
        self.config = get_config()
        self.workspace_root = Path(self.config.workspace_root)
        self.projects_file = self.workspace_root / "projects_index.json"
        self.session_file = self.workspace_root / "session_context.json"
        self.contexts_dir = self.workspace_root / "project_contexts"
        
    def build_context(
        self,
        project_name: str,
        task_content: str,
        include_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build minimal context for a task
        
        Args:
            project_name: Name of the project
            task_content: Content of task.md
            include_files: Optional list of file paths to include
            
        Returns:
            Context dict with all necessary information
        """
        
        # 1. Load project info
        project_info = self._load_project_info(project_name)
        
        # 2. Load project context (minimal)
        project_context = self._load_project_context(project_name)
        
        # 3. Load recent conversation history (last 5 messages)
        history = self._load_recent_history()
        
        # 4. Load file contents if specified
        file_contents = self._load_files(project_info.get('path'), include_files or [])
        
        # 5. Build system prompt
        system_prompt = self._build_system_prompt(project_info, project_context)
        
        # 6. Build user prompt
        user_prompt = self._build_user_prompt(
            task_content, 
            project_context,
            history,
            file_contents
        )
        
        return {
            "project_name": project_name,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "metadata": {
                "project_path": project_info.get('path'),
                "timestamp": datetime.now().isoformat(),
                "estimated_tokens": self._estimate_tokens(system_prompt, user_prompt)
            }
        }
    
    def _load_project_info(self, project_name: str) -> Dict[str, Any]:
        """Load project info from projects_index.json"""
        
        with open(self.projects_file, 'r', encoding='utf-8') as f:
            projects_index = json.load(f)
        
        for project in projects_index.get('projects', []):
            if project['name'] == project_name:
                return project
        
        raise ValueError(f"Project '{project_name}' not found in projects_index.json")
    
    def _load_project_context(self, project_name: str) -> Dict[str, Any]:
        """Load minimal project context"""
        
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
    
    def _load_recent_history(self, max_messages: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load recent conversation history"""
        
        max_messages = max_messages or self.config.max_history_messages
        
        if not self.session_file.exists():
            return []
        
        with open(self.session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
        
        history = session.get('conversation_history', [])
        
        # Return last N messages
        return history[-max_messages:] if history else []
    
    def _load_files(self, project_path: str, file_paths: List[str]) -> Dict[str, str]:
        """Load contents of specified files"""
        
        contents = {}
        project_root = Path(project_path)
        
        for file_path in file_paths:
            full_path = project_root / file_path
            
            if full_path.exists() and full_path.is_file():
                try:
                    # Check file size (skip if too large)
                    max_size_kb = self.config.get('context_limits.max_file_size_kb', 500)
                    size_kb = full_path.stat().st_size / 1024
                    
                    if size_kb > max_size_kb:
                        contents[file_path] = f"[File too large: {size_kb:.1f}KB > {max_size_kb}KB]"
                        continue
                    
                    with open(full_path, 'r', encoding='utf-8') as f:
                        contents[file_path] = f.read()
                        
                except Exception as e:
                    contents[file_path] = f"[Error reading file: {e}]"
        
        return contents
    
    def _build_system_prompt(
        self, 
        project_info: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> str:
        """Build system prompt for Claude"""
        
        prompt = f"""You are an expert {project_info.get('language', 'Python')} developer working on: {project_info['name']}

PROJECT: {project_info['name']}
DESCRIPTION: {project_info.get('description', 'N/A')}
PATH: {project_info.get('path')}

"""
        
        # Add project-specific context if available
        if project_context.get('description'):
            prompt += f"CONTEXT: {project_context['description']}\n\n"
        
        if project_context.get('key_files'):
            prompt += "KEY FILES:\n"
            for file in project_context['key_files']:
                prompt += f"  - {file}\n"
            prompt += "\n"
        
        if project_context.get('notes'):
            prompt += "IMPORTANT NOTES:\n"
            for note in project_context['notes'][:3]:  # Max 3 notes
                prompt += f"  - {note}\n"
            prompt += "\n"
        
        prompt += """YOUR ROLE:
- Analyze the task carefully
- Generate clean, production-ready code
- Follow project conventions
- Provide clear explanations
- Be concise but thorough

OUTPUT FORMAT:
- Use ```language code blocks for code
- Specify exact file paths for each code block
- Provide clear instructions for file operations
- Explain any important decisions
"""
        
        return prompt
    
    def _build_user_prompt(
        self,
        task_content: str,
        project_context: Dict[str, Any],
        history: List[Dict[str, Any]],
        file_contents: Dict[str, str]
    ) -> str:
        """Build user prompt with task and context"""
        
        prompt = "# Current Task\n\n"
        prompt += task_content + "\n\n"
        
        # Add recent changes context if available
        if project_context.get('recent_changes'):
            prompt += "# Recent Changes\n\n"
            for change in project_context['recent_changes'][:3]:  # Last 3 changes
                prompt += f"- {change}\n"
            prompt += "\n"
        
        # Add conversation history if available
        if history:
            prompt += "# Recent Conversation\n\n"
            for msg in history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')[:200]  # First 200 chars
                prompt += f"**{role}:** {content}...\n\n"
        
        # Add file contents if specified
        if file_contents:
            prompt += "# File Contents\n\n"
            for file_path, content in file_contents.items():
                prompt += f"## {file_path}\n\n```\n{content}\n```\n\n"
        
        return prompt
    
    def _estimate_tokens(self, system_prompt: str, user_prompt: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)"""
        total_chars = len(system_prompt) + len(user_prompt)
        return total_chars // 4
    
    def update_session_history(
        self,
        role: str,
        content: str,
        tokens_used: int
    ):
        """Add message to session history"""
        
        # Load current session
        if self.session_file.exists():
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
        else:
            session = {
                "conversation_history": [],
                "total_tokens_used": 0,
                "sessions_count": 0
            }
        
        # Add message
        session['conversation_history'].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens_used
        })
        
        # Update totals
        session['total_tokens_used'] += tokens_used
        session['last_updated'] = datetime.now().isoformat()
        
        # Keep only last N messages
        max_messages = self.config.max_history_messages * 2  # Store more, use less
        if len(session['conversation_history']) > max_messages:
            session['conversation_history'] = session['conversation_history'][-max_messages:]
        
        # Save
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Test context builder
    print("Testing Context Builder...")
    print("=" * 60)
    
    try:
        builder = ContextBuilder()
        
        # Test building context
        test_task = """PROJECT: uae-legal-agent
TASK: Test context builder
PRIORITY: LOW

This is a test task to verify context builder works correctly.
"""
        
        context = builder.build_context(
            project_name="uae-legal-agent",
            task_content=test_task
        )
        
        print("✅ Context built successfully!")
        print(f"\n📊 Estimated tokens: {context['metadata']['estimated_tokens']}")
        print(f"\n📝 System prompt length: {len(context['system_prompt'])} chars")
        print(f"📝 User prompt length: {len(context['user_prompt'])} chars")
        
        print(f"\n🎯 Target: <5000 tokens")
        print(f"   Actual: ~{context['metadata']['estimated_tokens']} tokens")
        
        if context['metadata']['estimated_tokens'] < 5000:
            print("   ✅ Within target!")
        else:
            print("   ⚠️  Exceeds target - optimization needed")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")