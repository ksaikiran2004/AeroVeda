using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

/// <summary>Creates and assigns a compact natural terrain palette and imports the supplied brand logo.</summary>
[InitializeOnLoad]
public static class AeroVedaEnvironmentSetup
{
    private const int SetupVersion = 1;
    private const string TerrainFolder = "Assets/Art/Terrain";
    private const string LogoPath = "Assets/Resources/Branding/AeroVeda_AV_Logo.png";
    private const string SetupPreference = "AeroVeda.PresentationSetupVersion";

    static AeroVedaEnvironmentSetup()
    {
        EditorApplication.delayCall += ApplyOnce;
    }

    private static void ApplyOnce()
    {
        if (EditorPrefs.GetInt(SetupPreference, 0) >= SetupVersion)
            return;

        try
        {
            ConfigureLogoImport();
            EnsureFolder("Assets/Art");
            EnsureFolder(TerrainFolder);

            TerrainLayer grass = CreateTerrainLayer("AeroVeda Grass", "Grass", new Color(0.26f, 0.31f, 0.20f), new Vector2(34f, 34f), 127);
            TerrainLayer earth = CreateTerrainLayer("AeroVeda Dry Earth", "Earth", new Color(0.37f, 0.29f, 0.19f), new Vector2(25f, 25f), 283);
            TerrainLayer rock = CreateTerrainLayer("AeroVeda Rocky Soil", "Rock", new Color(0.35f, 0.34f, 0.29f), new Vector2(20f, 20f), 419);
            Material terrainMaterial = CreateTerrainMaterial();

            Terrain[] terrains = Terrain.activeTerrains;
            int updatedTerrainCount = 0;
            foreach (Terrain terrain in terrains)
            {
                if (terrain == null || terrain.terrainData == null)
                    continue;

                TerrainData data = terrain.terrainData;
                data.terrainLayers = new[] { grass, earth, rock };
                PaintNaturalAlphamap(terrain, data);
                terrain.materialTemplate = terrainMaterial;
                terrain.drawInstanced = true;
                EditorUtility.SetDirty(data);
                EditorUtility.SetDirty(terrain);
                updatedTerrainCount++;
            }

            AssetDatabase.SaveAssets();
            if (updatedTerrainCount > 0)
            {
                var scene = EditorSceneManager.GetActiveScene();
                if (scene.IsValid() && scene.isLoaded)
                {
                    EditorSceneManager.MarkSceneDirty(scene);
                    EditorSceneManager.SaveScene(scene);
                }
            }

            EditorPrefs.SetInt(SetupPreference, SetupVersion);
            Debug.Log("AeroVeda presentation assets applied: natural terrain layers, terrain material, and transparent logo import. Terrains updated: " + updatedTerrainCount);
        }
        catch (System.Exception exception)
        {
            Debug.LogError("AeroVeda presentation setup failed: " + exception);
        }
    }

    private static void ConfigureLogoImport()
    {
        if (!File.Exists(LogoPath))
            throw new FileNotFoundException("The supplied logo was not copied into the project Resources folder.", LogoPath);

        AssetDatabase.ImportAsset(LogoPath, ImportAssetOptions.ForceUpdate);
        TextureImporter importer = AssetImporter.GetAtPath(LogoPath) as TextureImporter;
        if (importer == null)
            throw new System.InvalidOperationException("Unity could not create a texture importer for the supplied logo.");

        importer.textureType = TextureImporterType.Sprite;
        importer.spriteImportMode = SpriteImportMode.Single;
        importer.alphaIsTransparency = true;
        importer.sRGBTexture = true;
        importer.mipmapEnabled = true;
        importer.wrapMode = TextureWrapMode.Clamp;
        importer.maxTextureSize = 2048;
        importer.textureCompression = TextureImporterCompression.CompressedHQ;
        importer.SaveAndReimport();
    }

    private static TerrainLayer CreateTerrainLayer(string assetName, string textureName, Color baseColor,
        Vector2 tileSize, int seed)
    {
        string texturePath = TerrainFolder + "/AeroVeda_" + textureName + ".png";
        if (!File.Exists(texturePath))
        {
            Texture2D generatedTexture = MakeSeamlessTexture(baseColor, seed, textureName);
            File.WriteAllBytes(texturePath, generatedTexture.EncodeToPNG());
            Object.DestroyImmediate(generatedTexture);
        }

        AssetDatabase.ImportAsset(texturePath, ImportAssetOptions.ForceUpdate);
        TextureImporter importer = AssetImporter.GetAtPath(texturePath) as TextureImporter;
        if (importer != null)
        {
            importer.textureType = TextureImporterType.Default;
            importer.sRGBTexture = true;
            importer.alphaSource = TextureImporterAlphaSource.None;
            importer.mipmapEnabled = true;
            importer.wrapMode = TextureWrapMode.Repeat;
            importer.filterMode = FilterMode.Bilinear;
            importer.maxTextureSize = 512;
            importer.textureCompression = TextureImporterCompression.Compressed;
            importer.SaveAndReimport();
        }

        Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
        if (texture == null)
            throw new System.InvalidOperationException("Could not load generated terrain texture: " + texturePath);

        string layerPath = TerrainFolder + "/" + assetName + ".terrainlayer";
        TerrainLayer layer = AssetDatabase.LoadAssetAtPath<TerrainLayer>(layerPath);
        if (layer == null)
        {
            layer = new TerrainLayer();
            AssetDatabase.CreateAsset(layer, layerPath);
        }
        layer.diffuseTexture = texture;
        layer.tileSize = tileSize;
        layer.tileOffset = Vector2.zero;
        layer.metallic = 0f;
        layer.smoothness = 0f;
        EditorUtility.SetDirty(layer);
        return layer;
    }

