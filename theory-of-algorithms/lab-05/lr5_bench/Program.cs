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
                var buffer = new int[size];

                Array.Copy(source, data, size);
                MergeSort(data, buffer);

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
                    MergeSort(data, buffer);
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
                var random = new Random(20_260_505 + size);
                for (var i = 0; i < size; i++)
                    result[i] = random.Next();
                break;
        }

        return result;
    }

    private static void MergeSort(int[] array)
    {
        if (array.Length <= 1)
            return;

        var buffer = new int[array.Length];
        MergeSort(array, buffer);
    }

    private static void MergeSort(int[] array, int[] buffer)
    {
        if (array.Length <= 1)
            return;

        MergeSort(array, buffer, 0, array.Length - 1);
    }

    private static void MergeSort(int[] array, int[] buffer, int left, int right)
    {
        if (left >= right)
            return;

        var middle = left + (right - left) / 2;

        MergeSort(array, buffer, left, middle);
        MergeSort(array, buffer, middle + 1, right);
        Merge(array, buffer, left, middle, right);
    }

    private static void Merge(int[] array, int[] buffer, int left, int middle, int right)
    {
        var i = left;
        var j = middle + 1;
        var k = left;

        while (i <= middle && j <= right)
        {
            if (array[i] <= array[j])
                buffer[k++] = array[i++];
            else
                buffer[k++] = array[j++];
        }

        while (i <= middle)
            buffer[k++] = array[i++];

        while (j <= right)
            buffer[k++] = array[j++];

        for (var index = left; index <= right; index++)
            array[index] = buffer[index];
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
