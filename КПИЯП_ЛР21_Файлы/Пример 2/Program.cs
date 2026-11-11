using System;
using System.Text.Json;
using System.IO;
using System.Threading.Tasks;

public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
    public DateTime CreatedDate { get; set; }
}

class Program
{
    static async Task Main()
    {
        string filePath = "products.json";
        var product = new Product
        {
            Id = 1,
            Name = "Ноутбук",
            Price = 50000.50m,
            CreatedDate = DateTime.Now
        };

        // Запись в файл
        await WriteToJsonFile(filePath, product);
        Console.WriteLine("Данные записаны в файл");

        // Чтение из файла
        Product readProduct = await ReadFromJsonFile<Product>(filePath);
        Console.WriteLine($"Прочитанный продукт: {readProduct.Name}, Цена: {readProduct.Price}");
    }

    static async Task WriteToJsonFile<T>(string filePath, T data)
    {
        var options = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        using FileStream createStream = File.Create(filePath);
        await JsonSerializer.SerializeAsync(createStream, data, options);
        await createStream.DisposeAsync();
    }

    static async Task<T> ReadFromJsonFile<T>(string filePath)
    {
        // имена в файле записаны в camelCase — при чтении нужна та же политика имён
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        using FileStream openStream = File.OpenRead(filePath);
        return await JsonSerializer.DeserializeAsync<T>(openStream, options);
    }
}
