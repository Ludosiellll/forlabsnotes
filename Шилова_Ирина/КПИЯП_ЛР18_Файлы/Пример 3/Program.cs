using System;

class Counter
{
    public event EventHandler ThresholdReached;

    private int count;
    private int threshold = 10;

    public void Add(int value)
    {
        count += value;
        if (count >= threshold)
        {
            ThresholdReached?.Invoke(this, EventArgs.Empty);
        }
    }

    public void Reset()
    {
        count = 0;
    }
}

class Program
{
    static void Main()
    {
        var c = new Counter();
        // статический обработчик: подписан на всё время работы
        c.ThresholdReached += c_ThresholdReached;

        Console.Write("Сообщать о сбросе счётчика? (д/н): ");
        bool withReset = Console.ReadLine().Trim() == "д";
        // динамический обработчик: подключается по условию
        if (withReset)
        {
            c.ThresholdReached += Reset_Handler;
        }

        c.Add(6);
        c.Add(6);

        // обработчик можно отключить во время работы
        c.ThresholdReached -= Reset_Handler;
        Console.WriteLine("Обработчик сброса отключён");
        c.Add(12);
    }

    static void c_ThresholdReached(object sender, EventArgs e)
    {
        Console.WriteLine("Порог был достигнут.");
    }

    static void Reset_Handler(object sender, EventArgs e)
    {
        ((Counter)sender).Reset();
        Console.WriteLine("Счётчик сброшен.");
    }
}
