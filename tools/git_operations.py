#!/usr/bin/env python3
"""
Git Operations
Handles Git operations: commit, push, status, diff
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class GitOperations:
    """Manage Git operations for automation"""
    
    def __init__(self, project_path: str):
        """
        Initialize Git operations
        
        Args:
            project_path: Root path of the Git repository
        """
        self.project_root = Path(project_path)
        
        # Verify Git repository
        if not (self.project_root / ".git").exists():
            raise ValueError(f"Not a Git repository: {project_path}")
    
    def _run_git_command(
        self, 
        command: List[str],
        capture_output: bool = True
    ) -> Tuple[bool, str]:
        """
        Run Git command
        
        Args:
            command: Git command as list (e.g., ['status', '--short'])
            capture_output: Capture stdout/stderr
            
        Returns:
            Tuple of (success, output)
        """
        
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
                encoding='utf-8'
            )
            
            return (
                result.returncode == 0,
                result.stdout if capture_output else ""
            )
            
        except Exception as e:
            return False, str(e)
    
    def status(self) -> Dict[str, any]:
        """
        Get Git status
        
        Returns:
            Dict with status info
        """
        
        success, output = self._run_git_command(['status', '--short'])
        
        if not success:
            return {
                "success": False,
                "error": output
            }
        
        # Parse status
        changed_files = []
        for line in output.strip().split('\n'):
            if line:
                status_code = line[:2]
                file_path = line[3:].strip()
                changed_files.append({
                    "status": status_code.strip(),
                    "file": file_path
                })
        
        return {
            "success": True,
            "has_changes": len(changed_files) > 0,
            "changed_files": changed_files,
            "count": len(changed_files)
        }
    
    def diff(self, file_path: Optional[str] = None) -> Dict[str, any]:
        """
        Get Git diff
        
        Args:
            file_path: Specific file to diff (optional)
            
        Returns:
            Dict with diff output
        """
        
        command = ['diff']
        if file_path:
            command.append(file_path)
        
        success, output = self._run_git_command(command)
        
        return {
            "success": success,
            "diff": output if success else None,
            "error": output if not success else None
        }
    
    def add(self, files: List[str] = None) -> Dict[str, any]:
        """
        Stage files for commit
        
        Args:
            files: List of files to stage (None = all changes)
            
        Returns:
            Result dict
        """
        
        command = ['add']
        if files:
            command.extend(files)
        else:
            command.append('.')
        
        success, output = self._run_git_command(command)
        
        return {
            "success": success,
            "staged": files or "all changes",
            "error": output if not success else None
        }
    
    def commit(
        self,
        message: str,
        files: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Commit changes
        
        Args:
            message: Commit message
            files: Files to commit (None = all staged)
            
        Returns:
            Result dict with commit hash
        """
        
        # Stage files if specified
        if files:
            add_result = self.add(files)
            if not add_result["success"]:
                return add_result
        
        # Commit
        success, output = self._run_git_command(['commit', '-m', message])
        
        if not success:
            return {
                "success": False,
                "error": output
            }
        
        # Get commit hash
        success_hash, commit_hash = self._run_git_command(['rev-parse', '--short', 'HEAD'])
        
        return {
            "success": True,
            "message": message,
            "commit_hash": commit_hash.strip() if success_hash else "unknown",
            "timestamp": datetime.now().isoformat()
        }
    
    def push(
        self,
        remote: str = "origin",
        branch: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Push commits to remote
        
        Args:
            remote: Remote name (default: origin)
            branch: Branch name (None = current branch)
            
        Returns:
            Result dict
        """
        
        command = ['push', remote]
        
        if branch:
            command.append(branch)
        
        success, output = self._run_git_command(command, capture_output=True)
        
        return {
            "success": success,
            "remote": remote,
            "branch": branch or "current",
            "output": output if success else None,
            "error": output if not success else None
        }
    
    def get_current_branch(self) -> str:
        """Get current branch name"""
        
        success, output = self._run_git_command(['branch', '--show-current'])
        return output.strip() if success else "unknown"
    
    def get_last_commit(self) -> Dict[str, str]:
        """Get last commit info"""
        
        success, commit_hash = self._run_git_command(['rev-parse', '--short', 'HEAD'])
        success_msg, commit_msg = self._run_git_command(['log', '-1', '--pretty=%s'])
        
        return {
            "hash": commit_hash.strip() if success else "unknown",
            "message": commit_msg.strip() if success_msg else "unknown"
        }
    
    def commit_and_push(
        self,
        message: str,
        files: Optional[List[str]] = None,
        push_enabled: bool = False
    ) -> Dict[str, any]:
        """
        Commit and optionally push changes
        
        Args:
            message: Commit message
            files: Files to commit
            push_enabled: Whether to push after commit
            
        Returns:
            Result dict with commit and push status
        """
        
        # Commit
        commit_result = self.commit(message, files)
        
        if not commit_result["success"]:
            return {
                "commit": commit_result,
                "push": None
            }
        
        # Push if enabled
        push_result = None
        if push_enabled:
            push_result = self.push()
        
        return {
            "commit": commit_result,
            "push": push_result
        }


if __name__ == "__main__":
    # Test Git operations
    print("Testing Git Operations...")
    print("=" * 60)
    
    # Test with uae-legal-agent project (should have .git)
    test_project = "C:/Development/uae-legal-agent"
    
    try:
        git = GitOperations(test_project)
        
        print(f"✅ Git operations initialized for: {test_project}")
        
        # Test 1: Get current branch
        print("\n1. Current branch:")
        branch = git.get_current_branch()
        print(f"   Branch: {branch}")
        
        # Test 2: Get status
        print("\n2. Git status:")
        status = git.status()
        if status["success"]:
            print(f"   Has changes: {status['has_changes']}")
            print(f"   Changed files: {status['count']}")
            if status['changed_files']:
                for file in status['changed_files'][:5]:  # Max 5
                    print(f"      {file['status']} {file['file']}")
        
        # Test 3: Last commit
        print("\n3. Last commit:")
        last_commit = git.get_last_commit()
        print(f"   Hash: {last_commit['hash']}")
        print(f"   Message: {last_commit['message'][:60]}...")
        
        print("\n" + "=" * 60)
        print("✅ Git Operations test passed!")
        print("\n⚠️  Note: No actual commits/pushes made during test")
        
    except ValueError as e:
        print(f"⚠️  Cannot test: {e}")
        print("   This is expected if project is not a Git repo yet")
    except Exception as e:
        print(f"❌ Error: {e}")