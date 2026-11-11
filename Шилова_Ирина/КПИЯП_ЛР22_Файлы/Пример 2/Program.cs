using System;
using System.IO;
using System.Text.Json;
public class Person
{
    public string Name { get; set; }
    public int Age { get; set; }
}
class Program
{
    static void Main()
    {
        try
        {
            string jsonString = @"{
                ""Name"": ""Иван Иванов"",
                ""Age"": 25
            }";
            // Десериализация из строки
            Person person = JsonSerializer.Deserialize<Person>(jsonString);
            Console.WriteLine($"Имя: {person.Name}, Возраст: {person.Age}");
            // Чтение из файла
            if (File.Exists("person.json"))
            {
                string fileContent = File.ReadAllText("person.json");
                Person filePerson = JsonSerializer.Deserialize<Person>(fileContent);
                Console.WriteLine($"Из файла: {filePerson.Name}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Ошибка: {ex.Message}");
        }
    }
}
