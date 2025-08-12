#!/usr/bin/env python3
"""
Configuration management for Git Agent
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class LLMProviderConfig(BaseModel):
    """Configuration for LLM provider"""
    enabled: bool = False
    api_key: str = ""
    model: str = ""
    temperature: float = 0.3
    max_tokens: int = 1000
    base_url: Optional[str] = None


class GitSettings(BaseModel):
    """Git operation settings"""
    auto_stash: bool = True
    force_push_allowed: bool = True
    backup_before_operations: bool = True
    max_retry_attempts: int = 3
    conflict_resolution_strategy: str = "llm_guided"


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    file: str = "git_agent.log"
    console: bool = True


class Config:
    """Main configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.llm_providers: Dict[str, LLMProviderConfig] = {}
        self.git_settings = GitSettings()
        self.logging_config = LoggingConfig()
        self._load_config()
    
    def _find_config_file(self) -> str:
        """Find settings.config file"""
        # Try current directory first
        current_dir = Path.cwd()
        config_file = current_dir / "settings.config"
        if config_file.exists():
            return str(config_file)
        
        # Try git-agent directory
        git_agent_dir = current_dir / "git-agent"
        config_file = git_agent_dir / "settings.config"
        if config_file.exists():
            return str(config_file)
        
        # Try parent directories
        for parent in current_dir.parents:
            config_file = parent / "git-agent" / "settings.config"
            if config_file.exists():
                return str(config_file)
        
        # Default fallback
        return str(current_dir / "settings.config")
    
    def _expand_env_vars(self, value: str) -> str:
        """Expand environment variables in config values"""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value
    
    def _load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            logging.warning(f"Config file not found: {self.config_path}. Using defaults.")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Load LLM providers
            if "llm_providers" in config_data:
                for name, provider_config in config_data["llm_providers"].items():
                    # Expand environment variables
                    if "api_key" in provider_config:
                        provider_config["api_key"] = self._expand_env_vars(provider_config["api_key"])
                    
                    self.llm_providers[name] = LLMProviderConfig(**provider_config)
            
            # Load git settings
            if "git_settings" in config_data:
                self.git_settings = GitSettings(**config_data["git_settings"])
            
            # Load logging config
            if "logging" in config_data:
                self.logging_config = LoggingConfig(**config_data["logging"])
                
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            logging.info("Using default configuration")
    
    def get_enabled_llm_provider(self) -> Optional[tuple[str, LLMProviderConfig]]:
        """Get the first enabled LLM provider"""
        for name, config in self.llm_providers.items():
            if config.enabled and config.api_key:
                return name, config
        return None
    
    def save_config(self):
        """Save current configuration to file"""
        config_data = {
            "llm_providers": {
                name: config.model_dump() for name, config in self.llm_providers.items()
            },
            "git_settings": self.git_settings.model_dump(),
            "logging": self.logging_config.model_dump()
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)


# Global configuration instance
_config = None

def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config

def reload_config():
    """Reload configuration from file"""
    global _config
    _config = None
    return get_config()