"""
Flask API for Claude Dev Automation Context Building
Provides endpoints for task parsing, context building, and project management
"""

import sys
import re
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path to import tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.enhanced_context_builder import EnhancedContextBuilder

app = Flask(__name__)
CORS(app)

# Paths
BASE_PATH = Path(__file__).parent.parent
WORKSPACE_PATH = BASE_PATH / 'workspace'
PROJECTS_PATH = Path('C:/Development')

# Initialize components
context_builder = EnhancedContextBuilder()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Claude Dev Automation Context API',
        'version': '1.0.0'
    })


@app.route('/parse-task', methods=['POST'])
def parse_task():
    """Parse task description and extract project, task, priority"""
    try:
        data = request.get_json()
        task_description = data.get('task_description')

        if not task_description:
            return jsonify({
                'status': 'error',
                'message': 'task_description is required'
            }), 400

        # Parse format: "P1: project-name - task description"
        # Look for " - " (space-dash-space) as separator
        pattern = r'^(P\d+):\s*(.+?)\s+-\s+(.+)$'
        match = re.match(pattern, task_description.strip())

        if match:
            priority = match.group(1)
            project = match.group(2).strip()
            task = match.group(3).strip()
        else:
            # Fallback parsing
            parts = task_description.split(' - ', 1)
            if len(parts) == 2:
                project_part = parts[0].strip()
                task = parts[1].strip()

                # Extract priority if present
                priority_match = re.match(r'(P\d+):\s*(.+)', project_part)
                if priority_match:
                    priority = priority_match.group(1)
                    project = priority_match.group(2).strip()
                else:
                    priority = 'P2'
                    project = project_part
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid task format. Expected: "P1: project-name - task description"'
                }), 400

        return jsonify({
            'status': 'success',
            'project': project,
            'task': task,
            'priority': priority
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/simple-task', methods=['POST'])
def simple_task():
    """Execute simple task WITHOUT project context - just the task description"""
    try:
        data = request.get_json()
        task_description = data.get('task_description')

        if not task_description:
            return jsonify({
                'status': 'error',
                'message': 'task_description is required'
            }), 400

        # Return ONLY the task, no project context
        return jsonify({
            'status': 'success',
            'context': task_description
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/build-context', methods=['POST'])
def build_context():
    """Build smart context for a project and task"""
    try:
        data = request.get_json()
        project_name = data.get('project_name')
        task_description = data.get('task_description')

        if not project_name or not task_description:
            return jsonify({
                'status': 'error',
                'message': 'project_name and task_description are required'
            }), 400

        # Build context
        context = context_builder.build_context(
            project_name=project_name,
            task_description=task_description
        )

        # Add XML format instructions
        xml_instructions = """

**CRITICAL: File Operations Format**
When you need to create, modify, or delete files, you MUST use this exact XML format:

<file_operations>
  <operation type="create" path="filename.ext">
    <content>
File content here
    </content>
  </operation>
</file_operations>

Operation types: create, modify, delete
Always wrap file content in <content> tags.
"""

        full_context = context + xml_instructions

        return jsonify({
            'status': 'success',
            'context': full_context
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/list-projects', methods=['GET'])
def list_projects():
    """List all available projects"""
    try:
        projects = [d.name for d in PROJECTS_PATH.iterdir() if d.is_dir()]
        return jsonify({
            'status': 'success',
            'projects': projects,
            'count': len(projects)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/project-info/<int:n>', methods=['GET'])
def project_info(n):
    """Get info about project number N"""
    try:
        projects = sorted([d for d in PROJECTS_PATH.iterdir() if d.is_dir()])

        if n < 1 or n > len(projects):
            return jsonify({
                'status': 'error',
                'message': f'Invalid project number. Valid range: 1-{len(projects)}'
            }), 400

        project = projects[n - 1]

        return jsonify({
            'status': 'success',
            'number': n,
            'name': project.name,
            'path': str(project)
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/execute-operations', methods=['POST'])
def execute_operations():
    """Execute file operations (create, modify, delete files)"""
    try:
        data = request.get_json()
        project_name = data.get('project_name')
        operations = data.get('operations', [])

        if not project_name:
            return jsonify({
                'status': 'error',
                'message': 'project_name is required'
            }), 400

        project_path = PROJECTS_PATH / project_name

        if not project_path.exists():
            return jsonify({
                'status': 'error',
                'message': f'Project not found: {project_name}'
            }), 404

        results = []

        for op in operations:
            op_type = op.get('type')
            file_path = op.get('path')
            content = op.get('content', '')

            full_path = project_path / file_path

            try:
                if op_type == 'create' or op_type == 'modify':
                    # Create parent directories if needed
                    full_path.parent.mkdir(parents=True, exist_ok=True)

                    # Write file (overwrite if exists)
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    status = 'modified' if full_path.exists() else 'created'

                    results.append({
                        'success': True,
                        'operation': op_type,
                        'path': file_path,
                        'status': status
                    })

                elif op_type == 'delete':
                    if full_path.exists():
                        full_path.unlink()
                        results.append({
                            'success': True,
                            'operation': 'delete',
                            'path': file_path
                        })
                    else:
                        results.append({
                            'success': False,
                            'operation': 'delete',
                            'path': file_path,
                            'error': 'File not found'
                        })

            except Exception as e:
                results.append({
                    'success': False,
                    'operation': op_type,
                    'path': file_path,
                    'error': str(e)
                })

        return jsonify({
            'status': 'success',
            'file_results': results,
            'total': len(operations),
            'success_count': len([r for r in results if r['success']]),
            'fail_count': len([r for r in results if not r['success']])
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/save-response', methods=['POST'])
def save_response():
    """Save response.md to workspace"""
    try:
        data = request.get_json()
        markdown_content = data.get('markdown')

        if not markdown_content:
            return jsonify({
                'status': 'error',
                'message': 'markdown content is required'
            }), 400

        # Save to workspace/response.md
        response_path = WORKSPACE_PATH / 'response.md'
        with open(response_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return jsonify({
            'status': 'success',
            'message': 'Response saved successfully',
            'path': str(response_path)
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print(f"Starting Flask API on http://localhost:5000")
    print(f"Workspace: {WORKSPACE_PATH}")
    print(f"Projects: {PROJECTS_PATH}")
    app.run(host='127.0.0.1', port=5000, debug=True)