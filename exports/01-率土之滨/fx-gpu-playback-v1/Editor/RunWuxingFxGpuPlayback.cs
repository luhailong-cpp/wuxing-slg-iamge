using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;

[InitializeOnLoad]
public static class RunWuxingFxGpuPlayback
{
    [Serializable] public class Clip { public string id,assetPath; public string[] framePaths; }
    [Serializable] public class Effect { public string id; public int[] canvas; public float[] anchorNormalizedTopLeft; }
    [Serializable] public class Index { public Clip[] clips; public Effect[] effects; }
    [Serializable] public class BuildReport { public bool passed;public string error,unityVersion,verifiedAtUtc,sourcePackageSha256,demoPackageSha256;public long demoPackageBytes;public int clipCount=8;public bool actualPlayModeGPU=true; }
    static RunWuxingFxGpuPlayback() { EditorApplication.playModeStateChanged+=Changed; }
    private static string Hash(string p) { using(var h=SHA256.Create())using(var f=File.OpenRead(p))return BitConverter.ToString(h.ComputeHash(f)).Replace("-","").ToLowerInvariant(); }
    private static WuxingFxGpuPlaybackDemo.Config Config() {return JsonUtility.FromJson<WuxingFxGpuPlaybackDemo.Config>(File.ReadAllText(SessionState.GetString("WuxingFxGpuConfig","")));}
    public static void Run() {
        var args=Environment.GetCommandLineArgs();int n=Array.IndexOf(args,"-fxGpuConfig");if(n<0)throw new ArgumentException("Missing -fxGpuConfig");
        SessionState.SetString("WuxingFxGpuConfig",args[n+1]);SessionState.SetBool("WuxingFxGpuPlaybackDone",false);SessionState.SetBool("WuxingFxGpuActive",true);
        AssetDatabase.importPackageCompleted+=Imported;AssetDatabase.importPackageFailed+=ImportFailed;AssetDatabase.ImportPackage(Config().package,false);
    }
    private static void ImportFailed(string name,string error) { WriteError("FX dependency import failed: "+error); }
    private static void Imported(string name) {
        AssetDatabase.importPackageCompleted-=Imported;AssetDatabase.importPackageFailed-=ImportFailed;
        try {
            var cfg=Config();var index=JsonUtility.FromJson<Index>(File.ReadAllText(cfg.sourceIndex));if(index.clips.Length!=8)throw new InvalidDataException("Expected8 clips");
            const string root="Assets/WuxingSLGFXGpuPlaybackDemo";Directory.CreateDirectory(root+"/Controllers");
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);var go=new GameObject("WuxingActualFxGpuPlaybackDemo");var demo=go.AddComponent<WuxingFxGpuPlaybackDemo>();
            demo.effects=index.clips.Select(c=> {
                var controller=AnimatorController.CreateAnimatorControllerAtPath(root+"/Controllers/"+c.id+".controller");var state=controller.layers[0].stateMachine.AddState("Play");state.motion=AssetDatabase.LoadAssetAtPath<AnimationClip>(c.assetPath);controller.layers[0].stateMachine.defaultState=state;
                var e=index.effects.Single(x=>x.id==c.id);return new WuxingFxGpuPlaybackDemo.FxCase{id=c.id,clipPath=c.assetPath,clip=state.motion as AnimationClip,controller=controller,expectedSprites=c.framePaths.Select(p=>AssetDatabase.LoadAssetAtPath<Sprite>(p)).ToArray(),framePaths=c.framePaths,canvasWidth=e.canvas[0],canvasHeight=e.canvas[1],sourceAnchorTopLeft=new Vector2(e.anchorNormalizedTopLeft[0],e.anchorNormalizedTopLeft[1])};
            }).ToArray();
            EditorSceneManager.SaveScene(scene,root+"/FXGpuPlayback.unity");AssetDatabase.SaveAssets();SessionState.SetBool("WuxingFxGpuPrepared",true);EditorApplication.isPlaying=true;
        }catch(Exception e){WriteError(e.ToString());}
    }
    private static void Changed(PlayModeStateChange state) {
        if(state!=PlayModeStateChange.EnteredEditMode||!SessionState.GetBool("WuxingFxGpuActive",false)||!SessionState.GetBool("WuxingFxGpuPlaybackDone",false))return;
        try {
            var cfg=Config();var text=File.ReadAllText(cfg.reportPath);bool passed=JsonUtility.FromJson<MinimalReport>(text).passed;
            if(!passed)throw new InvalidDataException("Actual GPU playback result did not pass; inspect capture report");
            if(File.Exists(cfg.outputDemoPackage))throw new IOException("Refusing overwrite demo package");
            // No IncludeDependencies: existing FX assets retain their original GUIDs in the separately required source package.
            AssetDatabase.ExportPackage("Assets/WuxingSLGFXGpuPlaybackDemo",cfg.outputDemoPackage,ExportPackageOptions.Recurse);
            var r=new BuildReport{passed=true,verifiedAtUtc=DateTime.UtcNow.ToString("o"),unityVersion=Application.unityVersion,sourcePackageSha256=Hash(cfg.package),demoPackageSha256=Hash(cfg.outputDemoPackage),demoPackageBytes=new FileInfo(cfg.outputDemoPackage).Length};
            File.WriteAllText(cfg.bootstrapReport,JsonUtility.ToJson(r,true));SessionState.SetBool("WuxingFxGpuActive",false);EditorApplication.Exit(0);
        }catch(Exception e){WriteError(e.ToString());}
    }
    [Serializable] private class MinimalReport { public bool passed; }
    private static void WriteError(string error) { var cfg=Config();File.WriteAllText(cfg.bootstrapReport,JsonUtility.ToJson(new BuildReport{passed=false,error=error,verifiedAtUtc=DateTime.UtcNow.ToString("o"),unityVersion=Application.unityVersion},true));Debug.LogError(error);EditorApplication.Exit(1); }
}
