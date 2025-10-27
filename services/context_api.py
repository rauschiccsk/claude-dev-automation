"""
Flask Context API
Provides endpoints for Claude Dev Automation system
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Base paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_PATH = os.path.join(PROJECT_ROOT, 'workspace')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'service': 'context-api',
        'status': 'ok',
        'version': '1.0.0'
    }), 200


@app.route('/parse-task', methods=['POST'])
def parse_task():
    """Parse task description and extract metadata

    Request body:
    {
        "task_description": "Create a simple hello world function",
        "project_name": "claude-dev-automation" (optional)
    }

    Returns:
        JSON with parsed task metadata INCLUDING project and task fields
    """
    try:
        data = request.json
        task_description = data.get('task_description', '')
        project_name = data.get('project_name', 'claude-dev-automation')

        if not task_description:
            return jsonify({
                'status': 'error',
                'message': 'task_description is required'
            }), 400

        # Return fields that workflow expects
        result = {
            'project': project_name,  # BUILD SMART CONTEXT očakáva toto!
            'task': task_description,  # BUILD SMART CONTEXT očakáva toto!
            'task_id': f'task_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'task_description': task_description,
            'complexity': 'medium',
            'estimated_tokens': 5000,
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/build-context', methods=['POST'])
def build_context():
    """Build smart context for Claude API

    Request body:
    {
        "project_name": "uae-legal-agent",
        "task_description": "Vytvor API endpoint..."
    }

    Returns:
        JSON with context string and metadata
    """
    try:
        data = request.json
        project_name = data.get('project_name', '')
        task_description = data.get('task_description', '')

        if not project_name or not task_description:
            return jsonify({
                'status': 'error',
                'message': 'project_name and task_description are required'
            }), 400

        # Build context (simplified version)
        context = f"""# Project: {project_name}

## Task
{task_description}

## Instructions
- Použi XML format <file_operations>
- Vytvor súbor hello.txt v root adresári projektu
- Zodpovedaj v slovenčine

## Poznámky
- Použi XML format <file_operations>
   <operation type="create" path="hello.txt">
      <content>Hello from n8n automation!</content>
   </operation>
</file_operations>
"""

        result = {
            'project_name': project_name,
            'status': 'success',
            'context': context,
            'context_size': len(context)
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/execute-operations', methods=['POST'])
def execute_operations():
    """Execute file operations (create, modify, delete)

    Request body:
    {
        "project_name": "uae-legal-agent",
        "operations": [
            {
                "type": "create",
                "path": "src/test.py",
                "content": "print('hello')"
            }
        ]
    }

    Returns:
        JSON with results for each operation
    """
    try:
        data = request.json
        project_name = data.get('project_name')
        operations = data.get('operations', [])

        if not project_name:
            return jsonify({
                'status': 'error',
                'message': 'project_name is required'
            }), 400

        if not operations:
            return jsonify({
                'status': 'error',
                'message': 'operations list is required'
            }), 400

        # Project base path
        project_path = os.path.join('C:/Development', project_name)

        if not os.path.exists(project_path):
            return jsonify({
                'status': 'error',
                'message': f'Project directory not found: {project_path}'
            }), 404

        results = []

        for op in operations:
            op_type = op.get('type')
            rel_path = op.get('path')
            content = op.get('content', '')

            if not op_type or not rel_path:
                results.append({
                    'operation': op_type,
                    'path': rel_path,
                    'success': False,
                    'error': 'Missing type or path'
                })
                continue

            # Security: prevent path traversal
            if '..' in rel_path or rel_path.startswith('/') or rel_path.startswith('\\'):
                results.append({
                    'operation': op_type,
                    'path': rel_path,
                    'success': False,
                    'error': 'Invalid path (path traversal not allowed)'
                })
                continue

            full_path = os.path.join(project_path, rel_path)
            dir_path = os.path.dirname(full_path)

            try:
                # Ensure directory exists
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)

                if op_type == 'create':
                    if os.path.exists(full_path):
                        results.append({
                            'operation': op_type,
                            'path': rel_path,
                            'success': False,
                            'error': 'File already exists'
                        })
                    else:
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        results.append({
                            'operation': op_type,
                            'path': rel_path,
                            'success': True
                        })

                elif op_type == 'modify':
                    if not os.path.exists(full_path):
                        results.append({
                            'operation': op_type,
                            'path': rel_path,
                            'success': False,
                            'error': 'File does not exist'
                        })
                    else:
                        # Create backup
                        backup_path = full_path + '.backup'
                        shutil.copy2(full_path, backup_path)

                        # Write new content
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)

                        results.append({
                            'operation': op_type,
                            'path': rel_path,
                            'success': True,
                            'backup': os.path.basename(backup_path)
                        })

                elif op_type == 'delete':
                    if not os.path.exists(full_path):
                        results.append({
                            'operation': op_type,
                            'path': rel_path,
                            'success': False,
                            'error': 'File does not exist'
                        })
                    else:
                        # Create backup
                        backup_path = full_path + '.deleted'
                        shutil.copy2(full_path, backup_path)

                        # Delete file
                        os.remove(full_path)

                        results.append({
                            'operation': op_type,
                            'path': rel_path,
                            'success': True,
                            'backup': os.path.basename(backup_path)
                        })

                else:
                    results.append({
                        'operation': op_type,
                        'path': rel_path,
                        'success': False,
                        'error': f'Unknown operation type: {op_type}'
                    })

            except Exception as e:
                results.append({
                    'operation': op_type,
                    'path': rel_path,
                    'success': False,
                    'error': str(e)
                })

        # Calculate stats
        success_count = sum(1 for r in results if r.get('success'))
        fail_count = len(results) - success_count

        return jsonify({
            'status': 'success',
            'results': results,
            'success_count': success_count,
            'fail_count': fail_count,
            'total_operations': len(results)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # Ensure workspace directory exists
    os.makedirs(WORKSPACE_PATH, exist_ok=True)

    print("🚀 Starting Flask Context API...")
    print(f"📁 Workspace: {WORKSPACE_PATH}")
    print(f"🌐 Running on http://127.0.0.1:5000")

    app.run(host='0.0.0.0', port=5000, debug=True)