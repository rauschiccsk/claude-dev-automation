"""
Context API Service
Flask API that provides smart context building for n8n workflow.
Reuses existing Python modules from claude-dev-automation.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import sys
import logging
import re

# Add tools directory to path
tools_dir = Path(__file__).parent.parent / 'tools'
sys.path.insert(0, str(tools_dir))

from enhanced_context_builder import EnhancedContextBuilder

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from n8n

# Initialize context builder
builder = EnhancedContextBuilder(projects_path="C:/Development")


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    Returns:
        JSON with status
    """
    return jsonify({
        'status': 'ok',
        'service': 'context-api',
        'version': '1.0.0'
    })


@app.route('/parse-task', methods=['POST'])
def parse_task():
    """
    Parse task.md file.

    Request body:
    {
        "task_file": "C:/path/to/task.md"  # optional, default: workspace/task.md
    }

    Returns:
        JSON with parsed task data
    """
    try:
        data = request.json or {}

        # Get task file path
        task_file = data.get('task_file')
        if not task_file:
            workspace_path = Path(__file__).parent.parent / 'workspace'
            task_file = workspace_path / 'task.md'
        else:
            task_file = Path(task_file)

        if not task_file.exists():
            return jsonify({'error': f'Task file not found: {task_file}'}), 404

        logger.info(f"Parsing task file: {task_file}")

        # Read file
        content = task_file.read_text(encoding='utf-8')

        # Parse fields
        project_match = re.search(r'PROJECT:\s*(.+)', content, re.IGNORECASE)
        task_match = re.search(r'TASK:\s*(.+)', content, re.IGNORECASE)
        priority_match = re.search(r'PRIORITY:\s*(.+)', content, re.IGNORECASE)
        auto_commit_match = re.search(r'AUTO_COMMIT:\s*(yes|no)', content, re.IGNORECASE)
        auto_push_match = re.search(r'AUTO_PUSH:\s*(yes|no)', content, re.IGNORECASE)

        # Extract sections
        context_match = re.search(r'## Kontext\s*\n([\s\S]*?)(?=##|$)', content, re.IGNORECASE)
        notes_match = re.search(r'## Poznámky\s*\n([\s\S]*?)(?=##|$)', content, re.IGNORECASE)

        result = {
            'project': project_match.group(1).strip() if project_match else None,
            'task': task_match.group(1).strip() if task_match else None,
            'priority': priority_match.group(1).strip() if priority_match else 'NORMAL',
            'auto_commit': auto_commit_match.group(1).lower() == 'yes' if auto_commit_match else False,
            'auto_push': auto_push_match.group(1).lower() == 'yes' if auto_push_match else False,
            'context': context_match.group(1).strip() if context_match else '',
            'notes': notes_match.group(1).strip() if notes_match else '',
            'workspace_path': str(task_file.parent),
            'task_content': content
        }

        logger.info(f"Task parsed: project={result['project']}, task={result['task'][:50]}...")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Failed to parse task: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/build-context', methods=['POST'])
def build_context():
    """
    Build smart context for a project.

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

        # Validate input
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        project_name = data.get('project_name')
        task_description = data.get('task_description', '')

        if not project_name:
            return jsonify({'error': 'project_name is required'}), 400

        logger.info(f"Building context for project: {project_name}")

        # Build context using existing module
        context = builder.build_context(
            project_name=project_name,
            task_description=task_description
        )

        logger.info(f"Context built: {len(context)} chars")

        return jsonify({
            'context': context,
            'project_name': project_name,
            'context_size': len(context),
            'status': 'success'
        })

    except FileNotFoundError as e:
        logger.error(f"Project not found: {str(e)}")
        return jsonify({
            'error': f'Project not found: {str(e)}',
            'status': 'error'
        }), 404

    except Exception as e:
        logger.error(f"Context building failed: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/list-projects', methods=['GET'])
def list_projects():
    """
    List all available projects in projects directory.

    Returns:
        JSON with list of project names
    """
    try:
        projects_path = Path("C:/Development")

        if not projects_path.exists():
            return jsonify({'error': 'Projects directory not found'}), 404

        # Get all directories
        projects = [
            d.name for d in projects_path.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]

        projects.sort()

        return jsonify({
            'projects': projects,
            'count': len(projects),
            'projects_path': str(projects_path)
        })

    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/project-info/<project_name>', methods=['GET'])
def project_info(project_name: str):
    """
    Get information about a specific project.

    Args:
        project_name: Name of the project

    Returns:
        JSON with project information
    """
    try:
        project_path = builder._find_project_path(project_name)

        if not project_path:
            return jsonify({
                'error': f'Project {project_name} not found'
            }), 404

        # Get basic info
        info = {
            'project_name': project_name,
            'path': str(project_path),
            'exists': True
        }

        # Check for README
        readme_path = project_path / 'README.md'
        info['has_readme'] = readme_path.exists()

        # Check for session notes
        sessions_dir = project_path / 'docs' / 'sessions'
        info['has_sessions'] = sessions_dir.exists()
        if info['has_sessions']:
            session_files = list(sessions_dir.glob('*.md'))
            info['session_count'] = len(session_files)
            if session_files:
                latest = sorted(session_files, reverse=True)[0]
                info['latest_session'] = latest.name

        # Check for Git
        git_dir = project_path / '.git'
        info['is_git_repo'] = git_dir.exists()

        return jsonify(info)

    except Exception as e:
        logger.error(f"Failed to get project info: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Context API Service Starting...")
    print("="*60)
    print(f"📍 URL: http://localhost:5000")
    print(f"📂 Projects: C:/Development")
    print(f"🔍 Endpoints:")
    print(f"   - GET  /health")
    print(f"   - POST /parse-task")
    print(f"   - POST /build-context")
    print(f"   - GET  /list-projects")
    print(f"   - GET  /project-info/<name>")
    print("="*60 + "\n")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )