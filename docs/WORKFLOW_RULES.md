# 🔄 N8N WORKFLOW RULES

**Verzia:** 2.0  
**Dátum:** 2025-10-30  
**Projekt:** claude-dev-automation  

---

## ⚠️ KRITICKÉ PRAVIDLÁ

### Pravidlo #1: Jeden Task = Jeden Súbor

**Dôvod:** N8n workflow dokáže vytvoriť len 1 súbor za run.

```yaml
# ✅ CORRECT - Single file
requirements:
  files:
    - path: utils/module.py
      content: |
        ...

# ❌ WRONG - Multiple files (only first created!)
requirements:
  files:
    - path: utils/module.py
      content: |
        ...
    - path: tests/test_module.py  # ❌ This is IGNORED!
      content: |
        ...
```

**Workflow:**
1. Task 1 (`task-module.yaml`) → vytvorí `utils/module.py`
2. Task 2 (`task-tests.yaml`) → vytvorí `tests/test_module.py`

---

### Pravidlo #2: Jeden Task = Jeden Chat

**Dôvod:** 
- Claude chat má token limity
- Rate limits môžu blokovať aj pri 67% voľných tokenov
- Complexity issues pri dlhých konverzáciách

**Workflow:**
1. Otvor nový Claude chat
2. Load context z GitHub (session notes)
3. Vykonaj JEDEN task.yaml
4. Otestuj výsledok (ak potrebné)
5. Ukončiť chat
6. Ďalší task → nový chat

---

### Pravidlo #3: Task.yaml Musí Byť Kompletný

**Required Fields:**
```yaml
type: implementation | documentation | testing | configuration
project: exact-github-repo-name
priority: P1 | P2 | P3
description: "Clear description"
context: [background info]
requirements:
  files:
    - path: exact/path/to/file
      content: |
        Complete content, no placeholders
dependencies: [packages or []]
testing:
  commands: [verification commands]
  expected: [expected outcomes]
git_commit: "type: message"
notes: [important points]
```

**Validation:**
- ✅ Všetky povinné fields prítomné
- ✅ Len 1 súbor v requirements.files
- ✅ Content kompletný (NO placeholders!)
- ✅ Project name presne ako v GitHub

---

### Pravidlo #4: Session Notes Cez Automation

**Správne:**
```yaml
# task-session-notes.yaml
type: documentation
requirements:
  files:
    - path: docs/sessions/2025-10-30_topic.md
      content: |
        Complete session notes...
```

**Zle:**
```bash
# ❌ Manually editing session notes
code docs/sessions/2025-10-30_topic.md
git add .
git commit -m "docs: session notes"
```

**Dôvod:**
- Používame vlastnú automatizáciu
- Konzistentný workflow
- Automatický git commit & push

---

## 📋 Workflow Sequence

### Pre Modul s Testami (2 tasky)

#### Step 1: Create Module
```yaml
# task-01-module.yaml
type: implementation
project: uae-legal-agent
priority: P1
description: "Create utils/embeddings.py"
requirements:
  files:
    - path: utils/embeddings.py
      content: |
        # Complete implementation
```

**Actions:**
1. Ulož `task-01-module.yaml` do projektu
2. Spusti n8n workflow
3. Workflow vytvorí `utils/embeddings.py`
4. Workflow commitne & pushne
5. Overiť na GitHub

#### Step 2: Create Tests
```yaml
# task-02-tests.yaml
type: testing
project: uae-legal-agent
priority: P1
description: "Create tests for utils/embeddings.py"
requirements:
  files:
    - path: tests/test_embeddings.py
      content: |
        # Complete test suite
```

**Actions:**
1. Ulož `task-02-tests.yaml` do projektu
2. Spusti n8n workflow
3. Workflow vytvorí `tests/test_embeddings.py`
4. Workflow commitne & pushne
5. Spusti testy: `pytest tests/test_embeddings.py -v`

#### Step 3: Document Session
```yaml
# task-03-session.yaml
type: documentation
project: uae-legal-agent
priority: P2
description: "Document embeddings implementation"
requirements:
  files:
    - path: docs/sessions/2025-10-30_embeddings.md
      content: |
        # Session Notes: Embeddings Module
        # Complete documentation
```

---

## 🎯 Task Priority Guidelines

### P1 - Critical
- **Blocking:** Other work cannot proceed without this
- **Examples:**
  - Missing import in main.py
  - Required module for integration
  - Critical bug fix

