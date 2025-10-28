# Claude Dev Automation - Project Rules & Conventions

**Posledná aktualizácia:** 28. október 2025  
**Účel:** Pravidlá a preferencie pre interakciu s Claude v tomto projekte

---

## 🎯 Základné Pravidlá

### 1. Výstup Kódu
**PRAVIDLO:** Všetok kód VÝHRADNE do artifacts  
**Dôvod:** Lepšia organizácia, verziovanie, kopírovanie  
**Výnimka:** Žiadna - platí vždy

```
✅ Správne: Kód v <artifacts>
❌ Nesprávne: Kód v markdown code blokoch v odpovedi
```

### 2. Počet Riešení
**PRAVIDLO:** Ponúkať len JEDNO riešenie  
**Dôvod:** Znižuje rozhodovací overhead, rýchlejšia implementácia  
**Výnimka:** Len ak je explicitne požiadané o alternatívy

```
✅ Správne: "Najlepšie riešenie je X, pretože..."
❌ Nesprávne: "Máš 3 možnosti: A, B, C. Ktorú chceš?"
```

### 3. Iteratívny Prístup
**PRAVIDLO:** Krok po kroku, čakať na potvrdenie  
**Dôvod:** Umožňuje debugovanie, validáciu každého kroku  
**Aplikácia:** Pri viacstupňových taskoch

```
✅ Správne: 
  - Krok 1: Urob X
  - [čakaj na feedback]
  - Krok 2: Teraz Y
  
❌ Nesprávne: 
  - Urob kroky 1-5 naraz
```

### 4. Systematický Debugging
**PRAVIDLO:** Nenáhliť sa, nájsť príčinu  
**Dôvod:** Dlhodobé riešenie > quick fix  
**Prístup:** Debug → Analýza → Fix → Test

```
✅ Správne: "Zistíme príčinu. Skontroluj X, potom Y..."
❌ Nesprávne: "Skúsme iný prístup, možno to pomôže"
```

### 5. Token Usage Stats
**PRAVIDLO:** Každá odpoveď končí token statistics  
**Formát:** 
```
Tokeny: Used/Total | Zvyšok: X (Y%) [Status]
```

---

## 🛠️ Vývojové Prostredie

### IDE: PyCharm
- **Nie:** VS Code, iné editory
- **Dôvod:** Preferovaný nástroj
- **Implikácia:** Kompatibilita s PyCharm shortcuts, workflows

### Operačný Systém: Windows
- **Paths:** Forward slash `/` v n8n (C:/Development/)
- **Paths:** Backslash `\` v PowerShell (C:\Development\)
- **Terminal:** PowerShell (nie CMD, nie Bash)

### Jazyk: Slovenčina
- **Komunikácia:** Slovenčina
- **Kód:** Anglické názvy premenných/funkcií
- **Komentáre:** Slovenčina v komentároch OK
- **Dokumentácia:** Slovenčina

---

## 📁 Adresárová Štruktúra

### Produkčná Infraštruktúra
```
C:\Deployment\
├── claude-dev-automation\     ← Automation tool
│   ├── task.yaml              ← Input pre n8n
│   ├── response.md            ← Output z workflow
│   ├── flask_server.py        ← API endpoints
│   └── docs/sessions/         ← Session notes
```

### Vyvíjané Projekty
```
C:\Development\
├── uae-legal-agent\
├── monastier-online\
├── nex-genesis-server\
└── supplier-invoice-loader-v2\
```

### Konvencia:
- **C:\Deployment\** = Infraštruktúra, produkčné nástroje
- **C:\Development\** = Aktívne projekty
- **Nikdy nemiešať** deployment a development projekty

---

## 🔧 n8n Workflow Špecifiká

### Node References
```javascript
// ✅ Správne - explicitný node name
$('Parse YAML Task').item.json.project

// ❌ Nesprávne - môže byť nejednoznačné
$json.project
```

### Paths v n8n
```javascript
// ✅ Správne - forward slash
"C:/Development/project"

// ❌ Nesprávne - backslash (nefunguje!)
"C:\Development\project"
```

### Binary Data Reading
```javascript
// ✅ Správne - čítanie z Read/Write Files node
const buffer = Buffer.from($input.item.binary.data.data, 'base64');
const content = buffer.toString('utf8');

// ❌ Nesprávne - očakávanie textu v json
const content = $input.item.json.data;
```

### Always Output Data
- **Settings → Always Output Data: ON** pre debugging nodes
- Inak prázdne outputs nejdú do ďalších nodes

---

## 📝 Task YAML Format

### Štandardný Template
```yaml
task:
  type: feature|bugfix|refactor|structure|docs
  project: project-name
  description: |
    Multi-line task description
    Clear and specific
  
  context:
    - "Relevant context item 1"
    - "Relevant context item 2"
  
  requirements:
    - Clear requirement 1
    - Clear requirement 2
