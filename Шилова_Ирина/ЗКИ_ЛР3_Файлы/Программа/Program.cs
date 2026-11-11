using System;
using System.Text;

class Program
{
    const string Alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    // step = 1 — шифрование:     C = (P + K) mod 26
    // step = -1 — расшифрование: P = (C - K + 26) mod 26
    static string Vigenere(string text, string key, int step)
    {
        StringBuilder result = new StringBuilder();
        int k = 0;   // номер буквы ключа
        foreach (char c in text)
        {
            int p = Alphabet.IndexOf(c);
            if (p < 0)
            {
                result.Append(c);   // пробел и знаки не шифруются
                continue;
            }
            int shift = Alphabet.IndexOf(key[k % key.Length]);
            result.Append(Alphabet[(p + step * shift + 26) % 26]);
            k++;
        }
        return result.ToString();
    }

    // Ключ, циклически записанный под буквами текста
    static string KeyLine(string text, string key)
    {
        StringBuilder line = new StringBuilder();
        int k = 0;
        foreach (char c in text)
        {
            if (Alphabet.IndexOf(c) < 0)
            {
                line.Append(c);
            }
            else
            {
                line.Append(key[k % key.Length]);
                k++;
            }
        }
        return line.ToString();
    }

    static void Main()
    {
        Console.WriteLine("Шифр Виженера (английский алфавит)");
        Console.Write("Открытый текст: ");
        string text = Console.ReadLine().ToUpper();
        Console.Write("Ключ: ");
        string key = Console.ReadLine().ToUpper().Trim();
        foreach (char c in key)
        {
            if (Alphabet.IndexOf(c) < 0)
            {
                Console.WriteLine("Ключ: только буквы A-Z");
                return;
            }
        }
        if (key.Length == 0)
        {
            Console.WriteLine("Ключ не введён");
            return;
        }

        string cipher = Vigenere(text, key, 1);
        Console.WriteLine("Текст:       " + text);
        Console.WriteLine("Ключ:        " + KeyLine(text, key));
        Console.WriteLine("Шифротекст:  " + cipher);
        string plain = Vigenere(cipher, key, -1);
        Console.WriteLine("Расшифровка: " + plain);
    }
}
