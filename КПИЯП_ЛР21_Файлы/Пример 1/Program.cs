using System;
using System.Text.Json;
using System.IO;
using System.Threading.Tasks;

public class Person
{
    public string Name { get; set; }
    public int Age { get; set; }
    public string Email { get; set; }
}

class Program
{
    static void Main()
    {
        // Создание объекта
        var person = new Person
        {
            Name = "Иван Иванов",
            Age = 30,
            Email = "ivan@example.com"
        };

        // Сериализация в JSON
        string jsonString = JsonSerializer.Serialize(person,
            new JsonSerializerOptions { WriteIndented = true });

        Console.WriteLine("Сериализованный JSON:");

        Console.WriteLine(jsonString);

        // Десериализация из JSON
        Person deserializedPerson = JsonSerializer.Deserialize<Person>(jsonString);

        Console.WriteLine($"\nДесериализованный объект:");
        Console.WriteLine($"Имя: {deserializedPerson.Name}");
        Console.WriteLine($"Возраст: {deserializedPerson.Age}");
        Console.WriteLine($"Email: {deserializedPerson.Email}");
    }
}
