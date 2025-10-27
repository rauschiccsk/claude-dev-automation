"""
enhanced_context_builder.py - Smart context builder with auto-discovery
Automatically loads session notes, Git status, TODOs, and project files
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class EnhancedContextBuilder:
    """Builds smart context with automatic discovery of project information."""

    def __init__(self):
        """Initialize enhanced context builder."""
        self.max_session_chars = 3000
        self.max_file_chars = 2000
        self.max_todos = 10
        self.max_git_files = 10

    def build_context(
        self,
        project_name: str,
        project_path: Path,
        task_description: str = '',
        additional_notes: str = ''
    ) -> str:
        """
        Build comprehensive smart context.

        Args:
            project_name: Name of the project
            project_path: Path to project directory
            task_description: Task description/context
            additional_notes: Additional notes

        Returns:
            Complete context string for Claude
        """
        context_parts = []

        # 1. System prompt (Slovak language enforcement)
        context_parts.append(self._build_system_prompt())

        # 2. Project header
        context_parts.append(f"\n# 📁 Project: {project_name}\n")
        context_parts.append(f"**Path:** `{project_path}`\n")
        context_parts.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 3. Session notes (auto-loaded from docs/sessions/)
        session_notes = self._load_latest_session_notes(project_path)
        if session_notes:
            context_parts.append("\n## 📝 Recent Session Notes\n")
            context_parts.append(session_notes)

        # 4. Project status files (README, STATUS, etc.)
        project_status = self._load_project_status(project_path)
        if project_status:
            context_parts.append("\n## 📊 Project Status\n")
            context_parts.append(project_status)

        # 5. Git status
        git_status = self._get_git_info(project_path)
        if git_status:
            context_parts.append("\n## 🔀 Git Status\n")
            context_parts.append(git_status)

        # 6. TODO comments
        todos = self._find_todo_comments(project_path)
        if todos:
            context_parts.append("\n## ✅ TODO Comments Found\n")
            context_parts.append(f"Found {len(todos)} TODO items in code:\n\n")
            for i, todo in enumerate(todos[:self.max_todos], 1):
                context_parts.append(f"{i}. **{todo['file']}:{todo['line']}**\n")
                context_parts.append(f"   `{todo['text']}`\n\n")

        # 7. Task description
        if task_description:
            context_parts.append("\n## 🎯 Task Context\n")
            context_parts.append(task_description + "\n")

        # 8. Additional notes
        if additional_notes:
            context_parts.append("\n## 📌 Additional Notes\n")
            context_parts.append(additional_notes + "\n")

        return ''.join(context_parts)

    def _build_system_prompt(self) -> str:
        """Build system prompt with Slovak language enforcement."""
        return """
# SYSTEM INSTRUCTIONS

**CRITICAL: ALWAYS respond in Slovak language.**

You are an expert software development assistant. Your role is to:
- Analyze projects and provide actionable recommendations
- Write clean, maintainable code when requested
- Consider project context and history
- Be specific and practical

**Response Format:**
1. **For analysis tasks:** Provide thorough Slovak analysis with clear structure
2. **For code changes:** Use FILE_OPERATION format (CREATE/MODIFY/DELETE)
3. **Always:** Respond in Slovak, explain reasoning, be actionable

**Slovak Language Rules:**
- ALL sections, headers, explanations MUST be in Slovak
- Technical terms can remain in English if commonly used (e.g., "API", "Git")
- Code comments should be in Slovak
- Documentation should be in Slovak

