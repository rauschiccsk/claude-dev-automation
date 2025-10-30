# 📋 TASK.YAML FORMAT - Oficiálna Špecifikácia

**Verzia:** 2.0  
**Dátum:** 2025-10-30  
**Projekt:** claude-dev-automation  

---

## 🎯 Základné Pravidlá

### ⚠️ KRITICKÉ PRAVIDLO #1: Jeden Task = Jeden Súbor

```yaml
# ✅ SPRÁVNE - Jeden súbor
type: implementation
project: project-name
priority: P1
description: "Create utils/module.py"
requirements:
  files:
    - path: utils/module.py
      content: |
        # Complete file content here

# ❌ ZLE - Viac súborov
requirements:
  files:
    - path: utils/module.py
      content: |
        ...
    - path: tests/test_module.py  # ❌ Druhý súbor nefunguje!
      content: |
        ...
```

**Dôvod:**
- n8n workflow má problém s vytváraním viacerých súborov naraz
- Len prvý súbor sa vytvorí správne
- Druhý a ďalšie súbory sa ignorujú

**Riešenie:**
- 1 task.yaml = 1 súbor
- Pre modul + test = 2 separate tasky
- Task 1: `utils/module.py`
- Task 2: `tests/test_module.py`

---

## 📐 Povinná Štruktúra

### Top Level Fields (Required)

```yaml
type: implementation | documentation | configuration | testing
project: project-name-exactly-as-in-repo
priority: P1 | P2 | P3

description: |
  Brief description of what this task does.
  Can be multi-line.
  Should explain the purpose clearly.

context:
  - Current state information
  - Why this task is needed
  - Dependencies on other modules
  - Any relevant background

requirements:
  files:
    - path: relative/path/to/file.ext
      content: |
        Complete file content goes here.
        Include all code, no placeholders.
        Must be production-ready.

dependencies:
  - package-name>=version
  - another-package>=version

testing:
  commands:
    - pytest tests/test_file.py -v
    - python -c "import module; print('OK')"
  expected:
    - All tests passing
    - No import errors

git_commit: "type: Brief commit message"

notes:
  - Important note 1
  - Important note 2
  - Session-specific information
```

---

## 🔤 Field Specifications

### `type`
**Allowed Values:**
- `implementation` - Python kód (utils/, services/, api/)
- `documentation` - Markdown súbory (docs/, README)
- `configuration` - Config súbory (.env.example, pytest.ini)
- `testing` - Test súbory (tests/)

### `project`
**Format:** Exact GitHub repo name
**Examples:**
- `uae-legal-agent`
- `nex-genesis-server`
- `supplier-invoice-loader`

**⚠️ CRITICAL:** Musí byť presne ako v GitHub URL!

### `priority`
- `P1` - Critical (blocking other work)
- `P2` - Important (should do soon)
- `P3` - Nice to have (can wait)

### `description`
**Requirements:**
- Brief but complete
- Explains what will be created
- States purpose clearly
- Can be multi-line using `|`

### `context`
**Purpose:** Provide background for Claude
**Include:**
- Current project state
- Why this file is needed
- Dependencies on other modules
- Related files that exist
- Phase information

### `requirements.files`
**Structure:**
```yaml
requirements:
  files:
    - path: exact/path/from/project/root.py
      content: |
        Complete file content.
        No placeholders like "# Implementation here"
        Production-ready code only.
```

**⚠️ SINGLE FILE ONLY:**
```yaml
# ✅ Correct
files:
  - path: utils/module.py
    content: |
      ...

# ❌ Wrong - second file ignored
files:
  - path: utils/module.py
    content: |
      ...
  - path: tests/test.py  # This will NOT be created!
    content: |
      ...
```

### `dependencies`
**Format:** Simple list
```yaml
dependencies:
  - package-name>=version
  - another-package>=version
```

**Leave empty if no new dependencies:**
```yaml
dependencies: []
```

### `testing`
**Purpose:** Verify created file works
```yaml
testing:
  commands:
    - pytest tests/test_module.py -v
    - python -c "from utils.module import Class"
  expected:
    - All tests passing
    - No import errors
    - Module loads successfully
```

