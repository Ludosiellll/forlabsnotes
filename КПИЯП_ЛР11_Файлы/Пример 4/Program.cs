using System;

namespace Test_Lifecycle
{
    class MemoryBuffer : IDisposable
    {
        private byte[] buffer;
        public int Size { get; private set; }

        public MemoryBuffer(int size)
        {
            Size = size;
            buffer = new byte[size];
            Console.WriteLine($"Буфер размером {Size} байт создан");
        }

        public void WriteData(byte[] data)
        {
            Array.Copy(data, buffer, Math.Min(data.Length, Size));
            Console.WriteLine("Данные записаны в буфер");
        }

        public void Dispose()
        {
            buffer = null;
            Console.WriteLine($"Буфер размером {Size} байт освобожден");
        }
    }

    class DataProcessor : IDisposable
    {
        private MemoryBuffer inputBuffer;
        private MemoryBuffer outputBuffer;
        public string Name { get; set; }

        public DataProcessor(string name, int inputSize, int outputSize)
        {
            Name = name;
            inputBuffer = new MemoryBuffer(inputSize);
            outputBuffer = new MemoryBuffer(outputSize);
        }

        public void Process()
        {
            Console.WriteLine($"Обработчик {Name} выполняет обработку данных");
            byte[] testData = { 1, 2, 3, 4, 5 };
            inputBuffer.WriteData(testData);
        }

        public void Dispose()
        {
            if (inputBuffer != null) inputBuffer.Dispose();
            if (outputBuffer != null) outputBuffer.Dispose();
            Console.WriteLine($"Ресурсы обработчика {Name} освобождены");
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            using (var processor = new DataProcessor("Основной", 1024, 512))
            {
                processor.Process();
            }

            Console.Write("Press any key to continue... ");
            Console.ReadKey(true);
        }
    }
}
