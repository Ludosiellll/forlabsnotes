using System;
using System.Collections.Generic;
using System.Text.Json;
using System.IO;
using System.Threading.Tasks;

public class Student
{
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public List<int> Grades { get; set; } = new List<int>();
}

class Program
{
    static async Task Main()
    {
        var students = new List<Student>
        {
            new Student { FirstName = "Анна", LastName = "Петрова", Grades = new List<int> { 5, 4, 5 } },
            new Student { FirstName = "Петр", LastName = "Сидоров", Grades = new List<int> { 3, 4, 5 } },
            new Student { FirstName = "Мария", LastName = "Иванова", Grades = new List<int> { 5, 5, 5 } }
        };

        string filePath = "students.json";

        // Запись коллекции в файл
        await SaveCollectionToJson(filePath, students);
        Console.WriteLine("Коллекция записана в файл");

        // Чтение коллекции из файла
        List<Student> loadedStudents = await LoadCollectionFromJson<List<Student>>(filePath);
        Console.WriteLine($"Загружено {loadedStudents.Count} студентов");
    }

    static async Task SaveCollectionToJson<T>(string filePath, T collection)
    {
        var options = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        string jsonString = JsonSerializer.Serialize(collection, options);
        await File.WriteAllTextAsync(filePath, jsonString);
    }

    static async Task<T> LoadCollectionFromJson<T>(string filePath)
    {
        string jsonString = await File.ReadAllTextAsync(filePath);
        return JsonSerializer.Deserialize<T>(jsonString);
    }
}
