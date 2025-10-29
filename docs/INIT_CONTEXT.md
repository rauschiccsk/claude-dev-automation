# CLAUDE-DEV-AUTOMATION - INIT CONTEXT

**Quick Start Initialization File**  
**Version:** 1.0.0  
**Date:** 2025-10-29  
**Language:** SLOVENČINA

---

## CRITICAL INSTRUCTIONS FOR CLAUDE

### 1. Language & Communication
- **VŽDY komunikuj PO SLOVENSKY**
- Slovenčina je primárny jazyk projektu
- Technické termíny môžu byť anglicky
- **Token info na konci KAŽDEJ odpovede:**
```
Token usage: Used X / 190,000 | Remaining Y | Z% | Status
```

### 2. FILE LOADING - CRITICAL RULE 🛑

**Ak nemôžeš načítať súbor z project_file_access.json:**

```
🛑 STOP - FILE LOADING FAILED

Súbor: [názov súboru]
URL: [raw_url z manifestu]
Problém: [popis - napr. GitHub cache, permissions, etc]

AKCIA POTREBNÁ:
1. User musí regenerovať manifest: python scripts/generate_project_access.py
2. User musí commitnúť a pushnúť zmeny
3. User musí restartovať chat s novým cache version

NEPOKRAČUJEM bez prístupu k aktuálnym súborom!
```

**NIKDY:**
- ❌ Nevymýšľaj workaroundy (cache busting, alternative URLs)
- ❌ Nepokračuj s prácou na základe starých/cached dát
- ❌ Neproš používateľa o manuálne URLs

**VŽDY:**
- ✅ STOP immediately ak file loading fails
- ✅ Informuj používateľa o presnom probléme
- ✅ Poskytni konkrétne kroky na fix

### 3. Automatic Initialization Sequence

**Po načítaní INIT_CONTEXT.md + project_file_access.json, AUTOMATICKY načítaj:**

```
1. docs/sessions/ → Nájdi najnovšiu session (YYYY-MM-DD_*.md)
2. Načítaj najnovšiu session → Aktuálny stav, progress, next steps
3. AK ZLYHÁ NAČÍTANIE → STOP podľa pravidla #2
```

**Potom odpovedz:**
```
Projekt načítaný. 

Aktuálny stav:
[Zhrnutie z najnovšej session - progress, dokončené tasky]

Posledná session: [dátum]
[Kľúčové body z session notes]

Ďalší krok:
[Next steps z session notes]

Čo robíme?
```

**DÔLEŽITÉ:** 
- Načítaj **latest session** AUTOMATICKY pri inicializácii
- AK ZLYHÁ → použiť pravidlo 🛑 STOP
- Nezobrazuj XMLy ani raw content
- Len čisté zhrnutie v slovenčine
- Krátko a jasne

### 4. File Access via Manifest

S `project_file_access.json` máš prístup k všetkým súborom projektu.

**Každý súbor má:**
```json
{
  "path": "services/context_api.py",
  "raw_url": "https://raw.githubusercontent.com/.../file.py?v=TIMESTAMP",
  "size": 12345,
  "category": "python_services"
}
```

**Keď potrebuješ konkrétny súbor:**
1. Nájdi ho v `project_file_access.json`
2. Použiť `raw_url` (s cache version parametrom)
3. AK ZLYHÁ → 🛑 STOP
4. Nekopíruj celé súbory - referencuj ich

**Cache Version:**
- Každá URL obsahuje `?v=TIMESTAMP` parameter
- Zabezpečuje fresh content z GitHubu
- User regeneruje manifest po každom push

### 5. Key Documents (načítaj len podľa potreby)
- **Project workflow:** `docs/GIT_WORKFLOW.md`
- **Project rules:** `docs/PROJECT_RULES.md`
- **Installation:** `docs/INSTALLATION_GUIDE.md`
- **Setup guides:** `docs/PYCHARM_SETUP.md`, `docs/QUICK_INSTALL.md`
- **Testing:** `docs/TEST_TASKS.md`

---

## PROJEKT INFO

### Základné údaje
- **Názov:** Claude Dev Automation
- **Účel:** AI-Driven Multi-Project Development s 98% úsporou tokenov
- **Tech Stack:** Python 3.11+ + Flask + n8n + Claude API
- **Developer:** ICC (rauschiccsk)
- **Location:** Komárno, SK
- **GitHub:** https://github.com/rauschiccsk/claude-dev-automation

### Aktuálny stav -> Načítaj z session notes!
```
NEČÍTAJ TENTO HARDCODED STAV!
VŽDY načítaj najnovšiu session z docs/sessions/
Session notes sú single source of truth
AK ZLYHÁ NAČÍTANIE → 🛑 STOP
```

---

## ARCHITECTURE OVERVIEW

### System Components
```
┌─────────────────────────────────────────────────────┐
│ n8n Workflow (Main Orchestrator)                    │
│ - Parse task                                        │
│ - Build context                                     │
│ - Call Claude API                                   │
│ - Execute operations                                │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ Flask API: services/context_api.py                  │
│ - /parse-task                                       │
│ - /build-context                                    │
│ - /execute-operations                               │
│ - /verify-files                                     │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ Python Tools (Legacy - kept for reference)         │
│ - orchestrator.py                                   │
│ - claude_runner.py                                  │
│ - enhanced_context_builder.py                      │
│ - file_operations.py                                │
└─────────────────────────────────────────────────────┘
```

### Migration Status
- **OLD:** Python orchestrator (`tools/orchestrator.py`)
- **NEW:** n8n workflow + Flask API
- **Reason:** Better debugging, production-ready error handling

---

## KEY FILES

### Active System
- **Flask API:** `services/context_api.py` - All endpoints
- **n8n Workflow:** `workflows/n8n-claude-dev-automation.json`
- **Requirements:** `services/requirements.txt`

### Legacy System (Reference)
- **Orchestrator:** `tools/orchestrator.py`
- **Claude Runner:** `tools/claude_runner.py`
- **Context Builder:** `tools/enhanced_context_builder.py`
- **File Operations:** `tools/file_operations.py`

### Documentation
- **Complete Summary:** `docs/COMPLETE_SUMMARY.md` (ak existuje)
- **Session Notes:** `docs/sessions/YYYY-MM-DD_*.md`
- **Project Rules:** `docs/PROJECT_RULES.md`

---

## CURRENT PROBLEM (MODIFY Operations)

### Issue
**n8n Workflow NEčíta existujúce súbory pred MODIFY operáciou**

**Scenario:**
1. Task: "oprav `utils/config.py`"
2. Workflow zavolá Claude **BEZ obsahu `config.py`**
3. Claude nevie čo opravovať → vytvorí súbor from scratch
4. Výsledok: Zlý súbor na zlom mieste

**Solution Needed:**
```
IF task obsahuje MODIFY/UPDATE operáciu:
  1. Detekuj ktorý súbor sa má upraviť
  2. Načítaj existujúci súbor z disku
  3. Pridaj obsah do Claude promptu
  4. Potom zavolaj Claude API
ELSE (CREATE operácia):
  Pokračuj normálne
```

---

## TECH STACK

### Core Technologies
- **Python:** 3.11+
- **Flask:** REST API server
- **n8n:** Workflow automation
- **Claude API:** Sonnet 4.5 (claude-sonnet-4-5-20250929)
- **Git:** Version control

### Key Python Modules
- `anthropic` - Claude API client
- `python-dotenv` - Environment variables
- `flask` - API server

### System Architecture
- **Windows Server 2012 R2** (ICC server)
- **128GB RAM, 12 cores**
- **Remote Desktop Services** for multi-user

---

## CRITICAL REMINDERS

