"""
orchestrator.py - Main orchestration logic for Claude Dev Automation
Handles task execution, file operations, and response generation
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add tools directory to Python path
tools_dir = Path(__file__).parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from claude_runner import ClaudeRunner
from file_operations import FileOperations
from response_builder import ResponseBuilder
from task_parser import TaskParser
from enhanced_context_builder import EnhancedContextBuilder
from git_handler import GitHandler
from config_manager import ConfigManager


class Orchestrator:
    """Main orchestrator for Claude development automation."""

    def __init__(self, config_path: str = "workspace/config.json"):
        """Initialize orchestrator with configuration."""
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()

        # Initialize components
        self.claude_runner = ClaudeRunner(self.config['api_key'])
        self.file_ops = FileOperations()
        self.response_builder = ResponseBuilder()
        self.task_parser = TaskParser()
        self.context_builder = EnhancedContextBuilder()
        self.git_handler = GitHandler()

        # Paths
        self.workspace_path = Path(self.config['workspace_path'])
        self.task_file = self.workspace_path / "task.md"
        self.response_file = self.workspace_path / "response.md"

    def execute_task(self) -> Dict[str, Any]:
        """
        Execute task from task.md file.

        Returns:
            Dict with execution results
        """
        try:
            # 1. Parse task
            print("[INFO] Parsing task...")
            task_data = self._load_and_parse_task()

            if not task_data:
                return self._error_response("Failed to parse task.md")

            print(f"[OK] Task parsed: {task_data['project']}")
            print(f"     Priority: {task_data['priority']}")

            # 2. Build smart context
            print("\n[INFO] Building smart context...")
            context = self._build_context(task_data)
            print(f"[OK] Context built: ~{len(context)} chars")

            # 3. Execute with Claude
            print("\n[INFO] Sending to Claude...")
            result = self._execute_with_claude(task_data, context)

            if not result or 'response' not in result:
                return self._error_response("Claude execution failed")

            print(f"[OK] Claude response received: {result.get('usage', {}).get('total_tokens', 0)} tokens")

            # 4. Process file operations (if any)
            print("\n[INFO] Processing file operations...")
            file_results = self._process_file_operations(
                result['response'],
                task_data['project']
            )

            if file_results:
                print(f"[OK] Processed {len(file_results)} file operations")
            else:
                print("[INFO] No file operations (analysis only)")

            # 5. Handle Git operations
            git_status = None
            if task_data.get('auto_commit', False) and file_results:
                print("\n[INFO] Committing changes...")
                git_status = self._handle_git_operations(
                    task_data,
                    file_results
                )

            # 6. Extract Claude's response text when no files were changed
            claude_response_text = None
            if not file_results:
                # Claude provided analysis/recommendations without file changes
                claude_response_text = result['response']
                print("[INFO] Analysis-only response (no file changes)")

            # 7. Build and save response
            print("\n[INFO] Building response.md...")
            response_md = self.response_builder.build_response(
                task=task_data['task'],
                priority=task_data['priority'],
                file_changes=file_results,
                token_usage=result.get('usage'),
                timestamp=datetime.now().isoformat(),
                git_status=git_status,
                claude_response=claude_response_text,  # ← FIXED: Pass Claude's response
            )

            self._save_response(response_md)
            print("[OK] Response saved to response.md")

            return {
                'success': True,
                'task': task_data['task'],
                'file_count': len(file_results),
                'tokens_used': result.get('usage', {}).get('total_tokens', 0),
                'has_analysis': claude_response_text is not None,
            }

        except Exception as e:
            error_msg = f"Orchestration error: {str(e)}"
            print(f"\n[ERROR] {error_msg}")
            self._save_response(f"# Error\n\n{error_msg}")
            return self._error_response(error_msg)

    def _load_and_parse_task(self) -> Optional[Dict[str, Any]]:
        """Load and parse task from task.md."""
        if not self.task_file.exists():
            print(f"❌ Task file not found: {self.task_file}")
            return None

        task_content = self.task_file.read_text(encoding='utf-8')
        return self.task_parser.parse(task_content)

    def _build_context(self, task_data: Dict[str, Any]) -> str:
        """Build smart context for the task."""
        project_path = self._resolve_project_path(task_data['project'])

        # Build enhanced context with auto-discovery
        context = self.context_builder.build_context(
            project_name=task_data['project'],
            project_path=project_path,
            task_description=task_data.get('context', ''),
            additional_notes=task_data.get('notes', '')
        )

        return context

    def _resolve_project_path(self, project_name: str) -> Path:
        """Resolve full path to project."""
        projects_base = Path(self.config.get('projects_path', 'C:/Development'))
        return projects_base / project_name

    def _execute_with_claude(self, task_data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Execute task with Claude API."""
        return self.claude_runner.execute(
            task=task_data['task'],
            context=context,
            max_tokens=self.config.get('max_tokens', 8000)
        )

    def _process_file_operations(self, response: str, project_name: str) -> List[Dict]:
        """Process file operations from Claude's response."""
        project_path = self._resolve_project_path(project_name)

        # Extract file operations from response
        operations = self.file_ops.extract_operations(response)

        if not operations:
            return []

        # Execute operations
        results = []
        for op in operations:
            result = self.file_ops.execute_operation(
                op,
                base_path=project_path
            )
            if result:
                results.append(result)

        return results

    def _handle_git_operations(self, task_data: Dict[str, Any], file_results: List[Dict]) -> Optional[str]:
        """Handle Git commit and push operations."""
        project_path = self._resolve_project_path(task_data['project'])

        # Commit changes
        commit_msg = f"[Claude] {task_data['task'][:50]}"
        commit_result = self.git_handler.commit_changes(
            project_path,
            commit_msg
        )

        # Push if requested
        if task_data.get('auto_push', False):
            self.git_handler.push_changes(project_path)

        return self.git_handler.get_status(project_path)

    def _save_response(self, content: str):
        """Save response to response.md."""
        self.response_file.write_text(content, encoding='utf-8')

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            'success': False,
            'error': message,
            'file_count': 0,
            'tokens_used': 0
        }


def main():
    """Main entry point."""
    print("[START] Claude Dev Automation - Orchestrator\n")

    orchestrator = Orchestrator()
    result = orchestrator.execute_task()

    print("\n" + "="*60)
    if result['success']:
        print("[SUCCESS] Task completed successfully!")
        print(f"          Files modified: {result['file_count']}")
        print(f"          Tokens used: {result['tokens_used']}")
        if result.get('has_analysis'):
            print(f"          Analysis provided: Yes")
    else:
        print(f"[ERROR] Task failed: {result.get('error')}")
    print("="*60)


if __name__ == "__main__":
    main()