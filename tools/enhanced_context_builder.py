"""
Enhanced Context Builder with Smart File Detection
Builds smart context from project files, session notes, Git status, and TODO comments.
For MODIFY operations, loads complete file content for Claude to regenerate.
"""

import subprocess
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime


class EnhancedContextBuilder:
    """Builds smart context for Claude API calls with intelligent file loading."""

    # Keywords for operation detection
    CREATE_KEYWORDS = ['vytvor', 'create', 'pridaj', 'nový', 'novy', 'new', 'add']
    MODIFY_KEYWORDS = ['oprav', 'fix', 'updatuj', 'update', 'zmeň', 'zmen', 'change',
                       'upraviť', 'upravit', 'modify', 'edit']

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
        For MODIFY operations, includes full content of files to be modified.

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

        # ===== CRITICAL: ADD TASK DESCRIPTION FIRST =====
        context_parts.append(f"## 🎯 YOUR TASK\n\n")
        context_parts.append(f"**TASK:** {task_description}\n\n")
        context_parts.append(f"READ THIS TASK TWICE. DO ONLY WHAT IT EXPLICITLY ASKS.\n\n")
        # ================================================

        # Detect operation type and extract file paths
        file_paths = self._extract_file_paths(task_description)
        op_type, confidence = self._detect_operation_type(task_description, project_path, file_paths)

        context_parts.append(f"## Task Analysis\n\n")
        context_parts.append(f"**Operation Type:** {op_type} (confidence: {confidence}%)\n")
        if file_paths:
            files_status = []
            for fp in file_paths:
                exists = (project_path / fp).exists()
                status = "EXISTS" if exists else "NEW"
                files_status.append(f"{fp} ({status})")
            context_parts.append(f"**Target Files:** {', '.join(files_status)}\n")
        context_parts.append("\n")

        # For MODIFY operations, load target files
        if op_type == "MODIFY" and file_paths:
            context_parts.append("## Target Files Content\n\n")
            for file_path in file_paths:
                content = self._load_file_content(project_path, file_path)
                if content:
                    context_parts.append(f"### File: `{file_path}`\n\n")
                    context_parts.append(f"```python\n{content}\n```\n\n")
                else:
                    context_parts.append(f"### File: `{file_path}` (NOT FOUND)\n\n")
                    context_parts.append("*This file does not exist yet. Will be created.*\n\n")

            # Load related files (tests, dependencies)
            related = self._find_related_files(project_path, file_paths)
            if related:
                context_parts.append("## Related Files\n\n")
                for rel_path in related[:3]:  # Max 3 related files
                    content = self._load_file_content(project_path, rel_path)
                    if content:
                        context_parts.append(f"### Related: `{rel_path}`\n\n")
                        # Truncate long files
                        if len(content) > 2000:
                            content = content[:2000] + "\n... (truncated)"
                        context_parts.append(f"```python\n{content}\n```\n\n")

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

        return "".join(context_parts)

    def _detect_operation_type(self, task_description: str, project_path: Path, file_paths: List[str]) -> Tuple[str, int]:
        """
        Detect if task is CREATE or MODIFY operation.
        Uses both keyword analysis and file existence check.

        Returns:
            Tuple of (operation_type, confidence_percentage)
        """
        task_lower = task_description.lower()

        create_score = sum(1 for keyword in self.CREATE_KEYWORDS if keyword in task_lower)
        modify_score = sum(1 for keyword in self.MODIFY_KEYWORDS if keyword in task_lower)

        # Check if target files exist
        files_exist = []
        for file_path in file_paths:
            full_path = project_path / file_path
            files_exist.append(full_path.exists())

        # Decision logic: File existence is PRIMARY indicator
        if any(files_exist):
            # At least one file exists → MODIFY operation
            if modify_score > 0:
                # Has MODIFY keywords AND file exists → HIGH confidence
                confidence = min(100, (modify_score * 30) + 70)
            else:
                # File exists but no MODIFY keywords → MEDIUM confidence
                # (user might have used ambiguous language)
                confidence = 75
            return "MODIFY", confidence
        else:
            # No files exist → CREATE operation
            if create_score > 0:
                confidence = min(100, (create_score * 30) + 60)
            else:
                # No files exist, no clear keywords → assume CREATE
                confidence = 60
            return "CREATE", confidence

    def _extract_file_paths(self, task_description: str) -> List[str]:
        """
        Extract file paths from task description.

        Looks for patterns like:
        - utils/config.py
        - models/case.py
        - services/pdf_extractor.py
        """
        # Pattern: word/word.ext or word.ext
        pattern = r'(?:[\w-]+/)*[\w-]+\.(?:py|js|ts|java|cpp|h|md|txt|json|yaml|yml)'

        matches = re.findall(pattern, task_description)

        # Remove duplicates while preserving order
        seen = set()
        unique_matches = []
        for match in matches:
            if match not in seen:
                seen.add(match)
                unique_matches.append(match)

        return unique_matches

    def _load_file_content(self, project_path: Path, file_path: str) -> Optional[str]:
        """Load content of a specific file."""
        full_path = project_path / file_path

        if not full_path.exists():
            return None

        try:
            return full_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"[WARNING] Failed to read {file_path}: {e}")
            return None

    def _find_related_files(self, project_path: Path, target_files: List[str]) -> List[str]:
        """
        Find files related to target files.

        For example:
        - utils/config.py → tests/test_config.py
        - models/case.py → tests/test_case.py
        """
        related = []

        for target in target_files:
            # Extract base name without extension
            path_obj = Path(target)
            base_name = path_obj.stem

            # Look for test files
            test_patterns = [
                f"tests/test_{base_name}.py",
                f"test/test_{base_name}.py",
                f"tests/{base_name}_test.py",
                f"test_{base_name}.py"
            ]

            for pattern in test_patterns:
                test_path = project_path / pattern
                if test_path.exists() and pattern not in target_files:
                    related.append(pattern)
                    break

        return related

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


# Test section
if __name__ == "__main__":
    print("\n[TEST] Testing EnhancedContextBuilder with Smart Detection...")

    try:
        builder = EnhancedContextBuilder()

        # Test CREATE operation
        print(f"\n[INFO] Test 1: CREATE operation")
        context = builder.build_context(
            project_name="uae-legal-agent",
            task_description="Vytvor utils/validators.py so základnými funkciami"
        )
        print(f"[OK] Context size: {len(context)} chars")
        print(f"[INFO] Operation detected from context preview:")
        print(context.split('\n')[5:8])

        # Test MODIFY operation
        print(f"\n[INFO] Test 2: MODIFY operation")
        context = builder.build_context(
            project_name="uae-legal-agent",
            task_description="Oprav utils/config.py - zmeň debug default na False"
        )
        print(f"[OK] Context size: {len(context)} chars")
        print(f"[INFO] Should include config.py content")

        print("\n[SUCCESS] EnhancedContextBuilder test completed!")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()