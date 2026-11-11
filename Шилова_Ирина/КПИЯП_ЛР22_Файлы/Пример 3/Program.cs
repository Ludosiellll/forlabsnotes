using System;
using System.Text.Json;
using System.IO;
public class Student
{
    public string Name { get; set; }
    public int Grade { get; set; }
}
class Program
{
    static void Main()
    {
        string[] testFiles = { "correct.json", "invalid.json", "missing.json" };

        foreach (string file in testFiles)
        {
            try
            {
                ReadStudentFile(file);
            }
            catch (FileNotFoundException)
            {
                Console.WriteLine($"Файл {file} не найден");
            }
            catch (JsonException ex)
            {
                Console.WriteLine($"Ошибка JSON в файле {file}: {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Общая ошибка: {ex.Message}");
            }
        }
    }
    static void ReadStudentFile(string filename)
    {
        if (!File.Exists(filename))
            throw new FileNotFoundException();

        string json = File.ReadAllText(filename);
        Student student = JsonSerializer.Deserialize<Student>(json);

        Console.WriteLine($"Успешно прочитано: {student.Name}");
    }
}
