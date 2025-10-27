# 📦 Installation Guide - Inštalácia opráv

Rýchly návod ako nainštalovať opravené súbory do tvojho projektu.

---

## 🎯 Čo sa opravilo

### 1. **orchestrator.py**
- ✅ Pridaný parameter `claude_response` pre response builder
- ✅ Extrakcia Claude's response textu keď nedôjde k file changes
- ✅ Lepšie loggovanie progress-u

### 2. **response_builder.py**
- ✅ Nová sekcia "💬 Claude's Analysis"
- ✅ Zobrazenie Claude's response aj bez file changes
- ✅ Lepšie formátovanie token usage a cost estimate

---

## ⚡ Quick Install (5 minút)

### Krok 1: Backup existujúcich súborov

```bash
cd C:\Development\claude-dev-automation\tools

# Vytvor backup
copy orchestrator.py orchestrator.py.backup
copy response_builder.py response_builder.py.backup

echo ✅ Backup created
```

### Krok 2: Stiahni opravené súbory

**Manuálne (copy-paste):**
1. Otvor artifact "orchestrator.py (opravený)"
2. Skopíruj celý obsah
3. Nahraď `tools/orchestrator.py`

4. Otvor artifact "response_builder.py (opravený)"
5. Skopíruj celý obsah
6. Nahraď `tools/response_builder.py`

**Alebo cez Git (ak máš commity):**
```bash
cd C:\Development\claude-dev-automation

# Fetch latest changes
git pull origin main

# Verify changes
git diff HEAD~1 tools/orchestrator.py
git diff HEAD~1 tools/response_builder.py
```

### Krok 3: Overiť súbory

```bash
cd C:\Development\claude-dev-automation\tools

# Check že súbory obsahujú opravy:
findstr "claude_response" orchestrator.py
# Měl by nájsť riadky s claude_response parametrom

findstr "Claude's Analysis" response_builder.py
# Měl by nájsť novú sekciu
```

### Krok 4: Test run

```bash
cd C:\Development\claude-dev-automation

# Run quick test
python tools/orchestrator.py

# Ak všetko funguje, uvidíš:
# ✅ Components initialized
# ✅ Config loaded
```

---

## 🧪 Testovanie opráv

### Quick Test (2 minúty)

**1. Vytvor jednoduchý test task:**

Otvor `workspace/task.md` a vlož:

```markdown
PROJECT: claude-dev-automation
TASK: Povedz mi aktuálny dátum a čas
PRIORITY: LOW
AUTO_COMMIT: no
AUTO_PUSH: no

## Kontext
Jednoduchý test či systém funguje.

## Poznámky
Tento test by mal ukázať Claude's response v response.md.
```

**2. Spusti PyCharm External Tool:**
- Right-click na `task.md`
- External Tools → Claude Automation
- Počkaj na dokončenie (~10 sekúnd)

**3. Skontroluj `workspace/response.md`:**

Měl by obsahovať sekciu:
```markdown
## 💬 Claude's Analysis

Aktuálny dátum a čas je: [Claude's odpoveď]
```

✅ **AK VIDÍŠ túto sekciu s obsahom = Oprava funguje!**

❌ **AK JE prázdne alebo len template = Niečo nie je v poriadku**

---

## 📋 Kompletný test (15 minút)

Pre dôkladné otestovanie použi tri test scenarios z `test_tasks.md`:

### Test 1: Response Display
- Overiť že sa Claude's analysis zobrazuje
- Token usage ~2,000-4,000

### Test 2: Slovak Language  
- Celá odpoveď v slovenčine
- Natural language (nie strojový preklad)

### Test 3: Smart Context
- Auto-load session notes
- Auto-extract TODOs
- Git status detection

**Detailný postup nájdeš v artifact: "test_tasks.md"**

---

## 🔍 Overenie inštalácie

### Kontrolný checklist:

- [ ] **orchestrator.py obsahuje:**
  ```python
  claude_response=claude_response_text,  # riadok ~150
  ```

