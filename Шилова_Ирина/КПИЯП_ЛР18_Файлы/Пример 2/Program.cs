using System;

public class ThresholdReachedEventArgs : EventArgs
{
    public int Threshold { get; set; }
    public DateTime TimeReached { get; set; }
}

class Counter
{
    private int count;
    private int threshold;

    public Counter(int threshold)
    {
        this.threshold = threshold;
    }

    public event EventHandler<ThresholdReachedEventArgs>
        ThresholdReached;

    protected virtual void OnThresholdReached(
        ThresholdReachedEventArgs e)
    {
        ThresholdReached?.Invoke(this, e);
    }

    public void Add(int value)
    {
        count += value;
        if (count >= threshold)
        {
            ThresholdReachedEventArgs args =
                new ThresholdReachedEventArgs();
            args.Threshold = threshold;
            args.TimeReached = DateTime.Now;
            OnThresholdReached(args);
        }
    }

    public int Count => count;
}

class Program
{
    static void Main()
    {
        Counter c = new Counter(10);
        c.ThresholdReached += c_ThresholdReached;

        while (c.Count < 10)
        {
            Console.Write("Введите число: ");
            int value;
            if (!int.TryParse(Console.ReadLine(), out value))
            {
                Console.WriteLine("Нужно целое число");
                continue;
            }
            c.Add(value);
            Console.WriteLine("Счётчик = " + c.Count);
        }
    }

    static void c_ThresholdReached(object sender,
        ThresholdReachedEventArgs e)
    {
        Console.WriteLine($"Порог {e.Threshold} был достигнут "
            + $"в {e.TimeReached:HH:mm:ss}.");
    }
}
