using GitAgent.Models;
using LibGit2Sharp;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System.Diagnostics;
using System.Text.Json;

namespace GitAgent.Services;

public interface IGitOperationsService
{
    Task<GitOperationResult> PullAsync(string repositoryPath);
    Task<GitOperationResult> PushAsync(string repositoryPath);
    Task<GitRepoStatus> GetStatusAsync(string repositoryPath);
}

public class GitOperationsService : IGitOperationsService
{
    private readonly ILlmProviderFactory _llmProviderFactory;
    private readonly GitAgentConfig _config;
    private readonly ILogger<GitOperationsService> _logger;

    public GitOperationsService(
        ILlmProviderFactory llmProviderFactory,
        IOptions<GitAgentConfig> config,
        ILogger<GitOperationsService> logger)
    {
        _llmProviderFactory = llmProviderFactory;
        _config = config.Value;
        _logger = logger;
    }

    public async Task<GitOperationResult> PullAsync(string repositoryPath)
    {
        _logger.LogInformation("Starting git pull operation for {Path}", repositoryPath);

        try
        {
            using var repo = new Repository(repositoryPath);
            
            // Create backup if configured
            if (_config.GitSettings.BackupBeforeOperations)
            {
                await CreateBackupAsync(repo);
            }

            // Get current status
            var status = await GetStatusAsync(repositoryPath);

            // Handle dirty working directory
            if (!status.IsClean && _config.GitSettings.AutoStash)
            {
                _logger.LogInformation("Stashing changes before pull");
                var stashResult = await RunGitCommandAsync(repositoryPath, "stash", "push", "-m", "git-agent auto-stash");
                if (!stashResult.success)
                {
                    _logger.LogWarning("Failed to stash changes: {Output}", stashResult.output);
                }
            }

            // Attempt normal pull first
            var pullResult = await RunGitCommandAsync(repositoryPath, "pull");
            
            if (pullResult.success)
            {
                // Restore stashed changes if any
                if (!status.IsClean && _config.GitSettings.AutoStash)
                {
                    await RunGitCommandAsync(repositoryPath, "stash", "pop");
                }

                return new GitOperationResult
                {
                    Success = true,
                    Message = "Pull completed successfully",
                    Details = pullResult.output
                };
            }

            // Pull failed, use LLM to resolve
            _logger.LogInformation("Pull failed: {Output}", pullResult.output);

            var llmProvider = _llmProviderFactory.CreateProvider();
            if (llmProvider == null)
            {
                return new GitOperationResult
                {
                    Success = false,
                    Message = "Pull failed and no LLM available for resolution",
                    Details = pullResult.output
                };
            }

            // Get fresh status after failed pull
            var newStatus = await GetStatusAsync(repositoryPath);

            // Generate LLM prompt
            var prompt = GenerateLlmPrompt("pull", newStatus, pullResult.output);

            // Get LLM response
            var llmResponse = await llmProvider.GenerateResponseAsync(prompt);
            if (string.IsNullOrEmpty(llmResponse))
            {
                return new GitOperationResult
                {
                    Success = false,
                    Message = "Failed to get LLM response for conflict resolution"
                };
            }

            // Parse and execute strategy
            var strategy = ParseLlmResponse(llmResponse);
            if (strategy == null)
            {
                return new GitOperationResult
                {
                    Success = false,
                    Message = "Failed to parse LLM strategy",
                    Details = llmResponse
                };
            }

            var executionResult = await ExecuteLlmStrategyAsync(repositoryPath, strategy);

            // Restore stashed changes if pull was successful
            if (executionResult.Success && !status.IsClean && _config.GitSettings.AutoStash)
            {
                var stashPopResult = await RunGitCommandAsync(repositoryPath, "stash", "pop");
                if (!stashPopResult.success)
                {
                    _logger.LogWarning("Failed to restore stashed changes: {Output}", stashPopResult.output);
                }
            }

            return executionResult;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during pull operation");
            return new GitOperationResult
            {
                Success = false,
                Message = $"Pull operation failed: {ex.Message}"
            };
        }
    }

