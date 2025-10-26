#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Orchestrator
Executes the complete automation pipeline:
1. Parse task → 2. Build context → 3. Call Claude → 4. Apply changes → 5. Git ops → 6. Write response
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import io

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import get_config
from context_builder import ContextBuilder
from claude_api import ClaudeAPIClient
from file_operations import FileOperations
from git_operations import GitOperations
from project_manager import ProjectManager
from response_builder import ResponseBuilder

class Orchestrator:
    """Main orchestration class"""
    
    def __init__(self):
        """Initialize orchestrator"""
        self.config = get_config()
        self.workspace_root = Path(self.config.workspace_root)
        self.context_builder = ContextBuilder()
        self.claude_client = ClaudeAPIClient()
        self.project_manager = ProjectManager()
        self.response_builder = ResponseBuilder()
        
    def parse_task(self, task_file: Path) -> dict:
        """Parse task.md file"""
        
        content = task_file.read_text(encoding='utf-8')
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
        return metadata
    
    def execute_task(self, task_data: dict) -> dict:
        """Execute complete task pipeline"""
        
        project_name = task_data['project']
        
        try:
            # Step 1: Get project info and switch
            print(f"\n1️⃣  Switching to project: {project_name}")
            project_result = self.project_manager.switch_project(project_name)
            
            if not project_result['success']:
                raise ValueError(project_result['error'])
            
            project = project_result['project']
            print(f"   ✅ Project: {project['name']}")
            print(f"   📂 Path: {project['path']}")
            
            # Step 2: Build minimal context
            print(f"\n2️⃣  Building minimal context...")
            context = self.context_builder.build_context(
                project_name=project_name,
                task_content=task_data['full_content']
            )
            
            estimated_tokens = context['metadata']['estimated_tokens']
            print(f"   ✅ Context built: ~{estimated_tokens} tokens")
            print(f"   💰 Savings: ~{40000 - estimated_tokens:,} tokens vs chat")
            
            # Step 3: Call Claude API
            print(f"\n3️⃣  Calling Claude API...")
            result = self.claude_client.analyze(
                prompt=context['user_prompt'],
                system_prompt=context['system_prompt'],
                metadata={
                    'project': project_name,
                    'task': task_data['task']
                }
            )
            
            if not result['success']:
                raise Exception(result['error'])
            
            print(f"   ✅ Claude responded")
            print(f"   📊 Tokens used: {result['tokens']['total']:,}")
            print(f"   ⏱️  Duration: {result['duration_seconds']:.1f}s")
            
            # Step 4: Apply file changes
            print(f"\n4️⃣  Applying file changes...")
            file_ops = FileOperations(project['path'])
            
            # Extract and apply code blocks from Claude's response
            file_results = file_ops.apply_code_blocks(result['response'])
            
            if file_results:
                print(f"   ✅ Files changed: {len(file_results)}")
                for file_result in file_results:
                    if file_result['success']:
                        print(f"      ✅ {file_result['file']} - {file_result['action']}")
                    else:
                        print(f"      ❌ {file_result['file']} - {file_result.get('error', 'Failed')}")
            else:
                print(f"   ℹ️  No file changes detected")
            
            # Step 5: Git operations (if enabled)
            git_result = None
            if task_data['auto_commit'] and file_results:
                print(f"\n5️⃣  Git operations...")
                
                try:
                    git_ops = GitOperations(project['path'])
                    
                    # Create commit message
                    commit_msg = f"Auto: {task_data['task'][:50]}"
                    
                    # Commit and optionally push
                    git_result = git_ops.commit_and_push(
                        message=commit_msg,
                        push_enabled=task_data['auto_push']
                    )
                    
                    if git_result['commit']['success']:
                        commit_hash = git_result['commit']['commit_hash']
                        print(f"   ✅ Committed: {commit_hash}")
                        
                        if git_result['push']:
                            if git_result['push']['success']:
                                print(f"   ✅ Pushed to remote")
                            else:
                                print(f"   ❌ Push failed: {git_result['push']['error']}")
                    else:
                        print(f"   ❌ Commit failed: {git_result['commit']['error']}")
                        
                except ValueError as e:
                    print(f"   ⚠️  Git not available: {e}")
                    git_result = None
            else:
                print(f"\n5️⃣  Git operations: Skipped (AUTO_COMMIT: {task_data['auto_commit']})")
            
            # Step 6: Update project context
            print(f"\n6️⃣  Updating project context...")
            if file_results:
                change_desc = f"{len(file_results)} files modified"
                self.project_manager.add_recent_change(project_name, change_desc)
                print(f"   ✅ Context updated")
            
            # Step 7: Update session history
            self.context_builder.update_session_history(
                role="assistant",
                content=result['response'][:500],  # First 500 chars
                tokens_used=result['tokens']['total']
            )
            
            # Step 8: Build and write response
            print(f"\n7️⃣  Building response...")
            
            response_md = self.response_builder.build_response(
                project_name=project_name,
                task_summary=task_data['task'],
                status="✅ COMPLETED",
                tokens_used=result['tokens'],
                file_changes=file_results,
                git_result=git_result,
                notes=None,
                next_steps=[
                    "Review changes in PyCharm",
                    "Check git diff",
                    "Test the changes",
                    "Push to repository (if not auto-pushed)"
                ] if not task_data['auto_push'] else None
            )
            
            response_file = self.workspace_root / "response.md"
            response_file.write_text(response_md, encoding='utf-8')
            print(f"   ✅ Response written to: {response_file}")
            
            # Return summary
            return {
                'success': True,
                'project': project_name,
                'tokens_used': result['tokens']['total'],
                'files_changed': len(file_results) if file_results else 0,
                'git_committed': git_result['commit']['success'] if git_result and git_result.get('commit') else False,
                'git_pushed': git_result['push']['success'] if git_result and git_result.get('push') and git_result['push'] else False
            }
            
        except Exception as e:
            # Build error response
            print(f"\n❌ Error during execution: {e}")
            
            error_response = self.response_builder.build_error_response(
                project_name=project_name,
                error_message=str(e),
                error_details=None
            )
            
            response_file = self.workspace_root / "response.md"
            response_file.write_text(error_response, encoding='utf-8')
            
            return {
                'success': False,
                'error': str(e)
            }

