using System.Diagnostics;
using System.Globalization;

internal static class Program
{
    private static readonly int[] Sizes =
    [
        100_000,
        200_000,
        400_000,
        800_000,
        1_600_000,
        3_200_000,
        6_400_000
    ];

    private const double TargetMilliseconds = 2_200.0;

    private static void Main()
    {
        Console.WriteLine("case,n,k,repeats,total_ms,average_ms,sorted_ok");

        foreach (var inputKind in new[] { "sorted", "reversed", "random" })
        {
            foreach (var size in Sizes)
            {
                var maxValue = size - 1;
                var source = CreateInput(inputKind, size, maxValue);
                var output = new int[size];
                var count = new int[maxValue + 1];

                CountingSort(source, output, count, maxValue);

                GC.Collect();
                GC.WaitForPendingFinalizers();
                GC.Collect();

                long totalTicks = 0;
                int repeats = 0;
                bool sortedOk = true;

                do
                {
                    var stopwatch = Stopwatch.StartNew();
                    CountingSort(source, output, count, maxValue);
                    stopwatch.Stop();

                    totalTicks += stopwatch.ElapsedTicks;
                    repeats++;
                    sortedOk &= IsSorted(output);
                }
                while (TicksToMilliseconds(totalTicks) < TargetMilliseconds);

                var totalMs = TicksToMilliseconds(totalTicks);
                var averageMs = totalMs / repeats;

                Console.WriteLine(string.Join(',',
                    inputKind,
                    size.ToString(CultureInfo.InvariantCulture),
                    (maxValue + 1).ToString(CultureInfo.InvariantCulture),
                    repeats.ToString(CultureInfo.InvariantCulture),
                    totalMs.ToString("F3", CultureInfo.InvariantCulture),
                    averageMs.ToString("F3", CultureInfo.InvariantCulture),
                    sortedOk.ToString().ToLowerInvariant()));
            }
        }
    }

    private static int[] CreateInput(string inputKind, int size, int maxValue)
    {
        var result = new int[size];

        switch (inputKind)
        {
            case "sorted":
                for (var i = 0; i < size; i++)
                    result[i] = i;
                break;

            case "reversed":
                for (var i = 0; i < size; i++)
                    result[i] = maxValue - i;
                break;

            case "random":
                var random = new Random(20_260_509 + size);
                for (var i = 0; i < size; i++)
                    result[i] = random.Next(maxValue + 1);
                break;
        }

        return result;
    }

    private static void CountingSort(int[] input, int[] output, int[] count, int maxValue)
    {
        Array.Clear(count, 0, maxValue + 1);

        for (var i = 0; i < input.Length; i++)
            count[input[i]]++;

        for (var i = 1; i <= maxValue; i++)
            count[i] += count[i - 1];

        for (var i = input.Length - 1; i >= 0; i--)
        {
            var value = input[i];
            output[count[value] - 1] = value;
            count[value]--;
        }
    }

    private static bool IsSorted(int[] array)
    {
        for (var i = 1; i < array.Length; i++)
        {
            if (array[i - 1] > array[i])
                return false;
        }

        return true;
    }

    private static double TicksToMilliseconds(long ticks)
    {
        return ticks * 1_000.0 / Stopwatch.Frequency;
    }
}