    private static Texture2D MakeSeamlessTexture(Color baseColor, int seed, string textureName)
    {
        const int resolution = 512;
        Texture2D texture = new Texture2D(resolution, resolution, TextureFormat.RGB24, true, false)
        {
            name = "AeroVeda " + textureName + " Tile",
            wrapMode = TextureWrapMode.Repeat,
            filterMode = FilterMode.Bilinear
        };
        Color[] pixels = new Color[resolution * resolution];
        bool isGrass = textureName == "Grass";
        bool isRock = textureName == "Rock";

        for (int y = 0; y < resolution; y++)
        {
            float v = (float)y / resolution;
            for (int x = 0; x < resolution; x++)
            {
                float u = (float)x / resolution;
                float broad = PeriodicNoise(u, v, 2.4f, seed);
                float medium = PeriodicNoise(u, v, 7.5f, seed + 29);
                float fine = PeriodicNoise(u, v, 24f, seed + 61);
                float grain = PeriodicNoise(u, v, 69f, seed + 97);
                float value = broad * 0.48f + medium * 0.27f + fine * 0.17f + grain * 0.08f;

                float luminance = isGrass
                    ? 0.60f + value * 0.72f
                    : isRock ? 0.61f + value * 0.7f : 0.58f + value * 0.76f;
                Color color = baseColor * luminance;

                if (isGrass)
                {
                    float dryPatch = Mathf.Clamp01((broad - 0.58f) * 1.9f);
                    color = Color.Lerp(color, new Color(0.39f, 0.33f, 0.22f) * luminance, dryPatch * 0.45f);
                }
                else if (!isRock)
                {
                    float pebble = Mathf.SmoothStep(0.70f, 0.88f, fine * 0.55f + grain * 0.45f);
                    color = Color.Lerp(color, new Color(0.43f, 0.36f, 0.25f) * luminance, pebble * 0.25f);
                }
                else
                {
                    float fleck = Mathf.SmoothStep(0.72f, 0.91f, fine * 0.58f + grain * 0.42f);
                    color = Color.Lerp(color, new Color(0.46f, 0.43f, 0.36f) * luminance, fleck * 0.32f);
                }

                pixels[y * resolution + x] = color;
            }
        }

        texture.SetPixels(pixels);
        texture.Apply(true, false);
        return texture;
    }

    private static float PeriodicNoise(float u, float v, float scale, int seed)
    {
        float angleU = u * Mathf.PI * 2f;
        float angleV = v * Mathf.PI * 2f;
        float ux = Mathf.Cos(angleU) * scale;
        float uy = Mathf.Sin(angleU) * scale;
        float vx = Mathf.Cos(angleV) * scale;
        float vy = Mathf.Sin(angleV) * scale;
        float ox = seed * 0.173f;
        float oy = seed * 0.317f;
        return (Mathf.PerlinNoise(ux + ox, vx + oy) + Mathf.PerlinNoise(ux + ox, vy + oy) +
            Mathf.PerlinNoise(uy + ox, vx + oy) + Mathf.PerlinNoise(uy + ox, vy + oy)) * 0.25f;
    }

    private static Material CreateTerrainMaterial()
    {
        string path = TerrainFolder + "/AeroVeda Terrain Lit.mat";
        Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material != null)
            return material;

        Shader shader = Shader.Find("Universal Render Pipeline/Terrain/Lit");
        if (shader == null)
            shader = Shader.Find("Nature/Terrain/Standard");
        if (shader == null)
            throw new System.InvalidOperationException("Neither URP Terrain Lit nor built-in Terrain Standard shader is available.");

        material = new Material(shader) { name = "AeroVeda Terrain Lit" };
        AssetDatabase.CreateAsset(material, path);
        return material;
    }

    private static void PaintNaturalAlphamap(Terrain terrain, TerrainData data)
    {
        int width = data.alphamapWidth;
        int height = data.alphamapHeight;
        float[,,] map = new float[height, width, 3];
        Vector3 terrainOrigin = terrain.transform.position;
        Vector3 terrainSize = data.size;

        for (int y = 0; y < height; y++)
        {
            float v = (float)y / (height - 1);
            float worldZ = terrainOrigin.z + v * terrainSize.z;
            for (int x = 0; x < width; x++)
            {
                float u = (float)x / (width - 1);
                float worldX = terrainOrigin.x + u * terrainSize.x;
                float broad = Mathf.PerlinNoise((worldX + 327f) * 0.0013f, (worldZ - 91f) * 0.0013f);
                float patch = Mathf.PerlinNoise((worldX - 29f) * 0.0048f, (worldZ + 211f) * 0.0048f);
                float slope = data.GetSteepness(u, v);
                float rockWeight = Mathf.Clamp01((slope - 18f) / 35f) * 0.78f;
                float soilWeight = Mathf.Clamp01((broad - 0.44f) * 2.8f) * 0.48f +
                    Mathf.Clamp01((patch - 0.70f) * 1.8f) * 0.18f;
                float grassWeight = Mathf.Max(0.08f, 1f - soilWeight - rockWeight);
                float total = grassWeight + soilWeight + rockWeight;
                map[y, x, 0] = grassWeight / total;
                map[y, x, 1] = soilWeight / total;
                map[y, x, 2] = rockWeight / total;
            }
        }

        data.SetAlphamaps(0, 0, map);
    }

    private static void EnsureFolder(string path)
    {
        if (AssetDatabase.IsValidFolder(path))
            return;
        string parent = Path.GetDirectoryName(path).Replace('\\', '/');
        string folder = Path.GetFileName(path);
        if (!AssetDatabase.IsValidFolder(parent))
            EnsureFolder(parent);
        AssetDatabase.CreateFolder(parent, folder);
    }
}
