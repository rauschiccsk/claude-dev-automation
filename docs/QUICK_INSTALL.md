# ⚡ Quick Install - Rýchla inštalácia všetkých súborov

Tento návod ti pomôže rýchlo nainštalovať všetky potrebné súbory do projektu.

---

## 📦 Súbory na inštaláciu

Z artifacts potrebuješ skopírovať **7 súborov** do `C:\Development\claude-dev-automation\tools\`:

1. ✅ **orchestrator.py** - Hlavný orchestrátor (opravený)
2. ✅ **response_builder.py** - Response builder (opravený)
3. ✅ **claude_runner.py** - Claude API runner (NOVÝ)
4. ✅ **file_operations.py** - File handler (NOVÝ)
5. ✅ **task_parser.py** - Task parser (NOVÝ)
6. ✅ **git_handler.py** - Git operations (NOVÝ)
7. ✅ **config_manager.py** - Config manager (NOVÝ alebo UPDATE)
8. ✅ **enhanced_context_builder.py** - Smart context (UPDATE ak existuje)

---

## 🚀 Krok po kroku inštalácia

### 1️⃣ Backup existujúcich súborov (1 minúta)

```bash
cd C:\Development\claude-dev-automation\tools

# Vytvor backup folder
mkdir backup_2025-10-27

# Backup všetkých existujúcich súborov
copy *.py backup_2025-10-27\

echo ✅ Backup vytvorený
```

### 2️⃣ Skopíruj nové súbory (3 minúty)

**Pre každý artifact:**
1. Otvor artifact v Claude
2. Klikni na "Copy" (vpravo hore)
3. Otvor súbor v PyCharm alebo Notepad++
4. Paste obsah (Ctrl+V)
5. Save (Ctrl+S)

**Poradie inštalácie:**
```
1. claude_runner.py          → NOVÝ súbor
2. file_operations.py        → NOVÝ súbor
3. task_parser.py            → NOVÝ súbor
4. git_handler.py            → NOVÝ súbor
5. config_manager.py         → NAHRAĎ ak existuje
6. enhanced_context_builder.py → NAHRAĎ ak existuje
7. orchestrator.py           → NAHRAĎ (opravená verzia)
8. response_builder.py       → NAHRAĎ (opravená verzia)
```

### 3️⃣ Overiť inštaláciu (1 minúta)

```bash
cd C:\Development\claude-dev-automation\tools

# Skontroluj že všetky súbory existujú
dir *.py

# Mělo by ukázať:
# claude_runner.py
# config_manager.py
# enhanced_context_builder.py
# file_operations.py
# git_handler.py
# orchestrator.py
# response_builder.py
# task_parser.py
```

### 4️⃣ Test import (1 minúta)

```bash
cd C:\Development\claude-dev-automation

# Test že všetky moduly sa dajú importovať
python -c "from tools.claude_runner import ClaudeRunner; print('✅ claude_runner OK')"
python -c "from tools.orchestrator import Orchestrator; print('✅ orchestrator OK')"
python -c "from tools.file_operations import FileOperations; print('✅ file_operations OK')"
python -c "from tools.task_parser import TaskParser; print('✅ task_parser OK')"
python -c "from tools.git_handler import GitHandler; print('✅ git_handler OK')"
python -c "from tools.config_manager import ConfigManager; print('✅ config_manager OK')"
python -c "from tools.enhanced_context_builder import EnhancedContextBuilder; print('✅ enhanced_context_builder OK')"
python -c "from tools.response_builder import ResponseBuilder; print('✅ response_builder OK')"
```

**Všetky měli vypísať `✅ ... OK`**

---

## 🧪 Quick Test (2 minúty)

### Test 1: Simple Response

Vytvor `workspace/task.md`:

```markdown
PROJECT: claude-dev-automation
TASK: Povedz mi aktuálny deň v týždni
PRIORITY: LOW
AUTO_COMMIT: no
AUTO_PUSH: no

