\# PyCharm File Watcher Setup



\## 🎯 Cieľ

Nastaviť PyCharm tak, aby automaticky spúšťal `claude\_runner.py` pri každej zmene `task.md`.



---



\## 📝 Krok za krokom



\### 1. Otvor Master Workspace v PyCharm



```

File → Open → C:\\Development\\\_workspace

```



\*\*✅ Toto bude tvoje "veliteľstvo" okno\*\*



---



\### 2. Nastav File Watcher



\#### A) Otvor Settings

```

File → Settings (alebo Ctrl+Alt+S)

```



\#### B) Prejdi na File Watchers

```

Tools → File Watchers

```



\#### C) Klikni na \[+] (Add)

```

Vyber: <custom>

```



\#### D) Vyplň nasledovné:



\*\*Name:\*\* `Claude Task Watcher`



\*\*File type:\*\* `Markdown`



\*\*Scope:\*\* `Project Files`



\*\*Program:\*\* 

```

C:\\Development\\venv\\Scripts\\python.exe

```

\*(alebo cesta k tvojmu Python interpreteru)\*



\*\*Arguments:\*\*

```

C:\\Development\\\_tools\\claude\_runner.py

```



\*\*Output paths to refresh:\*\*

```

$ProjectFileDir$\\response.md

```



\*\*Working directory:\*\*

```

$ProjectFileDir$

```



\*\*Advanced Options (dole):\*\*

\- ✅ Check: `Auto-save edited files to trigger the watcher`

\- ✅ Check: `Trigger the watcher on external changes`

\- ❌ Uncheck: `Trigger the watcher regardless of syntax errors`

\- ❌ Uncheck: `Create output file from stdout`



\#### E) File Pattern

```

Show only files matching:  task.md

```



\#### F) Klikni \*\*OK\*\* a \*\*Apply\*\*



---



\### 3. Vytvor Split View pre task.md a response.md



\#### A) Otvor task.md

```

Dvojklik na \_workspace\\task.md

```



\#### B) Vytvor split

```

Pravý klik na tab task.md → Split Right

```



\#### C) Otvor response.md v pravej časti

```

V pravej časti otvor: response.md

```



\*\*Teraz máš:\*\*

```

┌─────────────────┬──────────────────┐

│  task.md        │  response.md     │

│                 │                  │

│  \[píšeš sem]    │  \[vidíš tu]      │

└─────────────────┴──────────────────┘

```



---



\### 4. Test File Watcher



\#### A) Napíš do task.md:



```markdown

PROJECT: uae-legal-agent

TASK: Test automation system

PRIORITY: LOW

AUTO\_COMMIT: no

AUTO\_PUSH: no



\## Context

This is a simple test to verify File Watcher works.



\## Requirements

\- Respond with "Automation system is working!"



\## Files



\## Notes

```



\#### B) Uložiš (Ctrl+S)



\#### C) Sleduj dolný panel v PyCharm

```

V dolnom paneli by si mal vidieť:

Tool Window → File Watchers

```



Tam uvidíš output z `claude\_runner.py`:

```

🚀 CLAUDE AUTOMATION RUNNER

📖 Reading task.md...

✅ Task parsed successfully

🔄 Triggering n8n workflow...

```



\#### D) Sleduj response.md

```

Po pár sekundách sa response.md automaticky aktualizuje!

```



---



\## ⚠️ Dôležité poznámky



\### Python Interpreter

Uisti sa, že používaš správny Python:

```

Settings → Project → Python Interpreter

→ Vyber: C:\\Development\\venv\\Scripts\\python.exe

```



\### n8n musí bežať

File Watcher zavolá n8n webhook, takže n8n musí byť spustený.



\### Auto-refresh response.md

PyCharm automaticky detekuje zmeny v `response.md` a refresh-ne ho.



---



\## 🎮 Ako to používať



\### 1. Otvor PyCharm s workspace

```

C:\\Development\\\_workspace

```



\### 2. Vidíš split view

```

task.md | response.md

```



\### 3. Napíš task do task.md

```markdown

PROJECT: supplier\_invoice\_loader

TASK: Add error logging to email poller

...

```



\### 4. Uložiš (Ctrl+S)



\### 5. File Watcher automaticky:

\- Spustí claude\_runner.py

\- Pošle task do n8n

\- n8n spracuje task (Claude API + file ops + git)

\- Aktualizuje response.md



\### 6. Vidíš výsledok v response.md

```

✅ COMPLETED

📝 Modified files: ...

📦 Git commit: abc123f

```



\### 7. Prejdeš do druhého PyCharm okna

```

Otvoríš: C:\\Development\\supplier\_invoice\_loader

Vidíš zmenené súbory

Review git diff

Test, push

```



---



\## 🐛 Troubleshooting



\### File Watcher sa nespúšťa

1\. Check: Settings → Tools → File Watchers → Je enabled?

2\. Check: Uložil si task.md? (Ctrl+S)

3\. Check: Je pattern správny? (`task.md`)



\### Python error

1\. Check: Máš správnu cestu k python.exe?

2\. Check: Je venv aktivovaný?

3\. Check: Sú nainštalované dependencies? (`pip install anthropic requests python-dotenv`)



\### n8n connection error

1\. Check: Je n8n spustený? (localhost:5678)

2\. Check: Je webhook URL správna v config.json?

3\. Check: Network connectivity?



\### response.md sa neaktualizuje

1\. Check: File Watcher dokončil? (pozri Tool Window)

2\. Check: n8n workflow dokončil?

3\. Try: Pravý klik na response.md → Reload from Disk



---



\## ✅ Verification Checklist



\- \[ ] PyCharm otvorený s \_workspace

\- \[ ] File Watcher nakonfigurovaný a enabled

\- \[ ] Split view: task.md | response.md

\- \[ ] Python interpreter správne nastavený

\- \[ ] n8n bežiaci a webhook dostupný

\- \[ ] Test task odoslaný a response dostený



---



\*\*Keď máš toto hotové, môžeš začať používať automatizáciu! 🚀\*\*

