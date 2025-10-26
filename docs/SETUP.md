\# Setup Guide



Kompletný návod na inštaláciu Claude Development Automation System.



---



\## 📋 Požiadavky



\- \*\*Python 3.11+\*\*

\- \*\*Git\*\*

\- \*\*PyCharm\*\* (voliteľné, ale odporúčané)

\- \*\*Claude API key\*\* od Anthropic



---



\## 🚀 Inštalácia



\### \*\*1. Clone repository\*\*



```bash

git clone https://github.com/YOUR-USERNAME/claude-dev-automation.git

cd claude-dev-automation

```



\### \*\*2. Nainštaluj dependencies\*\*



```bash

pip install -r requirements.txt

```



Alebo s virtual environment:



```bash

python -m venv venv

venv\\Scripts\\activate  # Windows

source venv/bin/activate  # Linux/Mac



pip install -r requirements.txt

```



\### \*\*3. Setup workspace\*\*



```bash

python setup\_workspace.py

```



Toto vytvorí:

\- `workspace/` adresár

\- Konfiguračné súbory

\- Project contexts

\- Logs adresár



\### \*\*4. Konfigur API key\*\*



```bash

\# Skopíruj template

copy workspace\\.env.template workspace\\.env



\# Otvor .env a pridaj svoj Claude API key

notepad workspace\\.env

```



V `.env`:

```bash

ANTHROPIC\_API\_KEY=sk-ant-your-key-here

N8N\_WEBHOOK\_URL=http://localhost:5678/webhook/claude-task

```



\### \*\*5. Pridaj svoje projekty\*\*



Uprav `workspace/projects\_index.json`:



```json

{

&nbsp; "version": "1.0.0",

&nbsp; "current\_project": null,

&nbsp; "projects": \[

&nbsp;   {

&nbsp;     "name": "my-project",

&nbsp;     "path": "C:/Development/my-project",

&nbsp;     "description": "My awesome project",

&nbsp;     "language": "python",

&nbsp;     "status": "active"

&nbsp;   },

&nbsp;   {

&nbsp;     "name": "another-project",

&nbsp;     "path": "C:/Development/another-project",

&nbsp;     "description": "Another project",

&nbsp;     "language": "python",

&nbsp;     "status": "active"

&nbsp;   }

&nbsp; ]

}

```



\### \*\*6. Test inštalácie\*\*



```bash

python tools/test\_all\_modules.py

```



Očakávaný výstup:

```

✅ Config Manager: PASSED

✅ Claude API Client: PASSED

✅ Context Builder: PASSED

✅ File Operations: PASSED

✅ Git Operations: PASSED

✅ Project Manager: PASSED

✅ Response Builder: PASSED

```



---



\## 🔧 PyCharm Setup (Voliteľné)



Viď \[PYCHARM\_SETUP.md](PYCHARM\_SETUP.md) pre detailný návod.



\*\*Quick version:\*\*



1\. Otvor `workspace/` v PyCharm

2\. Settings → Tools → External Tools → Add

3\. Nastavenia:

&nbsp;  - Name: `Claude Automation`

&nbsp;  - Program: `python`

&nbsp;  - Arguments: `C:/path/to/tools/claude\_runner.py`

&nbsp;  - Working directory: `$ProjectFileDir$`



---



\## ✅ Verifikácia



\### \*\*Test 1: Manual run\*\*



```bash

\# Napíš task do workspace/task.md

PROJECT: my-project

TASK: Test automation

...



\# Spusti automation

python tools/claude\_runner.py

```



\### \*\*Test 2: PyCharm integration\*\*



1\. Otvor `workspace/task.md`

2\. Pravý klik → External Tools → Claude Automation

3\. Sleduj console output

4\. Skontroluj `workspace/response.md`



---



\## 🐛 Troubleshooting



\### \*\*ModuleNotFoundError: No module named 'anthropic'\*\*



```bash

pip install anthropic python-dotenv requests

```



\### \*\*ANTHROPIC\_API\_KEY not set\*\*



\- Skontroluj že `.env` existuje v `workspace/`

\- Skontroluj že má správny formát

\- Reštartuj terminal/PyCharm



\### \*\*Project not found in projects\_index.json\*\*



\- Skontroluj `workspace/projects\_index.json`

\- Pridaj svoj projekt do zoznamu

\- Skontroluj že cesty sú správne (absolute paths)



\### \*\*File Watcher not triggering (PyCharm)\*\*



\- Settings → Tools → File Watchers → Enabled?

\- Pattern je správny? (`task.md`)

\- Program path je správny?



---



\## 📝 Ďalšie kroky



1\. Prečítaj \[USAGE.md](USAGE.md) - ako používať systém

2\. Prečítaj \[PYCHARM\_SETUP.md](PYCHARM\_SETUP.md) - PyCharm integrácia

3\. Vyskúšaj prvý reálny task!



---



\## 🔐 Bezpečnosť



⚠️ \*\*NIKDY neukladaj `.env` na GitHub!\*\*



`.gitignore` obsahuje:

```

.env

\*.env

workspace/.env

```



Overiť:

```bash

git status

\# .env by nemal byť v zozname

```



---



Máš problémy? \[Otvor Issue na GitHub](https://github.com/YOUR-USERNAME/claude-dev-automation/issues)