### `git_commit`
**Format:** Conventional Commits
```yaml
git_commit: "feat: Add embeddings module"
git_commit: "test: Add tests for config module"
git_commit: "docs: Add session notes for task X"
git_commit: "fix: Resolve import error in main.py"
```

**Types:**
- `feat:` - New feature/module
- `test:` - Test files
- `docs:` - Documentation
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `chore:` - Dependencies, config

### `notes`
**Purpose:** Session-specific info
```yaml
notes:
  - This resolves import error in main.py
  - Implements Phase 1 module 6/9
  - Uses lazy loading for performance
  - Multilingual support (AR/EN/SK)
```

---

## 📚 Complete Examples

### Example 1: Python Module

```yaml
type: implementation
project: uae-legal-agent
priority: P1

description: |
  Create utils/embeddings.py module with EmbeddingManager class.
  Generate text embeddings using sentence-transformers.

context:
  - main.py requires EmbeddingManager that doesn't exist
  - Part of Phase 1 core modules
  - Integrates with vector_store.py
  - Multilingual support needed (AR/EN/SK)

requirements:
  files:
    - path: utils/embeddings.py
      content: |
        """Text embedding generation."""
        
        from sentence_transformers import SentenceTransformer
        from typing import List
        
        class EmbeddingManager:
            def __init__(self):
                self._model = None
            
            # ... complete implementation

dependencies:
  - sentence-transformers>=2.2.0
  - torch>=2.0.0

testing:
  commands:
    - python -c "from utils.embeddings import EmbeddingManager"
  expected:
    - No import errors
    - Module loads successfully

git_commit: "feat: Add embeddings module with multilingual support"

notes:
  - Resolves main.py import error
  - Phase 1: 6/9 modules complete
  - Test file will be separate task
```

### Example 2: Test File

```yaml
type: testing
project: uae-legal-agent
priority: P1

description: |
  Create comprehensive tests for utils/embeddings.py module.
  Test all EmbeddingManager methods and edge cases.

context:
  - utils/embeddings.py already created and working
  - Need test coverage for all methods
  - Test multilingual support (AR/EN/SK)

requirements:
  files:
    - path: tests/test_embeddings.py
      content: |
        """Tests for embeddings module."""
        
        import pytest
        from utils.embeddings import EmbeddingManager
        
        @pytest.fixture
        def embedder():
            return EmbeddingManager()
        
        def test_initialization(embedder):
            # ... complete test implementation

dependencies: []

testing:
  commands:
    - pytest tests/test_embeddings.py -v
  expected:
    - All 13 tests passing
    - 95%+ coverage

git_commit: "test: Add comprehensive tests for embeddings module"

notes:
  - Covers all EmbeddingManager methods
  - Tests multilingual support
  - 13 test cases total
```

### Example 3: Documentation

```yaml
type: documentation
project: uae-legal-agent
priority: P2

description: |
  Create session notes for embeddings module implementation.
  Document what was done, decisions made, and next steps.

context:
  - utils/embeddings.py created successfully
  - tests/test_embeddings.py created and passing
  - Phase 1 now 67% complete (6/9 modules)

requirements:
  files:
    - path: docs/sessions/2025-10-30_embeddings.md
      content: |
        # Session Notes: Embeddings Module
        
        **Date:** 2025-10-30
        **Status:** ✅ Completed
        
        ## Completed
        - Created utils/embeddings.py
        - Created tests/test_embeddings.py
        - All 13 tests passing
        
        ## Next Steps
        - Implement vector_store integration
        - Test RAG pipeline

dependencies: []

testing:
  commands: []
  expected:
    - Session notes added to repo

git_commit: "docs: Add session notes for embeddings module"

notes:
  - Documents embeddings implementation
  - Records workflow improvements
```

---

## ⚠️ Common Mistakes

### ❌ Mistake 1: Multiple Files in One Task
```yaml
# WRONG - Only first file will be created!
requirements:
  files:
    - path: utils/module.py
      content: |
        ...
    - path: tests/test_module.py  # ❌ Ignored!
      content: |
        ...
```

