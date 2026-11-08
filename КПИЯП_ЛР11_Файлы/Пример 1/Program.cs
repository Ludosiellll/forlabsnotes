using System;

namespace Test_Composition
{
    class Engine
    {
        public double Power { get; set; }
        public string Type { get; set; }

        public Engine(double power, string type)
        {
            Power = power;
            Type = type;
        }

        public void Start()
        {
            Console.WriteLine($"Двигатель {Type} мощностью {Power} л.с. запущен");
        }
    }

    class Wheel
    {
        public double Diameter { get; set; }
        public string Season { get; set; }

        public Wheel(double diameter, string season)
        {
            Diameter = diameter;
            Season = season;
        }

        public void Rotate()
        {
            Console.WriteLine($"Колесо диаметром {Diameter} вращается");
        }
    }

    class Car
    {
        public string Brand { get; set; }
        public Engine Engine { get; set; }
        public Wheel[] Wheels { get; set; }

        public Car(string brand, Engine engine, Wheel[] wheels)
        {
            Brand = brand;
            Engine = engine;
            Wheels = wheels;
        }

        public void Drive()
        {
            Engine.Start();
            foreach (var wheel in Wheels)
            {
                wheel.Rotate();
            }
            Console.WriteLine($"Автомобиль {Brand} поехал");
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Engine engine = new Engine(150, "Бензиновый");
            Wheel[] wheels = {
                new Wheel(16, "Летние"),
                new Wheel(16, "Летние"),
                new Wheel(16, "Летние"),
                new Wheel(16, "Летние")
            };

            Car car = new Car("Toyota", engine, wheels);
            car.Drive();

            Console.Write("Press any key to continue... ");
            Console.ReadKey(true);
        }
    }
}
