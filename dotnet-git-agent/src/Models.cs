namespace GitAgent.Models;

public class GitAgentConfig
{
    public Dictionary<string, LlmProviderConfig> LlmProviders { get; set; } = new();
    public GitSettings GitSettings { get; set; } = new();
}

public class LlmProviderConfig
{
    public bool Enabled { get; set; }
    public string ApiKey { get; set; } = string.Empty;
    public string Model { get; set; } = string.Empty;
    public double Temperature { get; set; } = 0.3;
    public int MaxTokens { get; set; } = 1000;
    public string? BaseUrl { get; set; }
}

public class GitSettings
{
    public bool AutoStash { get; set; } = true;
    public bool ForcePushAllowed { get; set; } = true;
    public bool BackupBeforeOperations { get; set; } = true;
    public int MaxRetryAttempts { get; set; } = 3;
    public string ConflictResolutionStrategy { get; set; } = "LlmGuided";
}

public class GitOperationResult
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public string? Details { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.Now;
}

public class GitRepoStatus
{
    public bool IsClean { get; set; }
    public List<string> StagedFiles { get; set; } = new();
    public List<string> ModifiedFiles { get; set; } = new();
    public List<string> UntrackedFiles { get; set; } = new();
    public List<string> ConflictedFiles { get; set; } = new();
    public int AheadBy { get; set; }
    public int BehindBy { get; set; }
}

public class LlmStrategy
{
    public string Strategy { get; set; } = string.Empty;
    public List<GitCommand> Steps { get; set; } = new();
    public bool RequiresForce { get; set; }
    public bool SafeToProceed { get; set; }
    public string RiskLevel { get; set; } = "unknown";
}

public class GitCommand
{
    public string Command { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
}