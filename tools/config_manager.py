"""
config_manager.py - Configuration management
Loads and manages configuration from config.json and .env files
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration from config.json and environment variables."""

    def __init__(self, config_path: str = "workspace/config.json"):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to config.json file
        """
        self.config_path = Path(config_path)
        self.workspace_path = self.config_path.parent
        self.env_path = self.workspace_path / '.env'

        # Load environment variables from .env
        if self.env_path.exists():
            load_dotenv(self.env_path)

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from config.json.

        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            print(f"⚠️  Config file not found: {self.config_path}")
            return self._default_config()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Merge with environment variables
            config = self._merge_env_vars(config)

            return config

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            return self._default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return self._default_config()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to config.json.

        Args:
            config: Configuration dictionary

        Returns:
            True if successful
        """
        try:
            # Ensure workspace directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        config = self.load_config()

        # Support dot notation (e.g., "api.key")
        keys = key.split('.')
        value = config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def _default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            'workspace_path': str(self.workspace_path.absolute()),
            'projects_path': 'C:/Development',
            'api_key': os.getenv('ANTHROPIC_API_KEY', ''),
            'model': 'claude-sonnet-4-5-20250929',
            'max_tokens': 8000,
            'temperature': 1.0,
            'auto_commit': False,
            'auto_push': False
        }

    def _merge_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge environment variables into config.
        Environment variables override config file values.

        Args:
            config: Configuration from file

        Returns:
            Merged configuration
        """
        # API key from environment
        if 'ANTHROPIC_API_KEY' in os.environ:
            config['api_key'] = os.environ['ANTHROPIC_API_KEY']

        # Model from environment
        if 'CLAUDE_MODEL' in os.environ:
            config['model'] = os.environ['CLAUDE_MODEL']

        # Max tokens from environment
        if 'MAX_TOKENS' in os.environ:
            try:
                config['max_tokens'] = int(os.environ['MAX_TOKENS'])
            except ValueError:
                pass

        return config

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        required_keys = ['api_key', 'workspace_path', 'projects_path']

        for key in required_keys:
            if key not in config or not config[key]:
                print(f"❌ Missing required config key: {key}")
                return False

        # Validate paths exist
        workspace_path = Path(config['workspace_path'])
        if not workspace_path.exists():
            print(f"❌ Workspace path does not exist: {workspace_path}")
            return False

        projects_path = Path(config['projects_path'])
        if not projects_path.exists():
            print(f"⚠️  Projects path does not exist: {projects_path}")
            # Not critical, just a warning

        return True


# Example usage and testing
if __name__ == "__main__":
    print("[TEST] Testing ConfigManager...\n")

    # Test with default config
    manager = ConfigManager("workspace/config.json")

    print("[INFO] Loading configuration...")
    config = manager.load_config()

    print("\n[OK] Configuration loaded:")
    print(f"     Workspace: {config.get('workspace_path', 'N/A')}")
    print(f"     Projects: {config.get('projects_path', 'N/A')}")
    print(f"     Model: {config.get('model', 'N/A')}")
    print(f"     Max tokens: {config.get('max_tokens', 'N/A')}")

    # Check API key (don't print full key)
    api_key = config.get('api_key', '')
    if api_key:
        print(f"     API key: {api_key[:10]}...{api_key[-4:]} (length: {len(api_key)})")
    else:
        print(f"     API key: NOT SET [WARNING]")

    # Test validation
    print("\n[INFO] Validating configuration...")
    is_valid = manager.validate_config(config)
    print(f"     {'[OK]' if is_valid else '[ERROR]'} Configuration is {'valid' if is_valid else 'invalid'}")

    # Test get method with dot notation
    print("\n[INFO] Testing get method...")
    workspace = manager.get('workspace_path', 'default')
    print(f"     workspace_path: {workspace}")

    # Test save (create sample config)
    print("\n[INFO] Testing save configuration...")
    sample_config = {
        'workspace_path': 'C:/Development/claude-dev-automation/workspace',
        'projects_path': 'C:/Development',
        'api_key': 'sk-ant-...',
        'model': 'claude-sonnet-4-5-20250929',
        'max_tokens': 8000
    }

    # Save to test file
    test_manager = ConfigManager("workspace/test_config.json")
    success = test_manager.save_config(sample_config)
    print(f"     {'[OK]' if success else '[ERROR]'} Save {'successful' if success else 'failed'}")

    if success and Path("workspace/test_config.json").exists():
        # Clean up test file
        Path("workspace/test_config.json").unlink()
        print("     [OK] Test file cleaned up")

    print("\n[OK] All tests completed!")