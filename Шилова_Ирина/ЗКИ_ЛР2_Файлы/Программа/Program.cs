using System;
using System.Text;

class Program
{
    // 32 буквы без Ё, пробел, точка и запятая — 35 символов
    const string Alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ .,";
    const int Rows = 5;
    const int Cols = 7;

    // Таблица Трисемуса: ключевое слово без повторов,
    // затем остальные символы алфавита по порядку
    static char[,] BuildTable(string keyword)
    {
        StringBuilder seq = new StringBuilder();
        foreach (char c in keyword + Alphabet)
        {
            if (Alphabet.IndexOf(c) >= 0
                && seq.ToString().IndexOf(c) < 0)
            {
                seq.Append(c);
            }
        }
        char[,] table = new char[Rows, Cols];
        for (int i = 0; i < Rows * Cols; i++)
        {
            table[i / Cols, i % Cols] = seq[i];
        }
        return table;
    }

    // Сдвиг по столбцу: +1 — вниз (шифрование), -1 — вверх
    // (расшифрование); из крайней строки — на другой край
    static string Shift(string text, char[,] table, int step)
    {
        StringBuilder result = new StringBuilder();
        foreach (char c in text)
        {
            bool found = false;
            for (int r = 0; r < Rows && !found; r++)
            {
                for (int k = 0; k < Cols && !found; k++)
                {
                    if (table[r, k] == c)
                    {
                        int row = (r + step + Rows) % Rows;
                        result.Append(table[row, k]);
                        found = true;
                    }
                }
            }
            if (!found)
            {
                result.Append(c);   // символа нет в таблице
            }
        }
        return result.ToString();
    }

    static void PrintTable(char[,] table)
    {
        for (int r = 0; r < Rows; r++)
        {
            StringBuilder row = new StringBuilder("  ");
            for (int k = 0; k < Cols; k++)
            {
                // пробел показан знаком «_», чтобы его было видно
                char c = table[r, k];
                row.Append(c == ' ' ? '_' : c);
                row.Append(' ');
            }
            Console.WriteLine(row.ToString().TrimEnd());
        }
    }

    // Заглавные буквы; Ё заменяется на Е (в таблице 32 буквы)
    static string Prepare(string s)
    {
        return s.ToUpper().Replace('Ё', 'Е');
    }

    static void Main()
    {
        Console.WriteLine("Шифрующая таблица Трисемуса 5x7");
        Console.Write("Ключевое слово: ");
        string keyword = Prepare(Console.ReadLine());
        Console.Write("Открытый текст: ");
        string text = Prepare(Console.ReadLine());

        char[,] table = BuildTable(keyword);
        Console.WriteLine("Таблица:");
        PrintTable(table);

        string cipher = Shift(text, table, 1);
        Console.WriteLine("Шифротекст:  " + cipher);
        string plain = Shift(cipher, table, -1);
        Console.WriteLine("Расшифровка: " + plain);
    }
}
