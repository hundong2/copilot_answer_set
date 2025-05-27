using System.Threading;
using System.Threading.Tasks;

public interface IScheduledTask
{
    Task ExecuteAsync(CancellationToken cancellationToken);
}