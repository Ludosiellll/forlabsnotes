using System;
using System.Text;

class Program
{
    const char Filler = '_';   // заполняет пустые клетки таблицы

    // Место буквы в алфавите: Ё стоит сразу после Е
    static double Rank(char c)
    {
        return c == 'Ё' ? 'Е' + 0.5 : c;
    }

    // Номер каждой буквы ключа в алфавитном порядке (1, 2, ...);
    // одинаковые буквы нумеруются слева направо
    static int[] KeyNumbers(string key)
    {
        int n = key.Length;
        int[] numbers = new int[n];
        bool[] used = new bool[n];
        for (int k = 1; k <= n; k++)
        {
            int best = -1;
            for (int i = 0; i < n; i++)
            {
                if (!used[i] && (best == -1
                    || Rank(key[i]) < Rank(key[best])))
                {
                    best = i;
                }
            }
            used[best] = true;
            numbers[best] = k;
        }
        return numbers;
    }

    // Индекс столбца, который после перестановки стоит k-м
    static int ColumnAt(int[] numbers, int k)
    {
        return Array.IndexOf(numbers, k + 1);
    }

    static void PrintTable(char[,] table, string head)
    {
        Console.WriteLine("  " + head);
        for (int r = 0; r < table.GetLength(0); r++)
        {
            StringBuilder row = new StringBuilder("  ");
            for (int c = 0; c < table.GetLength(1); c++)
            {
                row.Append(table[r, c]).Append(' ');
            }
            Console.WriteLine(row.ToString().TrimEnd());
        }
    }

    static string Encrypt(string text, string key)
    {
        int[] numbers = KeyNumbers(key);
        int cols = key.Length;
        int rows = (text.Length + cols - 1) / cols;
        char[,] table = new char[rows, cols];

        // открытый текст вписывается в таблицу по столбцам
        for (int i = 0; i < rows * cols; i++)
        {
            table[i % rows, i / rows] = i < text.Length
                ? text[i] : Filler;
        }
        PrintTable(table, string.Join(" ", key.ToCharArray()));
        Console.WriteLine("  " + string.Join(" ", numbers));

        // столбцы переставляются по номерам букв ключа,
        // шифротекст выписывается по строкам
        char[,] moved = new char[rows, cols];
        StringBuilder result = new StringBuilder();
        for (int r = 0; r < rows; r++)
        {
            for (int k = 0; k < cols; k++)
            {
                moved[r, k] = table[r, ColumnAt(numbers, k)];
                result.Append(moved[r, k]);
            }
        }
        Console.WriteLine("Таблица после перестановки столбцов:");
        string order = "";
        for (int k = 1; k <= cols; k++)
        {
            order += k + " ";
        }
        PrintTable(moved, order.TrimEnd());
        return result.ToString();
    }

    static string Decrypt(string cipher, string key)
    {
        int[] numbers = KeyNumbers(key);
        int cols = key.Length;
        int rows = cipher.Length / cols;
        char[,] table = new char[rows, cols];

        // шифротекст вписывается по строкам, столбцы
        // возвращаются на места букв ключа
        for (int r = 0; r < rows; r++)
        {
            for (int k = 0; k < cols; k++)
            {
                int col = ColumnAt(numbers, k);
                table[r, col] = cipher[r * cols + k];
            }
        }

        // открытый текст читается по столбцам
        StringBuilder result = new StringBuilder();
        for (int c = 0; c < cols; c++)
        {
            for (int r = 0; r < rows; r++)
            {
                result.Append(table[r, c]);
            }
        }
        return result.ToString().TrimEnd(Filler);
    }

    // Группы по 4 символа — только для удобства чтения
    static string Groups(string s)
    {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.Length; i++)
        {
            if (i > 0 && i % 4 == 0)
            {
                sb.Append(' ');
            }
            sb.Append(s[i]);
        }
        return sb.ToString();
    }

    static void Main()
    {
        Console.WriteLine("Шифр одиночной перестановки по ключу");
        Console.Write("Открытый текст: ");
        string text = Console.ReadLine().ToUpper();
        text = text.Replace(" ", "");
        Console.Write("Ключевое слово: ");
        string key = Console.ReadLine().ToUpper();
        key = key.Replace(" ", "");
        if (text.Length == 0 || key.Length < 2)
        {
            Console.WriteLine("Введите текст и ключ (от 2 букв)");
            return;
        }

        Console.WriteLine("Таблица, текст вписан по столбцам:");
        string cipher = Encrypt(text, key);
        Console.WriteLine("Шифротекст: " + Groups(cipher));
        Console.WriteLine("Расшифровка: " + Decrypt(cipher, key));
    }
}
