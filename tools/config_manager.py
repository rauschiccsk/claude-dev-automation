#!/usr/bin/env python3
"""
Configuration Manager
Handles loading and accessing all configuration from workspace
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """
        Initialize config manager
        
        Args:
            workspace_root: Path to workspace root (default: C:/Development/_workspace)
        """
        self.workspace_root = Path(workspace_root or "C:/Development/_workspace")
        self.config_file = self.workspace_root / "config.json"
        self.env_file = self.workspace_root / ".env"
        
        # Load environment variables
        load_dotenv(self.env_file)
        
        # Load config
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get config value using dot notation
        
        Example:
            config.get('claude_api.model')
            config.get('automation.auto_commit_default')
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable"""
        return os.getenv(key, default)
    
    @property
    def anthropic_api_key(self) -> str:
        """Get Anthropic API key"""
        key = self.get_env('ANTHROPIC_API_KEY')
        if not key or key == 'your_api_key_here':
            raise ValueError("ANTHROPIC_API_KEY not set in .env file")
        return key
    
    @property
    def n8n_webhook_url(self) -> str:
        """Get n8n webhook URL"""
        return self.get_env('N8N_WEBHOOK_URL') or self.get('n8n_webhook_url')
    
    @property
    def claude_model(self) -> str:
        """Get Claude model name"""
        return self.get('claude_api.model', 'claude-sonnet-4-5-20250929')
    
    @property
    def claude_max_tokens(self) -> int:
        """Get Claude max tokens"""
        return self.get('claude_api.max_tokens', 8000)
    
    @property
    def claude_temperature(self) -> float:
        """Get Claude temperature"""
        return self.get('claude_api.temperature', 0.7)
    
    @property
    def auto_commit_default(self) -> bool:
        """Get auto commit default setting"""
        return self.get('automation.auto_commit_default', False)
    
    @property
    def auto_push_default(self) -> bool:
        """Get auto push default setting"""
        return self.get('automation.auto_push_default', False)
    
    @property
    def max_context_tokens(self) -> int:
        """Get max context tokens"""
        return self.get('context_limits.max_context_tokens', 5000)
    
    @property
    def max_history_messages(self) -> int:
        """Get max history messages"""
        return self.get('context_limits.max_history_messages', 5)
    
    def save_config(self, config: Dict[str, Any]):
        """Save updated configuration"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        self.config = config
    
    def update_config(self, key: str, value: Any):
        """
        Update config value using dot notation
        
        Example:
            config.update_config('automation.auto_commit_default', True)
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
        
        # Save
        self.save_config(self.config)
    
    def __repr__(self) -> str:
        return f"ConfigManager(workspace={self.workspace_root})"


# Singleton instance
_config_instance = None

def get_config() -> ConfigManager:
    """Get singleton config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance


if __name__ == "__main__":
    # Test configuration
    print("Testing Configuration Manager...")
    print("=" * 60)
    
    try:
        config = ConfigManager()
        
        print(f"✅ Config loaded from: {config.config_file}")
        print(f"✅ Model: {config.claude_model}")
        print(f"✅ Max tokens: {config.claude_max_tokens}")
        print(f"✅ Temperature: {config.claude_temperature}")
        print(f"✅ Auto commit: {config.auto_commit_default}")
        print(f"✅ Max context: {config.max_context_tokens}")
        print(f"✅ n8n URL: {config.n8n_webhook_url}")
        
        # Test API key (without showing it)
        key = config.anthropic_api_key
        print(f"✅ API Key: {'*' * 20}{key[-8:]}")
        
        print("\n" + "=" * 60)
        print("✅ Configuration test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")