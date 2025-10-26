#!/usr/bin/env python3
"""
Setup Master Workspace Structure
Creates the complete directory structure for Claude AI development automation
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Base paths
DEVELOPMENT_ROOT = Path("C:/Development")
WORKSPACE_ROOT = DEVELOPMENT_ROOT / "_workspace"
TOOLS_ROOT = DEVELOPMENT_ROOT / "_tools"

def create_directory_structure():
    """Create all necessary directories"""
    
    directories = [
        # Workspace directories
        WORKSPACE_ROOT,
        WORKSPACE_ROOT / "project_contexts",
        WORKSPACE_ROOT / "logs",
        WORKSPACE_ROOT / "history",
        
        # Tools directory
        TOOLS_ROOT,
        TOOLS_ROOT / "templates",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def create_initial_files():
    """Create initial configuration files"""
    
    # 1. task.md template
    task_template = """PROJECT: 
TASK: 
PRIORITY: NORMAL
AUTO_COMMIT: no
AUTO_PUSH: no

## Context


## Requirements


## Files


## Notes

"""
    
    task_file = WORKSPACE_ROOT / "task.md"
    if not task_file.exists():
        task_file.write_text(task_template, encoding='utf-8')
        print(f"✅ Created: {task_file}")
    
    # 2. response.md template
    response_template = """# Task Response
**Status:** Waiting for first task...

---
*This file will be automatically updated by the automation system*
"""
    
    response_file = WORKSPACE_ROOT / "response.md"
    if not response_file.exists():
        response_file.write_text(response_template, encoding='utf-8')
        print(f"✅ Created: {response_file}")
    
    # 3. projects_index.json
    projects_index = {
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "current_project": None,
        "projects": [
            {
                "name": "supplier_invoice_loader",
                "path": "C:/Development/supplier_invoice_loader",
                "description": "Multi-tenant SaaS invoice processing system",
                "language": "python",
                "status": "active"
            },
            {
                "name": "orthodox-portal",
                "path": "C:/Development/orthodox-portal",
                "description": "Slovak Orthodox Christian web portal",
                "language": "python",
                "status": "active"
            },
            {
                "name": "nex-genesis-server",
                "path": "C:/Development/nex-genesis-server",
                "description": "Python-based Btrieve database bridge for NEX Genesis ERP",
                "language": "python",
                "status": "active"
            },
            {
                "name": "pdf-translation",
                "path": "C:/Development/pdf-translation",
                "description": "Automated book translation system",
                "language": "python",
                "status": "active"
            },
            {
                "name": "uae-legal-agent",
                "path": "C:/Development/uae-legal-agent",
                "description": "AI-powered legal analysis system for UAE law",
                "language": "python",
                "status": "active"
            }
        ]
    }
    
    projects_file = WORKSPACE_ROOT / "projects_index.json"
    with open(projects_file, 'w', encoding='utf-8') as f:
        json.dump(projects_index, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {projects_file}")
    
    # 4. session_context.json
    session_context = {
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "current_project": None,
        "conversation_history": [],
        "total_tokens_used": 0,
        "sessions_count": 0
    }
    
    session_file = WORKSPACE_ROOT / "session_context.json"
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_context, f, indent=2)
    print(f"✅ Created: {session_file}")
    
    # 5. config.json for workspace
    config = {
        "version": "1.0.0",
        "workspace_root": str(WORKSPACE_ROOT),
        "tools_root": str(TOOLS_ROOT),
        "n8n_webhook_url": "http://localhost:5678/webhook/claude-task",
        "claude_api": {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 8000,
            "temperature": 0.7
        },
        "automation": {
            "auto_commit_default": False,
            "auto_push_default": False,
            "auto_test_before_commit": True,
            "notification_enabled": True
        },
        "context_limits": {
            "max_context_tokens": 5000,
            "max_history_messages": 5,
            "max_file_size_kb": 500
        }
    }
    
    config_file = WORKSPACE_ROOT / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Created: {config_file}")
    
    # 6. .env template for API keys
    env_template = """# Claude API Configuration
