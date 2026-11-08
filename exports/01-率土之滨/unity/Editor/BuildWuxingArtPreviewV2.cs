// Editor-only reproducible preview-package import, validation and export.
// Build with -batchmode and graphics enabled for actual Camera.Render sliced QA.
// Run with -batchmode -executeMethod BuildWuxingArtPreviewV2.Build
// and -wuxingBuildConfig <absolute JSON path>. The config supplies actual assets.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

public static class BuildWuxingArtPreviewV2
{
    [Serializable] public class Item
    {
        public string id, category, source, sourceRecord, sourceSha256, assetPath;
        public int width, height, sourceAlphaZero, sourceAlphaOne, sourceAlphaSemi, sourceAlphaOpaque;
        public float pivotX, pivotY;
        public int borderLeft, borderBottom, borderRight, borderTop;
        public bool renderSlice;
        public string packageRecordPath, sourceRecordSha256;
    }
    [Serializable] public class Config
    {
        public string outputPackage, reportPath, exportRoot;
        public string projectRoot, renderReportPath, renderOutputDir;
        public Item[] assets;
    }
    [Serializable] public class AssetResult
    {
        public string id, assetPath, category, sha256, textureFormat;
        public int sourceWidth, sourceHeight, importedWidth, importedHeight, spriteCount;
        public int alphaZero, alphaOne, alphaSemi, alphaOpaque, maximumTextureSize;
        public float expectedPivotX, expectedPivotY, spritePivotX, spritePivotY, pixelsPerUnit;
        public bool bytesMatchSource, nativeDimensionsMatch, alphaCountsMatch, sourceHasAlpha;
        public bool settingsMatch, pivotMatch, oneFullRectSprite, passed;
        public bool borderMatches, sourceRecordBytesMatch;
        public Vector4 spriteBorder;
    }
    [Serializable] public class Report
    {
        public string schema = "wuxing.unity_art_preview_validation.v1";
        public string verifiedAtUtc, unityVersion, mode, packageFile, packageSha256, error;
        public bool batchMode, graphicsDeviceIsNull, passed, clientIntegrated = false;
        public int spriteFileCount;
        public long packageBytes;
        public List<AssetResult> assets = new List<AssetResult>();
    }

    private static Config pendingImport;
    private static double importStarted;
    public static void Build() { Run(false); }
    // Unity 6000.6 queues package import. Verify only after its actual completion event.
    // Do not pass -quit for this asynchronous entry point; completion exits explicitly.
    public static void ImportAndVerify()
    {
        pendingImport = ReadConfig();
        importStarted = EditorApplication.timeSinceStartup;
        AssetDatabase.importPackageCompleted += Imported;
        AssetDatabase.importPackageFailed += ImportFailed;
        AssetDatabase.importPackageCancelled += ImportCancelled;
        EditorApplication.update += ImportTimeout;
        AssetDatabase.ImportPackage(pendingImport.outputPackage, false);
    }
    private static void ClearImportCallbacks()
    {
        AssetDatabase.importPackageCompleted -= Imported;
        AssetDatabase.importPackageFailed -= ImportFailed;
        AssetDatabase.importPackageCancelled -= ImportCancelled;
        EditorApplication.update -= ImportTimeout;
    }
    private static void Imported(string packageName)
    {
        ClearImportCallbacks();
        EditorApplication.delayCall += () => Run(true);
    }
    private static void ImportFailed(string packageName, string error)
    {
        ClearImportCallbacks();
        var report = new Report { verifiedAtUtc = DateTime.UtcNow.ToString("o"), unityVersion = Application.unityVersion,
            mode = "fresh_project_package_import_and_verification", passed = false, error = "Package import failed: " + error };
        File.WriteAllText(pendingImport.reportPath, JsonUtility.ToJson(report, true));
        EditorApplication.Exit(1);
    }
    private static void ImportCancelled(string packageName) { ImportFailed(packageName, "cancelled"); }
    private static void ImportTimeout()
    {
        if (EditorApplication.timeSinceStartup - importStarted > 180) ImportFailed("preview", "completion event timeout after 180 seconds");
    }

    private static string Hash(string path)
    {
        using (var sha = SHA256.Create())
        using (var stream = File.OpenRead(path))
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }

    private static Config ReadConfig()
    {
        var args = Environment.GetCommandLineArgs();
        var pos = Array.IndexOf(args, "-wuxingBuildConfig");
        if (pos < 0 || pos + 1 >= args.Length) throw new ArgumentException("Missing -wuxingBuildConfig");
        return JsonUtility.FromJson<Config>(File.ReadAllText(args[pos + 1]));
    }

