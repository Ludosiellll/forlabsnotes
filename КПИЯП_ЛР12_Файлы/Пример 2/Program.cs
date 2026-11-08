using System;

namespace Test_Enums
{
    enum DayOfWeek
    {
        Monday = 1,
        Tuesday,
        Wednesday,
        Thursday,
        Friday,
        Saturday,
        Sunday
    }

    enum OrderStatus
    {
        New,
        Processing,
        Shipped,
        Delivered,
        Cancelled
    }

    class Program
    {
        static void Main(string[] args)
        {
            DayOfWeek today = DayOfWeek.Wednesday;
            Console.WriteLine($"Сегодня: {today} ({(int)today})");

            if (today == DayOfWeek.Saturday || today == DayOfWeek.Sunday)
            {
                Console.WriteLine("Выходной день!");
            }
            else
            {
                Console.WriteLine("Рабочий день");
            }

            OrderStatus status = OrderStatus.Processing;
            Console.WriteLine($"\nСтатус заказа: {status}");

            status = OrderStatus.Shipped;
            Console.WriteLine($"Новый статус заказа: {status}");

            Console.WriteLine("\nВсе статусы заказов:");
            foreach (OrderStatus s in Enum.GetValues(typeof(OrderStatus)))
            {
                Console.WriteLine($"- {s} ({(int)s})");
            }

            Console.Write("Press any key to continue... ");
            Console.ReadKey(true);
        }
    }
}