def main():
    """Main entry point for orchestrator"""
    
    print("=" * 70)
    print("🎯 CLAUDE AUTOMATION ORCHESTRATOR")
    print("=" * 70)
    
    try:
        # Initialize
        orchestrator = Orchestrator()
        
        # Parse task
        task_file = orchestrator.workspace_root / "task.md"
        print(f"\n📖 Parsing task from: {task_file}")
        
        task_data = orchestrator.parse_task(task_file)
        
        if not task_data['project']:
            print("❌ Error: No PROJECT specified in task.md")
            sys.exit(1)
        
        print(f"✅ Task parsed:")
        print(f"   Project: {task_data['project']}")
        print(f"   Task: {task_data['task']}")
        print(f"   Priority: {task_data['priority']}")
        print(f"   Auto-commit: {task_data['auto_commit']}")
        print(f"   Auto-push: {task_data['auto_push']}")
        
        # Execute
        print(f"\n{'='*70}")
        print("🚀 EXECUTING PIPELINE")
        print("=" * 70)
        
        result = orchestrator.execute_task(task_data)
        
        # Summary
        print(f"\n{'='*70}")
        if result['success']:
            print("✅ TASK COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"\n📊 Summary:")
            print(f"   Project: {result['project']}")
            print(f"   Tokens used: {result['tokens_used']:,}")
            print(f"   Files changed: {result['files_changed']}")
            print(f"   Git committed: {'✅' if result['git_committed'] else '❌'}")
            print(f"   Git pushed: {'✅' if result['git_pushed'] else '❌'}")
            print(f"\n📝 Check response.md for details")
            sys.exit(0)
        else:
            print("❌ TASK FAILED")
            print("=" * 70)
            print(f"\nError: {result['error']}")
            print(f"\n📝 Check response.md for details")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()