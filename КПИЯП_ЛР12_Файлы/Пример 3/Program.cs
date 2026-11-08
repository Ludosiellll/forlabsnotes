using System;

namespace Test_StructEnum
{
    enum Position
    {
        Manager,
        Developer,
        Designer,
        Tester,
        Analyst
    }

    enum Department
    {
        IT,
        HR,
        Finance,
        Marketing,
        Sales
    }

    struct Employee
    {
        public string Name;
        public Position Position;
        public Department Department;
        public decimal Salary;
        public DateTime HireDate;

        public Employee(string name, Position position, Department department, decimal salary, DateTime hireDate)
        {
            Name = name;
            Position = position;
            Department = department;
            Salary = salary;
            HireDate = hireDate;
        }

        public void DisplayInfo()
        {
            Console.WriteLine($"Сотрудник: {Name}");
            Console.WriteLine($"Должность: {Position}");
            Console.WriteLine($"Отдел: {Department}");
            Console.WriteLine($"Зарплата: {Salary:C}");
            Console.WriteLine($"Дата приема: {HireDate:dd.MM.yyyy}");
            Console.WriteLine($"Стаж: {GetExperience()} лет");
            Console.WriteLine();
        }

        public int GetExperience()
        {
            return DateTime.Now.Year - HireDate.Year;
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Employee[] employees = new Employee[]
            {
                new Employee("Иван Иванов", Position.Manager, Department.Sales, 50000, new DateTime(2020, 5, 15)),
                new Employee("Петр Петров", Position.Developer, Department.IT, 80000, new DateTime(2019, 3, 10)),
                new Employee("Мария Сидорова", Position.Designer, Department.Marketing, 60000, new DateTime(2021, 8, 22))
            };

            Console.WriteLine("Информация о сотрудниках:\n");
            foreach (var employee in employees)
            {
                employee.DisplayInfo();
            }

            Console.WriteLine("Разработчики:");
            foreach (var employee in employees)
            {
                if (employee.Position == Position.Developer)
                {
                    Console.WriteLine($"- {employee.Name}");
                }
            }

            Console.Write("Press any key to continue... ");
            Console.ReadKey(true);
        }
    }
}
