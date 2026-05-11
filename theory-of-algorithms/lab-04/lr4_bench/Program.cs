using System.Diagnostics;
using System.Globalization;

const int targetMilliseconds = 2_000;

var sortedSizes = new[] { 50_000, 100_000, 150_000, 200_000, 250_000, 300_000, 350_000 };
var quadraticSizes = new[] { 1_000, 2_000, 3_000, 4_000, 5_000, 6_000, 7_000 };

Console.WriteLine("case,n,repeats,total_ms,avg_us,sorted_ok");

foreach (var n in sortedSizes)
{
    RunCase("best_sorted", n, MakeSorted(n), targetMilliseconds,
        fixedRepeats: Math.Max(1, (int)(3_000_000_000L / n)));
}

foreach (var n in quadraticSizes)
{
    RunCase("worst_reversed", n, MakeReversed(n), targetMilliseconds,
        fixedRepeats: Math.Max(10, (int)(3_000_000_000L / ((long)n * n))));
}

foreach (var n in quadraticSizes)
{
    RunCase("average_random", n, MakeRandom(n), targetMilliseconds,
        fixedRepeats: Math.Max(10, (int)(3_000_000_000L / ((long)n * n))));
}

static void OptimizedBubbleSort(int[] a)
{
    var right = a.Length - 1;
    var swapped = true;

    while (swapped && right > 0)
    {
        swapped = false;
        for (var i = 0; i < right; i++)
        {
            if (a[i] > a[i + 1])
            {
                (a[i], a[i + 1]) = (a[i + 1], a[i]);
                swapped = true;
            }
        }

        right--;
    }
}

static void RunCase(string name, int n, int[] input, int targetMilliseconds, int? fixedRepeats = null)
{
    var repeats = fixedRepeats ?? EstimateRepeats(name, input, targetMilliseconds);
    var elapsed = Measure(name, input, repeats, out var sortedOk);
    var averageUs = elapsed.TotalMilliseconds * 1000.0 / repeats;

    Console.WriteLine(string.Join(",",
        name,
        n.ToString(CultureInfo.InvariantCulture),
        repeats.ToString(CultureInfo.InvariantCulture),
        elapsed.TotalMilliseconds.ToString("F3", CultureInfo.InvariantCulture),
        averageUs.ToString("F3", CultureInfo.InvariantCulture),
        sortedOk ? "true" : "false"));
}

static int EstimateRepeats(string name, int[] input, int targetMilliseconds)
{
    var repeats = 1;
    TimeSpan elapsed;

    do
    {
        elapsed = Measure(name, input, repeats, out _);
        if (elapsed.TotalMilliseconds >= 150)
        {
            break;
        }

        repeats *= 2;
    }
    while (repeats < 1_000_000);

    if (elapsed.TotalMilliseconds <= 0)
    {
        return repeats;
    }

    var estimated = (int)Math.Ceiling(repeats * targetMilliseconds / elapsed.TotalMilliseconds);
    return Math.Clamp(estimated, 1, 2_000_000);
}

static TimeSpan Measure(string name, int[] input, int repeats, out bool sortedOk)
{
    int[] work = name == "best_sorted" ? (int[])input.Clone() : new int[input.Length];
    sortedOk = true;

    GC.Collect();
    GC.WaitForPendingFinalizers();
    GC.Collect();

    var sw = new Stopwatch();
    for (var r = 0; r < repeats; r++)
    {
        if (name != "best_sorted")
        {
            Array.Copy(input, work, input.Length);
        }

        sw.Start();
        OptimizedBubbleSort(work);
        sw.Stop();
    }

    sortedOk = IsSorted(work);
    return sw.Elapsed;
}

static int[] MakeSorted(int n)
{
    var a = new int[n];
    for (var i = 0; i < n; i++)
    {
        a[i] = i;
    }

    return a;
}

static int[] MakeReversed(int n)
{
    var a = new int[n];
    for (var i = 0; i < n; i++)
    {
        a[i] = n - i;
    }

    return a;
}

static int[] MakeRandom(int n)
{
    var random = new Random(20260505 + n);
    var a = new int[n];
    for (var i = 0; i < n; i++)
    {
        a[i] = random.Next();
    }

    return a;
}

static bool IsSorted(int[] a)
{
    for (var i = 1; i < a.Length; i++)
    {
        if (a[i - 1] > a[i])
        {
            return false;
        }
    }

    return true;
}
