"""
Generate unified project_file_access.json manifest
Combines documentation, source code, workflows, and configuration
WITH CACHE BUSTING for fresh GitHub content

Claude Dev Automation - AI-Driven Multi-Project Development System
"""
import os
import json
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_NAME = "claude-dev-automation"
BASE_URL = "https://raw.githubusercontent.com/rauschiccsk/claude-dev-automation/main"
OUTPUT_FILE = "docs/project_file_access.json"

# Categories to scan
CATEGORIES = {
    "documentation": {
        "description": "Project documentation and guides",
        "directories": ["docs"],
        "extensions": [".md"],
        "recursive": False,
        "exclude_dirs": ["sessions", "tasks"],
        "exclude_files": []
    },
    "session_notes": {
        "description": "Development session notes",
        "directories": ["docs/sessions"],
        "extensions": [".md"],
        "recursive": True,
        "exclude_dirs": []
    },
    "task_examples": {
        "description": "Example tasks and templates",
        "directories": ["docs/tasks"],
        "extensions": [".md", ".txt"],
        "recursive": True,
        "exclude_dirs": []
    },
    "python_services": {
        "description": "Flask API services",
        "directories": ["services"],
        "extensions": [".py"],
        "recursive": True,
        "exclude_dirs": ["__pycache__"]
    },
    "python_tools": {
        "description": "Core Python automation tools",
        "directories": ["tools"],
        "extensions": [".py"],
        "recursive": True,
        "exclude_dirs": ["__pycache__"]
    },
    "workflows": {
        "description": "n8n workflow definitions",
        "directories": ["workflows"],
        "extensions": [".json", ".md"],
        "recursive": False,
        "exclude_dirs": []
    },
    "workspace_setup": {
        "description": "Workspace setup scripts",
        "directories": ["workspace"],
        "extensions": [".py"],
        "recursive": False,
        "exclude_dirs": []
    },
    "configuration": {
        "description": "Configuration files and dependencies",
        "directories": [".", "workspace", "services"],
        "extensions": [".txt", ".gitignore"],
        "recursive": False,
        "exclude_dirs": [],
        "include_patterns": ["requirements", ".gitignore"]
    }
}


def should_skip(path):
    """Check if path should be skipped"""
    skip_patterns = [
        "__pycache__",
        ".git",
        ".pytest_cache",
        "venv",
        "venv32",
        ".venv",
        "node_modules",
        ".idea",
        ".vscode",
        "*.pyc",
        ".DS_Store",
        "logs",
        ".env",  # Never include actual .env!
        "*.log",
        "response.md",  # Generated files
        "task.md",  # User workspace files
        "config.json"  # User configuration
    ]

    path_str = str(path)
    for pattern in skip_patterns:
        if pattern in path_str:
            return True
    return False


def matches_include_pattern(file_name, patterns):
    """Check if file name matches any include pattern"""
    if not patterns:
        return True

    for pattern in patterns:
        if pattern in file_name.lower():
            return True
    return False


def scan_category(category_name, config, base_path, version_param):
    """Scan files for a specific category"""
    files = []

    for directory in config["directories"]:
        dir_path = base_path / directory if directory != "." else base_path

        if not dir_path.exists():
            print(f"   ⚠️  Directory not found: {dir_path}")
            continue

        # Scan directory
        if config["recursive"]:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and not should_skip(file_path):
                # Check if in excluded directory
                if any(excl in str(file_path) for excl in config.get("exclude_dirs", [])):
                    continue

                # Check extension
                if file_path.suffix in config["extensions"]:
                    # Check include patterns if specified
                    if "include_patterns" in config:
                        if not matches_include_pattern(file_path.name, config["include_patterns"]):
                            continue

                    # Check exclude files
                    if file_path.name in config.get("exclude_files", []):
                        continue

                    relative_path = file_path.relative_to(base_path)
                    clean_path = str(relative_path).replace(os.sep, '/')

                    files.append({
                        "path": clean_path,
                        "raw_url": f"{BASE_URL}/{clean_path}?v={version_param}",
                        "size": file_path.stat().st_size,
                        "extension": file_path.suffix,
                        "name": file_path.name,
                        "category": category_name
                    })

    return files


def find_latest_session(all_files):
    """Find latest session note from scanned files"""
    session_files = [f for f in all_files if f["category"] == "session_notes"]
    if not session_files:
        return None

    # Sort by name (dates in filename)
    session_files.sort(key=lambda x: x["name"], reverse=True)
    return session_files[0]