### VŽDY:
- Komunikuj PO SLOVENSKY
- Načítaj latest session pri inicializácii
- **AK ZLYHÁ FILE LOADING → 🛑 STOP**
- Buď konkrétny a actionable  
- Používaj emojis pre clarity (v odpovediach, NIE v INIT_CONTEXT.md)
- Odkazuj na súbory cez manifest
- Validuj všetky zmeny

### NIKDY:
- Nekopíruj celé súbory do odpovede
- Nemení jazyk na angličtinu
- Nepridávaj zbytočné vysvetlenia
- Nenavrhuj zmeny bez schválenia
- Nepoužívaj hardcoded stav z INIT_CONTEXT.md
- **NEPOKRAČUJ ak nemôžeš načítať súbory**
- **NEVYMÝŠĽAJ workaroundy pre file loading issues**

### Pri každom vytvorení súboru:
```
Nezabudni:
1. Commitnúť zmeny
2. Pushnúť na GitHub  
3. Regenerovať manifest: python scripts/generate_project_access.py
4. Updatnúť session notes (end of session)
```

---

## KONTAKT

- **Developer:** ICC (rausch@icc.sk)
- **GitHub:** https://github.com/rauschiccsk/claude-dev-automation
- **Location:** Komárno, SK

---

## QUICK LINKS

- **Aktuálny stav:** `docs/sessions/` NAJNOVŠIA SESSION = SINGLE SOURCE OF TRUTH!
- **Flask API:** `services/context_api.py`
- **n8n Workflow:** `workflows/n8n-claude-dev-automation.json`
- **Manifest:** `docs/project_file_access.json`

---

## INITIALIZATION CHECKLIST

**Claude musí urobiť pri každom novom chate:**

```
1. Načítaj INIT_CONTEXT.md (tento súbor)
2. Načítaj project_file_access.json
3. Nájdi najnovšiu session v docs/sessions/
4. Načítaj najnovšiu session <- KRITICKÉ!
   → AK ZLYHÁ: 🛑 STOP a informuj usera
5. Zhrň aktuálny stav (z session)
6. Zhrň poslednú session (kľúčové body)
7. Identifikuj ďalší krok (next steps)
8. Odpovedz PO SLOVENSKY s prehľadom
```

**Výstupný formát:**
```
Projekt načítaný. 

Aktuálny stav:
- Progress: [z session]
- Dokončené tasky: [z session]
- Aktuálny task: [z session]

Posledná session: [dátum]
- [kľúčové body z session]

Ďalší krok:
- [next steps z session]

Čo robíme?
```

---

## Session Notes Structure

**Každá session obsahuje:**
- Dokončené tasky (čo sa urobilo)
- Vytvorené/updatnuté súbory
- Technické rozhodnutia
- Progress update
- Next steps
- Files to commit
- Achievements

**Session naming:** `docs/sessions/YYYY-MM-DD_*.md`

---

## TROUBLESHOOTING

### Problem: Nemôžem načítať súbor z manifestu

**Symptómy:**
- web_fetch vracia starý cached obsah
- Súbor bol updatnutý na GitHube ale vidím starú verziu
- Error pri načítaní súboru

**Riešenie:**
```bash
# User musí:
1. cd C:\Development\claude-dev-automation
2. python scripts/generate_project_access.py
3. git add docs/project_file_access.json
4. git commit -m "Regenerated manifest with fresh cache version"
5. git push
6. Reštartovať Claude chat s novými URLs
```

**Claude:**
- 🛑 STOP immediately
- Informuj usera o presnom probléme
- Poskytni kroky vyššie
- NEPOKRAČUJ s prácou

---

**REMEMBER:** 
- **AUTOMATICKY načítaj latest session**
- **AK ZLYHÁ FILE LOADING → 🛑 STOP**
- **Nekopíruj XML/JSON** - len zhrnutie
- **Komunikuj PO SLOVENSKY**
- **Buď konkrétny**
- **Session notes = single source of truth**