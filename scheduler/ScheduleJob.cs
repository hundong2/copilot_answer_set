using System;
using NCrontab;

public class ScheduledJob
{
    public CrontabSchedule Schedule { get; }
    public IScheduledTask TaskInstance { get; }
    public string CronExpression { get; }
    public DateTime NextRun { get; set; }

    public ScheduledJob(string cronExpression, IScheduledTask taskInstance)
    {
        CronExpression = cronExpression;
        Schedule = CrontabSchedule.Parse(cronExpression);
        TaskInstance = taskInstance;
        NextRun = Schedule.GetNextOccurrence(DateTime.UtcNow);
    }
}