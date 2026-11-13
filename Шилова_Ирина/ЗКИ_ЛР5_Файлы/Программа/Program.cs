using System;
using System.Text;

class Program
{
    // Таблицы стандарта DES: число — номер бита источника (с 1)
    static readonly int[] IP =
    {
        58, 50, 42, 34, 26, 18, 10, 2,
        60, 52, 44, 36, 28, 20, 12, 4,
        62, 54, 46, 38, 30, 22, 14, 6,
        64, 56, 48, 40, 32, 24, 16, 8,
        57, 49, 41, 33, 25, 17, 9, 1,
        59, 51, 43, 35, 27, 19, 11, 3,
        61, 53, 45, 37, 29, 21, 13, 5,
        63, 55, 47, 39, 31, 23, 15, 7
    };

    // Конечная перестановка IP^-1, обратная IP
    static readonly int[] IP1 =
    {
        40, 8, 48, 16, 56, 24, 64, 32,
        39, 7, 47, 15, 55, 23, 63, 31,
        38, 6, 46, 14, 54, 22, 62, 30,
        37, 5, 45, 13, 53, 21, 61, 29,
        36, 4, 44, 12, 52, 20, 60, 28,
        35, 3, 43, 11, 51, 19, 59, 27,
        34, 2, 42, 10, 50, 18, 58, 26,
        33, 1, 41, 9, 49, 17, 57, 25
    };

    // Расширение E: 32 бита правой половины -> 48 бит
    static readonly int[] E =
    {
        32, 1, 2, 3, 4, 5,
        4, 5, 6, 7, 8, 9,
        8, 9, 10, 11, 12, 13,
        12, 13, 14, 15, 16, 17,
        16, 17, 18, 19, 20, 21,
        20, 21, 22, 23, 24, 25,
        24, 25, 26, 27, 28, 29,
        28, 29, 30, 31, 32, 1
    };

    // Перестановка P выхода S-блоков
    static readonly int[] P =
    {
        16, 7, 20, 21, 29, 12, 28, 17,
        1, 15, 23, 26, 5, 18, 31, 10,
        2, 8, 24, 14, 32, 27, 3, 9,
        19, 13, 30, 6, 22, 11, 4, 25
    };

    // Ключи раундов — как в лабораторной работе №4
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

    static readonly int[] Shifts =
        { 1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1 };

    // S-блоки S1..S8: по 4 строки из 16 чисел
    static readonly string[] SRows =
    {
        "14 4 13 1 2 15 11 8 3 10 6 12 5 9 0 7",
        "0 15 7 4 14 2 13 1 10 6 12 11 9 5 3 8",
        "4 1 14 8 13 6 2 11 15 12 9 7 3 10 5 0",
        "15 12 8 2 4 9 1 7 5 11 3 14 10 0 6 13",
        "15 1 8 14 6 11 3 4 9 7 2 13 12 0 5 10",
        "3 13 4 7 15 2 8 14 12 0 1 10 6 9 11 5",
        "0 14 7 11 10 4 13 1 5 8 12 6 9 3 2 15",
        "13 8 10 1 3 15 4 2 11 6 7 12 0 5 14 9",
        "10 0 9 14 6 3 15 5 1 13 12 7 11 4 2 8",
        "13 7 0 9 3 4 6 10 2 8 5 14 12 11 15 1",
        "13 6 4 9 8 15 3 0 11 1 2 12 5 10 14 7",
        "1 10 13 0 6 9 8 7 4 15 14 3 11 5 2 12",
        "7 13 14 3 0 6 9 10 1 2 8 5 11 12 4 15",
        "13 8 11 5 6 15 0 3 4 7 2 12 1 10 14 9",
        "10 6 9 0 12 11 7 13 15 1 3 14 5 2 8 4",
        "3 15 0 6 10 1 13 8 9 4 5 11 12 7 2 14",
        "2 12 4 1 7 10 11 6 8 5 3 15 13 0 14 9",
        "14 11 2 12 4 7 13 1 5 0 15 10 3 9 8 6",
        "4 2 1 11 10 13 7 8 15 9 12 5 6 3 0 14",
        "11 8 12 7 1 14 2 13 6 15 0 9 10 4 5 3",
        "12 1 10 15 9 2 6 8 0 13 3 4 14 7 5 11",
        "10 15 4 2 7 12 9 5 6 1 13 14 0 11 3 8",
        "9 14 15 5 2 8 12 3 7 0 4 10 1 13 11 6",
        "4 3 2 12 9 5 15 10 11 14 1 7 6 0 8 13",
        "4 11 2 14 15 0 8 13 3 12 9 7 5 10 6 1",
        "13 0 11 7 4 9 1 10 14 3 5 12 2 15 8 6",
        "1 4 11 13 12 3 7 14 10 15 6 8 0 5 9 2",
        "6 11 13 8 1 4 10 7 9 5 0 15 14 2 3 12",
        "13 2 8 4 6 15 11 1 10 9 3 14 5 0 12 7",
        "1 15 13 8 10 3 7 4 12 5 6 11 0 14 9 2",
        "7 11 4 1 9 12 14 2 0 6 10 13 15 3 5 8",
        "2 1 14 7 4 10 8 13 15 12 9 0 3 5 6 11"
    };