- [ ] **response_builder.py obsahuje:**
  ```python
  def build_response(..., claude_response: Optional[str] = None):
  ```
  
- [ ] **response_builder.py má sekciu:**
  ```python
  if claude_response:
      response += "## 💬 Claude's Analysis\n\n"
  ```

- [ ] **Quick test prešiel** - vidíš Claude's analysis v response.md

- [ ] **Slovak test prešiel** - odpovede sú v slovenčine

---

## 🐛 Troubleshooting

### Problém 1: Import errors

**Error:**
```
ModuleNotFoundError: No module named 'enhanced_context_builder'
```

**Riešenie:**
```bash
cd C:\Development\claude-dev-automation\tools
dir  # Overiť že enhanced_context_builder.py existuje

# Pridaj do PYTHONPATH ak treba
set PYTHONPATH=%PYTHONPATH%;C:\Development\claude-dev-automation\tools
```

### Problém 2: Response.md stále prázdny

**Možné príčiny:**
1. Staré súbory stále aktívne (neboli nahradené)
2. Python cache - stará verzia v pamäti
3. Syntax error v opravených súboroch

**Riešenie:**
```bash
# Vyčisti Python cache
cd C:\Development\claude-dev-automation\tools
del /s *.pyc
rmdir /s __pycache__

# Reštartuj Python interpreter
# Re-run task
```

### Problém 3: Claude odpovedá anglicky

**Riešenie:**

Skontroluj `enhanced_context_builder.py` že obsahuje:

```python
system_prompt = """
CRITICAL: ALWAYS respond in Slovak language.

[... zvyšok system promptu ...]
"""
```

Ak chýba, pridaj na začiatok system promptu.

### Problém 4: Token usage je vysoký (>10k)

**Riešenie:**

Overiť že `orchestrator.py` používa `EnhancedContextBuilder`:

```python
from enhanced_context_builder import EnhancedContextBuilder
...
self.context_builder = EnhancedContextBuilder()
```

Nie starý `ContextBuilder`.

---

## ✅ Success Indicators

Po úspešnej inštalácii uvidíš:

### V Console output:
```
📖 Parsing task...
✅ Task parsed: claude-dev-automation
🧠 Building smart context...
✅ Context built: ~1,852 chars
🤖 Sending to Claude...
✅ Claude response received: 2,300 tokens
ℹ️  No file operations (analysis only)
💬 Analysis-only response (no file changes)
📄 Building response.md...
✅ Response saved to response.md
```

### V response.md:
```markdown
# 🤖 Claude Development Response

**Timestamp:** 2025-10-26T...
**Priority:** NORMAL

---

## 🎯 Task
...

## 💰 Token Usage
- Input tokens: 1,500
- Output tokens: 800
- Total tokens: 2,300
- Estimated cost: $0.0165

## 💬 Claude's Analysis

[Tu je konkrétna Claude's odpoveď v slovenčine]

---
```

---

## 🚀 Ďalšie kroky

Po úspešnej inštalácii a testovaní:

1. **Commit changes:**
   ```bash
   cd C:\Development\claude-dev-automation
   git add tools/orchestrator.py tools/response_builder.py
   git commit -m "fix: Add claude_response display in response.md"
   git push
   ```

2. **Update dokumentáciu:**
   - Pridaj poznámky do session notes
   - Aktualizuj README.md
   - Mark tasks ako completed

3. **Začni používať:**
   - Test na reálnych projektoch
   - Analyze NEX Genesis Server
   - Create production tasks

---

## 📞 Support

Ak narazíš na problémy:

1. **Skontroluj session notes:**
   ```
   docs/sessions/2025-10-26_migration_and_upgrade.md
   ```

2. **Review code:**
   - Artifacts majú kompletný kód
   - Porovnaj s tvojimi súbormi
   - Check syntax errors

3. **Test incremental:**
   - Test každú zmenu samostatne
   - Verify s debug prints
   - Check Python errors

---

**Verzia:** 1.0  
**Dátum:** 2025-10-26  
**Status:** Ready for production ✅