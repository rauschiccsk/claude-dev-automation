# Session Notes: 2025-10-28 - n8n File Trigger Implementation

**Dátum:** 28. október 2025  
**Projekt:** claude-dev-automation  
**Status:** ✅ KOMPLETNÝ - Workflow 100% funkčný

---

## Prehľad Session

Úspešná migrácia n8n workflow z Manual Trigger na File Trigger s automatickým spúšťaním pri zmene task.yaml súboru. Workflow otestovaný end-to-end na reálnom projekte uae-legal-agent.

---

## Hlavné Úspechy

### ✅ File Trigger Workflow
- **Pred:** Manual Trigger - manuálne spúšťanie workflow
- **Po:** File Trigger - automatické spustenie pri zmene task.yaml
- **Benefit:** Nepotrebujeme meniť workflow, len upraviť task.yaml

### ✅ YAML Task Format
- Vytvorený štandardný formát pre task definíciu
- Verziovateľné v Git
- Čitateľnejšie než JSON v Manual Trigger

### ✅ Windows Path Fix
- **Problém:** Backslash `\` nefungoval v Read/Write Files node
- **Riešenie:** Forward slash `/` - `C:/Development/project`
- **Lesson learned:** n8n node vyžaduje forward slashes aj na Windows

### ✅ Binary Data Reading
- **Problém:** Read/Write Files vracia binary data, nie JSON
- **Riešenie:** Parse z `$input.item.binary.data` ako Buffer → UTF8

### ✅ Node Reference Fix
- **Problém:** Execute Operations a Git Commit používali `Parse Task Input` 
- **Riešenie:** Zmenené na `Parse YAML Task` pre správny project name

---

## Technické Detaily

### Workflow Nodes
```
File Trigger 
  → Read/Write Files from Disk (forward slash paths!)
    → Parse YAML Task (reads binary data)
      → Parse Task Input (Flask API)
        → Build Smart Context (Flask API)
          → Call Claude API
            → Parse File Operations
              → Execute Operations (Flask API)
                → Git Commit
                  → Generate Clean Response
                    → Save Response (Flask API)
```

### Kľúčové Opravy

**1. File Trigger Nastavenie:**
```
Trigger On: Changes to a Specific File
File Path: C:\Deployment\claude-dev-automation\task.yaml
```

**2. Read/Write Files from Disk:**
```
Operation: Read File(s) From Disk
File(s) Selector: ={{ $json.path }}
⚠️ FORWARD SLASH: C:/Development/project (nie C:\Development\project)
Settings → Always Output Data: ON
```

**3. Parse YAML Task (Function node):**
```javascript
// Read from binary data
const buffer = Buffer.from($input.item.binary.data.data, 'base64');
const fileContent = buffer.toString('utf8');
// ... parse YAML ...
```

**4. Execute Operations JSON Body:**
```javascript
={{ {
  "project_name": $('Parse YAML Task').item.json.project,
  "operations": $json.operations
} }}
```

**5. Git Commit Command:**
```
cd C:/Development/{{$node['Parse YAML Task'].json.project}} && git add . && git commit -m "Auto-commit: {{$node['Parse YAML Task'].json.task}}" && git status
```

---

## Test Run - UAE Legal Agent

**Task:** Vytvorenie directory structure pre uae-legal-agent projekt

**Výsledok:**
- ✅ Vytvorené 5 súborov (.gitkeep + README.md)
- ✅ Git commit úspešný
- ✅ Response.md vygenerovaný
- ✅ Token usage: 580 tokens
- ✅ Cost: $0.0054 USD

**Súbory:**
```
uae-legal-agent/
├── data/
│   ├── raw_documents/.gitkeep
│   ├── processed/.gitkeep
│   ├── embeddings/.gitkeep
│   └── README.md
└── logs/.gitkeep
```

---

## Debugging Process

### Problém #1: File Trigger nevracia obsah súboru
- **Symptóm:** Parse YAML Task dostal len metadata, nie obsah
- **Debug:** Pridaný Function node na kontrolu File Trigger outputu
- **Zistenie:** File Trigger vracia len `{event: "change", path: "..."}`
- **Riešenie:** Pridaný Read/Write Files node na čítanie obsahu

### Problém #2: Read/Write Files vracia prázdny output
- **Symptóm:** `No output data returned`
- **Debug:** Testovaný hardcoded path
- **Zistenie:** Backslash `\` nefunguje
- **Riešenie:** Forward slash `/` v cestách

### Problém #3: Parse YAML Task nedokáže parsovať
- **Symptóm:** `Cannot read properties of null (reading 'split')`
- **Debug:** Skontrolovaný INPUT Parse YAML Task
- **Zistenie:** Obsah je v binary.data, nie v json
- **Riešenie:** Buffer.from() → toString('utf8')

### Problém #4: Execute Operations - "Project not found"
- **Symptóm:** Flask hľadá projekt "structure: uae-legal-agent"
- **Debug:** Skontrolovaný OUTPUT Parse YAML Task vs Parse Task Input
- **Zistenie:** Execute Operations používa zlý node reference
- **Riešenie:** Zmenené z `Parse Task Input` na `Parse YAML Task`

### Problém #5: Git Commit - "path not found"
- **Symptóm:** Rovnaký ako #4, zlá cesta
- **Riešenie:** Zmenené node reference na `Parse YAML Task`

---

## Workflow Usage

### Ako spustiť task:

**1. Vytvor/uprav task.yaml:**
```yaml
task:
  type: feature
  project: project-name
  description: |
    Task description here
  
  context:
    - "Context info"
  
  requirements:
    - Requirement 1
    - Requirement 2
