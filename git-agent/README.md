# Git Agent

An LLM-powered Git repository management agent that can handle git pull and push operations autonomously, even when conflicts occur.

## Features

- **Autonomous Git Operations**: Handles git pull/push with minimal user intervention
- **LLM-Powered Conflict Resolution**: Uses AI to analyze and resolve merge conflicts
- **Multiple LLM Provider Support**: Works with Gemini, OpenAI, Anthropic
- **Smart Backup System**: Creates automatic backups before risky operations
- **Flexible Configuration**: JSON-based configuration with environment variable support
- **Rich CLI Interface**: Beautiful command-line interface with detailed feedback

## Quick Start

### 1. Install Dependencies

```bash
cd git-agent
pip install -r requirements.txt
```

### 2. Configure LLM Provider

Create or edit `settings.config` and add your API key:

```json
{
  "llm_providers": {
    "gemini": {
      "enabled": true,
      "api_key": "${GEMINI_API_KEY}",
      "model": "gemini-1.5-flash"
    }
  }
}
```

Or set environment variable:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Use the Agent

```bash
# Pull with automatic conflict resolution
python git_agent.py pull /path/to/repo

# Push with automatic handling of rejections
python git_agent.py push /path/to/repo

# Check repository status
python git_agent.py status /path/to/repo

# View configuration
python git_agent.py config-info
```

## Configuration

The agent uses a `settings.config` file for configuration:

```json
{
  "llm_providers": {
    "gemini": {
      "enabled": true,
      "api_key": "${GEMINI_API_KEY}",
      "model": "gemini-1.5-flash",
      "temperature": 0.3,
      "max_tokens": 1000
    },
    "openai": {
      "enabled": false,
      "api_key": "${OPENAI_API_KEY}",
      "model": "gpt-3.5-turbo",
      "temperature": 0.3,
      "max_tokens": 1000
    }
  },
  "git_settings": {
    "auto_stash": true,
    "force_push_allowed": true,
    "backup_before_operations": true,
    "max_retry_attempts": 3,
    "conflict_resolution_strategy": "llm_guided"
  }
}
```

## How It Works

1. **Status Analysis**: The agent analyzes the current repository state
2. **Standard Operation**: Attempts normal git pull/push first
3. **LLM Consultation**: If issues occur, consults the LLM for resolution strategy
4. **Smart Execution**: Executes LLM-suggested commands safely
5. **Backup & Recovery**: Maintains backups for safety

## LLM Providers

### Gemini (Google)
- **Free tier available**
- Get API key: https://makersuite.google.com/app/apikey

### OpenAI
- Requires paid account
- Get API key: https://platform.openai.com/api-keys

### Anthropic (Claude)
- Requires paid account  
- Get API key: https://console.anthropic.com/

## Safety Features

- **Automatic Backups**: Creates backup branches before risky operations
- **Force Push Protection**: Configurable force push protection
- **Smart Stashing**: Automatically stashes/unstashes changes
- **Risk Assessment**: LLM evaluates operation safety before execution

## Examples

### Handling Merge Conflicts
When a pull results in merge conflicts, the agent:
1. Analyzes the conflicted files
2. Asks the LLM for resolution strategy
3. Executes merge resolution commands
4. Verifies the result

### Handling Push Rejections
When a push is rejected, the agent:
1. Analyzes the rejection reason
2. Determines if rebase/merge is needed
3. Performs necessary operations
4. Retries the push

## Troubleshooting

### No LLM Provider Available
```bash
python git_agent.py setup-provider gemini your-api-key
```

### Permission Issues
Ensure the repository has proper git configuration:
```bash
git config user.name "Your Name"
git config user.email "your@email.com"
```

### Configuration Issues
Check configuration:
```bash
python git_agent.py config-info
```