    public async Task<GitOperationResult> PushAsync(string repositoryPath)
    {
        _logger.LogInformation("Starting git push operation for {Path}", repositoryPath);

        try
        {
            // Create backup if configured
            using var repo = new Repository(repositoryPath);
            if (_config.GitSettings.BackupBeforeOperations)
            {
                await CreateBackupAsync(repo);
            }

            // Attempt normal push first
            var pushResult = await RunGitCommandAsync(repositoryPath, "push");

            if (pushResult.success)
            {
                return new GitOperationResult
                {
                    Success = true,
                    Message = "Push completed successfully",
                    Details = pushResult.output
                };
            }

            // Push failed, use LLM to resolve
            _logger.LogInformation("Push failed: {Output}", pushResult.output);

            var llmProvider = _llmProviderFactory.CreateProvider();
            if (llmProvider == null)
            {
                return new GitOperationResult
                {
                    Success = false,
                    Message = "Push failed and no LLM available for resolution",
                    Details = pushResult.output
                };
            }

            var status = await GetStatusAsync(repositoryPath);
            var prompt = GenerateLlmPrompt("push", status, pushResult.output);

            var llmResponse = await llmProvider.GenerateResponseAsync(prompt);
            if (string.IsNullOrEmpty(llmResponse))
            {
                return new GitOperationResult
                {
                    Success = false,
                    Message = "Failed to get LLM response for conflict resolution"
                };
            }

            var strategy = ParseLlmResponse(llmResponse);
            if (strategy == null)
            {
                return new GitOperationResult
                {
                    Success = false,
                    Message = "Failed to parse LLM strategy",
                    Details = llmResponse
                };
            }

            return await ExecuteLlmStrategyAsync(repositoryPath, strategy);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during push operation");
            return new GitOperationResult
            {
                Success = false,
                Message = $"Push operation failed: {ex.Message}"
            };
        }
    }

