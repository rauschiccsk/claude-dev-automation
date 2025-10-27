# 🧪 Test Tasks - Claude Dev Automation

Tri testovacie scenáre pre overenie opráv a funkcionality systému.

---

## Test 1: Response Display Fix ✅

**Účel:** Overiť, že sa Claude's response správne zobrazuje v `response.md` aj keď nedôjde k zmenám súborov.

**Skopíruj do `workspace/task.md`:**

```markdown
PROJECT: claude-dev-automation
TASK: Zhodnoť súčasný stav projektu a identifikuj 3 najväčšie silné stránky systému
PRIORITY: NORMAL
AUTO_COMMIT: no
AUTO_PUSH: no

## Kontext
Potrebujem analýzu projektu bez úpravy súborov. Chcem vedieť čo systém robí dobre.

Systém by mal automaticky načítať:
- Session notes z docs/sessions/
- Git status
- Project status súbory

## Očakávaný výstup
Zhodnotenie silných stránok projektu - ŽIADNE zmeny súborov, len analýza.

## Poznámky
Tento test overí či sa Claude's response zobrazuje v response.md aj keď nedôjde k file operations.
```

**Očakávaný výsledek:**
- ✅ Claude odpovedá po slovensky
- ✅ V `response.md` sa zobrazí sekcia "💬 Claude's Analysis"
- ✅ Odpoveď obsahuje konkrétnu analýzu (nie len template)
- ✅ Smart context načítal session notes
- ✅ Žiadne file changes

---

## Test 2: Slovak Language Enforcement 🇸🇰

**Účel:** Overiť, že Claude konzistentne odpovedá v slovenčine.

**Skopíruj do `workspace/task.md`:**

```markdown
PROJECT: claude-dev-automation
TASK: Vytvor zoznam možných vylepšení pre enhanced_context_builder.py
PRIORITY: NORMAL
AUTO_COMMIT: no
AUTO_PUSH: no

## Kontext
Analyzuj súbor enhanced_context_builder.py a navrhni vylepšenia.

Zameraj sa na:
1. Pridanie nových automatických kontextov
2. Optimalizáciu token usage
3. Lepšie error handling

## Očakávaný výstup
Zoznam konkrétnych vylepšení s vysvetlením prečo by pomohli.

## Poznámky
Celá odpoveď MUSÍ byť v slovenčine, vrátane názvov sekcií a technických vysvetlení.
```

**Očakávaný výsledok:**
- ✅ Kompletná odpoveď v slovenčine
- ✅ Technické termíny preložené alebo vysvetlené
- ✅ Naturálny slovenský jazyk (nie strojový preklad)
- ✅ Sekcie a headers v slovenčine
- ✅ Žiadne file changes (len analýza)

---

## Test 3: Smart Context s NEX Genesis Server 🚀

**Účel:** Komplexný test smart context systému na reálnom projekte.

**Skopíruj do `workspace/task.md`:**

```markdown
PROJECT: nex-genesis-server
TASK: Vykonaj kompletnú analýzu projektu a identifikuj najpálčivejšie úlohy
PRIORITY: HIGH
AUTO_COMMIT: no
AUTO_PUSH: no

## Kontext
Potrebujem detailnú analýzu projektu NEX Genesis Server využívajúc všetky smart context features:
- Automatické načítanie session notes
- Git status a uncommitted changes
- Všetky TODO komentáre v kóde
- Project status súbory (README, STATUS, atď.)

## Očakávaný výstup
1. **Aktuálny stav projektu** - čo je hotové, čo prebieha
2. **Zoznam TODO úloh** - všetky nájdené TODO komentáre s priority
3. **Git analýza** - aké sú uncommitted changes
4. **Odporúčania** - čo riešiť ako prvé a prečo
5. **Potenciálne problémy** - čo by mohlo spôsobiť issues

## Poznámky
Tento test overí:
- Automatické načítanie kontextu z viacerých zdrojov
- Slovak language response
- Komplexnú analýzu bez file changes
- Token efficiency smart context systému

Odpoveď musí byť v SLOVENČINE.
```

