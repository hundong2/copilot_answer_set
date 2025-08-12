#!/usr/bin/env python3
"""
Git operations handler with LLM-powered conflict resolution
"""

import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

try:
    from git import Repo, GitCommandError, InvalidGitRepositoryError
    GIT_PYTHON_AVAILABLE = True
except ImportError:
    GIT_PYTHON_AVAILABLE = False

try:
    from .config import get_config
    from .llm_providers import LLMManager
except ImportError:
    from config import get_config
    from llm_providers import LLMManager

logger = logging.getLogger(__name__)


class GitOperationResult:
    """Result of a git operation"""
    
    def __init__(self, success: bool, message: str, details: Optional[str] = None):
        self.success = success
        self.message = message
        self.details = details
        self.timestamp = datetime.now()


class GitAgent:
    """LLM-powered Git repository management agent"""
    
    def __init__(self, repo_path: str, llm_manager: LLMManager):
        self.repo_path = Path(repo_path).resolve()
        self.llm_manager = llm_manager
        self.config = get_config()
        self.repo = None
        self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize git repository"""
        if not GIT_PYTHON_AVAILABLE:
            raise ImportError("GitPython library is required. Install with: pip install GitPython")
        
        try:
            self.repo = Repo(self.repo_path)
            logger.info(f"Initialized Git repository at: {self.repo_path}")
        except InvalidGitRepositoryError:
            logger.error(f"Invalid Git repository: {self.repo_path}")
            raise
    
    def _run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run git command and return result"""
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            return success, output.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def _create_backup(self) -> Optional[str]:
        """Create backup of current state"""
        if not self.config.git_settings.backup_before_operations:
            return None
        
        try:
            # Create a backup branch
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_branch = f"backup/git_agent_{timestamp}"
            
            success, output = self._run_git_command(["checkout", "-b", backup_branch])
            if success:
                logger.info(f"Created backup branch: {backup_branch}")
                # Switch back to original branch
                self._run_git_command(["checkout", "-"])
                return backup_branch
            else:
                logger.warning(f"Failed to create backup: {output}")
                return None
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def _analyze_git_status(self) -> Dict[str, Any]:
        """Analyze current git status"""
        status = {
            "clean": True,
            "staged_files": [],
            "modified_files": [],
            "untracked_files": [],
            "conflicts": [],
            "ahead": 0,
            "behind": 0
        }
        
        try:
            # Check status
            if self.repo.is_dirty():
                status["clean"] = False
                status["staged_files"] = [item.a_path for item in self.repo.index.diff("HEAD")]
                status["modified_files"] = [item.a_path for item in self.repo.index.diff(None)]
                status["untracked_files"] = self.repo.untracked_files
            
            # Check for conflicts
            success, output = self._run_git_command(["diff", "--name-only", "--diff-filter=U"])
            if success and output:
                status["conflicts"] = output.split('\n')
            
            # Check ahead/behind
            try:
                origin = self.repo.remotes.origin
                origin.fetch()
                current_branch = self.repo.active_branch.name
                ahead = len(list(self.repo.iter_commits(f'origin/{current_branch}..HEAD')))
                behind = len(list(self.repo.iter_commits(f'HEAD..origin/{current_branch}')))
                status["ahead"] = ahead
                status["behind"] = behind
            except:
                pass  # Remote tracking might not be set up
            
        except Exception as e:
            logger.error(f"Error analyzing git status: {e}")
        
        return status
    
    def _generate_llm_prompt(self, operation: str, status: Dict[str, Any], error_details: str = "") -> str:
        """Generate prompt for LLM to solve git issues"""
        
        base_prompt = f"""
You are an expert Git operations assistant. I need help with a Git {operation} operation that encountered issues.

Current repository status:
- Clean working directory: {status['clean']}
- Staged files: {len(status['staged_files'])} files
- Modified files: {len(status['modified_files'])} files  
- Untracked files: {len(status['untracked_files'])} files
- Merge conflicts: {len(status['conflicts'])} files
- Commits ahead: {status['ahead']}
- Commits behind: {status['behind']}

"""
        
        if error_details:
            base_prompt += f"\nError encountered: {error_details}\n"
        
        if status['conflicts']:
            base_prompt += f"\nConflicted files:\n" + "\n".join(f"- {f}" for f in status['conflicts'])
        
        base_prompt += f"""
Please provide a step-by-step solution to successfully complete the {operation} operation. 
Your response should be a JSON object with this structure:
{{
    "strategy": "brief description of the approach",
    "steps": [
        {{"command": "git command", "description": "what this does"}},
        {{"command": "git command", "description": "what this does"}}
    ],
    "requires_force": true/false,
    "safe_to_proceed": true/false,
    "risk_level": "low/medium/high"
}}

Focus on preserving data and ensuring the operation succeeds safely.
"""
        
        return base_prompt
    
    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response for git strategy"""
        try:
            import json
            # Extract JSON from response if it's embedded in text
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
        return None
    
    def _execute_llm_strategy(self, strategy: Dict[str, Any]) -> GitOperationResult:
        """Execute LLM-suggested strategy"""
        if not strategy.get("safe_to_proceed", False):
            return GitOperationResult(
                False, 
                "LLM determined operation is not safe to proceed",
                f"Risk level: {strategy.get('risk_level', 'unknown')}"
            )
        
        steps = strategy.get("steps", [])
        if not steps:
            return GitOperationResult(False, "No steps provided by LLM")
        
        results = []
        for step in steps:
            command = step.get("command", "")
            description = step.get("description", "")
            
            if not command.startswith("git "):
                logger.warning(f"Skipping non-git command: {command}")
                continue
            
            # Extract git arguments
            git_args = command[4:].split()
            
            # Handle force operations carefully
            if any(arg in git_args for arg in ["--force", "-f"]) and not self.config.git_settings.force_push_allowed:
                logger.warning(f"Force operation blocked by configuration: {command}")
                continue
            
            logger.info(f"Executing: {command} ({description})")
            success, output = self._run_git_command(git_args)
            
            results.append({
                "command": command,
                "success": success,
                "output": output,
                "description": description
            })
            
            if not success:
                return GitOperationResult(
                    False, 
                    f"Step failed: {command}",
                    f"Error: {output}"
                )
        
        return GitOperationResult(
            True, 
            f"Successfully executed LLM strategy: {strategy.get('strategy', 'Unknown')}",
            f"Completed {len(results)} steps"
        )
    
    def pull(self) -> GitOperationResult:
        """Perform git pull with LLM-powered conflict resolution"""
        logger.info("Starting git pull operation")
        
        # Create backup if configured
        backup_branch = self._create_backup()
        
        # Analyze current status
        status = self._analyze_git_status()
        
        # Handle dirty working directory
        if not status["clean"] and self.config.git_settings.auto_stash:
            logger.info("Stashing changes before pull")
            success, output = self._run_git_command(["stash", "push", "-m", "git-agent auto-stash"])
            if not success:
                logger.warning(f"Failed to stash changes: {output}")
        
        # Attempt normal pull first
        success, output = self._run_git_command(["pull"])
        
        if success:
            # Restore stashed changes if any
            if not status["clean"] and self.config.git_settings.auto_stash:
                self._run_git_command(["stash", "pop"])
            
            return GitOperationResult(True, "Pull completed successfully", output)
        
        # Pull failed, use LLM to resolve
        logger.info(f"Pull failed: {output}")
        
        if not self.llm_manager.is_available():
            return GitOperationResult(False, "Pull failed and no LLM available for resolution", output)
        
        # Get fresh status after failed pull
        status = self._analyze_git_status()
        
        # Generate LLM prompt
        prompt = self._generate_llm_prompt("pull", status, output)
        
        # Get LLM response
        llm_response = self.llm_manager.generate_response(prompt)
        if not llm_response:
            return GitOperationResult(False, "Failed to get LLM response for conflict resolution")
        
        # Parse and execute strategy
        strategy = self._parse_llm_response(llm_response)
        if not strategy:
            return GitOperationResult(False, "Failed to parse LLM strategy", llm_response)
        
        result = self._execute_llm_strategy(strategy)
        
        # Restore stashed changes if pull was successful
        if result.success and not status["clean"] and self.config.git_settings.auto_stash:
            stash_success, stash_output = self._run_git_command(["stash", "pop"])
            if not stash_success:
                logger.warning(f"Failed to restore stashed changes: {stash_output}")
        
        return result
    
    def push(self) -> GitOperationResult:
        """Perform git push with LLM-powered conflict resolution"""
        logger.info("Starting git push operation")
        
        # Create backup if configured
        backup_branch = self._create_backup()
        
        # Analyze current status
        status = self._analyze_git_status()
        
        # Attempt normal push first
        success, output = self._run_git_command(["push"])
        
        if success:
            return GitOperationResult(True, "Push completed successfully", output)
        
        # Push failed, use LLM to resolve
        logger.info(f"Push failed: {output}")
        
        if not self.llm_manager.is_available():
            return GitOperationResult(False, "Push failed and no LLM available for resolution", output)
        
        # Generate LLM prompt
        prompt = self._generate_llm_prompt("push", status, output)
        
        # Get LLM response
        llm_response = self.llm_manager.generate_response(prompt)
        if not llm_response:
            return GitOperationResult(False, "Failed to get LLM response for conflict resolution")
        
        # Parse and execute strategy
        strategy = self._parse_llm_response(llm_response)
        if not strategy:
            return GitOperationResult(False, "Failed to parse LLM strategy", llm_response)
        
        return self._execute_llm_strategy(strategy)
    
    def status(self) -> Dict[str, Any]:
        """Get detailed repository status"""
        return self._analyze_git_status()