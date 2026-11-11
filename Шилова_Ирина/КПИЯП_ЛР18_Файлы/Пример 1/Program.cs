using System;

class Counter
{
    public event EventHandler ThresholdReached;

    protected virtual void OnThresholdReached(EventArgs e)
    {
        ThresholdReached?.Invoke(this, e);
    }

    private int count;
    private int threshold = 10;

    public void Add(int value)
    {
        count += value;
        if (count >= threshold)
        {
            OnThresholdReached(EventArgs.Empty);
        }
    }

    public void Reset()
    {
        count = 0;
    }

    public int Count => count;
}

class Program
{
    static void Main()
    {
        Counter c = new Counter();
        c.ThresholdReached += c_ThresholdReached;

        int[] values = { 3, 4, 5 };
        foreach (int v in values)
        {
            c.Add(v);
            Console.WriteLine($"Добавлено {v}, "
                + $"счётчик = {c.Count}");
        }
    }

    static void c_ThresholdReached(object sender, EventArgs e)
    {
        Console.WriteLine("Порог был достигнут.");
    }
}
