# n8n Workflows

Tento adresár obsahuje n8n workflow súbory pre Claude Dev Automation.

---

## 📋 Dostupné Workflows

### **claude-dev-automation.json**

Hlavný workflow pre automatizáciu Claude API interakcií.

**Čo robí:**
1. Načíta task.md z workspace
2. Zbuilduje smart context (session notes, README, Git, TODOs)
3. Zavolá Claude API
4. Parsuje file operations z XML
5. Vykoná file operations (create/modify/delete)
6. Commitne zmeny do Gitu
7. Vygeneruje clean response.md (bez full source code)

**Nodes:** 9  
**Execution time:** ~20-30 sekúnd  
**Dependencies:** Context API (Flask) musí bežať na http://localhost:5000

---

## 🔧 Ako Importovať

### **Krok 1: Otvor n8n**
```
http://localhost:5678
```

### **Krok 2: Import**
1. Menu (≡) → **Import from File**
2. Vyber `claude-dev-automation.json`
3. Alebo copy-paste obsah súboru

### **Krok 3: Nastav Credentials**
1. Klikni na node **"Call Claude API"**
2. Create new credential: **HTTP Header Auth**
   - Header Name: `x-api-key`
   - Header Value: `sk-ant-api03-...`

### **Krok 4: Over Cesty**
Skontroluj tieto cesty v nodes:
- Workspace: `C:/Development/claude-dev-automation/workspace`
- Projects: `C:/Development`
- Context API: `http://localhost:5000`

### **Krok 5: Save & Test**
1. Save workflow (Ctrl+S)
2. Execute Workflow (▶️)

---

## 🚀 Použitie

### **Pred Spustením:**
1. Context API musí bežať:
   ```bash
   cd C:\Development\claude-dev-automation\services
   python context_api.py
   ```

2. Uprav `workspace/task.md`:
   ```markdown
   PROJECT: your-project
   TASK: Your task description
   ...
   ```

### **Spustenie:**
1. V n8n otvor workflow
2. Klikni **Execute Workflow** (▶️)
3. Sleduj progress
4. Skontroluj `workspace/response.md`

---

## 🐛 Troubleshooting

### **Node "Build Smart Context" červený**
- **Príčina:** Context API nebeží
- **Fix:** Spusti `python services/context_api.py`

### **Node "Call Claude API" červený**
- **Príčina:** Chybný API key alebo credentials
- **Fix:** Over credentials v n8n Settings

### **Node "Parse File Operations" prázdne**
- **Príčina:** Claude nevrátil XML `<file_operations>`
- **Fix:** Klikni na "Call Claude API" → Output → over response

### **Node "Execute File Operations" failed**
- **Príčina:** Projekt neexistuje alebo zlá cesta
- **Fix:** Over že projekt existuje v `C:/Development/`

---

## 📊 Výhody vs Python Orchestrator

| Feature | Python | n8n |
|---------|--------|-----|
| Debugging | Console logs | Visual nodes + data |
| Iteration | 5-10 min | 30 sec |
| Response.md | 25-30k | 1-2k |
| Error visibility | Hidden | Red node, click to see |

---

## 🔄 Update Workflow

Ak upravíš workflow v n8n:

1. V n8n: Menu → **Export**
2. Save ako `claude-dev-automation.json`
3. Prepíš starý súbor v tomto adresári
4. Git commit zmeny

---

## 📞 Related Files

- **Context API:** `../services/context_api.py`
- **Python Modules:** `../tools/`
- **Workspace:** `../workspace/`
- **Documentation:** `../docs/`

---

**Last Updated:** 2025-10-27  
**Version:** 1.0  
**Status:** Production Ready ✅