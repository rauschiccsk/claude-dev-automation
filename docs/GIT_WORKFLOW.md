# 🔄 Git Workflow - Commit & Push Changes

Návod na commit a push všetkých dnešných zmien.

---

## 📋 Čo bude commitnuté

### Nové súbory (8):
```
tools/
├── claude_runner.py          ← NEW
├── file_operations.py        ← NEW
├── task_parser.py            ← NEW
├── git_handler.py            ← NEW
├── config_manager.py         ← NEW/UPDATED
├── enhanced_context_builder.py ← NEW/UPDATED
├── orchestrator.py           ← UPDATED
└── response_builder.py       ← UPDATED
```

### Konfiguračné súbory:
```
workspace/
├── config.json               ← NEW
└── .env                      ← IGNORED (gitignore)
```

### Dokumentácia:
```
docs/
└── sessions/
    └── 2025-10-27_complete_system_fix.md ← NEW
```

---

## 🚀 Git Commands

### Krok 1: Skontroluj status

```bash
cd C:\Development\claude-dev-automation

git status
```

**Očakávaný výstup:**
```
On branch main
Untracked files:
  tools/claude_runner.py
  tools/file_operations.py
  ...
  docs/sessions/2025-10-27_complete_system_fix.md

Modified files:
  tools/orchestrator.py
  tools/response_builder.py
```

---

### Krok 2: Pridaj všetky súbory

```bash
# Pridaj všetky nové a upravené súbory
git add tools/*.py
git add workspace/config.json
git add docs/sessions/2025-10-27_complete_system_fix.md

# Alebo jednoducho všetko naraz
git add .
```

---

### Krok 3: Skontroluj čo bude commitnuté

```bash
git status
```

**Mělo by ukázať:**
```
Changes to be committed:
  new file:   tools/claude_runner.py
  new file:   tools/file_operations.py
  new file:   tools/task_parser.py
  new file:   tools/git_handler.py
  modified:   tools/orchestrator.py
  modified:   tools/response_builder.py
  ...
```

**Overiť že .env NIE JE v zozname!** (má byť v .gitignore)

---

### Krok 4: Commit zmeny

```bash
git commit -m "feat: Complete system implementation with all modules

- Add all 8 core Python modules (claude_runner, orchestrator, etc.)
- Fix Windows console emoji compatibility (emoji → ASCII)
- Fix response display bug (claude_response parameter)
- Add smart context system with auto-discovery
- Add Slovak language enforcement
- Fix import paths and API key loading
- Add comprehensive documentation
- All tests passing, system production ready

Token savings: 90% (40k → 4k tokens per task)
Status: Production ready ✅"
```

---

### Krok 5: Push do remote

```bash
git push origin main
```

Alebo ak máš iný branch:
```bash
# Zisti aktuálny branch
git branch

# Push na ten branch
git push origin <branch-name>
```

---

## 🔒 Overiť .gitignore

Skontroluj že `.gitignore` obsahuje:

```bash
# Zobraz .gitignore
cat .gitignore

# Alebo
type .gitignore
```

**Mělo by obsahovať:**
```
# Environment variables
workspace/.env
.env
*.env

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

**Ak .gitignore neexistuje, vytvor ho:**

```bash
cd C:\Development\claude-dev-automation

notepad .gitignore
```

Vlož obsah vyššie a ulož.

Potom:
```bash
git add .gitignore
git commit -m "chore: Add .gitignore for security"
git push
```

---

## 📊 Kompletný Workflow (All-in-one)

```bash
cd C:\Development\claude-dev-automation

# 1. Status check
git status

# 2. Add všetko
git add .

# 3. Commit
git commit -m "feat: Complete system implementation

- Add all 8 core Python modules
- Fix Windows console compatibility
- Fix response display bug
- Add smart context system
- Token savings: 90%
- Status: Production ready ✅"

# 4. Push
git push origin main

# 5. Verify
git log --oneline -n 5
```

---

## ✅ Verify Push

Po push-e skontroluj na GitHub/GitLab:

```bash
# Get remote URL
git remote -v

# Show last commit
git log --oneline -n 1
```

Alebo navštív repo v prehliadači a over že:
- ✅ Všetky súbory sú tam
- ✅ Commit message je viditeľný
- ✅ `.env` NIE JE v repo (security!)

---

## 🐛 Troubleshooting

### Problem: "nothing to commit"

**Riešenie:**
```bash
git status
# Skontroluj či sú súbory tracked

git add .
git commit -m "message"
```

### Problem: "rejected - non-fast-forward"

**Riešenie:**
```bash
# Pull najprv
git pull origin main

# Potom push
git push origin main
```

### Problem: ".env je v git!"

**CRITICAL - Odstráň ho!**
```bash
# Remove from git (keep local file)
git rm --cached workspace/.env

# Commit removal
git commit -m "security: Remove .env from git"

# Push
git push origin main

# Regeneruj API key na console.anthropic.com!
```

---

## 📝 Commit Message Best Practices

### Formát:
```
<type>: <short description>

<detailed description>

<breaking changes>
<references>
```

### Types:
- `feat:` - nová funkcionalita
- `fix:` - oprava bugu
- `docs:` - dokumentácia
- `chore:` - maintenance
- `refactor:` - refactoring
- `test:` - testy
- `style:` - formatting

### Príklady:
```bash
git commit -m "feat: Add smart context builder with auto-discovery"

git commit -m "fix: Windows console emoji compatibility issue"

git commit -m "docs: Add comprehensive session notes"

git commit -m "chore: Update .gitignore for security"
```

---

## 🎯 Quick Reference

```bash
# Basic workflow
git add .
git commit -m "feat: Description"
git push origin main

# Check status
git status
git log --oneline -n 5

# Undo last commit (keep changes)
git reset --soft HEAD~1

# See what changed
git diff

# Show commit history
git log --oneline --graph --all
```

---

## ✅ Final Checklist

Pred push-om skontroluj:

- [ ] Všetky súbory pridané (`git status`)
- [ ] `.env` NIE JE v commit
- [ ] Commit message je popisný
- [ ] Testy prešli
- [ ] Dokumentácia aktualizovaná
- [ ] Session notes vytvorené

Po push-e:
- [ ] Verify na GitHub/GitLab
- [ ] Check že `.env` nie je v repo
- [ ] Tag verzia (optional): `git tag v1.0`

---

**Status:** ✅ Ready to commit & push!  
**Version:** 1.0  
**Date:** 2025-10-27