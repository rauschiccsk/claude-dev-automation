"""
git_handler.py - Git operations handler
Handles Git status, commit, and push operations
"""

import subprocess
from pathlib import Path
from typing import Optional, List


class GitHandler:
    """Handles Git operations for projects."""

    def __init__(self):
        """Initialize Git handler."""
        pass

    def get_status(self, project_path: Path) -> Optional[str]:
        """
        Get Git status for project.

        Args:
            project_path: Path to project directory

        Returns:
            Git status output or None on error
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--short', '--branch'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError:
            print("⚠️  Git not found in PATH")
            return None

    def has_changes(self, project_path: Path) -> bool:
        """
        Check if project has uncommitted changes.

        Args:
            project_path: Path to project directory

        Returns:
            True if there are uncommitted changes
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_current_branch(self, project_path: Path) -> Optional[str]:
        """
        Get current Git branch name.

        Args:
            project_path: Path to project directory

        Returns:
            Branch name or None
        """
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def get_changed_files(self, project_path: Path, limit: int = 10) -> List[str]:
        """
        Get list of changed files.

        Args:
            project_path: Path to project directory
            limit: Maximum number of files to return

        Returns:
            List of changed file paths
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )

            files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # Format: "XY filename"
                    # X = status in index, Y = status in working tree
                    parts = line.strip().split(None, 1)
                    if len(parts) >= 2:
                        files.append(parts[1])

                if len(files) >= limit:
                    break

            return files

        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def commit_changes(self, project_path: Path, message: str) -> bool:
        """
        Commit all changes with given message.

        Args:
            project_path: Path to project directory
            message: Commit message

        Returns:
            True if successful, False otherwise
        """
        try:
            # Add all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=project_path,
                capture_output=True,
                check=True
            )

            # Commit
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )

            return True

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git commit failed: {e.stderr if e.stderr else str(e)}")
            return False
        except FileNotFoundError:
            print("⚠️  Git not found in PATH")
            return False

    def push_changes(self, project_path: Path, remote: str = 'origin') -> bool:
        """
        Push commits to remote repository.

        Args:
            project_path: Path to project directory
            remote: Remote name (default: 'origin')

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current branch
            branch = self.get_current_branch(project_path)
            if not branch:
                print("⚠️  Could not determine current branch")
                return False

            # Push to remote
            subprocess.run(
                ['git', 'push', remote, branch],
                cwd=project_path,
                capture_output=True,
                text=True,
                check=True
            )

            return True

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git push failed: {e.stderr if e.stderr else str(e)}")
            return False
        except FileNotFoundError:
            print("⚠️  Git not found in PATH")
            return False

    def is_git_repo(self, project_path: Path) -> bool:
        """
        Check if directory is a Git repository.

        Args:
            project_path: Path to check

        Returns:
            True if it's a Git repo
        """
        git_dir = project_path / '.git'
        return git_dir.exists() and git_dir.is_dir()


# Example usage and testing
if __name__ == "__main__":
    import tempfile
    import os

    print("🧪 Testing GitHandler...\n")

    # Create temporary Git repo for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir)

        print(f"📁 Test directory: {test_path}\n")

        # Initialize Git repo
        subprocess.run(['git', 'init'], cwd=test_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=test_path, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=test_path, capture_output=True)

        handler = GitHandler()

        # Test is_git_repo
        print("✅ is_git_repo:", handler.is_git_repo(test_path))

        # Create test file
        test_file = test_path / 'test.txt'
        test_file.write_text('Hello, Git!')

        # Test has_changes
        print("✅ has_changes:", handler.has_changes(test_path))

        # Test get_changed_files
        changed = handler.get_changed_files(test_path)
        print(f"✅ changed_files: {changed}")

        # Test get_status
        status = handler.get_status(test_path)
        print(f"✅ git_status:\n{status}\n")

        # Test commit
        success = handler.commit_changes(test_path, "Initial commit")
        print(f"✅ commit_changes: {success}")

        # Test get_current_branch
        branch = handler.get_current_branch(test_path)
        print(f"✅ current_branch: {branch}")

        # Test has_changes after commit
        print(f"✅ has_changes (after commit): {handler.has_changes(test_path)}")

    print("\n✅ All tests completed!")