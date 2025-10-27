"""
File Operations Handler
Extracts and executes file operations from Claude's responses.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET


class FileOperationExtractor:
    """Extracts file operations from Claude's XML-formatted responses."""

    def extract_operations(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract file operations from response.

        Args:
            response: Claude's response text

        Returns:
            List of operation dictionaries with keys:
            - type: 'create', 'modify', or 'delete'
            - path: relative file path
            - content: file content (for create/modify)
        """
        operations = []

        # Remove markdown code blocks if present
        # Pattern 1: ```xml ... ```
        response = re.sub(r'```xml\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'```\s*', '', response)

        # Try to find <file_operations> XML block
        pattern = r'<file_operations>(.*?)</file_operations>'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)

        if not matches:
            print(f"[INFO] No <file_operations> XML found in response")
            return operations

        print(f"[INFO] Found {len(matches)} <file_operations> block(s)")

        for match_idx, match in enumerate(matches):
            # Wrap in root element for XML parsing
            xml_text = f'<file_operations>{match}</file_operations>'

            try:
                root = ET.fromstring(xml_text)

                for op_elem in root.findall('operation'):
                    op_type = op_elem.get('type', '').lower()
                    op_path = op_elem.get('path', '')

                    if not op_type or not op_path:
                        print(f"[WARNING] Skipping operation with missing type or path")
                        continue

                    operation = {
                        'type': op_type,
                        'path': op_path
                    }

                    # Extract content for create/modify
                    if op_type in ['create', 'modify']:
                        content_elem = op_elem.find('content')
                        if content_elem is not None:
                            # Get text including nested content
                            content = content_elem.text or ''
                            # Add text from all child elements
                            for child in content_elem:
                                if child.text:
                                    content += child.text
                                if child.tail:
                                    content += child.tail
                            operation['content'] = content.strip()
                        else:
                            print(f"[WARNING] No content found for {op_type} operation: {op_path}")
                            continue

                    operations.append(operation)
                    print(f"[OK] Extracted {op_type} operation: {op_path}")

            except ET.ParseError as e:
                print(f"[WARNING] Failed to parse XML block {match_idx + 1}: {e}")
                print(f"[DEBUG] XML preview: {xml_text[:500]}...")
                continue

        return operations

    def validate_operation(self, operation: Dict[str, Any]) -> bool:
        """
        Validate file operation.

        Args:
            operation: Operation dictionary

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if 'type' not in operation or 'path' not in operation:
            return False

        # Check type
        if operation['type'] not in ['create', 'modify', 'delete']:
            return False

        # Check content for create/modify
        if operation['type'] in ['create', 'modify']:
            if 'content' not in operation or not operation['content']:
                return False

        # Check path safety (no absolute paths, no parent directory escapes)
        path = operation['path']
        if path.startswith('/') or path.startswith('\\'):
            return False
        if '..' in path:
            return False

        return True


class FileOperationExecutor:
    """Executes file operations safely."""

    def execute_operation(
        self,
        operation: Dict[str, Any],
        project_path: str
    ) -> bool:
        """
        Execute a single file operation.

        Args:
            operation: Operation dictionary from extractor
            project_path: Base path for project

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate operation
            extractor = FileOperationExtractor()
            if not extractor.validate_operation(operation):
                print(f"[ERROR] Invalid operation: {operation}")
                return False

            # Build full path
            project_path = Path(project_path)
            file_path = project_path / operation['path']

            # Execute based on type
            if operation['type'] == 'create':
                return self._create_file(file_path, operation['content'])

            elif operation['type'] == 'modify':
                return self._modify_file(file_path, operation['content'])

            elif operation['type'] == 'delete':
                return self._delete_file(file_path)

            return False

        except Exception as e:
            print(f"[ERROR] Operation execution failed: {e}")
            return False

    def _create_file(self, file_path: Path, content: str) -> bool:
        """Create new file."""
        try:
            # Check if file already exists
            if file_path.exists():
                print(f"[ERROR] File already exists: {file_path}")
                return False

            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            file_path.write_text(content, encoding='utf-8')
            print(f"[OK] Created: {file_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to create file: {e}")
            return False

    def _modify_file(self, file_path: Path, content: str) -> bool:
        """Modify existing file."""
        try:
            # Check if file exists
            if not file_path.exists():
                print(f"[ERROR] File does not exist: {file_path}")
                return False

            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
            print(f"[INFO] Backup created: {backup_path}")

            # Write new content
            file_path.write_text(content, encoding='utf-8')
            print(f"[OK] Modified: {file_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to modify file: {e}")
            return False

    def _delete_file(self, file_path: Path) -> bool:
        """Delete file."""
        try:
            # Check if file exists
            if not file_path.exists():
                print(f"[ERROR] File does not exist: {file_path}")
                return False

            # Create backup before deleting
            backup_path = file_path.with_suffix(file_path.suffix + '.deleted')
            backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
            print(f"[INFO] Backup created: {backup_path}")

            # Delete file
            file_path.unlink()
            print(f"[OK] Deleted: {file_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to delete file: {e}")
            return False


# Test section
if __name__ == "__main__":
    print("\n[TEST] Testing File Operations...")

    # Test with markdown-wrapped XML (simulating Claude response)
    test_response = """
Here is my analysis...

```xml
<file_operations>
  <operation type="create" path="test/new_file.py">
    <content>
# Test file
print("Hello World")
    </content>
  </operation>
  <operation type="modify" path="test/existing.py">
    <content>
# Modified content
print("Updated")
    </content>
  </operation>
</file_operations>
```

That's my recommendation.
"""

    try:
        # Test extraction
        extractor = FileOperationExtractor()
        operations = extractor.extract_operations(test_response)

        print(f"\n[OK] Extracted {len(operations)} operations:")
        for i, op in enumerate(operations, 1):
            print(f"     {i}. {op['type'].upper()}: {op['path']}")
            if 'content' in op:
                print(f"        Content length: {len(op['content'])} chars")

        # Test validation
        print(f"\n[INFO] Testing validation...")
        for op in operations:
            valid = extractor.validate_operation(op)
            print(f"     Operation {op['path']}: {'[OK]' if valid else '[INVALID]'}")

        print("\n[SUCCESS] File operations test completed!")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()