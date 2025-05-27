using System;
using System.Threading;
using System.Threading.Tasks;

public class PrintMessageTask : IScheduledTask
{
    private readonly string _message;

    public PrintMessageTask(string message)
    {
        _message = message;
    }

    public Task ExecuteAsync(CancellationToken cancellationToken)
    {
        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] {_message}");
        return Task.CompletedTask;
    }
}