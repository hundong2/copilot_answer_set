#!/usr/bin/env python3
"""
Git Agent CLI - Command line interface for LLM-powered Git operations
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .config import get_config, reload_config
from .llm_providers import LLMManager
from .git_operations import GitAgent, GitOperationResult

console = Console()


def setup_logging(level: str = "INFO"):
    """Setup logging with rich handler"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


def initialize_llm_manager() -> LLMManager:
    """Initialize LLM manager with configured providers"""
    config = get_config()
    llm_manager = LLMManager()
    
    # Add configured providers
    for name, provider_config in config.llm_providers.items():
        if provider_config.enabled:
            success = llm_manager.add_provider(name, provider_config.model_dump())
            if success:
                console.print(f"✅ Initialized {name} provider", style="green")
            else:
                console.print(f"❌ Failed to initialize {name} provider", style="red")
    
    if not llm_manager.is_available():
        console.print("⚠️ No LLM providers available. Some features will be limited.", style="yellow")
    
    return llm_manager


def print_operation_result(result: GitOperationResult):
    """Print formatted operation result"""
    if result.success:
        panel = Panel(
            f"[green]{result.message}[/green]",
            title="✅ Success",
            border_style="green"
        )
    else:
        panel = Panel(
            f"[red]{result.message}[/red]\n\n{result.details or ''}",
            title="❌ Failed",
            border_style="red"
        )
    
    console.print(panel)


@click.group()
@click.option('--config', '-c', help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """Git Agent - LLM-powered Git repository management"""
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)
    
    # Load configuration
    if config:
        os.environ['GIT_AGENT_CONFIG'] = config
        reload_config()
    
    # Store in context
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.pass_context
def pull(ctx, path):
    """Perform git pull with LLM-powered conflict resolution"""
    try:
        llm_manager = initialize_llm_manager()
        git_agent = GitAgent(path, llm_manager)
        
        console.print(f"🔄 Pulling repository: {Path(path).resolve()}")
        
        result = git_agent.pull()
        print_operation_result(result)
        
        if not result.success:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.pass_context
def push(ctx, path):
    """Perform git push with LLM-powered conflict resolution"""
    try:
        llm_manager = initialize_llm_manager()
        git_agent = GitAgent(path, llm_manager)
        
        console.print(f"⬆️ Pushing repository: {Path(path).resolve()}")
        
        result = git_agent.push()
        print_operation_result(result)
        
        if not result.success:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.pass_context
def status(ctx, path):
    """Show detailed repository status"""
    try:
        llm_manager = initialize_llm_manager()
        git_agent = GitAgent(path, llm_manager)
        
        console.print(f"📊 Repository status: {Path(path).resolve()}")
        
        status = git_agent.status()
        
        # Create status table
        table = Table(title="Git Repository Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        # Clean status
        clean_icon = "✅" if status['clean'] else "❌"
        table.add_row("Clean", f"{clean_icon} {status['clean']}")
        
        # File counts
        table.add_row("Staged files", str(len(status['staged_files'])))
        table.add_row("Modified files", str(len(status['modified_files'])))
        table.add_row("Untracked files", str(len(status['untracked_files'])))
        table.add_row("Conflicts", str(len(status['conflicts'])))
        
        # Sync status
        if status['ahead'] > 0:
            table.add_row("Ahead", f"⬆️ {status['ahead']} commits")
        if status['behind'] > 0:
            table.add_row("Behind", f"⬇️ {status['behind']} commits")
        
        console.print(table)
        
        # Show conflicts if any
        if status['conflicts']:
            console.print("\n🚨 Conflicted files:", style="red bold")
            for conflict in status['conflicts']:
                console.print(f"  - {conflict}", style="red")
                
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.pass_context
def config_info(ctx):
    """Show current configuration"""
    try:
        config = get_config()
        
        console.print("⚙️ Git Agent Configuration")
        
        # LLM Providers table
        providers_table = Table(title="LLM Providers")
        providers_table.add_column("Provider", style="cyan")
        providers_table.add_column("Enabled", style="white")
        providers_table.add_column("Model", style="yellow")
        providers_table.add_column("API Key", style="dim")
        
        for name, provider in config.llm_providers.items():
            enabled = "✅" if provider.enabled else "❌"
            api_key_status = "✅ Set" if provider.api_key else "❌ Missing"
            providers_table.add_row(name, enabled, provider.model, api_key_status)
        
        console.print(providers_table)
        
        # Git settings table
        git_table = Table(title="Git Settings")
        git_table.add_column("Setting", style="cyan")
        git_table.add_column("Value", style="white")
        
        settings = config.git_settings
        git_table.add_row("Auto stash", "✅" if settings.auto_stash else "❌")
        git_table.add_row("Force push allowed", "✅" if settings.force_push_allowed else "❌")
        git_table.add_row("Backup before operations", "✅" if settings.backup_before_operations else "❌")
        git_table.add_row("Max retry attempts", str(settings.max_retry_attempts))
        git_table.add_row("Conflict resolution", settings.conflict_resolution_strategy)
        
        console.print(git_table)
        
        # Configuration file path
        console.print(f"\n📄 Config file: {config.config_path}")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('provider', type=click.Choice(['gemini', 'openai', 'anthropic']))
@click.argument('api_key')
@click.pass_context
def setup_provider(ctx, provider, api_key):
    """Setup LLM provider with API key"""
    try:
        config = get_config()
        
        if provider in config.llm_providers:
            config.llm_providers[provider].enabled = True
            config.llm_providers[provider].api_key = api_key
            config.save_config()
            
            console.print(f"✅ {provider} provider configured successfully", style="green")
            console.print("💡 Tip: You can also set environment variables like GEMINI_API_KEY", style="dim")
        else:
            console.print(f"❌ Unknown provider: {provider}", style="red")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('message')
@click.argument('path', type=click.Path(exists=True), default='.')
@click.pass_context
def smart_commit(ctx, message, path):
    """Smart commit with LLM-suggested improvements"""
    try:
        llm_manager = initialize_llm_manager()
        git_agent = GitAgent(path, llm_manager)
        
        console.print(f"🧠 Smart commit for: {Path(path).resolve()}")
        
        if llm_manager.is_available():
            # Get repository status
            status = git_agent.status()
            
            # Generate LLM prompt for commit message improvement
            prompt = f"""
Please review and improve this git commit message: "{message}"

Current repository changes:
- Modified files: {len(status['modified_files'])}
- Staged files: {len(status['staged_files'])}

Provide a better commit message following conventional commit format if appropriate.
Respond with just the improved commit message, nothing else.
"""
            
            improved_message = llm_manager.generate_response(prompt)
            if improved_message:
                console.print(f"💡 LLM suggested: {improved_message.strip()}")
                if click.confirm("Use LLM-suggested commit message?"):
                    message = improved_message.strip()
        
        # Perform commit
        success, output = git_agent._run_git_command(["add", "."])
        if success:
            success, output = git_agent._run_git_command(["commit", "-m", message])
            if success:
                console.print("✅ Commit successful", style="green")
            else:
                console.print(f"❌ Commit failed: {output}", style="red")
        else:
            console.print(f"❌ Add failed: {output}", style="red")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


if __name__ == '__main__':
    cli()