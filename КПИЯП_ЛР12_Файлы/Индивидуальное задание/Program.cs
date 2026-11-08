using System;

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
                Console.Write("\nPress any key to continue... ");
                Console.ReadKey(true);
            }
        }
    }
}
