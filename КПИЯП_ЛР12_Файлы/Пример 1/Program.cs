using System;

namespace Test_Structures
{
    struct Point
    {
        public int X;
        public int Y;

        public Point(int x, int y)
        {
            X = x;
            Y = y;
        }

        public void Display()
        {
            Console.WriteLine($"Точка: ({X}, {Y})");
        }

        public double DistanceTo(Point other)
        {
            return Math.Sqrt(Math.Pow(X - other.X, 2) + Math.Pow(Y - other.Y, 2));
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Point point1 = new Point(10, 20);
            Point point2 = new Point(30, 40);

            point1.Display();
            point2.Display();

            Console.WriteLine($"Расстояние между точками: {point1.DistanceTo(point2):F2}");

            Point point3 = point1;
            point3.X = 50;
            Console.WriteLine("После изменения копии:");
            point1.Display();
            point3.Display();

            Console.Write("Press any key to continue... ");
            Console.ReadKey(true);
        }
    }
}
