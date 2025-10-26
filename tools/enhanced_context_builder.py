#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Context Builder
Automatically finds and loads relevant project information:
- Latest session notes
- README/PROJECT_STATUS
- Git status
- TODO comments
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from config_manager import get_config


class EnhancedContextBuilder:
    """Build intelligent context automatically"""

    def __init__(self):
        """Initialize enhanced context builder"""
        self.config = get_config()
        self.workspace_root = Path(self.config.workspace_root)
        self.projects_file = self.workspace_root / "projects_index.json"
        self.session_file = self.workspace_root / "session_context.json"
        self.contexts_dir = self.workspace_root / "project_contexts"

    def build_smart_context(
            self,
            project_name: str,
            task_content: str
    ) -> Dict[str, Any]:
        """
        Build intelligent context automatically

        Args:
            project_name: Name of the project
            task_content: Content of task.md

        Returns:
            Enhanced context with all relevant information
        """

        # 1. Get project info
        project_info = self._load_project_info(project_name)
        project_path = Path(project_info['path'])

        # 2. Auto-discover relevant files
        relevant_files = self._discover_project_files(project_path)

        # 3. Load latest session notes
        session_notes = self._load_latest_session(project_path)

        # 4. Get Git status
        git_status = self._get_git_status(project_path)

        # 5. Find TODO comments
        todos = self._find_todos(project_path)

        # 6. Load project README/STATUS
        project_status = self._load_project_status(project_path)

        # 7. Build comprehensive system prompt
        system_prompt = self._build_smart_system_prompt(
            project_info,
            session_notes,
            git_status,
            todos,
            project_status
        )

        # 8. Build user prompt
        user_prompt = self._build_smart_user_prompt(
            task_content,
            relevant_files
        )

        return {
            "project_name": project_name,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "metadata": {
                "project_path": project_info.get('path'),
                "session_notes_found": session_notes is not None,
                "git_status": git_status.get('has_changes', False),
                "todos_count": len(todos),
                "timestamp": datetime.now().isoformat(),
                "estimated_tokens": self._estimate_tokens(system_prompt, user_prompt)
            }
        }

    def _discover_project_files(self, project_path: Path) -> Dict[str, str]:
        """Auto-discover important project files"""

        important_files = {}

        # Priority files to check
        priority_patterns = [
            'README.md',
            'PROJECT_STATUS.md',
            'CHANGELOG.md',
            'TODO.md',
            'docs/STATUS.md',
            'docs/PROJECT.md'
        ]

        for pattern in priority_patterns:
            file_path = project_path / pattern
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Limit to first 2000 chars
                    important_files[pattern] = content[:2000]
                except Exception:
                    pass

        return important_files

    def _load_latest_session(self, project_path: Path) -> Optional[str]:
        """Load latest session notes from docs/sessions/"""

        sessions_dir = project_path / "docs" / "sessions"

        if not sessions_dir.exists():
            return None

        # Find all session files
        session_files = sorted(sessions_dir.glob("*.md"), reverse=True)

        if not session_files:
            return None

        # Load latest session
        latest = session_files[0]
        try:
            content = latest.read_text(encoding='utf-8')
            # Get last 3000 chars (most recent info)
            return content[-3000:]
        except Exception:
            return None

    def _get_git_status(self, project_path: Path) -> Dict[str, Any]:
        """Get Git status of project"""

        try:
            import subprocess

            # Check if git repo
            git_dir = project_path / ".git"
            if not git_dir.exists():
                return {"is_repo": False}

            # Get status
            result = subprocess.run(
                ['git', 'status', '--short'],
                cwd=project_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {"is_repo": True, "error": True}

            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []

            # Get current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

            return {
                "is_repo": True,
                "has_changes": len(changes) > 0,
                "changed_files": changes[:10],  # Max 10
                "branch": branch
            }

        except Exception:
            return {"is_repo": False}

    def _find_todos(self, project_path: Path) -> List[str]:
        """Find TODO comments in code"""

        todos = []

        # Search in common source directories
        search_dirs = [
            project_path / "src",
            project_path / "tests",
            project_path
        ]

        todo_pattern = re.compile(r'#\s*TODO:?\s*(.+)', re.IGNORECASE)

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            # Search Python files
            for py_file in search_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    matches = todo_pattern.findall(content)
                    for match in matches:
                        rel_path = py_file.relative_to(project_path)
                        todos.append(f"{rel_path}: {match.strip()}")

                        if len(todos) >= 10:  # Max 10 TODOs
                            return todos
                except Exception:
                    pass

        return todos

    def _load_project_status(self, project_path: Path) -> Optional[str]:
        """Load project status/README"""

        # Try multiple file names
        status_files = [
            "PROJECT_STATUS.md",
            "README.md",
            "STATUS.md"
        ]

        for filename in status_files:
            file_path = project_path / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Return first 2000 chars
                    return content[:2000]
                except Exception:
                    pass

        return None

    def _load_project_info(self, project_name: str) -> Dict[str, Any]:
        """Load project info from projects_index.json"""

        with open(self.projects_file, 'r', encoding='utf-8') as f:
            projects_index = json.load(f)

        for project in projects_index.get('projects', []):
            if project['name'] == project_name:
                return project

        raise ValueError(f"Project '{project_name}' not found in projects_index.json")

    def _build_smart_system_prompt(
            self,
            project_info: Dict[str, Any],
            session_notes: Optional[str],
            git_status: Dict[str, Any],
            todos: List[str],
            project_status: Optional[str]
    ) -> str:
        """Build comprehensive system prompt"""

        prompt = f"""You are an expert {project_info.get('language', 'Python')} developer analyzing project: {project_info['name']}

PROJECT INFO:
Name: {project_info['name']}
Description: {project_info.get('description', 'N/A')}
Path: {project_info.get('path')}
Language: {project_info.get('language', 'Python')}

"""

        # Add latest session info
        if session_notes:
            prompt += f"""LATEST SESSION NOTES:
{session_notes}

"""

        # Add project status
        if project_status:
            prompt += f"""PROJECT STATUS:
{project_status}

"""

        # Add Git status
        if git_status.get('is_repo'):
            prompt += f"""GIT STATUS:
Branch: {git_status.get('branch', 'unknown')}
Has changes: {git_status.get('has_changes', False)}
"""
            if git_status.get('changed_files'):
                prompt += "Changed files:\n"
                for file in git_status['changed_files'][:5]:
                    prompt += f"  - {file}\n"
            prompt += "\n"

        # Add TODOs
        if todos:
            prompt += "FOUND TODO COMMENTS:\n"
            for todo in todos[:5]:
                prompt += f"  - {todo}\n"
            prompt += "\n"

        prompt += """YOUR ROLE:
When user asks for "next steps" or "what to do next":
1. Analyze current project status from session notes
2. Check what's completed and what's in progress
3. Identify blockers or failing tests
4. Suggest concrete, actionable next steps
5. Prioritize based on importance and dependencies

CRITICAL: ALWAYS respond in Slovak language (slovenčina).
Use clear, professional Slovak technical terminology.

Provide specific, actionable recommendations.
Be concise but thorough.
Format response clearly with:
- Current status summary
- Identified issues/blockers
- Concrete next steps (numbered)
- Priority ranking
"""

        return prompt

    def _build_smart_user_prompt(
            self,
            task_content: str,
            relevant_files: Dict[str, str]
    ) -> str:
        """Build user prompt with discovered files"""

        prompt = f"""# Current Task

{task_content}

"""

        # Add discovered files
        if relevant_files:
            prompt += "# Relevant Project Files\n\n"
            for filename, content in relevant_files.items():
                prompt += f"## {filename}\n\n```\n{content}\n```\n\n"

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
        max_messages = self.config.max_history_messages * 2
        if len(session['conversation_history']) > max_messages:
            session['conversation_history'] = session['conversation_history'][-max_messages:]

        # Save
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Test enhanced context builder
    print("Testing Enhanced Context Builder...")
    print("=" * 60)

    try:
        builder = EnhancedContextBuilder()

        # Test with nex-genesis-server
        test_task = """PROJECT: nex-genesis-server
TASK: Analyzuj projekt a navrhni ďalšie kroky
PRIORITY: NORMAL

Chcem vedieť čo je ďalší krok v projekte.
"""

        context = builder.build_smart_context(
            project_name="nex-genesis-server",
            task_content=test_task
        )

        print("✅ Smart context built successfully!")
        print(f"\n📊 Metadata:")
        print(f"   Session notes found: {context['metadata']['session_notes_found']}")
        print(f"   Git changes: {context['metadata']['git_status']}")
        print(f"   TODOs found: {context['metadata']['todos_count']}")
        print(f"   Estimated tokens: ~{context['metadata']['estimated_tokens']}")

        print("\n" + "=" * 60)
        print("✅ Enhanced Context Builder ready!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()