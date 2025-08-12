using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System.CommandLine;
using GitAgent.Services;
using GitAgent.Models;

namespace GitAgent;

class Program
{
    static async Task<int> Main(string[] args)
    {
        // Create host builder
        var hostBuilder = Host.CreateDefaultBuilder(args)
            .ConfigureServices((context, services) =>
            {
                // Register configuration
                services.Configure<GitAgentConfig>(context.Configuration);
                
                // Register services
                services.AddSingleton<ILlmProviderFactory, LlmProviderFactory>();
                services.AddSingleton<IGitOperationsService, GitOperationsService>();
                services.AddLogging();
            });

        var host = hostBuilder.Build();

        // Create root command
        var rootCommand = new RootCommand("Git Agent - LLM-powered Git repository management");

        // Add pull command
        var pullCommand = new Command("pull", "Perform git pull with LLM-powered conflict resolution");
        var pullPathOption = new Option<string>("--path", () => ".", "Repository path");
        pullCommand.AddOption(pullPathOption);
        pullCommand.SetHandler(async (string path) =>
        {
            var gitService = host.Services.GetRequiredService<IGitOperationsService>();
            var result = await gitService.PullAsync(path);
            Console.WriteLine(result.Success ? $"✅ {result.Message}" : $"❌ {result.Message}");
            if (!result.Success && !string.IsNullOrEmpty(result.Details))
                Console.WriteLine(result.Details);
        }, pullPathOption);

        // Add push command
        var pushCommand = new Command("push", "Perform git push with LLM-powered conflict resolution");
        var pushPathOption = new Option<string>("--path", () => ".", "Repository path");
        pushCommand.AddOption(pushPathOption);
        pushCommand.SetHandler(async (string path) =>
        {
            var gitService = host.Services.GetRequiredService<IGitOperationsService>();
            var result = await gitService.PushAsync(path);
            Console.WriteLine(result.Success ? $"✅ {result.Message}" : $"❌ {result.Message}");
            if (!result.Success && !string.IsNullOrEmpty(result.Details))
                Console.WriteLine(result.Details);
        }, pushPathOption);

        // Add status command
        var statusCommand = new Command("status", "Show detailed repository status");
        var statusPathOption = new Option<string>("--path", () => ".", "Repository path");
        statusCommand.AddOption(statusPathOption);
        statusCommand.SetHandler(async (string path) =>
        {
            var gitService = host.Services.GetRequiredService<IGitOperationsService>();
            var status = await gitService.GetStatusAsync(path);
            
            Console.WriteLine($"📊 Repository Status: {Path.GetFullPath(path)}");
            Console.WriteLine($"Clean: {(status.IsClean ? "✅" : "❌")}");
            Console.WriteLine($"Staged files: {status.StagedFiles.Count}");
            Console.WriteLine($"Modified files: {status.ModifiedFiles.Count}");
            Console.WriteLine($"Untracked files: {status.UntrackedFiles.Count}");
            Console.WriteLine($"Conflicts: {status.ConflictedFiles.Count}");
            
            if (status.ConflictedFiles.Any())
            {
                Console.WriteLine("\n🚨 Conflicted files:");
                foreach (var file in status.ConflictedFiles)
                    Console.WriteLine($"  - {file}");
            }
        }, statusPathOption);

        // Add commands to root
        rootCommand.AddCommand(pullCommand);
        rootCommand.AddCommand(pushCommand);
        rootCommand.AddCommand(statusCommand);

        // Execute command
        return await rootCommand.InvokeAsync(args);
    }
}