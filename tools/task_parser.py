"""
task_parser.py - Task file parser
Parses task.md files into structured task data
"""

import re
from typing import Dict, Optional, Any


class TaskParser:
    """Parses task.md files into structured data."""

    def __init__(self):
        """Initialize task parser."""
        self.required_fields = ['PROJECT', 'TASK', 'PRIORITY']

    def parse(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse task.md content into structured data.

        Expected format:
        ```
        PROJECT: project-name
        TASK: Task description
        PRIORITY: LOW/NORMAL/HIGH
        AUTO_COMMIT: yes/no
        AUTO_PUSH: yes/no

        ## Kontext
        Context text here...

        ## Poznámky
        Notes here...
        ```

        Args:
            content: Content of task.md file

        Returns:
            Dictionary with parsed task data or None on error
        """
        try:
            task_data = {}

            # Parse header fields
            lines = content.split('\n')

            for line in lines:
                line = line.strip()

                # Parse key: value pairs
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()

                    if key == 'PROJECT':
                        task_data['project'] = value

                    elif key == 'TASK':
                        task_data['task'] = value

                    elif key == 'PRIORITY':
                        priority = value.upper()
                        if priority not in ['LOW', 'NORMAL', 'HIGH']:
                            priority = 'NORMAL'
                        task_data['priority'] = priority

                    elif key == 'AUTO_COMMIT':
                        task_data['auto_commit'] = value.lower() in ['yes', 'true', '1']

                    elif key == 'AUTO_PUSH':
                        task_data['auto_push'] = value.lower() in ['yes', 'true', '1']

            # Parse sections (## Kontext, ## Poznámky)
            task_data['context'] = self._extract_section(content, 'Kontext')
            task_data['notes'] = self._extract_section(content, 'Poznámky')

            # Validate required fields
            for field in self.required_fields:
                if field.lower() not in task_data:
                    print(f"⚠️  Missing required field: {field}")
                    return None

            # Set defaults
            task_data.setdefault('auto_commit', False)
            task_data.setdefault('auto_push', False)
            task_data.setdefault('context', '')
            task_data.setdefault('notes', '')

            return task_data

        except Exception as e:
            print(f"❌ Parse error: {e}")
            return None

    def _extract_section(self, content: str, section_name: str) -> str:
        """
        Extract content of a markdown section.

        Args:
            content: Full markdown content
            section_name: Section header name (without ##)

        Returns:
            Section content or empty string
        """
        # Pattern: ## Section_name followed by content until next ## or end
        pattern = rf'##\s+{re.escape(section_name)}\s*\n(.*?)(?=\n##|\Z)'

        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        if match:
            return match.group(1).strip()

        return ''

    def validate(self, task_data: Dict[str, Any]) -> bool:
        """
        Validate parsed task data.

        Args:
            task_data: Parsed task dictionary

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        for field in self.required_fields:
            if field.lower() not in task_data:
                print(f"❌ Validation failed: Missing {field}")
                return False

        # Check priority value
        if task_data['priority'] not in ['LOW', 'NORMAL', 'HIGH']:
            print(f"❌ Validation failed: Invalid priority '{task_data['priority']}'")
            return False

        # Check project name format
        project = task_data['project']
        if not re.match(r'^[a-zA-Z0-9_-]+$', project):
            print(f"❌ Validation failed: Invalid project name '{project}'")
            return False

        return True


# Example usage and testing
if __name__ == "__main__":
    print("[TEST] Testing TaskParser...\n")

    # Sample task.md content
    sample_task = """
PROJECT: claude-dev-automation
TASK: Implementuj nový feature pre automatické testovanie
PRIORITY: HIGH
AUTO_COMMIT: yes
AUTO_PUSH: no

## Kontext
Potrebujeme pridať automatické testovanie do CI/CD pipeline.
Testy by mali pokrývať všetky základné funkcie systému.

## Poznámky
- Použiť pytest framework
- Minimálne 80% code coverage
- Integrovať s GitHub Actions
"""

    # Test parsing
    parser = TaskParser()
    task_data = parser.parse(sample_task)

    if task_data:
        print("[OK] Task parsed successfully:\n")
        print(f"     Project: {task_data['project']}")
        print(f"     Task: {task_data['task']}")
        print(f"     Priority: {task_data['priority']}")
        print(f"     Auto-commit: {task_data['auto_commit']}")
        print(f"     Auto-push: {task_data['auto_push']}")
        print(f"\n     Context: {task_data['context'][:50]}...")
        print(f"     Notes: {task_data['notes'][:50]}...")

        # Test validation
        print(f"\n[OK] Validation: {parser.validate(task_data)}")
    else:
        print("[ERROR] Failed to parse task")

    # Test with invalid task
    print("\n" + "="*60)
    print("Testing with invalid task (missing PROJECT):\n")

    invalid_task = """
TASK: Some task
PRIORITY: NORMAL

## Kontext
Context here
"""

    task_data = parser.parse(invalid_task)
    if not task_data:
        print("[OK] Correctly rejected invalid task")
    else:
        print("[ERROR] Should have rejected invalid task")

    print("\n[OK] All tests completed!")