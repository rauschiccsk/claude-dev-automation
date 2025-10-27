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
    print("\n" + "=" * 60)
    print("🚀 Context API Service Starting...")
    print("=" * 60)
    print(f"📍 URL: http://localhost:5000")
    print(f"📂 Projects: C:/Development")
    print(f"🔍 Endpoints:")
    print(f"   - GET  /health")
    print(f"   - POST /build-context")
    print(f"   - GET  /list-projects")
    print(f"   - GET  /project-info/<name>")
    print("=" * 60 + "\n")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )