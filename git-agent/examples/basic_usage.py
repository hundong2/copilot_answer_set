#!/usr/bin/env python3
"""
Example usage of Git Agent
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_config
from llm_providers import LLMManager
from git_operations import GitAgent


def example_basic_usage():
    """Example of basic git agent usage"""
    print("🚀 Git Agent Example - Basic Usage")
    
    # Initialize LLM manager
    llm_manager = LLMManager()
    
    # Add Gemini provider (if API key is available)
    if os.getenv('GEMINI_API_KEY'):
        config = {
            "enabled": True,
            "api_key": os.getenv('GEMINI_API_KEY'),
            "model": "gemini-1.5-flash",
            "temperature": 0.3,
            "max_tokens": 1000
        }
        success = llm_manager.add_provider("gemini", config)
        print(f"✅ Gemini provider: {'Available' if success else 'Failed'}")
    else:
        print("⚠️ GEMINI_API_KEY not set - using basic git operations only")
    
    # Initialize git agent for current directory
    try:
        git_agent = GitAgent(".", llm_manager)
        print(f"📁 Repository: {git_agent.repo_path}")
        
        # Check status
        status = git_agent.status()
        print(f"📊 Status: Clean={status['clean']}, Modified={len(status['modified_files'])}")
        
        # Example: This would normally perform operations
        print("💡 To perform operations, use:")
        print("   result = git_agent.pull()")
        print("   result = git_agent.push()")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you're in a git repository")


def example_configuration():
    """Example of configuration management"""
    print("\n🔧 Git Agent Example - Configuration")
    
    config = get_config()
    print(f"📄 Config file: {config.config_path}")
    
    # Show LLM providers
    print("\n🤖 LLM Providers:")
    for name, provider in config.llm_providers.items():
        status = "✅ Enabled" if provider.enabled else "❌ Disabled"
        api_key_status = "🔑 Set" if provider.api_key else "❌ Missing"
        print(f"  {name}: {status}, API Key: {api_key_status}, Model: {provider.model}")
    
    # Show git settings
    print(f"\n⚙️ Git Settings:")
    settings = config.git_settings
    print(f"  Auto stash: {settings.auto_stash}")
    print(f"  Force push allowed: {settings.force_push_allowed}")
    print(f"  Backup before operations: {settings.backup_before_operations}")
    print(f"  Max retry attempts: {settings.max_retry_attempts}")


if __name__ == "__main__":
    example_basic_usage()
    example_configuration()