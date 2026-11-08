import os

base_dir = r"d:\1с лабы\КПИЯП_ЛР12_Файлы"

csproj_template = """<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>disable</ImplicitUsings>
    <Nullable>disable</Nullable>
  </PropertyGroup>

</Project>
"""

p1_code = """using System;

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
"""

p2_code = """using System;

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
            Console.WriteLine($"\\nСтатус заказа: {status}");

            status = OrderStatus.Shipped;
            Console.WriteLine($"Новый статус заказа: {status}");

            Console.WriteLine("\\nВсе статусы заказов:");
            foreach (OrderStatus s in Enum.GetValues(typeof(OrderStatus)))
            {
                Console.WriteLine($"- {s} ({(int)s})");
            }

            Console.Write("Press any key to continue... ");
            Console.ReadKey(true);
        }
    }
}
"""

p3_code = """using System;

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

            Console.WriteLine("Информация о сотрудниках:\\n");
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
"""

indiv_code = """using System;

namespace Lab12
{
    enum DishType
    {
        Soup,
        MainDish,
        Salad,
        Dessert,
        Drink
    }

    struct Recipe
    {
        public string Name;
        public int CookingTime;
        public string Difficulty;
        public DishType Type;
        public double Proteins;
        public double Fats;
        public double Carbs;

        public Recipe(string name, int cookingTime, string difficulty, DishType type, double proteins, double fats, double carbs)
        {
            Name = name;
            CookingTime = cookingTime;
            Difficulty = difficulty;
            Type = type;
            Proteins = proteins;
            Fats = fats;
            Carbs = carbs;
        }

        public double GetCalories()
        {
            return Proteins * 4 + Fats * 9 + Carbs * 4;
        }

        public void Display()
        {
            Console.WriteLine("Рецепт: " + Name);
            Console.WriteLine("Тип блюда: " + Type);
            Console.WriteLine("Время приготовления: " + CookingTime + " мин.");
            Console.WriteLine("Сложность: " + Difficulty);
            Console.WriteLine("Белки: " + Proteins + " г, Жиры: " + Fats + " г, Углеводы: " + Carbs + " г");
            Console.WriteLine("Калорийность: " + GetCalories() + " ккал");
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Recipe[] book = new Recipe[]
            {
                new Recipe("Борщ украинский", 60, "Средняя", DishType.Soup, 8, 5, 12),
                new Recipe("Плов с говядиной", 50, "Средняя", DishType.MainDish, 14, 12, 35),
                new Recipe("Греческий салат", 15, "Легкая", DishType.Salad, 3, 10, 5)
            };

            Console.WriteLine("Список рецептов:");
            for (int i = 0; i < book.Length; i++)
            {
                book[i].Display();
                Console.WriteLine();
            }

            Console.WriteLine("Добавление рецепта с клавиатуры:");
            Console.Write("Название блюда: ");
            string name = Console.ReadLine();

            Console.Write("Время приготовления (минут): ");
            int time;
            while (!int.TryParse(Console.ReadLine(), out time))
            {
                Console.Write("Введите число: ");
            }

            Console.Write("Сложность (Легкая, Средняя, Сложная): ");
            string diff = Console.ReadLine();

            Console.WriteLine("Выберите тип блюда (1 - Суп, 2 - Второе, 3 - Салат, 4 - Десерт, 5 - Напиток): ");
            int typeNum;
            while (!int.TryParse(Console.ReadLine(), out typeNum) || typeNum < 1 || typeNum > 5)
            {
                Console.Write("Введите число от 1 до 5: ");
            }
            DishType selectedType = (DishType)(typeNum - 1);

            Console.Write("Белки (г): ");
            double prot;
            while (!double.TryParse(Console.ReadLine(), out prot))
            {
                Console.Write("Введите число: ");
            }

            Console.Write("Жиры (г): ");
            double fats;
            while (!double.TryParse(Console.ReadLine(), out fats))
            {
                Console.Write("Введите число: ");
            }

            Console.Write("Углеводы (г): ");
            double carbs;
            while (!double.TryParse(Console.ReadLine(), out carbs))
            {
                Console.Write("Введите число: ");
            }

            Recipe userRecipe = new Recipe(name, time, diff, selectedType, prot, fats, carbs);

            Console.WriteLine();
            Console.WriteLine("Добавленный рецепт:");
            userRecipe.Display();

            if (!Console.IsInputRedirected)
            {
                Console.Write("\\nPress any key to continue... ");
                Console.ReadKey(true);
            }
        }
    }
}
"""

projects = [
    ("Пример 1", p1_code),
    ("Пример 2", p2_code),
    ("Пример 3", p3_code),
    ("Индивидуальное задание", indiv_code)
]

for folder_name, code in projects:
    p = os.path.join(base_dir, folder_name)
    os.makedirs(p, exist_ok=True)
    csproj_path = os.path.join(p, folder_name.replace(" ", "_") + ".csproj")
    with open(csproj_path, "w", encoding="utf-8") as f:
        f.write(csproj_template)
    prog_path = os.path.join(p, "Program.cs")
    with open(prog_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Project created: {folder_name}")

print("All LR12 projects created.")
