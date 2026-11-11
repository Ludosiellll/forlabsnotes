using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Unicode;
using System.Threading.Tasks;

public class Review
{
    public string Product { get; set; }
    public string Author { get; set; }
    public string Text { get; set; }
    public int Rating { get; set; }
}

class Program
{
    // одни настройки для записи и чтения
    static JsonSerializerOptions options =
        new JsonSerializerOptions
        {
            WriteIndented = true,
            Encoder = JavaScriptEncoder.Create(UnicodeRanges.All)
        };

    static async Task SaveToJson(string path, List<Review> list)
    {
        using (FileStream stream = File.Create(path))
        {
            await JsonSerializer.SerializeAsync(stream, list,
                options);
        }
    }

    static async Task<List<Review>> LoadFromJson(string path)
    {
        using (FileStream stream = File.OpenRead(path))
        {
            return await JsonSerializer
                .DeserializeAsync<List<Review>>(stream, options);
        }
    }

    static Review Make(string product, string author,
        string text, int rating)
    {
        return new Review { Product = product, Author = author,
            Text = text, Rating = rating };
    }

    static async Task Main()
    {
        List<Review> reviews = new List<Review>
        {
            Make("Ноутбук", "Анна",
                "Быстрый, батарея держит весь день", 5),
            Make("Ноутбук", "Пётр", "Шумит под нагрузкой", 3),
            Make("Мышь", "Мария", "Удобная, отклик точный", 4),
            Make("Мышь", "Иван",
                "Через месяц стёрлась краска", 2),
            Make("Клавиатура", "Ольга",
                "Тихая, приятно печатать", 5)
        };

        string path = "reviews.json";
        await SaveToJson(path, reviews);
        Console.WriteLine("Отзывы записаны в файл " + path);

        List<Review> loaded = await LoadFromJson(path);
        Console.WriteLine("Прочитано отзывов из файла: "
            + loaded.Count);
        Console.WriteLine();

        int sum = 0;
        foreach (Review r in loaded)
        {
            Console.WriteLine(r.Product + " | " + r.Author + " | "
                + r.Rating + " | " + r.Text);
            sum += r.Rating;
        }

        double average = (double)sum / loaded.Count;
        Console.WriteLine();
        Console.WriteLine("Средний рейтинг: "
            + average.ToString("F2"));
    }
}
