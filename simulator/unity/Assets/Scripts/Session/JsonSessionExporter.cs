using System;
using System.IO;
using UnityEngine;

namespace AeroVeda.Session;

public interface ISessionExporter
{
    void Export(SessionRecord record, string outputPath);
}

public sealed class JsonSessionExporter : ISessionExporter
{
    public void Export(SessionRecord record, string outputPath)
    {
        if (record == null)
        {
            throw new ArgumentNullException(nameof(record));
        }

        var directory = Path.GetDirectoryName(outputPath);

        if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }

        var json = JsonUtility.ToJson(record, true);
        File.WriteAllText(outputPath, json);
    }
}
