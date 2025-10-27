"""
Enhanced Context Builder
Builds smart context from project files, session notes, Git status, and TODO comments.
"""

import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class EnhancedContextBuilder:
    """Builds smart context for Claude API calls."""

    def __init__(self, projects_path: str = "C:/Development"):
        """
        Initialize context builder.

        Args:
            projects_path: Base path where projects are located
        """
        self.projects_path = Path(projects_path)

    def build_context(
        self,
        project_name: str,
        task_description: str
    ) -> str:
        """
        Build comprehensive context for task.

        Args:
            project_name: Name of the project
            task_description: Task description

        Returns:
            Formatted context string
        """
        context_parts = []

        # Find project
        project_path = self._find_project_path(project_name)
        if not project_path:
            return f"Project '{project_name}' not found in {self.projects_path}"

        context_parts.append(f"# Project: {project_name}\n")
        context_parts.append(f"Path: {project_path}\n\n")

        # Session notes (latest 3000 chars)
        session_notes = self._load_latest_session_notes(project_path)
        if session_notes:
            context_parts.append("## Latest Session Notes\n\n")
            context_parts.append(session_notes[:3000] + "\n\n")

        # README or STATUS
        readme = self._load_readme(project_path)
        if readme:
            context_parts.append("## Project Overview\n\n")
            context_parts.append(readme[:2000] + "\n\n")

        # Git status
        git_status = self._get_git_status(project_path)
        if git_status:
            context_parts.append("## Git Status\n\n")
            context_parts.append(git_status + "\n\n")

        # TODO comments
        todos = self._find_todo_comments(project_path)
        if todos:
            context_parts.append("## TODO Comments\n\n")
            for todo in todos[:10]:  # Max 10 TODOs
                context_parts.append(f"- {todo}\n")
            context_parts.append("\n")

        return "".join(context_parts)

    def _find_project_path(self, project_name: str) -> Optional[Path]:
        """Find project directory."""
        project_path = self.projects_path / project_name

        if project_path.exists() and project_path.is_dir():
            return project_path

        return None

    def _load_latest_session_notes(self, project_path: Path) -> Optional[str]:
        """Load most recent session notes."""
        sessions_dir = project_path / "docs" / "sessions"

        if not sessions_dir.exists():
            return None

        # Find latest session file
        session_files = sorted(sessions_dir.glob("*.md"), reverse=True)

        if not session_files:
            return None

        try:
            return session_files[0].read_text(encoding='utf-8')
        except Exception as e:
            print(f"[WARNING] Failed to read session notes: {e}")
            return None

    def _load_readme(self, project_path: Path) -> Optional[str]:
        """Load README or STATUS file."""
        # Try README.md
        readme_path = project_path / "README.md"
        if readme_path.exists():
            try:
                return readme_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"[WARNING] Failed to read README: {e}")

        # Try STATUS.md
        status_path = project_path / "STATUS.md"
        if status_path.exists():
            try:
                return status_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"[WARNING] Failed to read STATUS: {e}")

        return None

    def _get_git_status(self, project_path: Path) -> Optional[str]:
        """Get Git status information."""
        try:
            # Check if it's a git repo
            git_dir = project_path / ".git"
            if not git_dir.exists():
                return None

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return None

            branch = result.stdout.strip()
            status_lines = [f"Current branch: {branch}"]

            # Get status
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and result.stdout.strip():
                status_lines.append("\nUncommitted changes:")
                status_lines.append(result.stdout.strip())
            else:
                status_lines.append("Working tree clean")

            return "\n".join(status_lines)

        except Exception as e:
            print(f"[WARNING] Failed to get git status: {e}")
            return None

    def _find_todo_comments(self, project_path: Path) -> List[str]:
        """Find TODO comments in code."""
        todos = []

        # Search in common code files
        extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']

        try:
            for ext in extensions:
                for file_path in project_path.rglob(f"*{ext}"):
                    # Skip common directories
                    if any(skip in str(file_path) for skip in [
                        'node_modules', 'venv', '.venv', '__pycache__',
                        '.git', 'dist', 'build'
                    ]):
                        continue

                    try:
                        content = file_path.read_text(encoding='utf-8')

                        for line_num, line in enumerate(content.splitlines(), 1):
                            if 'TODO' in line or 'FIXME' in line:
                                rel_path = file_path.relative_to(project_path)
                                todos.append(f"{rel_path}:{line_num}: {line.strip()}")

                    except Exception:
                        continue

        except Exception as e:
            print(f"[WARNING] Failed to search TODO comments: {e}")

        return todos


# Test section
if __name__ == "__main__":
    print("\n[TEST] Testing EnhancedContextBuilder...")

    try:
        builder = EnhancedContextBuilder()

        # Test with claude-dev-automation project
        print(f"\n[INFO] Building context for claude-dev-automation...")
        context = builder.build_context(
            project_name="claude-dev-automation",
            task_description="Test context building"
        )

        print(f"\n[OK] Context built successfully:")
        print(f"     Context size: {len(context)} chars")
        print(f"\n[INFO] Context preview (first 500 chars):")
        print("-" * 60)
        print(context[:500])
        print("-" * 60)

        print("\n[SUCCESS] EnhancedContextBuilder test completed!")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()