    private static void Configure(Item item)
    {
        var importer = AssetImporter.GetAtPath(item.assetPath) as TextureImporter;
        if (importer == null) throw new InvalidDataException("Missing texture importer: " + item.assetPath);
        importer.textureType = TextureImporterType.Sprite;
        importer.spriteImportMode = SpriteImportMode.Single;
        importer.spritePixelsPerUnit = 100;
        importer.spriteBorder = new Vector4(item.borderLeft, item.borderBottom, item.borderRight, item.borderTop);
        importer.npotScale = TextureImporterNPOTScale.None;
        importer.maxTextureSize = 4096;
        importer.textureCompression = TextureImporterCompression.Uncompressed;
        importer.crunchedCompression = false;
        importer.mipmapEnabled = false;
        importer.sRGBTexture = true;
        importer.alphaSource = TextureImporterAlphaSource.FromInput;
        // Preserve source transparent RGB too; do not dilate/key/repaint this preview.
        importer.alphaIsTransparency = false;
        importer.isReadable = true; // Explicit preview convention, enables real imported-alpha verification.
        importer.filterMode = FilterMode.Bilinear;
        importer.wrapMode = TextureWrapMode.Clamp;
        importer.anisoLevel = 0;
        var settings = new TextureImporterSettings();
        importer.ReadTextureSettings(settings);
        settings.spriteAlignment = (int)SpriteAlignment.Custom;
        settings.spritePivot = new Vector2(item.pivotX, item.pivotY);
        settings.spriteMeshType = SpriteMeshType.FullRect;
        importer.SetTextureSettings(settings);
        var platform = importer.GetDefaultPlatformTextureSettings();
        platform.maxTextureSize = 4096;
        platform.format = TextureImporterFormat.RGBA32;
        platform.textureCompression = TextureImporterCompression.Uncompressed;
        importer.SetPlatformTextureSettings(platform);
        importer.SaveAndReimport();
    }

    private static AssetResult Verify(Item item)
    {
        var importer = AssetImporter.GetAtPath(item.assetPath) as TextureImporter;
        var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(item.assetPath);
        if (importer == null || texture == null) throw new InvalidDataException("Imported texture missing: " + item.assetPath);
        int sw, sh;
        importer.GetSourceTextureWidthAndHeight(out sw, out sh);
        var sprites = AssetDatabase.LoadAllAssetsAtPath(item.assetPath).OfType<Sprite>().ToArray();
        var r = new AssetResult {
            id = item.id, category = item.category, assetPath = item.assetPath,
            sha256 = Hash(item.assetPath), sourceWidth = sw, sourceHeight = sh,
            importedWidth = texture.width, importedHeight = texture.height,
            textureFormat = texture.format.ToString(), spriteCount = sprites.Length,
            sourceHasAlpha = importer.DoesSourceTextureHaveAlpha(), maximumTextureSize = importer.maxTextureSize,
            expectedPivotX = item.pivotX * item.width, expectedPivotY = item.pivotY * item.height
        };
        foreach (var p in texture.GetPixels32()) {
            if (p.a == 0) r.alphaZero++;
            if (p.a == 1) r.alphaOne++;
            if (p.a > 0 && p.a < 255) r.alphaSemi++;
            if (p.a == 255) r.alphaOpaque++;
        }
        r.bytesMatchSource = r.sha256 == item.sourceSha256;
        r.nativeDimensionsMatch = sw == item.width && sh == item.height && texture.width == item.width && texture.height == item.height;
        r.alphaCountsMatch = r.alphaZero == item.sourceAlphaZero && r.alphaOne == item.sourceAlphaOne && r.alphaSemi == item.sourceAlphaSemi && r.alphaOpaque == item.sourceAlphaOpaque;
        r.settingsMatch = importer.textureType == TextureImporterType.Sprite && importer.spriteImportMode == SpriteImportMode.Single
            && importer.npotScale == TextureImporterNPOTScale.None && importer.maxTextureSize >= 2048
            && importer.textureCompression == TextureImporterCompression.Uncompressed && !importer.mipmapEnabled
            && importer.sRGBTexture && importer.alphaSource == TextureImporterAlphaSource.FromInput
            && !importer.alphaIsTransparency && texture.format == TextureFormat.RGBA32;
        if (sprites.Length == 1) {
            var sprite = sprites[0];
            r.spritePivotX = sprite.pivot.x; r.spritePivotY = sprite.pivot.y; r.pixelsPerUnit = sprite.pixelsPerUnit;
            r.pivotMatch = Mathf.Abs(r.spritePivotX - r.expectedPivotX) < 0.01f && Mathf.Abs(r.spritePivotY - r.expectedPivotY) < 0.01f;
            r.oneFullRectSprite = Mathf.Abs(sprite.rect.width - item.width) < 0.01f && Mathf.Abs(sprite.rect.height - item.height) < 0.01f && Mathf.Abs(sprite.pixelsPerUnit - 100) < 0.001f;
        }
        r.sourceRecordBytesMatch = File.Exists(item.packageRecordPath) && Hash(item.packageRecordPath) == item.sourceRecordSha256;
        if (sprites.Length == 1) {
            r.spriteBorder = sprites[0].border;
            r.borderMatches = (r.spriteBorder - new Vector4(item.borderLeft, item.borderBottom, item.borderRight, item.borderTop)).sqrMagnitude < 0.001f;
        }
        r.passed = r.bytesMatchSource && r.nativeDimensionsMatch && r.alphaCountsMatch && r.sourceHasAlpha && r.settingsMatch && r.pivotMatch && r.oneFullRectSprite && r.borderMatches && r.sourceRecordBytesMatch;
        return r;
    }


