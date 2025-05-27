using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

public class CronScheduler : IAsyncDisposable
{
    private readonly List<ScheduledJob> _jobs = new();
    private readonly CancellationTokenSource _cts = new();
    private readonly TimeSpan _pollInterval;
    private Task? _workerTask;
    private readonly object _lock = new();

    public CronScheduler(TimeSpan? pollInterval = null)
    {
        _pollInterval = pollInterval ?? TimeSpan.FromSeconds(10);
    }

    public void AddJob(string cronExpression, IScheduledTask taskInstance)
    {
        lock (_lock)
        {
            _jobs.Add(new ScheduledJob(cronExpression, taskInstance));
        }
    }

    public void Start()
    {
        if (_workerTask != null)
            throw new InvalidOperationException("Scheduler already started.");

        _workerTask = Task.Run(WorkerAsync);
    }

    private async Task WorkerAsync()
    {
        while (!_cts.Token.IsCancellationRequested)
        {
            var now = DateTime.UtcNow;
            List<ScheduledJob> dueJobs = new();

            lock (_lock)
            {
                foreach (var job in _jobs)
                {
                    if (job.NextRun <= now)
                    {
                        dueJobs.Add(job);
                        job.NextRun = job.Schedule.GetNextOccurrence(now);
                    }
                }
            }

            var tasks = new List<Task>();
            foreach (var job in dueJobs)
            {
                tasks.Add(Task.Run(() => job.TaskInstance.ExecuteAsync(_cts.Token), _cts.Token));
            }

            await Task.WhenAll(tasks);

            await Task.Delay(_pollInterval, _cts.Token);
        }
    }

    public async ValueTask DisposeAsync()
    {
        _cts.Cancel();
        if (_workerTask != null)
        {
            await _workerTask;
        }
        _cts.Dispose();
    }
}