    public async Task<GitRepoStatus> GetStatusAsync(string repositoryPath)
    {
        var status = new GitRepoStatus();

        try
        {
            using var repo = new Repository(repositoryPath);

            var repoStatus = repo.RetrieveStatus();
            status.IsClean = !repoStatus.IsDirty;

            foreach (var item in repoStatus)
            {
                switch (item.State)
                {
                    case FileStatus.NewInIndex:
                    case FileStatus.ModifiedInIndex:
                    case FileStatus.DeletedFromIndex:
                    case FileStatus.RenamedInIndex:
                    case FileStatus.TypeChangeInIndex:
                        status.StagedFiles.Add(item.FilePath);
                        break;

                    case FileStatus.NewInWorkdir:
                        status.UntrackedFiles.Add(item.FilePath);
                        break;

                    case FileStatus.ModifiedInWorkdir:
                    case FileStatus.DeletedFromWorkdir:
                    case FileStatus.TypeChangeInWorkdir:
                        status.ModifiedFiles.Add(item.FilePath);
                        break;

                    case FileStatus.Conflicted:
                        status.ConflictedFiles.Add(item.FilePath);
                        break;
                }
            }

            // Check ahead/behind status
            try
            {
                var trackingBranch = repo.Head.TrackedBranch;
                if (trackingBranch != null)
                {
                    var divergence = repo.ObjectDatabase.CalculateHistoryDivergence(repo.Head.Tip, trackingBranch.Tip);
                    status.AheadBy = divergence.AheadBy ?? 0;
                    status.BehindBy = divergence.BehindBy ?? 0;
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Could not determine ahead/behind status");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting repository status for {Path}", repositoryPath);
        }

        return status;
    }

    private async Task CreateBackupAsync(Repository repo)
    {
        try
        {
            var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            var backupBranchName = $"backup/git_agent_{timestamp}";

            var currentBranch = repo.Head;
            var backupBranch = repo.CreateBranch(backupBranchName, currentBranch.Tip);
            
            _logger.LogInformation("Created backup branch: {BackupBranch}", backupBranchName);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to create backup branch");
        }
    }

    private async Task<(bool success, string output)> RunGitCommandAsync(string repositoryPath, params string[] args)
    {
        try
        {
            var startInfo = new ProcessStartInfo
            {
                FileName = "git",
                WorkingDirectory = repositoryPath,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            foreach (var arg in args)
            {
                startInfo.ArgumentList.Add(arg);
            }

            using var process = Process.Start(startInfo);
            if (process == null)
            {
                return (false, "Failed to start git process");
            }

            await process.WaitForExitAsync();
            
            var output = process.ExitCode == 0 
                ? await process.StandardOutput.ReadToEndAsync()
                : await process.StandardError.ReadToEndAsync();

            return (process.ExitCode == 0, output.Trim());
        }
        catch (Exception ex)
        {
            return (false, ex.Message);
        }
    }

    private string GenerateLlmPrompt(string operation, GitRepoStatus status, string errorDetails)
    {
        return $@"
You are an expert Git operations assistant. I need help with a Git {operation} operation that encountered issues.

Current repository status:
- Clean working directory: {status.IsClean}
- Staged files: {status.StagedFiles.Count} files
- Modified files: {status.ModifiedFiles.Count} files  
- Untracked files: {status.UntrackedFiles.Count} files
- Merge conflicts: {status.ConflictedFiles.Count} files
- Commits ahead: {status.AheadBy}
- Commits behind: {status.BehindBy}

Error encountered: {errorDetails}

{(status.ConflictedFiles.Any() ? $"\nConflicted files:\n{string.Join('\n', status.ConflictedFiles.Select(f => $"- {f}"))}" : "")}

Please provide a step-by-step solution to successfully complete the {operation} operation. 
Your response should be a JSON object with this structure:
{{
    ""strategy"": ""brief description of the approach"",
    ""steps"": [
        {{""command"": ""git command"", ""description"": ""what this does""}},
        {{""command"": ""git command"", ""description"": ""what this does""}}
    ],
    ""requires_force"": true/false,
    ""safe_to_proceed"": true/false,
    ""risk_level"": ""low/medium/high""
}}

Focus on preserving data and ensuring the operation succeeds safely.
";
    }

    private LlmStrategy? ParseLlmResponse(string response)
    {
        try
        {
            // Extract JSON from response if it's embedded in text
            var startIndex = response.IndexOf('{');
            var endIndex = response.LastIndexOf('}');
            
            if (startIndex >= 0 && endIndex > startIndex)
            {
                var jsonStr = response.Substring(startIndex, endIndex - startIndex + 1);
                return JsonSerializer.Deserialize<LlmStrategy>(jsonStr, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to parse LLM response");
        }
        
        return null;
    }

    private async Task<GitOperationResult> ExecuteLlmStrategyAsync(string repositoryPath, LlmStrategy strategy)
    {
        if (!strategy.SafeToProceed)
        {
            return new GitOperationResult
            {
                Success = false,
                Message = "LLM determined operation is not safe to proceed",
                Details = $"Risk level: {strategy.RiskLevel}"
            };
        }

        if (!strategy.Steps.Any())
        {
            return new GitOperationResult
            {
                Success = false,
                Message = "No steps provided by LLM"
            };
        }

        var results = new List<string>();
        
        foreach (var step in strategy.Steps)
        {
            if (!step.Command.StartsWith("git "))
            {
                _logger.LogWarning("Skipping non-git command: {Command}", step.Command);
                continue;
            }

            var gitArgs = step.Command[4..].Split(' ', StringSplitOptions.RemoveEmptyEntries);
            
            // Handle force operations carefully
            if (gitArgs.Any(arg => arg is "--force" or "-f") && !_config.GitSettings.ForcePushAllowed)
            {
                _logger.LogWarning("Force operation blocked by configuration: {Command}", step.Command);
                continue;
            }

            _logger.LogInformation("Executing: {Command} ({Description})", step.Command, step.Description);
            var (success, output) = await RunGitCommandAsync(repositoryPath, gitArgs);
            
            results.Add($"{step.Command}: {(success ? "✅" : "❌")} {output}");
            
            if (!success)
            {
                return new GitOperationResult
                {
                    Success = false,
                    Message = $"Step failed: {step.Command}",
                    Details = $"Error: {output}"
                };
            }
        }

        return new GitOperationResult
        {
            Success = true,
            Message = $"Successfully executed LLM strategy: {strategy.Strategy}",
            Details = string.Join("\n", results)
        };
    }
}