using System;
using System.Threading.Tasks;

// NuGet: NCrontab.Signed

class Program
{
    static async Task Main(string[] args)
    {
        await using var scheduler = new CronScheduler();

        // 매 분 5초마다 실행
        scheduler.AddJob("*/1 * * * *", new PrintMessageTask("첫 번째 작업 실행!"));

        // 매 2분마다 실행
        scheduler.AddJob("*/2 * * * *", new PrintMessageTask("두 번째 작업 실행!"));

        scheduler.Start();

        Console.WriteLine("스케쥴러가 실행 중입니다. 종료하려면 Enter를 누르세요.");
        Console.ReadLine();
    }
}