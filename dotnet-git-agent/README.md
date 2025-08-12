# Git Agent (.NET 8)

A .NET 8 implementation of the LLM-powered Git repository management agent that can handle git pull and push operations autonomously, even when conflicts occur.

## Features

- **Autonomous Git Operations**: Handles git pull/push with minimal user intervention
- **LLM-Powered Conflict Resolution**: Uses AI to analyze and resolve merge conflicts
- **Multiple LLM Provider Support**: Works with Gemini, OpenAI, Anthropic
- **Smart Backup System**: Creates automatic backups before risky operations
- **Flexible Configuration**: JSON-based configuration with dependency injection
- **Modern .NET CLI**: Built with System.CommandLine and .NET 8

## Quick Start

### 1. Build the Project

```bash
cd dotnet-git-agent
dotnet build
```

### 2. Configure LLM Provider

Edit `appsettings.json` and add your API key:

```json
{
  "LlmProviders": {
    "Gemini": {
      "Enabled": true,
      "ApiKey": "your-gemini-api-key",
      "Model": "gemini-1.5-flash"
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
dotnet run -- pull --path /path/to/repo

# Push with automatic handling of rejections
dotnet run -- push --path /path/to/repo

# Check repository status
dotnet run -- status --path /path/to/repo
```

## Configuration

The agent uses `appsettings.json` for configuration:

```json
{
  "LlmProviders": {
    "Gemini": {
      "Enabled": true,
      "ApiKey": "",
      "Model": "gemini-1.5-flash",
      "Temperature": 0.3,
      "MaxTokens": 1000
    },
    "OpenAI": {
      "Enabled": false,
      "ApiKey": "",
      "Model": "gpt-3.5-turbo",
      "Temperature": 0.3,
      "MaxTokens": 1000,
      "BaseUrl": "https://api.openai.com/v1"
    }
  },
  "GitSettings": {
    "AutoStash": true,
    "ForcePushAllowed": true,
    "BackupBeforeOperations": true,
    "MaxRetryAttempts": 3,
    "ConflictResolutionStrategy": "LlmGuided"
  }
}
```

## Architecture

The .NET implementation follows clean architecture principles:

- **Models**: Data models and configuration classes
- **Services**: Business logic for git operations and LLM providers
- **Program.cs**: CLI interface and dependency injection setup

### Key Components

1. **GitOperationsService**: Handles all git operations with LibGit2Sharp
2. **LlmProviderFactory**: Creates and manages LLM provider instances
3. **Configuration System**: Uses .NET's built-in configuration with options pattern

## Dependencies

- **.NET 8**: Modern .NET runtime
- **LibGit2Sharp**: Native git operations
- **System.CommandLine**: Modern CLI framework
- **Microsoft.Extensions.**: Dependency injection, logging, configuration
- **OpenAI/Anthropic SDKs**: LLM provider integrations

## Safety Features

- **Automatic Backups**: Creates backup branches before risky operations
- **Force Push Protection**: Configurable force push protection
- **Smart Stashing**: Automatically stashes/unstashes changes
- **Risk Assessment**: LLM evaluates operation safety before execution

## Examples

### Building and Running

```bash
# Build the project
dotnet build

# Run with specific repository
dotnet run -- pull --path ../my-repo

# Check status
dotnet run -- status --path .
```

### Development

```bash
# Run tests (if any)
dotnet test

# Publish for deployment
dotnet publish -c Release
```

## Comparison with Python Version

| Feature | .NET Version | Python Version |
|---------|--------------|----------------|
| Performance | ✅ Fast startup | ⚠️ Slower startup |
| Native Git | ✅ LibGit2Sharp | ✅ GitPython |
| LLM Integration | ✅ Official SDKs | ✅ Official SDKs |
| Configuration | ✅ appsettings.json | ✅ settings.config |
| CLI Framework | ✅ System.CommandLine | ✅ Click |
| Deployment | ✅ Single executable | ✅ Python script |

Both implementations provide the same core functionality with language-specific optimizations.