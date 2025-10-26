\# Claude Development Automation System



\*\*AI-Driven Multi-Project Development with 98% Token Savings\*\*



Automatizovaný vývojový systém využívajúci Claude API pre správu viacerých projektov s minimálnou spotrebou tokenov a maximálnou efektivitou.



\[!\[Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

\[!\[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



---



\## 🎯 Prečo tento systém?



\### \*\*Problém:\*\*

\- Chat rozhrania míňajú \*\*40,000 tokenov\*\* na inicializáciu každého nového chatu

\- \*\*200k token limit\*\* núti prepínať chaty a strácať kontext

\- Manuálne copy-paste kódu a Git operácie zabera čas

\- Prepínanie medzi projektami je neefektívne



\### \*\*Riešenie:\*\*

\- \*\*Minimal context:\*\* len ~500 tokenov namiesto 40k (\*\*98% úspora!\*\*)

\- \*\*Automatické file operations:\*\* súbory sa vytvárajú priamo v projekte

\- \*\*Multi-project support:\*\* prepínanie jedným riadkom

\- \*\*Git integrácia:\*\* voliteľné auto-commit a auto-push

\- \*\*PyCharm integrácia:\*\* spusti automation jedným klikom



---



\## 📊 Štatistiky



| Metrika | Chat rozhranie | Tento systém | Úspora |

|---------|---------------|--------------|--------|

| \*\*Tokeny per task\*\* | 45,000 | 500-3,000 | \*\*93-98%\*\* |

| \*\*Cena per task\*\* | $0.18 | $0.004-0.015 | \*\*92-98%\*\* |

| \*\*Čas per task\*\* | 10-15 min | 5-30 sec | \*\*95%\*\* |

| \*\*Manual work\*\* | Vysoký | Žiadny | \*\*100%\*\* |



---



\## ✨ Hlavné features



\### \*\*🤖 AI Orchestration\*\*

\- Automatické volanie Claude API s minimal context

\- Inteligentné parsovanie task.md → orchestrácia → response.md

\- Token tracking a cost estimation



\### \*\*📂 Multi-Project Management\*\*

\- Centralizované riadenie všetkých projektov

\- Prepínanie projektov jedným príkazom

\- Per-project kontext a história



\### \*\*⚡ Automation Pipeline\*\*

1\. Parse task.md

2\. Build minimal context (~500 tokens)

3\. Call Claude API

4\. Extract \& apply code blocks

5\. Git operations (optional)

6\. Update response.md



\### \*\*🔧 PyCharm Integration\*\*

\- External Tool setup

\- Split view: task.md | response.md

\- Spustenie automation jedným pravým klikom



\### \*\*💾 Intelligent Context\*\*

\- Iba posledných 5 správ z histórie

\- Project-specific minimal context

\- Automatic context update po každom tasku



---



\## 🚀 Quick Start



\### \*\*1. Inštalácia\*\*



```bash

git clone https://github.com/your-username/claude-dev-automation.git

cd claude-dev-automation



\# Nainštaluj dependencies

pip install -r requirements.txt



\# Setup workspace

python setup\_workspace.py

```



\### \*\*2. Konfigurácia\*\*



```bash

\# Skopíruj .env template

cp workspace/.env.template workspace/.env



\# Pridaj Claude API key

\# ANTHROPIC\_API\_KEY=sk-ant-your-key-here

```



\### \*\*3. Pridaj svoje projekty\*\*



Uprav `workspace/projects\_index.json`:



```json

{

&nbsp; "projects": \[

&nbsp;   {

&nbsp;     "name": "my-project",

&nbsp;     "path": "C:/Development/my-project",

&nbsp;     "description": "My awesome project",

&nbsp;     "language": "python",

&nbsp;     "status": "active"

&nbsp;   }

&nbsp; ]

}

```



\### \*\*4. Prvý task\*\*



Napíš do `workspace/task.md`:



```markdown

PROJECT: my-project

TASK: Create hello world function

PRIORITY: NORMAL

AUTO\_COMMIT: no

AUTO\_PUSH: no



\## Requirements

\- Create function hello() that returns "Hello World!"

\- File: src/utils.py

```



\### \*\*5. Spusti automation\*\*



```bash

python tools/claude\_runner.py

```



Alebo z PyCharm: \*\*Pravý klik → External Tools → Claude Automation\*\*



---



\## 📖 Dokumentácia



\- \[\*\*SETUP.md\*\*](docs/SETUP.md) - Detailná inštalácia

\- \[\*\*PYCHARM\_SETUP.md\*\*](docs/PYCHARM\_SETUP.md) - PyCharm integrácia

\- \[\*\*USAGE.md\*\*](docs/USAGE.md) - Ako používať systém

\- \[\*\*ARCHITECTURE.md\*\*](docs/ARCHITECTURE.md) - Technická architektúra



---



\## 🏗️ Architektúra



```

┌─────────────────────────────────────────┐

│           PyCharm / Terminal            │

│              (task.md)                  │

└────────────────┬────────────────────────┘

&nbsp;                │

&nbsp;                ▼

┌─────────────────────────────────────────┐

│          claude\_runner.py               │

│       (Parse \& Trigger)                 │

└────────────────┬────────────────────────┘

&nbsp;                │

&nbsp;                ▼

┌─────────────────────────────────────────┐

│          orchestrator.py                │

│         (Main Pipeline)                 │

├─────────────────────────────────────────┤

│  1. Context Builder (~500 tokens)       │

│  2. Claude API Client                   │

│  3. File Operations                     │

│  4. Git Operations                      │

│  5. Response Builder                    │

└────────────────┬────────────────────────┘

&nbsp;                │

&nbsp;                ▼

┌─────────────────────────────────────────┐

│         Your Project Files              │

│           + response.md                 │

└─────────────────────────────────────────┘

```



---



\## 🔧 Komponenty



\### \*\*Core Modules\*\*



| Modul | Popis |

|-------|-------|

| `config\_manager.py` | Centrálna konfigurácia |

| `claude\_api.py` | Claude API wrapper + token tracking |

| `context\_builder.py` | Minimal context builder (98% úspora!) |

| `file\_operations.py` | Automatické vytváranie/update súborov |

| `git\_operations.py` | Git commit/push automation |

| `project\_manager.py` | Multi-project management |

| `response\_builder.py` | Formatted response builder |

| `orchestrator.py` | Main pipeline orchestration |

| `claude\_runner.py` | Entry point / trigger |



---



\## 💡 Príklady použitia



\### \*\*Jednoduchý feature\*\*



```markdown

PROJECT: my-app

TASK: Add email validation

PRIORITY: HIGH

AUTO\_COMMIT: yes

AUTO\_PUSH: no



\## Requirements

\- Add email validation to user registration

\- Use regex pattern

\- Add tests



\## Files

src/validators.py

tests/test\_validators.py

```



\*\*Výsledok:\*\* 

\- ✅ Súbory vytvorené

\- ✅ Git commit automatický

\- ⏱️ Čas: 8 sekúnd

\- 🪙 Tokeny: ~1,200



\### \*\*Bug fix\*\*



```markdown

PROJECT: my-app

TASK: Fix memory leak in data processor

PRIORITY: CRITICAL

AUTO\_COMMIT: yes

AUTO\_PUSH: yes



\## Context

Users report increasing memory usage over time.



\## Files

src/processors/data\_processor.py

```



\*\*Výsledok:\*\*

\- ✅ Bug opravený

\- ✅ Auto-commit + auto-push

\- ⏱️ Čas: 12 sekúnd

\- 🪙 Tokeny: ~2,500



---



\## 🔒 Bezpečnosť



⚠️ \*\*NIKDY neukladaj `.env` súbor na GitHub!\*\*



`.gitignore` obsahuje všetky citlivé súbory:

\- `.env` - API keys

\- `logs/\*.jsonl` - API usage logs

\- `session\_context.json` - session data



---



\## 🤝 Prispievanie



Contributions sú vítané! 



1\. Fork repo

2\. Vytvor feature branch

3\. Commit zmeny

4\. Push do branch

5\. Otvor Pull Request



---



\## 📄 Licencia



MIT License - viď \[LICENSE](LICENSE)



---



\## 👨‍💻 Autor



\*\*Zoltán Rauscher\*\*  

ICC Komárno - Innovation \& Consulting Center  

Senior Developer | 40 rokov programovacích skúseností



---



\## 🙏 Acknowledgments



\- \[Anthropic Claude](https://www.anthropic.com/) - AI model

\- \[n8n](https://n8n.io/) - Workflow automation inspiration

\- PyCharm - Best Python IDE



---



\## 📞 Kontakt \& Podpora



\- Issues: \[GitHub Issues](https://github.com/your-username/claude-dev-automation/issues)

\- Email: your-email@example.com



---



\*\*⭐ Ak ti tento projekt pomohol, daj mu hviezdu na GitHub!\*\*