**Fix:** Create two separate task.yaml files.

### ❌ Mistake 2: Wrong Project Name
```yaml
# WRONG
project: uae_legal_agent  # ❌ Underscore instead of dash

# CORRECT
project: uae-legal-agent  # ✅ Exact GitHub repo name
```

### ❌ Mistake 3: Placeholder Content
```yaml
# WRONG
content: |
  def function():
      # TODO: Implement this  # ❌ Placeholder!
      pass

# CORRECT
content: |
  def function():
      """Complete implementation."""
      result = do_actual_work()  # ✅ Real code
      return result
```

### ❌ Mistake 4: Missing Required Fields
```yaml
# WRONG - Missing 'description'
type: implementation
project: my-project
requirements:
  files:
    - path: file.py

# CORRECT - All required fields
type: implementation
project: my-project
priority: P1
description: "Create file.py module"
requirements:
  files:
    - path: file.py
      content: |
        ...
```

---

## ✅ Validation Checklist

Before submitting task.yaml, verify:

- [ ] `type` is valid (implementation/documentation/configuration/testing)
- [ ] `project` exactly matches GitHub repo name
- [ ] `priority` is set (P1/P2/P3)
- [ ] `description` is present and clear
- [ ] `context` provides enough background
- [ ] `requirements.files` has ONLY ONE file
- [ ] `requirements.files[0].path` is correct relative path
- [ ] `requirements.files[0].content` is complete (no placeholders)
- [ ] `dependencies` lists new packages (or is empty list)
- [ ] `testing.commands` can verify the file works
- [ ] `git_commit` follows conventional commits format
- [ ] `notes` document important points

---

## 🔄 Workflow Process

### 1. Modul s Testami = 2 Tasky

**Task 1: Create Module**
```yaml
type: implementation
requirements:
  files:
    - path: utils/module.py
```

**Task 2: Create Tests**
```yaml
type: testing
requirements:
  files:
    - path: tests/test_module.py
```

### 2. Execution Order

1. Ulož `task.yaml` do projektu
2. Spusti n8n workflow
3. Workflow vytvorí súbor
4. Workflow commitne a pushne
5. Overiť že súbor existuje na GitHub
6. Ak potrebuješ ďalší súbor → nový task.yaml

### 3. Session Notes

Na konci session vytvoriť documentation task:
```yaml
type: documentation
requirements:
  files:
    - path: docs/sessions/YYYY-MM-DD_topic.md
```

---

## 📊 Task Types by Use Case

| Use Case | Type | Example Path |
|----------|------|--------------|
| Python module | `implementation` | `utils/module.py` |
| Test file | `testing` | `tests/test_module.py` |
| Config file | `configuration` | `.env.example` |
| Session notes | `documentation` | `docs/sessions/2025-10-30.md` |
| API endpoint | `implementation` | `api/endpoints/cases.py` |
| README update | `documentation` | `README.md` |

---

## 🎯 Best Practices

### 1. Descriptive Task Names
```yaml
# Good
description: "Create embeddings module with multilingual support"

# Bad
description: "Create file"
```

### 2. Complete Context
```yaml
context:
  - What exists: "vector_store.py already implemented"
  - What's needed: "main.py requires EmbeddingManager"
  - Why: "For RAG pipeline integration"
  - Phase: "Phase 1 module 6/9"
```

### 3. Realistic Testing
```yaml
testing:
  commands:
    - pytest tests/test_module.py -v  # Real command
    - python -c "from utils.module import Class"  # Verify import
  expected:
    - All 10 tests passing  # Specific number
    - No import errors
```

### 4. Informative Notes
```yaml
notes:
  - Resolves issue #X
  - Implements feature Y from roadmap
  - Uses pattern Z for consistency
  - Next: Integrate with module A
```

---

**Autor:** Zoltán Rauscher  
**Projekt:** claude-dev-automation  
**Účel:** Štandardizácia task.yaml formátu pre n8n workflow  
**Verzia:** 2.0 (2025-10-30)

✅ **Remember: 1 Task = 1 File!**