    [Serializable] public class RenderImageResult
    {
        public string id, file, sha256, drawMode;
        public int width, height, pixelsAboveAlpha16;
        public Vector4 border;
        public bool nonempty;
    }
    [Serializable] public class RenderReport
    {
        public string schema = "wuxing.unity_ui_sliced_gpu_render.v1";
        public string renderedAtUtc, unityVersion, graphicsDeviceType, graphicsDeviceName, graphicsDeviceVersion, colorSpace, error;
        public bool batchMode, commandLineUsedNographics, attempted, supported, passed, clientVerified = false;
        public int expectedImageCount = 48;
        public List<RenderImageResult> images = new List<RenderImageResult>();
    }
    private static string Portable(Config cfg, string path)
    {
        var value = path.Replace('\\', '/');
        var root = cfg.projectRoot.Replace('\\', '/').TrimEnd('/') + "/";
        return value.StartsWith(root, StringComparison.OrdinalIgnoreCase) ? value.Substring(root.Length) : value;
    }
    private static RenderImageResult RenderOne(Config cfg, Item item, int width, int height)
    {
        var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(item.assetPath);
        if (sprite == null) throw new InvalidDataException("No Sprite for sliced render: " + item.id);
        var shader = Shader.Find("Sprites/Default");
        if (shader == null) throw new InvalidDataException("Builtin Sprites/Default shader missing");
        var go = new GameObject("SlicedQA-" + item.id);
        go.layer = 31;
        var renderer = go.AddComponent<SpriteRenderer>();
        renderer.sprite = sprite;
        renderer.color = Color.white;
        renderer.drawMode = SpriteDrawMode.Sliced;
        renderer.size = new Vector2(width / 100f, height / 100f);
        var material = new Material(shader);
        renderer.sharedMaterial = material;
        var cameraGo = new GameObject("SlicedQA-Camera");
        var camera = cameraGo.AddComponent<Camera>();
        camera.enabled = false;
        camera.transform.position = new Vector3(0, 0, -10);
        camera.orthographic = true;
        camera.orthographicSize = height / 200f;
        camera.aspect = width / (float)height;
        camera.nearClipPlane = 0.1f;
        camera.farClipPlane = 100f;
        camera.cullingMask = 1 << 31;
        camera.clearFlags = CameraClearFlags.SolidColor;
        camera.backgroundColor = new Color(0, 0, 0, 0);
        camera.allowHDR = false;
        camera.allowMSAA = false;
        var target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
        target.antiAliasing = 1;
        target.Create();
        camera.targetTexture = target;
        var previous = RenderTexture.active;
        Texture2D readback = null;
        try {
            camera.Render();
            RenderTexture.active = target;
            readback = new Texture2D(width, height, TextureFormat.RGBA32, false, false);
            readback.ReadPixels(new Rect(0, 0, width, height), 0, 0, false);
            readback.Apply(false, false);
            var file = Path.Combine(cfg.renderOutputDir, item.id + "-" + width + "x" + height + ".png");
            if (File.Exists(file)) throw new IOException("Refusing to overwrite render PNG: " + file);
            File.WriteAllBytes(file, readback.EncodeToPNG());
            var result = new RenderImageResult { id = item.id, file = Portable(cfg, file), sha256 = Hash(file),
                drawMode = renderer.drawMode.ToString(), width = width, height = height, border = sprite.border };
            foreach (var pixel in readback.GetPixels32()) if (pixel.a > 16) result.pixelsAboveAlpha16++;
            result.nonempty = result.pixelsAboveAlpha16 > 0;
            return result;
        } finally {
            RenderTexture.active = previous;
            camera.targetTexture = null;
            target.Release();
            UnityEngine.Object.DestroyImmediate(target);
            if (readback != null) UnityEngine.Object.DestroyImmediate(readback);
            UnityEngine.Object.DestroyImmediate(cameraGo);
            UnityEngine.Object.DestroyImmediate(go);
            UnityEngine.Object.DestroyImmediate(material);
        }
    }
    private static void RenderSlices(Config cfg)
    {
        var result = new RenderReport { renderedAtUtc = DateTime.UtcNow.ToString("o"), unityVersion = Application.unityVersion,
            batchMode = Application.isBatchMode, graphicsDeviceType = SystemInfo.graphicsDeviceType.ToString(),
            graphicsDeviceName = SystemInfo.graphicsDeviceName, graphicsDeviceVersion = SystemInfo.graphicsDeviceVersion,
            colorSpace = QualitySettings.activeColorSpace.ToString(), commandLineUsedNographics = Environment.GetCommandLineArgs().Contains("-nographics") };
        try {
            result.attempted = true;
            result.supported = !result.commandLineUsedNographics && SystemInfo.graphicsDeviceType != UnityEngine.Rendering.GraphicsDeviceType.Null;
            if (!result.supported) throw new NotSupportedException("No actual graphics device for Camera.Render; sliced render NOT verified");
            Directory.CreateDirectory(cfg.renderOutputDir);
            QualitySettings.antiAliasing = 0;
            var selected = cfg.assets.Where(a => a.renderSlice).ToArray();
            if (selected.Length != 16) throw new InvalidDataException("Expected16 UI sliced candidates");
            foreach (var item in selected) {
                result.images.Add(RenderOne(cfg, item, 500, 204));
                result.images.Add(RenderOne(cfg, item, 900, 204));
                result.images.Add(RenderOne(cfg, item, 500, 300));
            }
            result.passed = result.images.Count == 48 && result.images.All(x => x.nonempty);
        } catch (Exception e) {
            result.error = e.GetType().Name + ": " + e.Message;
            result.passed = false;
            Debug.LogWarning("Sliced GPU render unverified: " + result.error);
        }
        Directory.CreateDirectory(Path.GetDirectoryName(cfg.renderReportPath));
        File.WriteAllText(cfg.renderReportPath, JsonUtility.ToJson(result, true));
    }

