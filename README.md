# 🤖 Claude Dev Automation

**Intelligent development automation system that reduces Claude API token usage by 90% through smart context management and automated workflows.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## 🎯 Problem It Solves

**Traditional Claude Chat Interface:**
- Every new conversation: ~40,000 tokens initialization
- Cost per task: ~$0.20
- Manual context switching
- Repetitive explanations

**Claude Dev Automation:**
- Smart context loading: ~4,000 tokens
- Cost per task: ~$0.02
- Automatic context from session notes, Git, TODOs
- **90% token reduction**

---

## ✨ Features

### 🧠 Smart Context System
- Auto-loads latest session notes (3,000 chars)
- Auto-reads README/STATUS files (2,000 chars)
- Auto-checks Git status (branch, uncommitted changes)
- Auto-finds TODO comments in code (up to 10)
- Reduces token usage from 40k → 4k (90% savings)

### 🌍 Slovak Language Support
- Enforced Slovak responses via system prompt
- Natural language (not machine translation)
- UTF-8 console output for correct character display

### 📝 Automated Response Generation
- Generates detailed response.md files
- Includes Claude's analysis
- Token usage & cost calculation
- Financial balance reminders
- Markdown formatting

### 📁 File Operations
- Create, modify, delete files
- XML-based operation format
- Automatic backups before changes
- Safety validation

### 🔧 Git Integration
- Auto-detect Git repositories
- Get status (branch, changes)
- Optional auto-commit
- Optional auto-push

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key
- Git (optional, for Git features)

### Installation

1. **Clone repository:**
```bash
git clone https://github.com/rauschiccsk/claude-dev-automation.git
cd claude-dev-automation
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies:**
```bash
pip install anthropic python-dotenv
```

4. **Configure API key:**

Create `workspace/.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

5. **Configure paths:**

Edit `workspace/config.json`:
```json
{
  "workspace_path": "C:/Development/claude-dev-automation/workspace",
  "projects_path": "C:/Development",
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 8000
}
```

---

## 📖 Usage

### 1. Create Task

Edit `workspace/task.md`:
```markdown
PROJECT: your-project-name
TASK: Your task description here
PRIORITY: NORMAL
AUTO_COMMIT: no
AUTO_PUSH: no

## Kontext
(Optional context - smart context loads automatically)

## Poznámky
- Any special requirements
- Preferences
```

### 2. Run Automation

```bash
cd workspace
python ../tools/orchestrator.py
```

### 3. Check Results

Open `workspace/response.md` to see:
- Claude's analysis (in Slovak)
- Token usage & cost
- File operations performed
- Git status

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              orchestrator.py (Main)                 │
│         - Loads .env (API key)                      │
│         - Loads config.json                         │
│         - Coordinates all components                │
└─────────────────────────────────────────────────────┘
         │         │         │         │         │
         ▼         ▼         ▼         ▼         ▼
    ┌─────────┬─────────┬─────────┬─────────┬─────────┐
    │  task   │ context │ claude  │  file   │   git   │
    │ parser  │ builder │ runner  │  ops    │ handler │
    └─────────┴─────────┴─────────┴─────────┴─────────┘
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐         ┌─────────┐       ┌─────────┐
    │ config  │         │response │       │  .env   │
    │ manager │         │ builder │       │(API key)│
    └─────────┘         └─────────┘       └─────────┘
```

### Core Modules

| Module | Purpose | Lines |
|--------|---------|-------|
| `orchestrator.py` | Main coordination | 246 |
| `claude_runner.py` | Claude API interaction | 190 |
| `enhanced_context_builder.py` | Smart context building | 250 |
| `file_operations.py` | File operation handler | 180 |
| `task_parser.py` | Task.md parser | 150 |
| `git_handler.py` | Git operations | 170 |
| `response_builder.py` | Response generator | 220 |
| `config_manager.py` | Configuration manager | 160 |

**Total:** ~1,566 lines of production code

---

## 💰 Cost Comparison

| System | Tokens per Task | Cost per Task | Savings |
|--------|----------------|---------------|---------|
| **Chat Interface** | 40,000 | $0.20 | - |
| **Claude Dev Automation** | 4,000 | $0.02 | **90%** |

**Example costs:**
- Simple analysis: ~2,000 tokens = $0.01
- Medium task: ~4,000 tokens = $0.02
- Complex project: ~8,000 tokens = $0.04

**Claude Sonnet 4.5 Pricing:**
- Input: $3 per million tokens
- Output: $15 per million tokens

---

## 📊 Project Structure

```
claude-dev-automation/
├── tools/                          # Core Python modules
│   ├── orchestrator.py             # Main orchestrator
│   ├── claude_runner.py            # Claude API wrapper
│   ├── config_manager.py           # Configuration handler
│   ├── file_operations.py          # File operations
│   ├── task_parser.py              # Task parser
│   ├── enhanced_context_builder.py # Smart context
│   ├── git_handler.py              # Git wrapper
│   └── response_builder.py         # Response generator
├── workspace/                       # Working directory
│   ├── config.json                 # Configuration
│   ├── task.md                     # Current task
│   ├── response.md                 # Generated response
│   └── .env                        # API key (gitignored)
├── docs/                           # Documentation
│   ├── sessions/                   # Session notes
│   └── examples/                   # Example tasks
└── README.md                       # This file
```

---

## 🎓 How It Works

### 1. Smart Context Loading

Instead of manually providing context in every conversation:

**Traditional approach:**
```
User: "Here's my entire project structure... (40,000 tokens)
       Now help me with X"
