#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Repository Setup Script
Prepares the project structure for GitHub
"""

import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run shell command"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_git_repo():
    """Setup Git repository structure"""
    
    print("=" * 70)
    print("🚀 CLAUDE DEV AUTOMATION - GIT SETUP")
    print("=" * 70)
    print()
    
    # Get current directory
    root_dir = Path.cwd()
    print(f"📂 Working directory: {root_dir}")
    print()
    
    # Check if Git is installed
    print("1️⃣  Checking Git installation...")
    success, output, error = run_command("git --version")
    if not success:
        print("❌ Git is not installed!")
        print("   Please install Git: https://git-scm.com/downloads")
        return False
    print(f"   ✅ {output.strip()}")
    print()
    
    # Check if already a Git repo
    git_dir = root_dir / ".git"
    if git_dir.exists():
        print("⚠️  Git repository already exists!")
        response = input("   Reinitialize? (y/n): ")
        if response.lower() != 'y':
            print("   Cancelled.")
            return False
        shutil.rmtree(git_dir)
        print("   ✅ Removed existing .git directory")
        print()
    
    # Initialize Git repo
    print("2️⃣  Initializing Git repository...")
    success, output, error = run_command("git init", cwd=root_dir)
    if not success:
        print(f"❌ Failed to initialize Git: {error}")
        return False
    print("   ✅ Git repository initialized")
    print()
    
    # Create .gitignore if not exists
    gitignore = root_dir / ".gitignore"
    if not gitignore.exists():
        print("⚠️  .gitignore not found!")
        print("   Please create .gitignore file first")
        return False
    print("   ✅ .gitignore exists")
    print()
    
    # Check for .env file
    print("3️⃣  Checking for sensitive files...")
    env_files = list(root_dir.rglob(".env"))
    if env_files:
        print(f"   ⚠️  Found {len(env_files)} .env file(s):")
        for env_file in env_files:
            print(f"      {env_file.relative_to(root_dir)}")
        print("   ✅ These will be ignored by .gitignore")
    else:
        print("   ✅ No .env files found")
    print()
    
    # Stage all files
    print("4️⃣  Staging files...")
    success, output, error = run_command("git add .", cwd=root_dir)
    if not success:
        print(f"❌ Failed to stage files: {error}")
        return False
    
    # Check what will be committed
    success, output, error = run_command("git status --short", cwd=root_dir)
    if output:
        lines = output.strip().split('\n')
        print(f"   ✅ Staged {len(lines)} files")
        print()
        print("   Files to be committed:")
        for line in lines[:10]:  # Show first 10
            print(f"      {line}")
        if len(lines) > 10:
            print(f"      ... and {len(lines) - 10} more")
    print()
    
    # Initial commit
    print("5️⃣  Creating initial commit...")
    commit_msg = "Initial commit: Claude Development Automation System"
    success, output, error = run_command(f'git commit -m "{commit_msg}"', cwd=root_dir)
    if not success:
        print(f"❌ Failed to commit: {error}")
        return False
    print(f"   ✅ Committed: {commit_msg}")
    print()
    
    # Create main branch
    print("6️⃣  Setting up main branch...")
    success, output, error = run_command("git branch -M main", cwd=root_dir)
    if success:
        print("   ✅ Branch renamed to 'main'")
    print()
    
    print("=" * 70)
    print("✅ GIT SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("📝 Next steps:")
    print()
    print("1. Create GitHub repository:")
    print("   https://github.com/new")
    print()
    print("2. Add remote:")
    print("   git remote add origin https://github.com/YOUR-USERNAME/claude-dev-automation.git")
    print()
    print("3. Push to GitHub:")
    print("   git push -u origin main")
    print()
    print("⚠️  IMPORTANT: Verify .env is NOT in your commits!")
    print("   Run: git log --all --full-history -- '*/.env'")
    print("   (Should show nothing)")
    print()
    
    return True

if __name__ == "__main__":
    try:
        setup_git_repo()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()