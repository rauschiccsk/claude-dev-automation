#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Runner - Main Orchestration Script
Called by PyCharm File Watcher when task.md changes
This triggers the entire automation pipeline via n8n
"""

import sys
import json
import requests
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import get_config

def parse_task_file(task_file: Path) -> dict:
    """Parse task.md and extract metadata"""
    
    if not task_file.exists():
        raise FileNotFoundError(f"Task file not found: {task_file}")
    
    content = task_file.read_text(encoding='utf-8')
    
    # Extract metadata from first lines
    lines = content.split('\n')
    metadata = {
        'project': None,
        'task': None,
        'priority': 'NORMAL',
        'auto_commit': False,
        'auto_push': False,
        'files': []
    }
    
    for line in lines:
        line = line.strip()
        if line.startswith('PROJECT:'):
            metadata['project'] = line.split(':', 1)[1].strip()
        elif line.startswith('TASK:'):
            metadata['task'] = line.split(':', 1)[1].strip()
        elif line.startswith('PRIORITY:'):
            metadata['priority'] = line.split(':', 1)[1].strip()
        elif line.startswith('AUTO_COMMIT:'):
            metadata['auto_commit'] = line.split(':', 1)[1].strip().lower() in ['yes', 'true', '1']
        elif line.startswith('AUTO_PUSH:'):
            metadata['auto_push'] = line.split(':', 1)[1].strip().lower() in ['yes', 'true', '1']
    
    metadata['full_content'] = content
    metadata['timestamp'] = datetime.now().isoformat()
    
    return metadata

def trigger_n8n_workflow(task_data: dict, webhook_url: str) -> dict:
    """Send task to n8n webhook"""
    
    try:
        print(f"🔄 Triggering n8n workflow...")
        print(f"   Project: {task_data.get('project', 'unknown')}")
        print(f"   Task: {task_data.get('task', 'unknown')[:60]}...")
        
        response = requests.post(
            webhook_url,
            json=task_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ n8n workflow triggered successfully")
            return {
                "success": True,
                "result": result
            }
        else:
            print(f"❌ n8n returned status {response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to n8n at {webhook_url}")
        print(f"   Make sure n8n is running!")
        return {
            "success": False,
            "error": "n8n not reachable - is it running?"
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def write_pending_response(workspace_root: Path, project_name: str):
    """Write initial pending response"""
    
    response_file = workspace_root / "response.md"
    
    pending_content = f"""# Task Response
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project:** {project_name}  
**Status:** ⏳ PROCESSING...

---

## Progress

🔄 Task received and sent to n8n workflow...  
🔄 Claude is analyzing your request...  
🔄 Please wait, this usually takes 5-15 seconds...

---

*This file will be updated automatically when processing is complete.*
"""
    
    response_file.write_text(pending_content, encoding='utf-8')
    print(f"📝 Wrote pending response to: {response_file}")

def main():
    """Main entry point"""
    
    print("=" * 70)
    print("🚀 CLAUDE AUTOMATION RUNNER")
    print("=" * 70)
    print()
    
    try:
        # Load config
        config = get_config()
        workspace_root = Path(config.workspace_root)
        task_file = workspace_root / "task.md"
        
        # Parse task
        print("📖 Reading task.md...")
        task_data = parse_task_file(task_file)
        
        if not task_data['project']:
            print("❌ Error: No PROJECT specified in task.md")
            print("   Please add: PROJECT: your-project-name")
            sys.exit(1)
        
        print(f"✅ Task parsed successfully")
        print(f"   Project: {task_data['project']}")
        print(f"   Priority: {task_data['priority']}")
        print(f"   Auto-commit: {task_data['auto_commit']}")
        print(f"   Auto-push: {task_data['auto_push']}")
        print()
        
        # Write pending response
        write_pending_response(workspace_root, task_data['project'])
        print()
        
        # Execute directly with orchestrator
        print("🔄 Executing task with orchestrator...")
        print()
        
        import subprocess
        import sys
        
        tools_dir = Path(__file__).parent
        orchestrator_path = tools_dir / "orchestrator.py"
        
        # Run orchestrator
        result = subprocess.run(
            [sys.executable, str(orchestrator_path)],
            capture_output=False,
            text=True
        )
        
        print()
        print("=" * 70)
        
        if result.returncode == 0:
            print("✅ TASK COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print()
            print("📝 Check response.md for detailed results")
            print("🎯 Review changes in PyCharm project window")
            sys.exit(0)
        else:
            print("❌ TASK FAILED")
            print("=" * 70)
            print()
            print("📝 Check response.md for error details")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()