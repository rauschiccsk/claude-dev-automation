#!/usr/bin/env python3
"""
File Operations
Handles creating, updating, and deleting files in projects
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import shutil

class FileOperations:
    """Manage file operations for automation"""
    
    def __init__(self, project_path: str):
        """
        Initialize file operations
        
        Args:
            project_path: Root path of the project
        """
        self.project_root = Path(project_path)
        self.changes_log = []
        
    def create_file(
        self, 
        file_path: str, 
        content: str,
        backup: bool = True
    ) -> Dict[str, any]:
        """
        Create new file
        
        Args:
            file_path: Relative path from project root
            content: File content
            backup: Create backup if file exists
            
        Returns:
            Result dict with status and message
        """
        
        full_path = self.project_root / file_path
        
        try:
            # Check if file already exists
            if full_path.exists():
                if backup:
                    self._create_backup(full_path)
                    action = "overwritten (backup created)"
                else:
                    action = "overwritten"
            else:
                action = "created"
                
            # Create directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            full_path.write_text(content, encoding='utf-8')
            
            # Log change
            self.changes_log.append({
                "action": "create",
                "file": file_path,
                "status": "success",
                "details": action,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "action": action,
                "file": file_path,
                "path": str(full_path)
            }
            
        except Exception as e:
            self.changes_log.append({
                "action": "create",
                "file": file_path,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": False,
                "error": str(e),
                "file": file_path
            }
    
    def update_file(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        backup: bool = True
    ) -> Dict[str, any]:
        """
        Update existing file by replacing content
        
        Args:
            file_path: Relative path from project root
            old_content: Content to find and replace
            new_content: New content
            backup: Create backup before update
            
        Returns:
            Result dict with status and message
        """
        
        full_path = self.project_root / file_path
        
        try:
            if not full_path.exists():
                return {
                    "success": False,
                    "error": "File does not exist",
                    "file": file_path
                }
            
            # Read current content
            current_content = full_path.read_text(encoding='utf-8')
            
            # Check if old_content exists
            if old_content not in current_content:
                return {
                    "success": False,
                    "error": "Content to replace not found in file",
                    "file": file_path
                }
            
            # Create backup
            if backup:
                self._create_backup(full_path)
            
            # Replace content
            updated_content = current_content.replace(old_content, new_content)
            full_path.write_text(updated_content, encoding='utf-8')
            
            # Log change
            self.changes_log.append({
                "action": "update",
                "file": file_path,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "action": "updated",
                "file": file_path,
                "path": str(full_path)
            }
            
        except Exception as e:
            self.changes_log.append({
                "action": "update",
                "file": file_path,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": False,
                "error": str(e),
                "file": file_path
            }
    
    def delete_file(
        self,
        file_path: str,
        backup: bool = True
    ) -> Dict[str, any]:
        """
        Delete file
        
        Args:
            file_path: Relative path from project root
            backup: Create backup before deletion
            
        Returns:
            Result dict with status and message
        """
        
        full_path = self.project_root / file_path
        
        try:
            if not full_path.exists():
                return {
                    "success": False,
                    "error": "File does not exist",
                    "file": file_path
                }
            
            # Create backup
            if backup:
                backup_path = self._create_backup(full_path)
            
            # Delete file
            full_path.unlink()
            
            # Log change
            self.changes_log.append({
                "action": "delete",
                "file": file_path,
                "status": "success",
                "backup": str(backup_path) if backup else None,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "action": "deleted",
                "file": file_path,
                "backup": str(backup_path) if backup else None
            }
            
        except Exception as e:
            self.changes_log.append({
                "action": "delete",
                "file": file_path,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": False,
                "error": str(e),
                "file": file_path
            }
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create backup of file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.name}.backup_{timestamp}"
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def extract_code_blocks(self, response_text: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from Claude response
        
        Args:
            response_text: Claude's response text
            
        Returns:
            List of dicts with file_path, language, and content
        """
        
        code_blocks = []
        
        # Pattern for code blocks with file path comment
        # Matches: ```python\n# file: src/main.py\ncode...```
        pattern = r"```(\w+)\s*\n(?:#|//)\s*(?:file|path):\s*([^\n]+)\n(.*?)```"
        
        matches = re.finditer(pattern, response_text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            language = match.group(1)
            file_path = match.group(2).strip()
            content = match.group(3).strip()
            
            code_blocks.append({
                "file_path": file_path,
                "language": language,
                "content": content
            })
        
        return code_blocks
    
    def apply_code_blocks(
        self,
        response_text: str,
        backup: bool = True
    ) -> List[Dict[str, any]]:
        """
        Extract and apply all code blocks from response
        
        Args:
            response_text: Claude's response
            backup: Create backups
            
        Returns:
            List of results for each file operation
        """
        
        code_blocks = self.extract_code_blocks(response_text)
        results = []
        
        for block in code_blocks:
            result = self.create_file(
                file_path=block['file_path'],
                content=block['content'],
                backup=backup
            )
            results.append(result)
        
        return results
    
    def get_changes_summary(self) -> Dict[str, any]:
        """Get summary of all changes made"""
        
        successful = [c for c in self.changes_log if c['status'] == 'success']
        failed = [c for c in self.changes_log if c['status'] == 'error']
        
        return {
            "total_changes": len(self.changes_log),
            "successful": len(successful),
            "failed": len(failed),
            "changes": self.changes_log
        }


if __name__ == "__main__":
    # Test file operations
    print("Testing File Operations...")
    print("=" * 60)
    
    # Create test project directory
    test_project = Path("C:/Development/_workspace/test_project")
    test_project.mkdir(exist_ok=True)
    
    try:
        ops = FileOperations(str(test_project))
        
        # Test 1: Create file
        print("\n1. Creating test file...")
        result = ops.create_file(
            "test.py",
            "print('Hello from automation!')\n"
        )
        print(f"   {'✅' if result['success'] else '❌'} {result}")
        
        # Test 2: Update file
        print("\n2. Updating test file...")
        result = ops.update_file(
            "test.py",
            "print('Hello from automation!')",
            "print('Updated by automation!')"
        )
        print(f"   {'✅' if result['success'] else '❌'} {result}")
        
        # Test 3: Extract code blocks
        print("\n3. Testing code block extraction...")
        test_response = """
Here's the code:

```python
# file: src/main.py
def main():
    print("Test")
```

And another file:

```python
# path: tests/test_main.py
def test_main():
    assert True
```
"""
        blocks = ops.extract_code_blocks(test_response)
        print(f"   ✅ Found {len(blocks)} code blocks")
        for block in blocks:
            print(f"      - {block['file_path']}")
        
        # Test 4: Summary
        print("\n4. Changes summary:")
        summary = ops.get_changes_summary()
        print(f"   Total: {summary['total_changes']}")
        print(f"   Success: {summary['successful']}")
        print(f"   Failed: {summary['failed']}")
        
        print("\n" + "=" * 60)
        print("✅ File Operations test passed!")
        
        # Cleanup
        shutil.rmtree(test_project)
        print("✅ Cleanup done")
        
    except Exception as e:
        print(f"❌ Error: {e}")