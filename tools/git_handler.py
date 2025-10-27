"""
Git Handler
Manages Git operations for projects.
"""

import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


class GitHandler:
    """Handles Git operations."""

    def get_status(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Get Git status for project.

        Args:
            project_path: Path to project directory

        Returns:
            Dictionary with Git status or None if not a Git repo
        """
        try:
            project_path = Path(project_path)

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

            # Get status
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )

            has_changes = bool(result.stdout.strip())

            return {
                'branch': branch,
                'has_changes': has_changes,
                'changes': result.stdout.strip() if has_changes else 'Working tree clean'
            }

        except Exception as e:
            print(f"[WARNING] Failed to get git status: {e}")
            return None

    def commit_changes(self, project_path: str, message: str) -> bool:
        """
        Commit all changes.

        Args:
            project_path: Path to project directory
            message: Commit message

        Returns:
            True if successful, False otherwise
        """
        try:
            project_path = Path(project_path)

            # Add all changes
            result = subprocess.run(
                ["git", "add", "."],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"[ERROR] Git add failed: {result.stderr}")
                return False

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                # Check if it's "nothing to commit"
                if "nothing to commit" in result.stdout.lower():
                    print(f"[INFO] Nothing to commit")
                    return True

                print(f"[ERROR] Git commit failed: {result.stderr}")
                return False

            print(f"[OK] Changes committed: {message}")
            return True

        except Exception as e:
            print(f"[ERROR] Git commit failed: {e}")
            return False

    def push_changes(self, project_path: str) -> bool:
        """
        Push changes to remote.

        Args:
            project_path: Path to project directory

        Returns:
            True if successful, False otherwise
        """
        try:
            project_path = Path(project_path)

            # Push
            result = subprocess.run(
                ["git", "push"],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"[ERROR] Git push failed: {result.stderr}")
                return False

            print(f"[OK] Changes pushed to remote")
            return True

        except Exception as e:
            print(f"[ERROR] Git push failed: {e}")
            return False


# Test section
if __name__ == "__main__":
    print("\n[TEST] Testing GitHandler...")

    try:
        handler = GitHandler()

        # Test with current project
        project_path = Path(__file__).parent.parent

        print(f"\n[INFO] Getting git status for: {project_path}")
        status = handler.get_status(str(project_path))

        if status:
            print(f"\n[OK] Git status retrieved:")
            print(f"     Branch: {status['branch']}")
            print(f"     Has changes: {status['has_changes']}")
            print(f"     Changes: {status['changes'][:100]}...")
        else:
            print(f"\n[INFO] Not a git repository")

        print("\n[SUCCESS] GitHandler test completed!")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()