ANTHROPIC_API_KEY=your_api_key_here

# n8n Configuration
N8N_WEBHOOK_URL=http://localhost:5678/webhook/claude-task

# GitHub Configuration (optional)
GITHUB_TOKEN=your_github_token_here

# Notification Settings
NOTIFICATION_METHOD=console  # console, email, discord
"""
    
    env_file = WORKSPACE_ROOT / ".env.template"
    env_file.write_text(env_template)
    print(f"✅ Created: {env_file}")

def create_project_contexts():
    """Create empty context files for each project"""
    
    projects = [
        "supplier_invoice_loader",
        "orthodox-portal",
        "nex-genesis-server",
        "pdf-translation",
        "uae-legal-agent"
    ]
    
    contexts_dir = WORKSPACE_ROOT / "project_contexts"
    
    for project in projects:
        context = {
            "project_name": project,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "description": "",
            "key_files": [],
            "recent_changes": [],
            "notes": []
        }
        
        context_file = contexts_dir / f"{project}_context.json"
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2)
        print(f"✅ Created context: {context_file.name}")

def create_readme():
    """Create README for workspace"""
    
    readme_content = """# Claude AI Development Automation - Master Workspace

## Overview
This workspace is the command center for AI-driven multi-project development.

## Structure

```
_workspace/
├── task.md                 # Write your tasks here
├── response.md            # Automated responses appear here
├── config.json            # Workspace configuration
├── projects_index.json    # All projects registry
├── session_context.json   # Current session state
├── project_contexts/      # Minimal contexts for each project
├── logs/                  # API usage and error logs
└── history/              # Task history archive
```

## Usage

### 1. Write Task
Open `task.md` and write your task:

```markdown
PROJECT: supplier_invoice_loader
TASK: Add email retry mechanism
PRIORITY: HIGH
AUTO_COMMIT: yes
AUTO_PUSH: no

## Requirements
- Exponential backoff
- Max 3 retries
...
```

### 2. Save File
PyCharm File Watcher automatically triggers the workflow

### 3. Check Response
Results appear in `response.md` automatically

### 4. Review Changes
Check git diff in PyCharm, test, and push manually

## Configuration

Edit `config.json` to customize:
- Token limits
- Auto-commit/push behavior
- Notification settings
- API endpoints

## Projects

All projects are listed in `projects_index.json`:
- supplier_invoice_loader
- orthodox-portal
- nex-genesis-server
- pdf-translation
- uae-legal-agent

## Next Steps

1. Copy `.env.template` to `.env` and add your API keys
2. Configure PyCharm File Watcher
3. Setup n8n workflow
4. Test with simple task

---
**Version:** 1.0.0
**Created:** """ + datetime.now().strftime("%Y-%m-%d") + """
**Author:** Zoltán Rauscher @ ICC Komárno
"""
    
    readme_file = WORKSPACE_ROOT / "README.md"
    readme_file.write_text(readme_content, encoding='utf-8')
    print(f"✅ Created: {readme_file}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 Setting up Claude AI Development Automation Workspace")
    print("=" * 60)
    print()
    
    print("📁 Creating directory structure...")
    create_directory_structure()
    print()
    
    print("📝 Creating initial files...")
    create_initial_files()
    print()
    
    print("🗂️  Creating project contexts...")
    create_project_contexts()
    print()
    
    print("📖 Creating README...")
    create_readme()
    print()
    
    print("=" * 60)
    print("✅ Workspace setup complete!")
    print("=" * 60)
    print()
    print(f"📂 Workspace location: {WORKSPACE_ROOT}")
    print(f"🔧 Tools location: {TOOLS_ROOT}")
    print()
    print("Next steps:")
    print("1. Copy .env.template to .env and add your API key")
    print("2. Open workspace in PyCharm")
    print("3. Configure File Watcher")
    print("4. Setup n8n workflow")
    print()
    print("Run this script to create the structure:")
    print(f"  python {__file__}")

if __name__ == "__main__":
    main()