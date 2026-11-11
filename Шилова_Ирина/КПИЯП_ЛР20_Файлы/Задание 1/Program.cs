using System;
using System.Collections.Generic;
using System.IO;

class Program
{
    static string[] GetWords(string line)
    {
        char[] separators = { ' ', ',', '.', '!', '?', ';', ':' };
        return line.Split(separators,
            StringSplitOptions.RemoveEmptyEntries);
    }

    static bool HasSameWords(string line)
    {
        string[] words = GetWords(line.ToLower());
        for (int i = 0; i < words.Length; i++)
        {
            for (int j = i + 1; j < words.Length; j++)
            {
                if (words[i] == words[j])
                {
                    return true;
                }
            }
        }
        return false;
    }

    static int CountA(string word)
    {
        int count = 0;
        foreach (char c in word)
        {
            if (c == 'а' || c == 'А')
            {
                count++;
            }
        }
        return count;
    }

    static void Main(string[] args)
    {
        string pathF1 = "F1.txt";
        string pathF2 = "F2.txt";

        List<string> lines = new List<string>();
        using (StreamReader reader = new StreamReader(pathF1))
        {
            string line;
            while ((line = reader.ReadLine()) != null)
            {
                lines.Add(line);
            }
        }

        Console.WriteLine("Содержимое файла F1:");
        for (int i = 0; i < lines.Count; i++)
        {
            Console.WriteLine((i + 1) + ". " + lines[i]);
        }

        using (StreamWriter writer = new StreamWriter(pathF2))
        {
            foreach (string line in lines)
            {
                if (HasSameWords(line))
                {
                    writer.WriteLine(line);
                }
            }
        }

        Console.WriteLine();
        Console.WriteLine("Содержимое файла F2:");
        int number = 0;
        int bestNumber = 0;
        int bestCount = 0;
        string bestWord = "";
        using (StreamReader reader = new StreamReader(pathF2))
        {
            string line;
            while ((line = reader.ReadLine()) != null)
            {
                Console.WriteLine(line);
                foreach (string word in GetWords(line))
                {
                    number++;
                    int count = CountA(word);
                    if (count > bestCount)
                    {
                        bestCount = count;
                        bestNumber = number;
                        bestWord = word;
                    }
                }
            }
        }

        Console.WriteLine();
        if (bestCount == 0)
        {
            Console.WriteLine("В файле F2 нет слов с буквой «А»");
        }
        else
        {
            Console.WriteLine("Больше всего букв «А» в слове №"
                + bestNumber + " («" + bestWord + "»): "
                + bestCount);
        }
    }
}