## Kontext
Jednoduchý test systému.
```

**Spusti:**
- PyCharm: Right-click na task.md → External Tools → Claude Automation
- Alebo: `python tools/claude_runner.py` (ak máš main script)

**Očakávaný výsledok:**
- ✅ `response.md` obsahuje sekciu "💬 Claude's Analysis"
- ✅ Odpoveď je v slovenčine
- ✅ Token usage je zobrazený
- ✅ Žiadne errory v console

---

## 🔍 Verifikácia po inštalácii

### Kontrolný checklist:

**Súbory:**
- [ ] Všetkých 8 súborov existuje v `tools/`
- [ ] Žiadne `.pyc` súbory (vyčisti ak sú)
- [ ] Backup folder vytvorený

**Import test:**
- [ ] Všetky imports fungujú bez erroru
- [ ] Žiadne `ModuleNotFoundError`
- [ ] Žiadne `ImportError`

**Quick test:**
- [ ] Task.md sa parsuje správne
- [ ] Claude API call funguje
- [ ] Response.md sa vytvorí
- [ ] Sekcia "Claude's Analysis" sa zobrazí
- [ ] Odpoveď je v slovenčine

---

## 🐛 Troubleshooting

### Error: "cannot import name 'ClaudeRunner'"

**Riešenie:**
```bash
# Skontroluj že claude_runner.py existuje
dir C:\Development\claude-dev-automation\tools\claude_runner.py

# Vymaž Python cache
cd C:\Development\claude-dev-automation\tools
del /s *.pyc
rmdir /s /q __pycache__

# Reštartuj Python interpreter
```

### Error: "API key not provided"

**Riešenie:**
```bash
# Skontroluj .env súbor
type C:\Development\claude-dev-automation\workspace\.env

# Měl by obsahovať:
# ANTHROPIC_API_KEY=sk-ant-api03-...

# Ak chýba, vytvor ho
notepad C:\Development\claude-dev-automation\workspace\.env
```

### Error: "Task file not found"

**Riešenie:**
```bash
# Skontroluj že task.md existuje
dir C:\Development\claude-dev-automation\workspace\task.md

# Vytvor ho ak chýba
notepad C:\Development\claude-dev-automation\workspace\task.md
```

### Warning: Vysoký token usage (>10k)

**Príčina:** Smart context sa nenačítava správne

**Riešenie:**
```bash
# Skontroluj enhanced_context_builder.py
python -c "from tools.enhanced_context_builder import EnhancedContextBuilder; print('OK')"

# Overiť limity v kóde
# max_session_chars = 3000
# max_file_chars = 2000
```

---

## ✅ Success Indicators

Po úspešnej inštalácii mělo by to vyzerať takto:

### Console output:
```
🚀 Claude Dev Automation - Orchestrator

📖 Parsing task...
✅ Task parsed: claude-dev-automation
   Priority: LOW

🧠 Building smart context...
✅ Context built: ~1,852 chars

🤖 Sending to Claude...
✅ Claude response received: 2,300 tokens

📝 Processing file operations...
ℹ️  No file operations (analysis only)
💬 Analysis-only response (no file changes)

📄 Building response.md...
✅ Response saved to response.md

============================================================
✅ Task completed successfully!
   Files modified: 0
   Tokens used: 2,300
   Analysis provided: Yes
============================================================
```

### Response.md obsahuje:
```markdown
# 🤖 Claude Development Response

**Timestamp:** 2025-10-27T...
**Priority:** LOW

---

## 🎯 Task
Povedz mi aktuálny deň v týždni

## 💰 Token Usage
- Input tokens: 1,500
- Output tokens: 800
- Total tokens: 2,300
- Estimated cost: $0.0165

## 💬 Claude's Analysis

Dnes je pondelok, 27. októbra 2025.

---
```

---

## 🎯 Ďalšie kroky

Po úspešnej inštalácii:

1. **Commit changes:**
   ```bash
   cd C:\Development\claude-dev-automation
   git add tools/*.py
   git commit -m "feat: Complete system update with all components"
   git push
   ```

2. **Run full test suite:**
   - Použi test_tasks.md (z artifacts)
   - Test všetky 3 scenáre
   - Overiť Slovak language responses

3. **Update dokumentáciu:**
   - Pridaj session notes
   - Update README.md
   - Mark completed tasks

4. **Production use:**
   - Test na reálnych projektoch
   - Analyze nex-genesis-server
   - Create production workflows

---

## 📞 Pomoc

Ak niečo nefunguje:

1. **Skontroluj backup:**
   ```bash
   dir C:\Development\claude-dev-automation\tools\backup_2025-10-27
   ```

2. **Restore z backupu:**
   ```bash
   cd C:\Development\claude-dev-automation\tools
   copy backup_2025-10-27\*.py .
   ```

3. **Znovu nainštaluj:**
   - Vyčisti tools folder
   - Skopíruj súbory znovu z artifacts
   - Opakuj test import

4. **Skontroluj Python verziu:**
   ```bash
   python --version
   # Mělo by byť Python 3.8+
   ```

---

**Trvanie celej inštalácie: ~10 minút**  
**Verzia:** 1.0  
**Dátum:** 2025-10-27  
**Status:** Production ready ✅