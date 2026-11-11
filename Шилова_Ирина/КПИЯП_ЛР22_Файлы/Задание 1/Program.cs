using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

public class Review
{
    public string Product { get; set; }
    public string Author { get; set; }
    public string Text { get; set; }
    public int Rating { get; set; }
}

class Program
{
    static List<Review> ReadReviews(string path)
    {
        if (!File.Exists(path))
        {
            throw new FileNotFoundException("Нет файла", path);
        }
        string json = File.ReadAllText(path);
        List<Review> reviews =
            JsonSerializer.Deserialize<List<Review>>(json);
        if (reviews == null || reviews.Count == 0)
        {
            throw new InvalidDataException(
                "в файле нет ни одного отзыва");
        }
        return reviews;
    }

    static bool IsValid(Review r)
    {
        return r.Rating >= 1 && r.Rating <= 5;
    }

    static void PrintReport(List<Review> reviews)
    {
        Console.WriteLine("Отзывы из файла:");
        int sum = 0;
        int valid = 0;
        Review best = null;
        Review worst = null;
        List<string> products = new List<string>();
        foreach (Review r in reviews)
        {
            if (!IsValid(r))
            {
                Console.WriteLine("  пропущен отзыв " + r.Author
                    + ": рейтинг " + r.Rating + " вне 1-5");
                continue;
            }
            Console.WriteLine("  " + r.Product + " | " + r.Author
                + " | " + r.Rating + " | " + r.Text);
            sum += r.Rating;
            valid++;
            if (best == null || r.Rating > best.Rating)
            {
                best = r;
            }
            if (worst == null || r.Rating < worst.Rating)
            {
                worst = r;
            }
            if (!products.Contains(r.Product))
            {
                products.Add(r.Product);
            }
        }
        if (valid == 0)
        {
            Console.WriteLine("Нет отзывов с рейтингом 1-5");
            return;
        }

        Console.WriteLine();
        Console.WriteLine("Средний рейтинг по товарам:");
        foreach (string product in products)
        {
            int productSum = 0;
            int count = 0;
            foreach (Review r in reviews)
            {
                if (r.Product == product && IsValid(r))
                {
                    productSum += r.Rating;
                    count++;
                }
            }
            double avg = (double)productSum / count;
            Console.WriteLine("  " + product + ": "
                + avg.ToString("F2"));
        }

        Console.WriteLine();
        Console.WriteLine("Общий средний рейтинг: "
            + ((double)sum / valid).ToString("F2"));
        Console.WriteLine("Лучший отзыв: " + best.Product + ", "
            + best.Author + " (" + best.Rating + ")");
        Console.WriteLine("Худший отзыв: " + worst.Product + ", "
            + worst.Author + " (" + worst.Rating + ")");
    }

    static void Main()
    {
        Console.Write("Имя JSON-файла (Enter - reviews.json): ");
        string path = Console.ReadLine();
        if (string.IsNullOrWhiteSpace(path))
        {
            path = "reviews.json";
        }
        path = path.Trim();

        try
        {
            PrintReport(ReadReviews(path));
        }
        catch (FileNotFoundException)
        {
            Console.WriteLine("Ошибка: нет файла " + path);
        }
        catch (JsonException ex)
        {
            Console.WriteLine("Ошибка: в файле " + path
                + " неверный JSON (" + ex.Message + ")");
        }
        catch (InvalidDataException ex)
        {
            Console.WriteLine("Ошибка: " + ex.Message);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Другая ошибка: " + ex.Message);
        }
    }
}
