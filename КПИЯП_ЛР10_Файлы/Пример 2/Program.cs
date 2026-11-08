using System;

namespace Test_Indeksator2
{
    class Matr
    {
        private int n;
        private int m;
        private double[,] x;

        public Matr()
        {
            n = m = 1;
            x = new double[n, m];
            x[0, 0] = 1;
        }

        public Matr(int n0, int m0)
        {
            n = n0;
            if (n < 1) n = 1;
            m = m0;
            if (m < 1) m = 1;
            x = new double[n, m];
            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < m; j++)
                {
                    x[i, j] = (i + 1) * 10 + j + 1;
                }
            }
        }

        public double this[int i, int j]
        {
            set
            {
                x[i, j] = value;
            }
            get
            {
                return x[i, j];
            }
        }

        public void print()
        {
            Console.WriteLine("РњР°С‚СЂРёС†Р°:");
            for (int i = 0; i < n; i++)
            {
                for (int j = 0; j < m; j++)
                {
                    Console.Write(x[i, j].ToString() + " ");
                }
                Console.WriteLine();
            }
        }
    }

    class Program
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("РўРµСЃС‚РёСЂРѕРІР°РЅРёРµ СЂР°Р±РѕС‚С‹ РёРЅРґРµРєСЃР°С‚РѕСЂРѕРІ");
            Matr x = new Matr(3, 3);

            x[0, 0] = 5;

            Console.WriteLine(x[1, 1]);

            x.print();
        }
    }
}
