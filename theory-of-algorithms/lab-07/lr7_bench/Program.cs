using System.Diagnostics;
using System.Globalization;

internal static class Program
{
    private static readonly int[] Sizes =
    [
        50_000,
        100_000,
        200_000,
        400_000,
        800_000,
        1_200_000,
        1_600_000
    ];

    private const double TargetMilliseconds = 2_200.0;

    private static void Main()
    {
        Console.WriteLine("case,n,repeats,total_ms,average_ms,sorted_ok");

        foreach (var inputKind in new[] { "sorted", "reversed", "random" })
        {
            foreach (var size in Sizes)
            {
                var source = CreateInput(inputKind, size);
                var data = new int[size];

                Array.Copy(source, data, size);
                HeapSort(data);

                GC.Collect();
                GC.WaitForPendingFinalizers();
                GC.Collect();

                long totalTicks = 0;
                int repeats = 0;
                bool sortedOk = true;

                do
                {
                    Array.Copy(source, data, size);

                    var stopwatch = Stopwatch.StartNew();
                    HeapSort(data);
                    stopwatch.Stop();

                    totalTicks += stopwatch.ElapsedTicks;
                    repeats++;
                    sortedOk &= IsSorted(data);
                }
                while (TicksToMilliseconds(totalTicks) < TargetMilliseconds);

                var totalMs = TicksToMilliseconds(totalTicks);
                var averageMs = totalMs / repeats;

                Console.WriteLine(string.Join(',',
                    inputKind,
                    size.ToString(CultureInfo.InvariantCulture),
                    repeats.ToString(CultureInfo.InvariantCulture),
                    totalMs.ToString("F3", CultureInfo.InvariantCulture),
                    averageMs.ToString("F3", CultureInfo.InvariantCulture),
                    sortedOk.ToString().ToLowerInvariant()));
            }
        }
    }

    private static int[] CreateInput(string inputKind, int size)
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
                    result[i] = size - i;
                break;

            case "random":
                var random = new Random(20_260_509 + size);
                for (var i = 0; i < size; i++)
                    result[i] = random.Next();
                break;
        }

        return result;
    }

    private static void HeapSort(int[] array)
    {
        BuildMaxHeap(array);

        for (var heapSize = array.Length; heapSize > 1; heapSize--)
        {
            Swap(array, 0, heapSize - 1);
            Heapify(array, 0, heapSize - 1);
        }
    }

    private static void BuildMaxHeap(int[] array)
    {
        for (var i = array.Length / 2 - 1; i >= 0; i--)
            Heapify(array, i, array.Length);
    }

    private static void Heapify(int[] array, int index, int heapSize)
    {
        while (true)
        {
            var left = 2 * index + 1;
            var right = 2 * index + 2;
            var largest = index;

            if (left < heapSize && array[left] > array[largest])
                largest = left;

            if (right < heapSize && array[right] > array[largest])
                largest = right;

            if (largest == index)
                return;

            Swap(array, index, largest);
            index = largest;
        }
    }

    private static void Swap(int[] array, int first, int second)
    {
        (array[first], array[second]) = (array[second], array[first]);
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
