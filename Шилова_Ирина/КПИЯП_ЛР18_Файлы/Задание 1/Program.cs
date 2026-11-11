using System;

namespace LR18Zad1
{
    public delegate int NumberDelegate(int min, int max);

    // Данные события «изменился диапазон»
    public class RangeChangedEventArgs : EventArgs
    {
        public bool HasOld { get; set; }
        public int OldMin { get; set; }
        public int OldMax { get; set; }
        public int NewMin { get; set; }
        public int NewMax { get; set; }
    }

    // Данные события «получено новое число»
    public class NumberGeneratedEventArgs : EventArgs
    {
        public string Method { get; set; }
        public int Value { get; set; }
        public bool HasPrevious { get; set; }
        public int Previous { get; set; }
    }

    public class NumberGenerator
    {
        private Random rnd = new Random();
        private int min;
        private int max;
        private bool hasRange = false;
        private NumberDelegate method;
        private string methodName = "";
        private int last;
        private bool hasLast = false;

        public event EventHandler<RangeChangedEventArgs>
            RangeChanged;
        public event EventHandler MethodChanged;
        public event EventHandler<NumberGeneratedEventArgs>
            NumberGenerated;

        public string MethodName => methodName;

        // Новый диапазон; событие — только если он изменился
        public void SetRange(int newMin, int newMax)
        {
            if (newMin > newMax)
            {
                int temp = newMin;
                newMin = newMax;
                newMax = temp;
            }
            if (hasRange && newMin == min && newMax == max)
            {
                return;
            }
            RangeChangedEventArgs e = new RangeChangedEventArgs();
            e.HasOld = hasRange;
            e.OldMin = min;
            e.OldMax = max;
            e.NewMin = newMin;
            e.NewMax = newMax;
            min = newMin;
            max = newMax;
            hasRange = true;
            OnRangeChanged(e);
        }

        // Выбор метода генерации; событие — при смене метода
        public void SetMethod(NumberDelegate newMethod,
            string name)
        {
            if (name == methodName)
            {
                return;
            }
            method = newMethod;
            methodName = name;
            OnMethodChanged(EventArgs.Empty);
        }

        public int Generate()
        {
            NumberGeneratedEventArgs e =
                new NumberGeneratedEventArgs();
            e.Method = methodName;
            e.Value = method(min, max);
            e.HasPrevious = hasLast;
            e.Previous = last;
            last = e.Value;
            hasLast = true;
            OnNumberGenerated(e);
            return e.Value;
        }

        protected virtual void OnRangeChanged(
            RangeChangedEventArgs e)
        {
            RangeChanged?.Invoke(this, e);
        }

        protected virtual void OnMethodChanged(EventArgs e)
        {
            MethodChanged?.Invoke(this, e);
        }

        protected virtual void OnNumberGenerated(
            NumberGeneratedEventArgs e)
        {
            NumberGenerated?.Invoke(this, e);
        }

        // методы генерации из лабораторной работы №16
        public int RandomInRange(int min, int max)
        {
            return rnd.Next(min, max + 1);
        }

        public int EvenNumber(int min, int max)
        {
            for (int i = 0; i < 1000; i++)
            {
                int n = rnd.Next(min, max + 1);
                if (n % 2 == 0) return n;
            }
            return min % 2 == 0 ? min : min + 1;
        }

        public int OddNumber(int min, int max)
        {
            for (int i = 0; i < 1000; i++)
            {
                int n = rnd.Next(min, max + 1);
                if (n % 2 != 0) return n;
            }
            return min % 2 != 0 ? min : min + 1;
        }
    }

    // Второй подписчик: считает полученные числа
    public class Statistics
    {
        private int count;
        private int sum;

        public void Subscribe(NumberGenerator gen)
        {
            gen.NumberGenerated += OnNumberGenerated;
        }

        private void OnNumberGenerated(object sender,
            NumberGeneratedEventArgs e)
        {
            count++;
            sum += e.Value;
            Console.WriteLine($"  [Статистика] чисел: {count}, "
                + $"сумма: {sum}");
        }
    }

    class Program
    {
        static void Main()
        {
            Console.OutputEncoding = System.Text.Encoding.UTF8;
            NumberGenerator gen = new NumberGenerator();
            // подписка обработчиков на события генератора
            gen.RangeChanged += Gen_RangeChanged;
            gen.MethodChanged += Gen_MethodChanged;
            gen.NumberGenerated += Gen_NumberGenerated;
            Statistics stat = new Statistics();
            stat.Subscribe(gen);

            ReadRange(gen);
            while (true)
            {
                Console.WriteLine();
                Console.WriteLine("1 - случайное, 2 - чётное, "
                    + "3 - нечётное, 4 - диапазон, 0 - выход");
                Console.Write("Выбор: ");
                string choice = Console.ReadLine();
                if (choice == "0") break;
                if (choice == "4")
                {
                    ReadRange(gen);
                    continue;
                }
                if (choice == "1")
                    gen.SetMethod(gen.RandomInRange, "случайное");
                else if (choice == "2")
                    gen.SetMethod(gen.EvenNumber, "чётное");
                else if (choice == "3")
                    gen.SetMethod(gen.OddNumber, "нечётное");
                else
                {
                    Console.WriteLine("Нет такого пункта");
                    continue;
                }
                Console.WriteLine("Результат: " + gen.Generate());
            }
        }

        static void ReadRange(NumberGenerator gen)
        {
            int min = ReadInt("Минимум: ");
            int max = ReadInt("Максимум: ");
            gen.SetRange(min, max);
        }

        static void Gen_RangeChanged(object sender,
            RangeChangedEventArgs e)
        {
            string range = $"[{e.NewMin}; {e.NewMax}]";
            if (e.HasOld)
                Console.WriteLine("  [Событие] Диапазон изменён: "
                    + $"[{e.OldMin}; {e.OldMax}] -> {range}");
            else
                Console.WriteLine("  [Событие] Диапазон задан: "
                    + range);
        }

        static void Gen_MethodChanged(object sender, EventArgs e)
        {
            NumberGenerator gen = (NumberGenerator)sender;
            Console.WriteLine("  [Событие] Метод генерации: "
                + gen.MethodName);
        }

        static void Gen_NumberGenerated(object sender,
            NumberGeneratedEventArgs e)
        {
            string prev = e.HasPrevious
                ? e.Previous.ToString() : "нет";
            Console.WriteLine("  [Событие] Новое число "
                + $"{e.Value} ({e.Method}), предыдущее: {prev}");
        }

        static int ReadInt(string text)
        {
            Console.Write(text);
            int value;
            while (!int.TryParse(Console.ReadLine(), out value))
            {
                Console.Write("Ещё раз: ");
            }
            return value;
        }
    }
}