```

### Best Practices:
- **type:** Konzistentné kategórie
- **project:** Presný názov z C:\Development\
- **description:** Konkrétny, nie vágny
- **context:** Len relevantné info
- **requirements:** Testovateľné podmienky

---

## 🔄 Git Workflow

### Commit Process
- **Tool:** PyCharm Git integration
- **Nepotrebujeme:** Git príkazy v PowerShell
- **Stačí:** Commit message do artifacts

### Commit Message Format
```
type(scope): short description

Longer description if needed
- Detail 1
- Detail 2

Co-authored-by: Claude (Anthropic AI)
```

**Types:** feat, fix, docs, refactor, test, chore

---

## 💰 Cost Tracking

### Token Management
- **Budget:** ~$2.50 USD v kredite
- **Monitor:** Každý task cost v response.md
- **Target:** <$0.01 per task
- **Alert:** Ak task >$0.05, optimalizovať

### Efficiency Metriky
- **Cieľ:** 95%+ token reduction vs manual chat
- **Benchmark:** Manual ~20k-50k tokens, Automated ~500-1000 tokens

---

## 🚨 Anti-patterns

### ❌ ČO NEROBIŤ:

1. **Preskakovanie riešení**
   - Nenáhliť sa na iné riešenie bez nájdenia príčiny
   - Systematický debug vždy

2. **Viacero alternatív**
   - Neposkytovať 3-4 možnosti
   - Dať najlepšie riešenie

3. **Kód mimo artifacts**
   - Nikdy kód v odpovedi
   - Vždy artifacts

4. **Hardcoded hodnoty**
   - Vždy použiť node references
   - Žiadne hardcoded paths v n8n

5. **Ignorovanie conventions**
   - Forward slash v n8n
   - Node references explicitné
   - Binary data handling

---

## 📚 Technológie & Stack

### Backend
- **Python 3.11+**
- **Flask** - API endpoints
- **FastAPI** - v niektorých projektoch

### Automation
- **n8n** - workflow orchestration
- **Claude API** - Sonnet 4.5

### Data Processing
- **ChromaDB** - vector database (UAE Legal Agent)
- **Pervasive/Btrieve** - legacy databases (NEX Genesis)
- **ISDOC XML** - invoice processing

### Infrastructure
- **Windows Server 2012 R2**
- **Cloudflare Tunnels**
- **Remote Desktop Services**

---

## 🎯 Project Context

### Aktívne Projekty

**1. claude-dev-automation** (tento projekt)
- AI-driven development automation
- n8n workflow orchestration
- Token efficiency optimization

**2. uae-legal-agent**
- AI-powered legal analysis
- UAE federal law processing
- Slovak language support
- RAG with ChromaDB

**3. nex-genesis-server**
- Legacy Btrieve database integration
- FastAPI REST API bridge
- ISDOC invoice processing

**4. monastier-online**
- Orthodox Christian web portal
- Slovak/Hungarian content
- Community platform

**5. supplier-invoice-loader-v2**
- Multi-tenant architecture
- Centralized n8n workflows
- Distributed FastAPI servers

---

## 🔄 Session Flow

### Štandardný Priebeh

1. **Inicializácia**
   - Krátky prehľad čo chceme robiť
   - Potvrdenie prístupu

2. **Implementácia**
   - Krok po kroku
   - Artifacts pre všetok kód
   - Debug systematicky

3. **Testing**
   - Overiť funkčnosť
   - Dokumentovať výsledky

4. **Dokumentácia**
   - Session notes
   - Update rules ak potrebné
   - Commit message

---

## 📖 Reference Links

### Dokumentácia
- Claude API: https://docs.anthropic.com
- n8n Docs: https://docs.n8n.io
- Flask: https://flask.palletsprojects.com

### Monitorovanie
- Anthropic Console: https://console.anthropic.com/settings/billing
- n8n Local: http://localhost:5678

---

## ✅ Quick Checklist

Pre začiatok každého chatu:
- [ ] Načítať PROJECT_RULES.md
- [ ] Skontrolovať aktívny projekt
- [ ] Overiť context (Windows, PyCharm, Slovenčina)
- [ ] Pripraviť artifacts pre kód
- [ ] Systematický prístup
- [ ] Token stats na konci

---

**Poznámka:** Tento dokument sa aktualizuje pri zavedení nových konvencií alebo pravidiel. Vždy kontrolovať najnovšiu verziu.