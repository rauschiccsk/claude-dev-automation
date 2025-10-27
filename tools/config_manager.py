"""
Configuration Manager
Handles loading and managing configuration.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages configuration loading and validation."""

    DEFAULT_CONFIG = {
        'workspace_path': 'workspace',
        'projects_path': 'C:/Development',
        'model': 'claude-sonnet-4-5-20250929',
        'max_tokens': 8000
    }

    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialize config manager.

        Args:
            workspace_path: Path to workspace directory (optional)
        """
        if workspace_path:
            self.workspace_path = Path(workspace_path)
        else:
            # Try to find workspace relative to script
            script_dir = Path(__file__).parent
            self.workspace_path = script_dir.parent / 'workspace'

        self.config_file = self.workspace_path / 'config.json'

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from config.json.

        Returns:
            Configuration dictionary
        """
        if not self.config_file.exists():
            print(f"[WARNING] Config file not found: {self.config_file}")
            print(f"[INFO] Using default configuration")
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Merge with defaults (in case some keys are missing)
            full_config = self.DEFAULT_CONFIG.copy()
            full_config.update(config)

            print(f"[OK] Config loaded from: {self.config_file}")
            return full_config

        except Exception as e:
            print(f"[WARNING] Failed to load config: {e}")
            print(f"[INFO] Using default configuration")
            return self.DEFAULT_CONFIG.copy()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to config.json.

        Args:
            config: Configuration dictionary to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure workspace directory exists
            self.workspace_path.mkdir(parents=True, exist_ok=True)

            # Save config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            print(f"[OK] Config saved to: {self.config_file}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
            return False

    def get_project_path(self, project_name: str) -> Optional[Path]:
        """
        Get full path to a project.

        Args:
            project_name: Name of the project

        Returns:
            Path to project or None if not found
        """
        config = self.load_config()
        projects_path = Path(config.get('projects_path', 'C:/Development'))
        project_path = projects_path / project_name

        if project_path.exists():
            return project_path

        return None


# Test section
if __name__ == "__main__":
    print("\n[TEST] Testing ConfigManager...")

    try:
        # Test loading
        manager = ConfigManager()
        config = manager.load_config()

        print(f"\n[OK] Config loaded successfully:")
        print(f"     Workspace: {config['workspace_path']}")
        print(f"     Projects: {config['projects_path']}")
        print(f"     Model: {config['model']}")
        print(f"     Max tokens: {config['max_tokens']}")

        # Test project path
        project_path = manager.get_project_path('claude-dev-automation')
        if project_path:
            print(f"\n[OK] Project found: {project_path}")
        else:
            print(f"\n[INFO] Project not found (expected if not exists)")

        print("\n[SUCCESS] ConfigManager test completed!")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()