#!/usr/bin/env python3
"""
Tests for Git Agent configuration
"""

import json
import os
import tempfile
import pytest
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config, LLMProviderConfig, GitSettings


class TestConfig:
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            config = Config(str(config_path))
            
            assert config.git_settings.auto_stash is True
            assert config.git_settings.force_push_allowed is True
            assert config.logging_config.level == "INFO"
    
    def test_config_loading(self):
        """Test loading configuration from file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            
            # Create test config
            test_config = {
                "llm_providers": {
                    "gemini": {
                        "enabled": True,
                        "api_key": "test-key",
                        "model": "gemini-1.5-flash",
                        "temperature": 0.5
                    }
                },
                "git_settings": {
                    "auto_stash": False,
                    "max_retry_attempts": 5
                }
            }
            
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            # Load config
            config = Config(str(config_path))
            
            assert "gemini" in config.llm_providers
            assert config.llm_providers["gemini"].enabled is True
            assert config.llm_providers["gemini"].api_key == "test-key"
            assert config.llm_providers["gemini"].temperature == 0.5
            assert config.git_settings.auto_stash is False
            assert config.git_settings.max_retry_attempts == 5
    
    def test_env_var_expansion(self):
        """Test environment variable expansion"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            
            # Set environment variable
            os.environ["TEST_API_KEY"] = "secret-key"
            
            test_config = {
                "llm_providers": {
                    "test": {
                        "enabled": True,
                        "api_key": "${TEST_API_KEY}",
                        "model": "test-model"
                    }
                }
            }
            
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            config = Config(str(config_path))
            assert config.llm_providers["test"].api_key == "secret-key"
            
            # Cleanup
            del os.environ["TEST_API_KEY"]
    
    def test_get_enabled_provider(self):
        """Test getting enabled LLM provider"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            
            test_config = {
                "llm_providers": {
                    "disabled": {
                        "enabled": False,
                        "api_key": "key1",
                        "model": "model1"
                    },
                    "enabled": {
                        "enabled": True,
                        "api_key": "key2",
                        "model": "model2"
                    }
                }
            }
            
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            config = Config(str(config_path))
            result = config.get_enabled_llm_provider()
            
            assert result is not None
            name, provider_config = result
            assert name == "enabled"
            assert provider_config.api_key == "key2"


if __name__ == "__main__":
    pytest.main([__file__])