def generate_manifest():
    """Generate unified project file access manifest"""
    print("=" * 70)
    print("🛠️  Claude Dev Automation - Project File Access Manifest Generator")
    print("=" * 70)

    # Get project root (script is in scripts/ directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Generate version parameter for cache busting
    now = datetime.now()
    version_param = now.strftime("%Y%m%d-%H%M%S")

    print(f"\n📂 Project root: {project_root}")
    print(f"🔄 Cache version: {version_param}")

    # Collect all files by category
    all_files = []
    category_stats = {}

    for category_name, category_config in CATEGORIES.items():
        print(f"\n🔍 Scanning: {category_name}")
        print(f"   Description: {category_config['description']}")
        print(f"   Directories: {', '.join(category_config['directories'])}")
        print(f"   Extensions: {', '.join(category_config['extensions'])}")

        files = scan_category(category_name, category_config, project_root, version_param)
        all_files.extend(files)
        category_stats[category_name] = len(files)

        print(f"   ✅ Found: {len(files)} files")

    # Sort files by path
    all_files.sort(key=lambda x: x["path"])

    # Find latest session
    latest_session = find_latest_session(all_files)

    # Create quick access section for most important files
    quick_access = {
        "essential_docs": [
            {
                "name": "COMPLETE_SUMMARY.md",
                "description": "Complete project overview and status",
                "url": f"{BASE_URL}/docs/COMPLETE_SUMMARY.md?v={version_param}"
            },
            {
                "name": "PROJECT_RULES.md",
                "description": "Development rules and conventions",
                "url": f"{BASE_URL}/docs/PROJECT_RULES.md?v={version_param}"
            },
            {
                "name": "GIT_WORKFLOW.md",
                "description": "Git workflow and branching strategy",
                "url": f"{BASE_URL}/docs/GIT_WORKFLOW.md?v={version_param}"
            }
        ],
        "latest_session": {
            "name": latest_session["name"] if latest_session else "N/A",
            "description": "Most recent development session",
            "url": latest_session["raw_url"] if latest_session else None
        } if latest_session else None,
        "core_services": [
            {
                "name": "context_api.py",
                "description": "Flask API for context management",
                "url": f"{BASE_URL}/services/context_api.py?v={version_param}"
            }
        ],
        "workflows": [
            {
                "name": "n8n-claude-dev-automation.json",
                "description": "n8n workflow definition",
                "url": f"{BASE_URL}/workflows/n8n-claude-dev-automation.json?v={version_param}"
            }
        ]
    }

    # Create manifest
    manifest = {
        "project_name": PROJECT_NAME,
        "description": "AI-Driven Multi-Project Development with 98% Token Savings - Unified file access manifest",
        "repository": "https://github.com/rauschiccsk/claude-dev-automation",
        "generated_at": now.isoformat(),
        "cache_version": version_param,
        "base_url": BASE_URL,
        "quick_access": quick_access,
        "categories": list(CATEGORIES.keys()),
        "category_descriptions": {
            name: config["description"]
            for name, config in CATEGORIES.items()
        },
        "statistics": {
            "total_files": len(all_files),
            "by_category": category_stats,
            "generated_by": "generate_project_access.py"
        },
        "files": all_files,
        "usage_instructions": {
            "step_1": "Load COMPLETE_SUMMARY.md first for project overview",
            "step_2": "Load this manifest for access to all project files",
            "step_3": "Access individual files using raw_url with cache version",
            "note": "Always regenerate manifest after pushing changes to get fresh cache version"
        }
    }

    # Write manifest
    output_path = project_root / OUTPUT_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("✅ Manifest Generated Successfully!")
    print("=" * 70)
    print(f"\n📄 Output: {output_path}")
    print(f"📊 Total files: {len(all_files)}")
    print(f"🔄 Cache version: {version_param}")
    print(f"\n📈 Files by category:")
    for category, count in category_stats.items():
        print(f"   • {category}: {count} files")

    print(f"\n🔗 GitHub URLs:")
    print(f"   Manifest: {BASE_URL}/docs/project_file_access.json?v={version_param}")
    print(f"   Summary:  {BASE_URL}/docs/COMPLETE_SUMMARY.md?v={version_param}")

    print("\n💡 Usage in Claude:")
    print("   Paste these TWO URLs to load complete project:")
    print(f"   1. {BASE_URL}/docs/COMPLETE_SUMMARY.md?v={version_param}")
    print(f"   2. {BASE_URL}/docs/project_file_access.json?v={version_param}")

    print("\n⚠️  IMPORTANT:")
    print("   After pushing ANY changes to GitHub:")
    print("   1. Run this script: python scripts/generate_project_access.py")
    print("   2. Commit updated manifest")
    print("   3. Push to GitHub")
    print("   4. Use NEW cache version in Claude")

    return manifest


if __name__ == "__main__":
    try:
        manifest = generate_manifest()
        print("\n✅ Done! Ready to commit and push.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()