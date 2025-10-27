"""
file_operations.py - File operation handler
Extracts and executes file operations from Claude's responses
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Any


class FileOperations:
    """Handles file creation, modification, and deletion operations."""

    def __init__(self):
        """Initialize file operations handler."""
        self.supported_operations = ['CREATE', 'MODIFY', 'DELETE']

    def extract_operations(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract file operations from Claude's response.

        Args:
            response: Claude's text response

        Returns:
            List of operation dictionaries
        """
        operations = []

        # Pattern to match file operations
        # FILE_OPERATION: CREATE/MODIFY/DELETE
        # PATH: relative/path/to/file.py
        # CONTENT:
        # ```language
        # ... content ...
        # ```

        pattern = r'FILE_OPERATION:\s*(CREATE|MODIFY|DELETE)\s*\nPATH:\s*([^\n]+)\s*\n(?:CONTENT:\s*\n```[\w]*\n(.*?)\n```)?'

        matches = re.finditer(pattern, response, re.DOTALL | re.MULTILINE)

        for match in matches:
            operation = match.group(1).strip()
            path = match.group(2).strip()
            content = match.group(3) if match.group(3) else None

            if content:
                content = content.strip()

            operations.append({
                'operation': operation,
                'path': path,
                'content': content
            })

        return operations

    def execute_operation(
        self,
        operation: Dict[str, Any],
        base_path: Path
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a single file operation.

        Args:
            operation: Operation dictionary with 'operation', 'path', 'content'
            base_path: Base project path

        Returns:
            Result dictionary or None on failure
        """
        op_type = operation['operation']
        rel_path = operation['path']
        content = operation.get('content')

        # Build full path
        full_path = base_path / rel_path

        try:
            if op_type == 'CREATE':
                return self._create_file(full_path, content)

            elif op_type == 'MODIFY':
                return self._modify_file(full_path, content)

            elif op_type == 'DELETE':
                return self._delete_file(full_path)

            else:
                return {
                    'operation': op_type,
                    'path': str(rel_path),
                    'success': False,
                    'error': f"Unsupported operation: {op_type}"
                }

        except Exception as e:
            return {
                'operation': op_type,
                'path': str(rel_path),
                'success': False,
                'error': str(e)
            }

    def _create_file(self, path: Path, content: str) -> Dict[str, Any]:
        """Create a new file."""
        if path.exists():
            return {
                'operation': 'CREATE',
                'path': str(path),
                'success': False,
                'error': 'File already exists'
            }

        if not content:
            return {
                'operation': 'CREATE',
                'path': str(path),
                'success': False,
                'error': 'No content provided'
            }

        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        path.write_text(content, encoding='utf-8')

        return {
            'operation': 'CREATE',
            'path': str(path),
            'success': True,
            'content': content,
            'size': len(content)
        }

    def _modify_file(self, path: Path, content: str) -> Dict[str, Any]:
        """Modify existing file."""
        if not path.exists():
            # If file doesn't exist, create it instead
            return self._create_file(path, content)

        if not content:
            return {
                'operation': 'MODIFY',
                'path': str(path),
                'success': False,
                'error': 'No content provided'
            }

        # Backup original content
        original_content = path.read_text(encoding='utf-8')

        # Write new content
        path.write_text(content, encoding='utf-8')

        return {
            'operation': 'MODIFY',
            'path': str(path),
            'success': True,
            'content': content,
            'size': len(content),
            'original_size': len(original_content)
        }

    def _delete_file(self, path: Path) -> Dict[str, Any]:
        """Delete a file."""
        if not path.exists():
            return {
                'operation': 'DELETE',
                'path': str(path),
                'success': False,
                'error': 'File does not exist'
            }

        # Read content before deletion (for logging)
        content = path.read_text(encoding='utf-8')

        # Delete file
        path.unlink()

        return {
            'operation': 'DELETE',
            'path': str(path),
            'success': True,
            'deleted_size': len(content)
        }


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing FileOperations...")

    # Sample Claude response with file operations
    sample_response = """
Vykonám nasledujúce zmeny v projekte:

FILE_OPERATION: CREATE
PATH: tests/test_example.py
CONTENT:
```python
import pytest

def test_example():
    assert True
```

FILE_OPERATION: MODIFY
PATH: src/main.py
CONTENT:
```python
def main():
    print("Modified version")
    return 0

if __name__ == "__main__":
    main()
```

FILE_OPERATION: DELETE
PATH: old/deprecated.py

Tieto zmeny vylepšia štruktúru projektu.
"""

    # Test extraction
    file_ops = FileOperations()
    operations = file_ops.extract_operations(sample_response)

    print(f"\n✅ Extracted {len(operations)} operations:")
    for i, op in enumerate(operations, 1):
        print(f"\n{i}. Operation: {op['operation']}")
        print(f"   Path: {op['path']}")
        if op.get('content'):
            print(f"   Content: {len(op['content'])} chars")

    # Test execution (in temp directory)
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)

        print(f"\n📝 Testing execution in: {tmpdir}")

        for op in operations:
            result = file_ops.execute_operation(op, base_path)

            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['operation']}: {result['path']}")

            if not result['success']:
                print(f"   Error: {result['error']}")

    print("\n✅ All tests completed!")