```

**2. Ulož súbor:**
```
C:\Deployment\claude-dev-automation\task.yaml
```

**3. Workflow sa automaticky spustí!**

**4. Over výsledok:**
- Executions v n8n
- Súbory v C:\Development\{project}/
- Git log
- response.md

---

## Optimalizácie (Budúce)

### Drobné fixes:
- [ ] Response.md: "Project" zobrazuje celý task string namiesto len názvu
- [ ] Validácia task.yaml pred spustením (check project exists)
- [ ] Better error handling v Parse YAML Task

### Možné rozšírenia:
- [ ] Support pre viacero taskov v jednom YAML (batch processing)
- [ ] Notification system (email/Slack pri dokončení)
- [ ] Task templates pre rôzne typy taskov
- [ ] Web UI pre task.yaml editor

---

## Súbory

**Exportované:**
- `n8n-claude-dev-automation.json` - finálny workflow (bez API key)

**Dokumentácia:**
- Tento session notes
- Project rules/conventions (separátny dokument)

---

## Metriky

**Token Efficiency:**
- Manual chat: ~20,000-50,000 tokens pre podobný task
- Automated workflow: 580 tokens
- **Redukcia: ~98%** 🚀

**Time Efficiency:**
- Manual: 5-10 minút interakcie
- Automated: <30 sekúnd execution

**Cost:**
- Task: $0.0054 USD
- Zostatok: ~$2.50 USD

---

## Lessons Learned

1. **n8n paths:** Vždy forward slash `/` aj na Windows
2. **Binary data:** Read/Write Files vracia binary, nie text
3. **Node references:** Pozor na správne node names v expressions
4. **Debug systematicky:** Nepreskakovať od riešenia k riešeniu
5. **Settings matter:** "Always Output Data" je kritické pre debugging
6. **File Trigger limitations:** Nevracia obsah, len path

---

## Next Steps

1. ✅ Export workflow JSON
2. ✅ Session notes
3. ✅ Project rules documentation
4. ⏳ Commit & push
5. ⏳ Test na ďalších reálnych taskoch

---

**Status:** Production ready ✅  
**Workflow:** 100% funkčný  
**Dokumentácia:** Kompletná