---
"""

    def _load_latest_session_notes(self, project_path: Path) -> Optional[str]:
        """
        Load latest session notes from docs/sessions/ directory.

        Args:
            project_path: Project directory path

        Returns:
            Session notes content (last N chars) or None
        """
        sessions_dir = project_path / 'docs' / 'sessions'

        if not sessions_dir.exists():
            return None

        # Find latest session file
        session_files = sorted(
            sessions_dir.glob('*.md'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not session_files:
            return None

        latest_file = session_files[0]

        try:
            content = latest_file.read_text(encoding='utf-8')

            # Take last N chars (most recent info at end)
            if len(content) > self.max_session_chars:
                content = "...\n" + content[-self.max_session_chars:]

            return f"**Latest session:** `{latest_file.name}`\n\n```\n{content}\n```\n"

        except Exception as e:
            return f"⚠️ Could not read session notes: {e}\n"

    def _load_project_status(self, project_path: Path) -> Optional[str]:
        """
        Load project status from README, STATUS, etc.

        Args:
            project_path: Project directory path

        Returns:
            Project status content or None
        """
        status_files = [
            'PROJECT_STATUS.md',
            'STATUS.md',
            'README.md',
            'readme.md'
        ]

        for filename in status_files:
            filepath = project_path / filename
            if filepath.exists():
                try:
                    content = filepath.read_text(encoding='utf-8')

                    # Take first N chars
                    if len(content) > self.max_file_chars:
                        content = content[:self.max_file_chars] + "\n..."

                    return f"**From:** `{filename}`\n\n```\n{content}\n```\n"

                except Exception as e:
                    continue

        return None

    def _get_git_info(self, project_path: Path) -> Optional[str]:
        """
        Get Git status information.

        Args:
            project_path: Project directory path

        Returns:
            Git status information or None
        """
        try:
            # Check if it's a Git repo
            git_dir = project_path / '.git'
            if not git_dir.exists():
                return None

            info_parts = []

            # Current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if branch_result.returncode == 0:
                branch = branch_result.stdout.strip()
                info_parts.append(f"**Branch:** `{branch}`\n")

            # Status
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if status_result.returncode == 0:
                status_lines = status_result.stdout.strip().split('\n')
                if status_lines and status_lines[0]:
                    info_parts.append(f"**Uncommitted changes:** {len(status_lines)} files\n\n")

                    # Show first N files
                    info_parts.append("**Changed files:**\n")
                    for line in status_lines[:self.max_git_files]:
                        if line:
                            info_parts.append(f"- `{line}`\n")

                    if len(status_lines) > self.max_git_files:
                        info_parts.append(f"- ... and {len(status_lines) - self.max_git_files} more\n")
                else:
                    info_parts.append("**Status:** Clean (no uncommitted changes)\n")

            return ''.join(info_parts) if info_parts else None

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return None

    def _find_todo_comments(self, project_path: Path) -> List[Dict[str, Any]]:
        """
        Find TODO comments in Python files.

        Args:
            project_path: Project directory path

        Returns:
            List of TODO items with file, line, and text
        """
        todos = []

        # Directories to search
        search_dirs = ['src', 'tests', 'tools']

        # TODO patterns
        todo_pattern = re.compile(r'#\s*(TODO|FIXME|HACK|XXX):\s*(.+)', re.IGNORECASE)

        for dir_name in search_dirs:
            search_path = project_path / dir_name
            if not search_path.exists():
                continue

            # Find all Python files
            for py_file in search_path.rglob('*.py'):
                try:
                    content = py_file.read_text(encoding='utf-8')

                    for line_num, line in enumerate(content.split('\n'), 1):
                        match = todo_pattern.search(line)
                        if match:
                            todos.append({
                                'file': str(py_file.relative_to(project_path)),
                                'line': line_num,
                                'type': match.group(1).upper(),
                                'text': match.group(2).strip()
                            })

                            if len(todos) >= self.max_todos:
                                return todos

                except Exception:
                    continue

        return todos


# Example usage and testing
if __name__ == "__main__":
    print("[TEST] Testing EnhancedContextBuilder...\n")

    builder = EnhancedContextBuilder()

    # Test with current project
    project_path = Path.cwd()
    project_name = project_path.name

    print(f"[INFO] Building context for: {project_name}")
    print(f"       Path: {project_path}\n")

    context = builder.build_context(
        project_name=project_name,
        project_path=project_path,
        task_description="Test task for context builder",
        additional_notes="Testing automatic context discovery"
    )

    print(f"[OK] Context built: {len(context)} characters\n")
    print("="*60)
    print("Preview (first 1000 chars):")
    print("="*60)
    print(context[:1000])
    print("="*60)

    # Count sections
    sections = [
        'Session Notes',
        'Project Status',
        'Git Status',
        'TODO Comments'
    ]

    print("\n[INFO] Context sections included:")
    for section in sections:
        if section in context:
            print(f"       [OK] {section}")
        else:
            print(f"       [ ] {section}")

    print("\n[OK] Test completed!")