### P2 - Important
- **Should do:** Important but not blocking
- **Examples:**
  - Test files for existing modules
  - Documentation updates
  - Non-critical features

### P3 - Nice to Have
- **Can wait:** Improvements, optimizations
- **Examples:**
  - Refactoring existing code
  - Additional documentation
  - Performance optimizations

---

## 🔍 Common Issues & Solutions

### Issue 1: Second File Not Created
**Symptom:** Task.yaml má 2 files, len prvý sa vytvorí

**Solution:** Split do 2 tasks
```yaml
# Task 1
files:
  - path: utils/module.py

# Task 2 (separate yaml)
files:
  - path: tests/test_module.py
```

---

### Issue 2: Git Push Fails
**Symptom:** Files created but not on GitHub

**Check:** Git Commit node v n8n
```bash
# Should have:
git add . && git commit -m "..." && git push origin main
```

---

### Issue 3: Import Errors After Creation
**Symptom:** File created but imports fail

**Solution:** Verify v testing section
```yaml
testing:
  commands:
    - python -c "from utils.module import Class"
  expected:
    - No import errors
```

---

### Issue 4: Wrong Project Name
**Symptom:** API error "project not found"

**Solution:** Check exact GitHub repo name
```yaml
# ✅ Correct
project: uae-legal-agent

# ❌ Wrong
project: uae_legal_agent
project: UAELegalAgent
```

---

## 📊 Workflow Statistics

### Token Usage per Task Type

| Task Type | Avg Tokens | Recommended Chat |
|-----------|-----------|------------------|
| Small module (<100 lines) | 15k-25k | Single chat OK |
| Large module (>200 lines) | 30k-50k | Single chat OK |
| Test suite (15+ tests) | 20k-35k | Single chat OK |
| Session notes | 5k-10k | Single chat OK |
| Multiple related tasks | 50k+ | NEW CHAT required |

### Success Rates

| Scenario | Success Rate | Notes |
|----------|-------------|-------|
| 1 file per task | 98% | ✅ Recommended |
| 2 files per task | 50% | ❌ Only first created |
| 3+ files per task | 0% | ❌ Never works |

---

## ✅ Pre-Submit Checklist

Before running workflow, verify:

**Task.yaml Structure:**
- [ ] Type is valid
- [ ] Project name exact match
- [ ] Priority set
- [ ] Description clear
- [ ] Context provided
- [ ] **ONLY 1 file in requirements.files**
- [ ] Content complete (no TODOs)
- [ ] Dependencies listed or []
- [ ] Testing commands present
- [ ] Git commit message formatted
- [ ] Notes added

**Workflow Readiness:**
- [ ] Task.yaml saved in project root
- [ ] N8n workflow running
- [ ] Git credentials configured
- [ ] Target project exists on GitHub

**Post-Execution:**
- [ ] File created on GitHub
- [ ] Git commit visible
- [ ] File content correct
- [ ] No syntax errors
- [ ] Imports work (if Python)

---

## 🔄 Continuous Improvement

### Logging Issues

When workflow fails, document:
```yaml
issue:
  date: 2025-10-30
  task: "Create utils/module.py"
  symptom: "Second file not created"
  root_cause: "Workflow limitation - 1 file only"
  solution: "Split into 2 separate tasks"
  status: "Documented in WORKFLOW_RULES.md"
```

### Updating Rules

When discovering new patterns:
1. Document in this file
2. Update TASK_YAML_FORMAT.md if needed
3. Inform all projects using workflow
4. Test with simple example
5. Roll out to production

---

## 📚 Related Documentation

- `TASK_YAML_FORMAT.md` - Task.yaml specification
- `README.md` - Overall workflow documentation
- `docs/examples/` - Example task.yaml files
- `docs/troubleshooting/` - Common issues & fixes

---

## 🎓 Learning from Experience

### 2025-10-29: Config Module
**Learned:** Git push nebolo automatické
**Fix:** Pridaný `git push origin main` do Git Commit node
**Rule:** Always include push in workflow

### 2025-10-30: Embeddings Module
**Learned:** Workflow vytvorí len 1 súbor aj keď task má 2
**Fix:** Split do 2 separate tasks
**Rule:** 1 task.yaml = 1 súbor MAXIMUM

---

**Autor:** Zoltán Rauscher  
**Projekt:** claude-dev-automation  
**Účel:** Pravidlá pre efektívne používanie n8n workflow  
**Verzia:** 2.0 (2025-10-30)

⚠️ **Remember: 1 Task = 1 File = Best Results!**