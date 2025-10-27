"""
Main Orchestrator for Claude Dev Automation
Coordinates all components and manages workflow.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load .env file FIRST (before any other imports)
env_path = Path(__file__).parent.parent / 'workspace' / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Loaded .env from: {env_path}")
else:
    print(f"[WARNING] .env file not found: {env_path}")

# Add tools directory to Python path
tools_dir = Path(__file__).parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from claude_runner import ClaudeRunner
from task_parser import TaskParser
from enhanced_context_builder import EnhancedContextBuilder
from file_operations import FileOperationExtractor, FileOperationExecutor
from git_handler import GitHandler
from response_builder import ResponseBuilder
from config_manager import ConfigManager


class Orchestrator:
    """Main orchestration class that coordinates all components."""

    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialize orchestrator with all components.

        Args:
            workspace_path: Path to workspace directory (optional)
        """
        # Initialize config manager
        self.config_manager = ConfigManager(workspace_path)
        self.config = self.config_manager.load_config()

        # Initialize Claude runner (reads API key from .env)
        self.claude_runner = ClaudeRunner(
            model=self.config.get('model', 'claude-sonnet-4-5-20250929'),
            max_tokens=self.config.get('max_tokens', 8000)
        )

        # Initialize other components
        self.task_parser = TaskParser()
        self.context_builder = EnhancedContextBuilder(
            projects_path=self.config.get('projects_path', 'C:/Development')
        )
        self.file_extractor = FileOperationExtractor()
        self.file_executor = FileOperationExecutor()
        self.git_handler = GitHandler()
        self.response_builder = ResponseBuilder()

        # Workspace path
        self.workspace_path = Path(self.config.get('workspace_path', 'workspace'))

    def run_task(self, task_file: str = "task.md") -> Dict[str, Any]:
        """
        Execute complete task workflow.

        Args:
            task_file: Path to task.md file

        Returns:
            Dict with execution results
        """
        print("\n[START] Claude Dev Automation - Orchestrator")

        try:
            # 1. Parse task
            print(f"[INFO] Parsing task from: {task_file}")
            task_path = self.workspace_path / task_file

            if not task_path.exists():
                raise FileNotFoundError(f"Task file not found: {task_path}")

            task = self.task_parser.parse_task(str(task_path))
            print(f"[OK] Task parsed: {task['project']}")

            # 2. Build smart context
            print(f"[INFO] Building smart context...")
            context = self.context_builder.build_context(
                project_name=task['project'],
                task_description=task['task']
            )
            print(f"[OK] Context built: ~{len(context)} chars")

            # 3. Send to Claude
            print(f"[INFO] Sending to Claude...")
            result = self.claude_runner.send_task(
                task_description=task['task'],
                context=context,
                notes=task.get('notes', '')
            )
            print(f"[OK] Claude response received: {result['usage']['total_tokens']} tokens")

            # 4. Extract file operations
            print(f"[INFO] Checking for file operations...")
            file_ops = self.file_extractor.extract_operations(result['response'])

            file_results = []
            if file_ops:
                print(f"[INFO] Found {len(file_ops)} file operations")

                # Execute file operations
                project_path = self.context_builder._find_project_path(task['project'])
                if project_path:
                    for op in file_ops:
                        try:
                            success = self.file_executor.execute_operation(
                                op,
                                str(project_path)
                            )
                            file_results.append({
                                'operation': op,
                                'success': success
                            })
                        except Exception as e:
                            print(f"[ERROR] File operation failed: {e}")
                            file_results.append({
                                'operation': op,
                                'success': False,
                                'error': str(e)
                            })
            else:
                print(f"[INFO] No file operations found")

            # 5. Git operations (if requested)
            git_status = None
            if task.get('auto_commit', False) or task.get('auto_push', False):
                project_path = self.context_builder._find_project_path(task['project'])
                if project_path and file_results:
                    print(f"[INFO] Running git operations...")

                    if task.get('auto_commit', False):
                        commit_msg = f"Auto-commit: {task['task'][:50]}"
                        self.git_handler.commit_changes(str(project_path), commit_msg)

                    if task.get('auto_push', False):
                        self.git_handler.push_changes(str(project_path))

                    git_status = self.git_handler.get_status(str(project_path))

            # 6. Build response
            print(f"[INFO] Generating response.md...")

            # Only include claude_response if there are no file operations
            # (if there are file operations, they are already in the response)
            claude_response_text = None
            if not file_results:
                claude_response_text = result['response']

            response_md = self.response_builder.build_response(
                task=task,
                usage=result['usage'],
                file_operations=file_results,
                git_status=git_status,
                claude_response=claude_response_text,
                context_size=len(context)
            )

            # Save response
            response_path = self.workspace_path / "response.md"
            response_path.write_text(response_md, encoding='utf-8')
            print(f"[OK] Response saved to: {response_path}")

            print(f"\n[SUCCESS] Task completed successfully!")

            return {
                'success': True,
                'task': task,
                'usage': result['usage'],
                'file_operations': file_results,
                'git_status': git_status,
                'response_file': str(response_path)
            }

        except Exception as e:
            print(f"\n[ERROR] Task execution failed: {e}")
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Main entry point."""
    # Determine workspace path
    workspace_path = None
    if len(sys.argv) > 1:
        workspace_path = sys.argv[1]
    else:
        # Try to find workspace relative to script
        script_dir = Path(__file__).parent
        default_workspace = script_dir.parent / 'workspace'
        if default_workspace.exists():
            workspace_path = str(default_workspace)

    # Create and run orchestrator
    orchestrator = Orchestrator(workspace_path)
    result = orchestrator.run_task()

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()