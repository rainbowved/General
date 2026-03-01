using System.Text.RegularExpressions;

var roots = new[] { "tools", "client", "content", "docs" };
var banned = new Regex("Guid\\.NewGuid|DateTime\\.Now|new Random\\(|\\bfloat\\b|\\bdouble\\b", RegexOptions.Compiled);

var beginBlocks = 0;
if (Directory.Exists("docs/concept"))
{
    foreach (var p in Directory.EnumerateFiles("docs/concept", "*.md", SearchOption.AllDirectories))
    {
        beginBlocks += File.ReadLines(p).Count(l => l.Contains("@@BEGIN:B"));
    }
}

Console.WriteLine($"[METRIC] begin_blocks={beginBlocks}");

var violations = new List<string>();
foreach (var root in roots)
{
    if (!Directory.Exists(root)) continue;
    foreach (var file in Directory.EnumerateFiles(root, "*.*", SearchOption.AllDirectories))
    {
        var normalized = file.Replace('\\', '/');
        if (normalized.StartsWith("docs/concept/") || normalized.Contains("/.git/") || normalized.Contains("/_logs/"))
            continue;
        var ext = Path.GetExtension(file).ToLowerInvariant();
        if (ext is not (".cs" or ".py" or ".ps1" or ".sh" or ".sql" or ".json" or ".md"))
            continue;
        foreach (var (line, idx) in File.ReadLines(file).Select((v, i) => (v, i + 1)))
        {
            if (banned.IsMatch(line)) violations.Add($"{file}:{idx}:{line.Trim()}");
        }
    }
}

if (violations.Count > 0)
{
    Console.WriteLine("[FAIL] banned deterministic sins detected");
    foreach (var v in violations) Console.WriteLine(v);
    return 1;
}

Console.WriteLine("[PASS] check_sins");
return 0;