**Očakávaný výsledok:**
- ✅ Smart context načítal session notes z projektu
- ✅ Git status zobrazený (branch, changes)
- ✅ TODO komentáre extrahované (až 10 ks)
- ✅ Project status súbory načítané
- ✅ Komplexná analýza po slovensky
- ✅ Token usage ~2000-5000 (nie 40,000+)
- ✅ Response.md obsahuje Claude's Analysis sekciu

---

## 📊 Ako testovať

### Príprava (jednorazovo):

1. **Skontroluj že máš oprávené súbory:**
   ```bash
   cd C:\Development\claude-dev-automation\tools
   # Nahraď orchestrator.py a response_builder.py opravenými verziami
   ```

2. **Otvor PyCharm:**
   ```
   Súbor: workspace/task.md (na úpravu)
   Súbor: workspace/response.md (na výsledky)
   Split view - vedľa seba
   ```

### Postup pre každý test:

1. **Skopíruj test task** do `workspace/task.md`
2. **Right-click na task.md** → External Tools → Claude Automation
3. **Počkaj** na dokončenie (sleduj console output)
4. **Skontroluj `response.md`:**
   - Je tam sekcia "💬 Claude's Analysis"?
   - Je odpoveď v slovenčine?
   - Obsahuje konkrétnu analýzu?
   - Smart context načítal čo mal?

### Kontrolné otázky pre každý test:

**Test 1 - Response Display:**
- [ ] Vidím Claude's Analysis sekciu?
- [ ] Odpoveď obsahuje konkrétny obsah (nie template)?
- [ ] Token usage je zobrazené?
- [ ] Odpoveď je po slovensky?

**Test 2 - Slovak Language:**
- [ ] Celá odpoveď je v slovenčine?
- [ ] Headers a sekcie po slovensky?
- [ ] Technické termíny správne preložené?
- [ ] Text je prirodzený (nie strojový)?

**Test 3 - Smart Context:**
- [ ] Session notes boli načítané?
- [ ] Git status zobrazený?
- [ ] TODO komentáre extrahované?
- [ ] Token usage rozumný (~2-5k)?
- [ ] Komplexná analýza v slovenčine?

---

## 🐛 Troubleshooting

### Problém: Response.md je prázdny alebo len template

**Riešenie:**
1. Skontroluj console output - sú tam errory?
2. Overiť že orchestrator.py obsahuje fix (riadok ~150)
3. Overiť že response_builder.py má `claude_response` parameter

### Problém: Claude odpovedá po anglicky

**Riešenie:**
1. Skontroluj enhanced_context_builder.py - má "CRITICAL: ALWAYS respond in Slovak"?
2. Pridaj do task.md explicitne: "Odpoveď MUSÍ byť v SLOVENČINE"
3. Reštartuj Claude session

### Problém: Smart context nenačíta session notes

**Riešenie:**
1. Overiť že projekt má `docs/sessions/` folder
2. Skontroluj že existuje aspoň 1 session note súbor
3. Overiť cesty v config.json

### Problém: Token usage je vysoký (>10,000)

**Riešenie:**
1. Smart context pravdepodobne nenačítava správne
2. Check enhanced_context_builder.py limity (3000 chars session notes)
3. Skontroluj že sa nepoužíva starý context builder

---

## 📝 Výsledky testov

Po dokončení všetkých testov vyplň:

| Test | Status | Token Usage | Slovak? | Notes |
|------|--------|-------------|---------|-------|
| Test 1: Response Display | ⬜ Pass / ⬜ Fail | _______ | ⬜ Áno | ____________ |
| Test 2: Slovak Language | ⬜ Pass / ⬜ Fail | _______ | ⬜ Áno | ____________ |
| Test 3: Smart Context | ⬜ Pass / ⬜ Fail | _______ | ⬜ Áno | ____________ |

### Poznámky k testom:
```
(Sem napíš zistené problémy alebo úspechy)
```

---

## ✅ Success Criteria

Systém je plne funkčný keď:
- ✅ Všetky 3 testy prešli
- ✅ Response.md vždy zobrazuje Claude's analysis
- ✅ Claude konzistentne odpovedá v slovenčine
- ✅ Smart context načítava všetky zdroje
- ✅ Token usage je optimalizovaný (~2-5k pre analýzu)
- ✅ Žiadne crashe alebo errory v console

**Po úspešnom otestovaní môžeš pokračovať s reálnymi projektami! 🚀**