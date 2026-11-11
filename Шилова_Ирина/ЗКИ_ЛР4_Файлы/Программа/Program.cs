using System;
using System.Text;

class Program
{
    // PC-1: выбор 56 бит из 64, биты чётности 8, 16, ..., 64
    // отбрасываются; первые 28 бит — C(0), остальные — D(0)
    static readonly int[] PC1 =
    {
        57, 49, 41, 33, 25, 17, 9,
        1, 58, 50, 42, 34, 26, 18,
        10, 2, 59, 51, 43, 35, 27,
        19, 11, 3, 60, 52, 44, 36,
        63, 55, 47, 39, 31, 23, 15,
        7, 62, 54, 46, 38, 30, 22,
        14, 6, 61, 53, 45, 37, 29,
        21, 13, 5, 28, 20, 12, 4
    };

    // PC-2: выбор 48 бит раундового ключа из 56 бит C(i)D(i)
    static readonly int[] PC2 =
    {
        14, 17, 11, 24, 1, 5,
        3, 28, 15, 6, 21, 10,
        23, 19, 12, 4, 26, 8,
        16, 7, 27, 20, 13, 2,
        41, 52, 31, 37, 47, 55,
        30, 40, 51, 45, 33, 48,
        44, 49, 39, 56, 34, 53,
        46, 42, 50, 36, 29, 32
    };

    // Число сдвигов влево в раундах 1–16
    static readonly int[] Shifts =
        { 1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1 };

    // Ключ: 8 символов ASCII или 16 шестнадцатеричных цифр
    static string KeyToBits(string key)
    {
        StringBuilder bits = new StringBuilder();
        if (key.Length == 16 && IsHex(key))
        {
            foreach (char c in key)
            {
                int v = Convert.ToInt32(c.ToString(), 16);
                string four = Convert.ToString(v, 2);
                bits.Append(four.PadLeft(4, '0'));
            }
            return bits.ToString();
        }
        if (key.Length != 8)
        {
            return null;
        }
        foreach (char c in key)
        {
            if (c > 127)
            {
                return null;   // только символы ASCII (1 байт)
            }
            bits.Append(Convert.ToString(c, 2).PadLeft(8, '0'));
        }
        return bits.ToString();
    }

    static bool IsHex(string s)
    {
        foreach (char c in s)
        {
            if (!Uri.IsHexDigit(c))
            {
                return false;
            }
        }
        return true;
    }

    // Перестановка: n-й бит результата — бит table[n] источника
    static string Permute(string bits, int[] table)
    {
        StringBuilder result = new StringBuilder();
        foreach (int n in table)
        {
            result.Append(bits[n - 1]);
        }
        return result.ToString();
    }

    // Циклический сдвиг влево: первые биты уходят в конец
    static string RotateLeft(string bits, int n)
    {
        return bits.Substring(n) + bits.Substring(0, n);
    }

    // Деление на группы для удобства чтения
    static string Groups(string bits, int size)
    {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < bits.Length; i += size)
        {
            if (i > 0)
            {
                sb.Append(' ');
            }
            sb.Append(bits.Substring(i, size));
        }
        return sb.ToString();
    }

    static void Main()
    {
        Console.WriteLine("Формирование раундовых ключей DES");
        Console.Write("Ключ (8 символов или 16 hex-цифр): ");
        string key = Console.ReadLine().Trim();
        string bits = KeyToBits(key);
        if (bits == null)
        {
            Console.WriteLine("Нужно 8 символов ASCII "
                + "или 16 hex-цифр");
            return;
        }
        Console.WriteLine("Ключ, 64 бита:  " + Groups(bits, 8));
        string k56 = Permute(bits, PC1);
        Console.WriteLine("После PC-1, 56: " + Groups(k56, 7));

        string c = k56.Substring(0, 28);
        string d = k56.Substring(28);
        string head = " i сдвиг " + "C(i)".PadRight(29);
        Console.WriteLine(head + "D(i)");
        Console.WriteLine($" 0   -   {c} {d}");
        string[] keys = new string[16];
        for (int i = 0; i < 16; i++)
        {
            c = RotateLeft(c, Shifts[i]);
            d = RotateLeft(d, Shifts[i]);
            keys[i] = Permute(c + d, PC2);   // K(i) из C(i)D(i)
            Console.WriteLine(
                $"{i + 1,2}   {Shifts[i]}   {c} {d}");
        }

        Console.WriteLine("Раундовые ключи, 48 бит:");
        for (int i = 0; i < 16; i++)
        {
            string k = Groups(keys[i], 6);
            Console.WriteLine($"K{i + 1,-3} {k}");
        }
    }
}