    static int[,] SBox = new int[32, 16];

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

    static string RotateLeft(string bits, int n)
    {
        return bits.Substring(n) + bits.Substring(0, n);
    }

    // Сложение по модулю 2 (XOR) двух строк битов
    static string Xor(string a, string b)
    {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < a.Length; i++)
        {
            result.Append(a[i] == b[i] ? '0' : '1');
        }
        return result.ToString();
    }

    // 16 ключей раундов по 48 бит из 64-битного ключа
    static string[] RoundKeys(string key64)
    {
        string k56 = Permute(key64, PC1);
        string c = k56.Substring(0, 28);
        string d = k56.Substring(28);
        string[] keys = new string[16];
        for (int i = 0; i < 16; i++)
        {
            c = RotateLeft(c, Shifts[i]);
            d = RotateLeft(d, Shifts[i]);
            keys[i] = Permute(c + d, PC2);
        }
        return keys;
    }

    // Функция f: расширение E, XOR с ключом, S-блоки, P
    static string F(string r, string k)
    {
        string x = Xor(Permute(r, E), k);
        StringBuilder s = new StringBuilder();
        for (int i = 0; i < 8; i++)
        {
            string b = x.Substring(i * 6, 6);
            int row = Convert.ToInt32("" + b[0] + b[5], 2);
            int col = Convert.ToInt32(b.Substring(1, 4), 2);
            int v = SBox[i * 4 + row, col];
            s.Append(Convert.ToString(v, 2).PadLeft(4, '0'));
        }
        return Permute(s.ToString(), P);
    }

    // Один 64-битный блок: 16 раундов сети Фейстеля.
    // При расшифровании ключи берутся в обратном порядке.
    static string Block(string bits, string[] keys, bool decrypt,
        bool show)
    {
        string ip = Permute(bits, IP);
        string l = ip.Substring(0, 32);
        string r = ip.Substring(32);
        if (show)
        {
            Console.WriteLine("IP = " + Hex(ip));
            Console.WriteLine(" i   L(i)       R(i)");
            Console.WriteLine($" 0   {Hex(l)}   {Hex(r)}");
        }
        for (int i = 0; i < 16; i++)
        {
            string k = decrypt ? keys[15 - i] : keys[i];
            string next = Xor(l, F(r, k));   // R(i) = L(i-1) + f
            l = r;                            // L(i) = R(i-1)
            r = next;
            if (show)
            {
                Console.WriteLine($"{i + 1,2}   {Hex(l)}   "
                    + Hex(r));
            }
        }
        return Permute(r + l, IP1);   // R16L16 и IP^-1
    }

    static string BytesToBits(byte[] data, int start)
    {
        StringBuilder bits = new StringBuilder();
        for (int i = start; i < start + 8; i++)
        {
            string b = Convert.ToString(data[i], 2);
            bits.Append(b.PadLeft(8, '0'));
        }
        return bits.ToString();
    }

    static byte[] BitsToBytes(string bits)
    {
        byte[] data = new byte[bits.Length / 8];
        for (int i = 0; i < data.Length; i++)
        {
            data[i] = Convert.ToByte(bits.Substring(i * 8, 8), 2);
        }
        return data;
    }

    // Биты -> шестнадцатеричная запись
    static string Hex(string bits)
    {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < bits.Length; i += 4)
        {
            int v = Convert.ToInt32(bits.Substring(i, 4), 2);
            sb.Append(v.ToString("X"));
        }
        return sb.ToString();
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

    static string HexToBits(string hex)
    {
        StringBuilder bits = new StringBuilder();
        foreach (char c in hex)
        {
            int v = Convert.ToInt32(c.ToString(), 16);
            bits.Append(Convert.ToString(v, 2).PadLeft(4, '0'));
        }
        return bits.ToString();
    }

    // Ключ: 8 символов ASCII или 16 шестнадцатеричных цифр
    static string ReadKey()
    {
        while (true)
        {
            Console.Write("Ключ (8 символов или 16 hex-цифр): ");
            string key = Console.ReadLine().Trim();
            if (key.Length == 16 && IsHex(key))
            {
                return HexToBits(key);
            }
            byte[] b = Encoding.ASCII.GetBytes(key);
            bool ascii = Encoding.ASCII.GetString(b) == key;
            if (key.Length == 8 && ascii)
            {
                return BytesToBits(b, 0);
            }
            Console.WriteLine("Нужно 8 латинских букв/цифр "
                + "или 16 hex-цифр");
        }
    }

    static void Main()
    {
        for (int i = 0; i < 32; i++)
        {
            string[] nums = SRows[i].Split(' ');
            for (int j = 0; j < 16; j++)
            {
                SBox[i, j] = int.Parse(nums[j]);
            }
        }

        Console.WriteLine("Шифрование DES");
        Console.WriteLine("1 - зашифровать текст");
        Console.WriteLine("2 - один блок (16 hex-цифр)");
        Console.Write("Выбор: ");
        string mode = Console.ReadLine().Trim();
        string[] keys = RoundKeys(ReadKey());

        if (mode == "2")
        {
            string block;
            while (true)
            {
                Console.Write("Блок (16 hex-цифр): ");
                block = Console.ReadLine().Trim().ToUpper();
                if (block.Length == 16 && IsHex(block)) break;
                Console.WriteLine("Нужно ровно 16 hex-цифр");
            }
            string c = Block(HexToBits(block), keys, false, true);
            Console.WriteLine("Шифротекст:  " + Hex(c));
            string back = Block(c, keys, true, false);
            Console.WriteLine("Расшифровка: " + Hex(back));
            return;
        }

        string text;
        while (true)
        {
            Console.Write("Текст (не менее 8 символов): ");
            text = Console.ReadLine();
            if (text.Length >= 8) break;
            Console.WriteLine("Слишком короткий текст");
        }
        // Текст -> байты UTF-8, дополнение нулями до кратного 8
        byte[] plain = Encoding.UTF8.GetBytes(text);
        byte[] data = new byte[(plain.Length + 7) / 8 * 8];
        Array.Copy(plain, data, plain.Length);
        Console.WriteLine($"Байтов: {plain.Length}, блоков по 64 "
            + $"бита: {data.Length / 8}");

        StringBuilder cipher = new StringBuilder();
        StringBuilder open = new StringBuilder();
        for (int i = 0; i < data.Length; i += 8)
        {
            string m = BytesToBits(data, i);
            string c = Block(m, keys, false, false);
            Console.WriteLine($"Блок {i / 8 + 1}: {Hex(m)} -> "
                + Hex(c));
            cipher.Append(c);
            open.Append(Block(c, keys, true, false));
        }
        string all = Hex(cipher.ToString());
        Console.WriteLine("Шифротекст (hex):");
        for (int i = 0; i < all.Length; i += 32)
        {
            int n = Math.Min(32, all.Length - i);
            Console.WriteLine("  " + all.Substring(i, n));
        }

        // Расшифрование: те же раунды, ключи в обратном порядке
        byte[] dec = BitsToBytes(open.ToString());
        int len = dec.Length;
        while (len > 0 && dec[len - 1] == 0) len--;
        Console.WriteLine("Расшифровка: "
            + Encoding.UTF8.GetString(dec, 0, len));
    }
}
