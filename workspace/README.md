# Claude AI Development Automation - Master Workspace

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
**Created:** 2025-10-26
**Author:** Zoltán Rauscher @ ICC Komárno
