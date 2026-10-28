// Editor-only FX package builder. Sprite PNGs are copied by a separate preparation step.
// Build: -batchmode -nographics -executeMethod BuildWuxingFXAnimationPreview.Build
// Roundtrip: use ImportAndVerify without -quit; it waits for the import completion event.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

public static class BuildWuxingFXAnimationPreview
{
    [Serializable] public class Frame {
        public string id, effect, source, record, sourceSha256, assetPath;
        public int width, height, alphaZero, alphaOne, alphaSemi, alphaOpaque;
        public float pivotX, pivotY;
    }
    [Serializable] public class ClipInput {
        public string id, assetPath, manifest;
        public string[] framePaths;
        public float durationSeconds, frameDurationSeconds;
    }
    [Serializable] public class Config {
        public string outputPackage, reportPath, exportRoot;
        public Frame[] frames;
        public ClipInput[] clips;
    }
    [Serializable] public class FrameResult {
        public string id, effect, assetPath, sha256, textureFormat;
        public int width, height, spriteCount, alphaZero, alphaOne, alphaSemi, alphaOpaque;
        public float pivotX, pivotY;
        public bool bytesMatch, dimensionsMatch, alphaCountsMatch, pivotMatch, settingsMatch, passed;
    }
    [Serializable] public class ClipResult {
        public string id, assetPath, bindingPath, bindingType, bindingProperty;
        public int objectKeyCount, uniqueSpriteCount, eventCount;
        public float durationSeconds, frameRate, terminalFrameKeyTimeSeconds, effectiveHoldUntilSeconds;
        public float[] times;
        public string[] referencedSpritePaths;
        public bool oneSpriteBinding, orderedEightUniqueFrameKeys, holdUsesAutomaticFinalSampleDuration, loopTime, passed;
    }
    [Serializable] public class Report {
        public string schema="wuxing.unity_fx_animation_preview_validation.v1", verifiedAtUtc, unityVersion, mode, packageFile, packageSha256, error;
        public bool passed, batchMode, graphicsDeviceIsNull, clientIntegrated=false;
        public long packageBytes;
        public int spriteFileCount, animationClipCount;
        public List<FrameResult> frames=new List<FrameResult>();
        public List<ClipResult> clips=new List<ClipResult>();
    }
    private static Config pending;
    private static double importStarted;
    private static string Hash(string p) {
        using(var sha=SHA256.Create()) using(var stream=File.OpenRead(p))
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
    }
    private static Config ReadConfig() {
        var args=Environment.GetCommandLineArgs(); var i=Array.IndexOf(args,"-wuxingFXConfig");
        if(i<0||i+1>=args.Length)throw new ArgumentException("Missing -wuxingFXConfig");
        return JsonUtility.FromJson<Config>(File.ReadAllText(args[i+1]));
    }
    public static void Build() { Run(false); }
    public static void ExportVerifiedExisting() { Run(false,true); }
    public static void CompileProbe() {
        var clip=new AnimationClip();var settings=AnimationUtility.GetAnimationClipSettings(clip);
        settings.loopTime=false;AnimationUtility.SetAnimationClipSettings(clip,settings);
        Debug.Log("WUXING_FX_COMPILE_PROBE "+Application.unityVersion);EditorApplication.Exit(0);
    }
    [Serializable] public class TimingCase { public float requestedLastKey, clipLength, stopTime; public int keyCount; }
    [Serializable] public class TimingCases { public string unityVersion; public List<TimingCase> cases=new List<TimingCase>(); }
    public static void TimingProbe() {
        var cfg=ReadConfig();var sample=cfg.clips[0];var cases=new TimingCases{unityVersion=Application.unityVersion};
        foreach(var last in new[]{.7f}) {
            var clip=new AnimationClip{frameRate=10};var keys=new ObjectReferenceKeyframe[8];
            for(int i=0;i<8;i++)keys[i]=new ObjectReferenceKeyframe{time=i*.1f,value=AssetDatabase.LoadAssetAtPath<Sprite>(sample.framePaths[i])};
            AnimationUtility.SetObjectReferenceCurve(clip,Binding(),keys);var settings=AnimationUtility.GetAnimationClipSettings(clip);settings.stopTime=.8f;AnimationUtility.SetAnimationClipSettings(clip,settings);
            cases.cases.Add(new TimingCase{requestedLastKey=last,clipLength=clip.length,stopTime=AnimationUtility.GetAnimationClipSettings(clip).stopTime,keyCount=AnimationUtility.GetObjectReferenceCurve(clip,Binding()).Length});
        }
        File.WriteAllText(Path.Combine(Path.GetDirectoryName(cfg.reportPath),"unity-fx-timing-probe-20261027.json"),JsonUtility.ToJson(cases,true));EditorApplication.Exit(0);
    }
    public static void ImportAndVerify() {
        pending=ReadConfig(); importStarted=EditorApplication.timeSinceStartup;
        AssetDatabase.importPackageCompleted+=Imported; AssetDatabase.importPackageFailed+=ImportFailed;
        AssetDatabase.importPackageCancelled+=Cancelled; EditorApplication.update+=Timeout;
        AssetDatabase.ImportPackage(pending.outputPackage,false);
    }
    private static void Clear() {
        AssetDatabase.importPackageCompleted-=Imported; AssetDatabase.importPackageFailed-=ImportFailed;
        AssetDatabase.importPackageCancelled-=Cancelled; EditorApplication.update-=Timeout;
    }
    private static void Imported(string name) { Clear(); EditorApplication.delayCall+=()=>Run(true); }
    private static void Cancelled(string name) { ImportFailed(name,"cancelled"); }
    private static void Timeout() { if(EditorApplication.timeSinceStartup-importStarted>180)ImportFailed("preview","import completion timeout"); }
    private static void ImportFailed(string name,string error) {
        Clear(); File.WriteAllText(pending.reportPath,JsonUtility.ToJson(new Report{verifiedAtUtc=DateTime.UtcNow.ToString("o"),unityVersion=Application.unityVersion,mode="package_import",error=error,passed=false},true)); EditorApplication.Exit(1);
    }
    private static void Configure(Frame frame) {
        var t=AssetImporter.GetAtPath(frame.assetPath) as TextureImporter;
        if(t==null)throw new InvalidDataException("Missing texture importer: "+frame.assetPath);
        t.textureType=TextureImporterType.Sprite; t.spriteImportMode=SpriteImportMode.Single;
        t.spritePixelsPerUnit=100; t.npotScale=TextureImporterNPOTScale.None; t.maxTextureSize=4096;
        t.textureCompression=TextureImporterCompression.Uncompressed; t.crunchedCompression=false;
        t.mipmapEnabled=false; t.sRGBTexture=true; t.alphaSource=TextureImporterAlphaSource.FromInput;
        t.alphaIsTransparency=false; t.isReadable=true; t.wrapMode=TextureWrapMode.Clamp; t.filterMode=FilterMode.Bilinear;
        var settings=new TextureImporterSettings();t.ReadTextureSettings(settings);
        settings.spriteAlignment=(int)SpriteAlignment.Custom; settings.spritePivot=new Vector2(frame.pivotX,frame.pivotY);
        settings.spriteMeshType=SpriteMeshType.FullRect;t.SetTextureSettings(settings);
        var platform=t.GetDefaultPlatformTextureSettings();platform.maxTextureSize=4096;platform.format=TextureImporterFormat.RGBA32;
        platform.textureCompression=TextureImporterCompression.Uncompressed;t.SetPlatformTextureSettings(platform);t.SaveAndReimport();
    }
    private static FrameResult VerifyFrame(Frame frame) {
        var t=AssetImporter.GetAtPath(frame.assetPath) as TextureImporter;
        var texture=AssetDatabase.LoadAssetAtPath<Texture2D>(frame.assetPath);
        if(t==null||texture==null)throw new InvalidDataException("Missing texture: "+frame.assetPath);
        var sprites=AssetDatabase.LoadAllAssetsAtPath(frame.assetPath).OfType<Sprite>().ToArray();
        var r=new FrameResult{id=frame.id,effect=frame.effect,assetPath=frame.assetPath,sha256=Hash(frame.assetPath),width=texture.width,height=texture.height,spriteCount=sprites.Length,textureFormat=texture.format.ToString()};
        foreach(var p in texture.GetPixels32()) {if(p.a==0)r.alphaZero++;if(p.a==1)r.alphaOne++;if(p.a>0&&p.a<255)r.alphaSemi++;if(p.a==255)r.alphaOpaque++;}
        r.bytesMatch=r.sha256==frame.sourceSha256;r.dimensionsMatch=r.width==frame.width&&r.height==frame.height;
        r.alphaCountsMatch=r.alphaZero==frame.alphaZero&&r.alphaOne==frame.alphaOne&&r.alphaSemi==frame.alphaSemi&&r.alphaOpaque==frame.alphaOpaque;
        r.settingsMatch=t.textureType==TextureImporterType.Sprite&&t.spriteImportMode==SpriteImportMode.Single&&t.npotScale==TextureImporterNPOTScale.None&&t.maxTextureSize>=2048&&t.textureCompression==TextureImporterCompression.Uncompressed&&!t.mipmapEnabled&&t.sRGBTexture&&t.alphaSource==TextureImporterAlphaSource.FromInput&&!t.alphaIsTransparency&&t.DoesSourceTextureHaveAlpha()&&texture.format==TextureFormat.RGBA32;
        if(sprites.Length==1) {var sp=sprites[0];r.pivotX=sp.pivot.x;r.pivotY=sp.pivot.y;r.pivotMatch=Mathf.Abs(sp.pivot.x-frame.pivotX*frame.width)<.01f&&Mathf.Abs(sp.pivot.y-frame.pivotY*frame.height)<.01f&&Mathf.Abs(sp.rect.width-frame.width)<.01f&&Mathf.Abs(sp.rect.height-frame.height)<.01f&&Mathf.Abs(sp.pixelsPerUnit-100)<.001f;}
        r.passed=r.bytesMatch&&r.dimensionsMatch&&r.alphaCountsMatch&&r.settingsMatch&&r.pivotMatch&&r.spriteCount==1;return r;
    }
    private static EditorCurveBinding Binding() {return EditorCurveBinding.PPtrCurve("",typeof(SpriteRenderer),"m_Sprite");}
    private static void CreateClip(ClipInput input) {
        if(File.Exists(input.assetPath))throw new IOException("Refusing to overwrite clip: "+input.assetPath);
        var directory=Path.GetDirectoryName(input.assetPath).Replace('\\','/');
        if(!AssetDatabase.IsValidFolder(directory))AssetDatabase.CreateFolder(Path.GetDirectoryName(directory).Replace('\\','/'),Path.GetFileName(directory));
        var clip=new AnimationClip{name=input.id,frameRate=10,legacy=false,wrapMode=WrapMode.Once};
        var keys=new ObjectReferenceKeyframe[8];
        // Unity object-reference clips include one sample interval after their last key.
        // Eight unique keys at0..0.7s naturally hold frame07 through the real0.8s end.
        for(int i=0;i<8;i++)keys[i]=new ObjectReferenceKeyframe{time=i*input.frameDurationSeconds,value=AssetDatabase.LoadAssetAtPath<Sprite>(input.framePaths[i])};
        if(keys.Any(k=>k.value==null))throw new InvalidDataException("Sprite reference missing before clip creation");
        AssetDatabase.CreateAsset(clip,input.assetPath);AnimationUtility.SetObjectReferenceCurve(clip,Binding(),keys);
        var settings=AnimationUtility.GetAnimationClipSettings(clip);settings.loopTime=false;settings.loopBlend=false;settings.startTime=0;settings.stopTime=input.durationSeconds;AnimationUtility.SetAnimationClipSettings(clip,settings);
        AnimationUtility.SetAnimationEvents(clip,new AnimationEvent[0]);EditorUtility.SetDirty(clip);
    }
    private static ClipResult VerifyClip(ClipInput input) {
        var clip=AssetDatabase.LoadAssetAtPath<AnimationClip>(input.assetPath);if(clip==null)throw new InvalidDataException("Clip missing: "+input.assetPath);
        var bindings=AnimationUtility.GetObjectReferenceCurveBindings(clip);var keys=AnimationUtility.GetObjectReferenceCurve(clip,Binding());
        if(keys==null)keys=new ObjectReferenceKeyframe[0];
        var r=new ClipResult{id=input.id,assetPath=input.assetPath,durationSeconds=clip.length,frameRate=clip.frameRate,objectKeyCount=keys.Length,eventCount=AnimationUtility.GetAnimationEvents(clip).Length,loopTime=AnimationUtility.GetAnimationClipSettings(clip).loopTime,times=keys.Select(k=>k.time).ToArray(),referencedSpritePaths=keys.Select(k=>AssetDatabase.GetAssetPath(k.value)).ToArray()};
        r.uniqueSpriteCount=r.referencedSpritePaths.Distinct().Count();
        if(bindings.Length==1){r.bindingPath=bindings[0].path;r.bindingType=bindings[0].type.FullName;r.bindingProperty=bindings[0].propertyName;r.oneSpriteBinding=bindings[0].path==""&&bindings[0].type==typeof(SpriteRenderer)&&bindings[0].propertyName=="m_Sprite";}
        r.orderedEightUniqueFrameKeys=keys.Length==8;
        for(int i=0;i<keys.Length;i++){var expected=i*input.frameDurationSeconds;if(i>7||Mathf.Abs(keys[i].time-expected)>.0001f||r.referencedSpritePaths[i]!=input.framePaths[Math.Min(i,7)])r.orderedEightUniqueFrameKeys=false;}
        r.terminalFrameKeyTimeSeconds=keys.Length==8?keys[7].time:-1;r.effectiveHoldUntilSeconds=clip.length;
        r.holdUsesAutomaticFinalSampleDuration=Mathf.Abs(clip.length-r.terminalFrameKeyTimeSeconds-input.frameDurationSeconds)<.0001f;
        r.passed=r.oneSpriteBinding&&r.orderedEightUniqueFrameKeys&&r.holdUsesAutomaticFinalSampleDuration&&r.uniqueSpriteCount==8&&!r.loopTime&&r.eventCount==0&&Mathf.Abs(clip.length-.8f)<.0001f&&Mathf.Abs(clip.frameRate-10)<.0001f;return r;
    }
    private static void Run(bool roundtrip,bool existing=false) {
        Config cfg=null;var report=new Report{verifiedAtUtc=DateTime.UtcNow.ToString("o"),unityVersion=Application.unityVersion,mode=roundtrip?"independent_package_import":(existing?"verified_existing_clips_export":"source_import_clip_creation_export"),batchMode=Application.isBatchMode,graphicsDeviceIsNull=SystemInfo.graphicsDeviceType==UnityEngine.Rendering.GraphicsDeviceType.Null};
        try {
            cfg=ReadConfig();if(cfg.frames.Length!=64||cfg.clips.Length!=8)throw new InvalidDataException("Expected64 frames and8 clips");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            if(!roundtrip&&!existing){foreach(var f in cfg.frames)Configure(f);foreach(var c in cfg.clips)CreateClip(c);AssetDatabase.SaveAssets();AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);}
            foreach(var f in cfg.frames)report.frames.Add(VerifyFrame(f));foreach(var c in cfg.clips)report.clips.Add(VerifyClip(c));
            report.spriteFileCount=report.frames.Count;report.animationClipCount=report.clips.Count;
            if(report.frames.Any(f=>!f.passed)||report.clips.Any(c=>!c.passed))throw new InvalidDataException("At least one frame/clip verification failed");
            if(!roundtrip){if(File.Exists(cfg.outputPackage))throw new IOException("Refusing to overwrite package");AssetDatabase.ExportPackage(cfg.exportRoot,cfg.outputPackage,ExportPackageOptions.Recurse);}
            report.packageFile=Path.GetFileName(cfg.outputPackage);report.packageBytes=new FileInfo(cfg.outputPackage).Length;report.packageSha256=Hash(cfg.outputPackage);report.passed=report.packageBytes>0;
            File.WriteAllText(cfg.reportPath,JsonUtility.ToJson(report,true));Debug.Log("WUXING_FX_VERIFIED 64 sprites8 clips; mode="+report.mode+"; unity="+report.unityVersion);EditorApplication.Exit(0);
        }catch(Exception e){report.error=e.GetType().Name+": "+e.Message;report.passed=false;if(cfg!=null)File.WriteAllText(cfg.reportPath,JsonUtility.ToJson(report,true));Debug.LogException(e);EditorApplication.Exit(1);}
    }
}