```

**Claude Dev Automation:**
```python
# Automatically loads:
- Latest session notes (3,000 chars)
- README.md (2,000 chars)
- Git status (branch, changes)
- TODO comments (up to 10)
# Total: ~4,000 tokens
```

### 2. Task Execution Flow

1. **Parse task.md** → Extract project, task, settings
2. **Build context** → Load session notes, README, Git, TODOs
3. **Call Claude API** → Send optimized context
4. **Extract operations** → Parse file operations from response
5. **Execute operations** → Create/modify/delete files
6. **Git operations** → Optional commit & push
7. **Generate response.md** → Save formatted results

### 3. Response Format

Generated `response.md` includes:
- ✅ Task summary
- 💬 Claude's analysis (Slovak)
- 📁 File operations performed
- 🔧 Git status
- 📊 Token usage & cost
- 💰 Financial balance reminder

---

## 🔧 Configuration

### workspace/config.json

```json
{
  "workspace_path": "C:/Development/claude-dev-automation/workspace",
  "projects_path": "C:/Development",
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 8000
}
```

**Fields:**
- `workspace_path`: Where task.md and response.md are located
- `projects_path`: Base directory for all projects
- `model`: Claude model to use
- `max_tokens`: Maximum tokens for Claude response

### workspace/.env

```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

**⚠️ Important:** Never commit `.env` to Git!

---

## 📚 Examples

### Example 1: Continue Project Work

**task.md:**
```markdown
PROJECT: my-app
TASK: Continue development - what's the next priority task?
PRIORITY: NORMAL
AUTO_COMMIT: no
AUTO_PUSH: no

## Kontext
(Empty - smart context loads automatically)

## Poznámky
- Check TODO comments
- Prioritize by: incomplete features > bugs > optimizations
```

**Result:** Claude analyzes project state and suggests next 3 priority tasks.

### Example 2: Create New Feature

**task.md:**
```markdown
PROJECT: my-app
TASK: Create user authentication module with JWT tokens
PRIORITY: HIGH
AUTO_COMMIT: yes
AUTO_PUSH: no

## Poznámky
- Use FastAPI
- Store tokens in Redis
- Add login/logout/refresh endpoints
```

**Result:** Claude creates authentication files, Claude commits changes.

---

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not set"

**Solution:** Create `workspace/.env` with your API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### "Project not found"

**Solution:** Check `projects_path` in `config.json` points to correct directory.

### Slovak characters display as `?`

**Solution:** Upgrade to latest version - UTF-8 console output is now automatic.

### "Module not found"

**Solution:** Make sure you're running from the correct directory:
```bash
cd workspace
python ../tools/orchestrator.py
```

---

## 🤝 Contributing

Contributions welcome! This is an open-source project.

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes
4. Test thoroughly
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature-name`
7. Create Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Anthropic's Claude API](https://www.anthropic.com)
- Developed at ICC Komárno (Innovation & Consulting Center)
- Python libraries: anthropic, python-dotenv

---

## 📞 Contact

**Author:** Zoltán Rausch  
**Organization:** ICC Komárno  
**Project:** https://github.com/rauschiccsk/claude-dev-automation

---

## 🗺️ Roadmap

### Version 1.0 (Current) ✅
- Smart context system
- Slovak language support
- File operations
- Git integration
- Response generation

### Version 1.1 (Planned)
- [ ] CLI interface improvements
- [ ] Session history viewer
- [ ] Project templates
- [ ] Multi-language support

### Version 2.0 (Future)
- [ ] Web interface
- [ ] Team collaboration features
- [ ] Advanced analytics
- [ ] Plugin system

---

**Made with 🤖 by AI Conductor Zoltán Rausch**

_"Why write code when you can conduct AI to write it for you?"_