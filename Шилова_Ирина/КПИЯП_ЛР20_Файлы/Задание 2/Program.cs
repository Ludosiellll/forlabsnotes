using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;

struct Guest
{
    public string Surname;
    public string Name;
    public string Passport;
    public DateTime Arrival;
    public DateTime Departure;
    public int Room;
    public string Placement;

    public string ToLine()
    {
        return Surname + ";" + Name + ";" + Passport + ";"
            + Arrival.ToString("dd.MM.yyyy") + ";"
            + Departure.ToString("dd.MM.yyyy") + ";"
            + Room + ";" + Placement;
    }

    public string ToRow()
    {
        return string.Format(
            "{0,-10} {1,-8} {2,-10} {3,-10} {4,-10} {5,5}  {6}",
            Surname, Name, Passport,
            Arrival.ToString("dd.MM.yyyy"),
            Departure.ToString("dd.MM.yyyy"), Room, Placement);
    }
}

class Program
{
    static List<Guest> guests = new List<Guest>();
    static string[] placements = { "люкс", "одноместный",
        "двухместный", "трехместный", "апартаменты" };

    static DateTime ParseDate(string text)
    {
        return DateTime.ParseExact(text.Trim(), "dd.MM.yyyy",
            CultureInfo.InvariantCulture);
    }

    static bool IsPlacement(string text)
    {
        foreach (string p in placements)
        {
            if (p == text)
            {
                return true;
            }
        }
        return false;
    }

    static void LoadFromFile(string path)
    {
        if (!File.Exists(path))
        {
            Console.WriteLine("Файл " + path + " не найден");
            return;
        }
        int added = 0;
        using (StreamReader reader = new StreamReader(path))
        {
            string line;
            while ((line = reader.ReadLine()) != null)
            {
                string[] parts = line.Split(';');
                if (parts.Length != 7)
                {
                    continue;
                }
                Guest g = new Guest();
                g.Surname = parts[0];
                g.Name = parts[1];
                g.Passport = parts[2];
                g.Arrival = ParseDate(parts[3]);
                g.Departure = ParseDate(parts[4]);
                g.Room = int.Parse(parts[5]);
                g.Placement = parts[6];
                guests.Add(g);
                added++;
            }
        }
        Console.WriteLine("Загружено записей: " + added);
    }

    static void InputFromKeyboard()
    {
        Guest g = new Guest();
        Console.Write("Фамилия: ");
        g.Surname = Console.ReadLine().Trim();
        Console.Write("Имя: ");
        g.Name = Console.ReadLine().Trim();
        Console.Write("Паспорт: ");
        g.Passport = Console.ReadLine().Trim();
        try
        {
            Console.Write("Дата приезда (дд.мм.гггг): ");
            g.Arrival = ParseDate(Console.ReadLine());
            Console.Write("Дата отъезда (дд.мм.гггг): ");
            g.Departure = ParseDate(Console.ReadLine());
            Console.Write("Номер комнаты: ");
            g.Room = int.Parse(Console.ReadLine());
        }
        catch (FormatException)
        {
            Console.WriteLine("Неверный формат данных");
            return;
        }
        if (g.Departure < g.Arrival)
        {
            Console.WriteLine("Отъезд раньше приезда");
            return;
        }
        Console.Write("Тип размещения ("
            + string.Join(", ", placements) + "): ");
        g.Placement = Console.ReadLine().Trim().ToLower();
        if (!IsPlacement(g.Placement))
        {
            Console.WriteLine("Нет такого типа размещения");
            return;
        }
        guests.Add(g);
        Console.WriteLine("Гость добавлен");
    }

    static void PrintHeader()
    {
        Console.WriteLine(string.Format(
            "{0,-3} {1,-10} {2,-8} {3,-10} {4,-10} {5,-10} "
            + "{6,5}  {7}",
            "№", "Фамилия", "Имя", "Паспорт", "Приезд", "Отъезд",
            "Номер", "Размещение"));
    }

    static void PrintGuest(int i)
    {
        Console.WriteLine(string.Format("{0,-3} ", i + 1)
            + guests[i].ToRow());
    }

    static void PrintAll()
    {
        if (guests.Count == 0)
        {
            Console.WriteLine("Список гостей пуст");
            return;
        }
        PrintHeader();
        for (int i = 0; i < guests.Count; i++)
        {
            PrintGuest(i);
        }
    }

    static void FindBySurname()
    {
        Console.Write("Введите фамилию: ");
        string surname = Console.ReadLine().Trim().ToLower();
        bool found = false;
        for (int i = 0; i < guests.Count; i++)
        {
            if (guests[i].Surname.ToLower() == surname)
            {
                if (!found)
                {
                    PrintHeader();
                    found = true;
                }
                PrintGuest(i);
            }
        }
        if (!found)
        {
            Console.WriteLine("Гость с такой фамилией не найден");
        }
    }

    static void DeleteGuest()
    {
        Console.Write("Номер записи для удаления: ");
        int n;
        if (!int.TryParse(Console.ReadLine(), out n)
            || n < 1 || n > guests.Count)
        {
            Console.WriteLine("Записи с таким номером нет");
            return;
        }
        Console.WriteLine("Удалён гость: " + guests[n - 1].Surname
            + " " + guests[n - 1].Name);
        guests.RemoveAt(n - 1);
    }

    static void SaveToFile(string path)
    {
        using (StreamWriter writer = new StreamWriter(path))
        {
            foreach (Guest g in guests)
            {
                writer.WriteLine(g.ToLine());
            }
        }
        Console.WriteLine("Сохранено в файл " + path + ": "
            + guests.Count);
    }

    static void Main(string[] args)
    {
        Console.WriteLine("1 - загрузить гостей из файла");
        Console.WriteLine("2 - добавить гостя с клавиатуры");
        Console.WriteLine("3 - показать всех гостей");
        Console.WriteLine("4 - найти гостя по фамилии");
        Console.WriteLine("5 - удалить гостя");
        Console.WriteLine("6 - сохранить список в файл");
        Console.WriteLine("0 - выход");
        while (true)
        {
            Console.WriteLine();
            Console.Write("Выберите пункт: ");
            string choice = Console.ReadLine();
            if (choice == null || choice.Trim() == "0")
            {
                break;
            }
            switch (choice.Trim())
            {
                case "1":
                    LoadFromFile("guests.txt");
                    break;
                case "2":
                    InputFromKeyboard();
                    break;
                case "3":
                    PrintAll();
                    break;
                case "4":
                    FindBySurname();
                    break;
                case "5":
                    DeleteGuest();
                    break;
                case "6":
                    SaveToFile("guests_out.txt");
                    break;
                default:
                    Console.WriteLine("Нет такого пункта меню");
                    break;
            }
        }
    }
}
