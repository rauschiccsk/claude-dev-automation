"""
Task Parser
Parses task.md files and extracts task information.
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional


class TaskParser:
    """Parses task.md files."""

    def parse_task(self, task_file: str) -> Dict[str, Any]:
        """
        Parse task.md file.

        Args:
            task_file: Path to task.md file

        Returns:
            Dictionary with task information:
            {
                'project': str,
                'task': str,
                'priority': str,
                'auto_commit': bool,
                'auto_push': bool,
                'context': str,
                'notes': str
            }
        """
        task_path = Path(task_file)

        if not task_path.exists():
            raise FileNotFoundError(f"Task file not found: {task_file}")

        content = task_path.read_text(encoding='utf-8')

        # Parse header fields
        task_data = {
            'project': self._extract_field(content, 'PROJECT'),
            'task': self._extract_field(content, 'TASK'),
            'priority': self._extract_field(content, 'PRIORITY', 'NORMAL'),
            'auto_commit': self._extract_bool(content, 'AUTO_COMMIT', False),
            'auto_push': self._extract_bool(content, 'AUTO_PUSH', False),
            'context': self._extract_section(content, 'Kontext'),
            'notes': self._extract_section(content, 'Poznámky')
        }

        # Validate required fields
        if not task_data['project']:
            raise ValueError("PROJECT field is required in task.md")
        if not task_data['task']:
            raise ValueError("TASK field is required in task.md")

        return task_data

    def _extract_field(self, content: str, field_name: str, default: str = '') -> str:
        """Extract single-line field value."""
        pattern = rf'^{field_name}:\s*(.+)$'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)

        if match:
            return match.group(1).strip()

        return default

    def _extract_bool(self, content: str, field_name: str, default: bool = False) -> bool:
        """Extract boolean field value."""
        value = self._extract_field(content, field_name, '').lower()

        if value in ['yes', 'true', '1', 'ano']:
            return True
        elif value in ['no', 'false', '0', 'nie']:
            return False

        return default

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract multi-line section content."""
        # Match section header and content until next section or end
        pattern = rf'##\s+{section_name}\s*\n(.*?)(?=##|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        if match:
            section_content = match.group(1).strip()
            return section_content if section_content else ''

        return ''


# Test section
if __name__ == "__main__":
    print("\n[TEST] Testing TaskParser...")

    # Create test task.md
    test_content = """PROJECT: test-project
TASK: This is a test task
PRIORITY: HIGH
AUTO_COMMIT: yes
AUTO_PUSH: no

## Kontext
This is context information.
Multiple lines are supported.

## Poznámky
Some notes here.
- Note 1
- Note 2
"""

    try:
        # Create temporary test file
        test_file = Path("test_task.md")
        test_file.write_text(test_content, encoding='utf-8')

        # Parse task
        parser = TaskParser()
        task = parser.parse_task(str(test_file))

        print(f"\n[OK] Task parsed successfully:")
        print(f"     Project: {task['project']}")
        print(f"     Task: {task['task']}")
        print(f"     Priority: {task['priority']}")
        print(f"     Auto-commit: {task['auto_commit']}")
        print(f"     Auto-push: {task['auto_push']}")
        print(f"     Context length: {len(task['context'])} chars")
        print(f"     Notes length: {len(task['notes'])} chars")

        # Cleanup
        test_file.unlink()

        print("\n[SUCCESS] TaskParser test completed!")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()