    private static void Run(bool roundtrip)
    {
        Config cfg = null;
        var report = new Report { verifiedAtUtc = DateTime.UtcNow.ToString("o"), unityVersion = Application.unityVersion,
            batchMode = Application.isBatchMode, graphicsDeviceIsNull = SystemInfo.graphicsDeviceType == UnityEngine.Rendering.GraphicsDeviceType.Null,
            mode = roundtrip ? "fresh_project_package_import_and_verification" : "source_import_validation_and_export" };
        try {
            cfg = ReadConfig();
            if (cfg.assets == null || cfg.assets.Length != 111) throw new InvalidDataException("Expected exactly 111 Sprite PNGs");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            if (!roundtrip) foreach (var item in cfg.assets) Configure(item);
            foreach (var item in cfg.assets) report.assets.Add(Verify(item));
            report.spriteFileCount = report.assets.Count;
            if (report.assets.Any(a => !a.passed)) throw new InvalidDataException("At least one asset import verification failed; inspect asset results");
            if (!roundtrip) {
                RenderSlices(cfg);
                if (File.Exists(cfg.outputPackage)) throw new IOException("Refusing to overwrite existing package");
                AssetDatabase.ExportPackage(cfg.exportRoot, cfg.outputPackage, ExportPackageOptions.Recurse);
            }
            if (!File.Exists(cfg.outputPackage)) throw new FileNotFoundException("Unity package not written");
            report.packageFile = Path.GetFileName(cfg.outputPackage);
            report.packageSha256 = Hash(cfg.outputPackage);
            report.packageBytes = new FileInfo(cfg.outputPackage).Length;
            report.passed = report.packageBytes > 0;
            Directory.CreateDirectory(Path.GetDirectoryName(cfg.reportPath));
            File.WriteAllText(cfg.reportPath, JsonUtility.ToJson(report, true));
            Debug.Log("WUXING_PREVIEW_VERIFIED " + report.spriteFileCount + " sprites; mode=" + report.mode + "; unity=" + report.unityVersion);
            EditorApplication.Exit(0);
        } catch (Exception e) {
            report.error = e.GetType().Name + ": " + e.Message;
            report.passed = false;
            if (cfg != null) File.WriteAllText(cfg.reportPath, JsonUtility.ToJson(report, true));
            Debug.LogException(e);
            EditorApplication.Exit(1);
        }
    }
}
