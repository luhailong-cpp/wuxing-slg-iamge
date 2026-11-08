using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;

[InitializeOnLoad]
public static class VerifyWuxingFxGpuDemoImport
{
    [Serializable] public class Config { public string sourcePackage,demoPackage,reportPath; }
    [Serializable] public class Report { public string verifiedAtUtc,unityVersion,error,sourcePackageSha256,demoPackageSha256;public bool passed,freshProjectDependencyThenDemoActualImportVerified,clientIntegrated=false;public int resolvedCases,resolvedClipReferences,resolvedControllerReferences,resolvedSpriteReferences; }
    static VerifyWuxingFxGpuDemoImport(){EditorApplication.update+=Tick;}
    private static Config Read(){return JsonUtility.FromJson<Config>(File.ReadAllText(SessionState.GetString("FxDemoImportConfig","")));}
    private static string Hash(string p){using(var h=SHA256.Create())using(var f=File.OpenRead(p))return BitConverter.ToString(h.ComputeHash(f)).Replace("-","").ToLowerInvariant();}
    public static void Run(){var args=Environment.GetCommandLineArgs();int n=Array.IndexOf(args,"-fxDemoImportConfig");if(n<0)throw new ArgumentException("Missing config");SessionState.SetString("FxDemoImportConfig",args[n+1]);SessionState.SetString("FxDemoImportStage","source");SessionState.SetFloat("FxDemoImportStarted",(float)EditorApplication.timeSinceStartup);AssetDatabase.importPackageCompleted+=SourceImported;AssetDatabase.ImportPackage(Read().sourcePackage,false);}
    private static void SourceImported(string name){AssetDatabase.importPackageCompleted-=SourceImported;SessionState.SetString("FxDemoImportStage","demo");AssetDatabase.ImportPackage(Read().demoPackage,false);}
    private static void Tick(){
        var stage=SessionState.GetString("FxDemoImportStage","");if(stage==""||stage=="done")return;
        if(EditorApplication.timeSinceStartup-SessionState.GetFloat("FxDemoImportStarted",0)>240){Verify("Import timeout");return;}
        if(stage!="demo"||EditorApplication.isCompiling||EditorApplication.isUpdating)return;
        var script=AssetDatabase.LoadAssetAtPath<MonoScript>("Assets/WuxingSLGFXGpuPlaybackDemo/Runtime/WuxingFxGpuPlaybackDemo.cs");
        if(script==null||script.GetClass()==null||AssetDatabase.LoadAssetAtPath<SceneAsset>("Assets/WuxingSLGFXGpuPlaybackDemo/FXGpuPlayback.unity")==null)return;
        Verify(null);
    }
    private static void Verify(string initialError){
        SessionState.SetString("FxDemoImportStage","done");var cfg=Read();var r=new Report{verifiedAtUtc=DateTime.UtcNow.ToString("o"),unityVersion=Application.unityVersion,sourcePackageSha256=Hash(cfg.sourcePackage),demoPackageSha256=Hash(cfg.demoPackage)};
        try{
            if(initialError!=null)throw new InvalidDataException(initialError);
            var scene=EditorSceneManager.OpenScene("Assets/WuxingSLGFXGpuPlaybackDemo/FXGpuPlayback.unity",OpenSceneMode.Single);
            var demo=scene.GetRootGameObjects().SelectMany(g=>g.GetComponents<MonoBehaviour>()).Single(m=>m!=null&&m.GetType().Name=="WuxingFxGpuPlaybackDemo");
            var data=new SerializedObject(demo);var effects=data.FindProperty("effects");if(effects.arraySize!=8)throw new InvalidDataException("Expected8 resolved effect cases");
            for(int n=0;n<effects.arraySize;n++){
                var e=effects.GetArrayElementAtIndex(n);var clip=e.FindPropertyRelative("clip").objectReferenceValue as AnimationClip;var cp=e.FindPropertyRelative("clipPath").stringValue;
                if(clip==null||clip!=AssetDatabase.LoadAssetAtPath<AnimationClip>(cp))throw new InvalidDataException("Clip dependency missing");r.resolvedClipReferences++;
                var controller=e.FindPropertyRelative("controller").objectReferenceValue as AnimatorController;if(controller==null||controller.animationClips.Length!=1||controller.animationClips[0]!=clip)throw new InvalidDataException("Controller dependency mismatch");r.resolvedControllerReferences++;
                var sprites=e.FindPropertyRelative("expectedSprites");var paths=e.FindPropertyRelative("framePaths");if(sprites.arraySize!=8||paths.arraySize!=8)throw new InvalidDataException("Expected8 source sprites");
                for(int j=0;j<8;j++){var s=sprites.GetArrayElementAtIndex(j).objectReferenceValue as Sprite;var path=paths.GetArrayElementAtIndex(j).stringValue;if(s==null||s!=AssetDatabase.LoadAssetAtPath<Sprite>(path))throw new InvalidDataException("Sprite dependency missing "+path);r.resolvedSpriteReferences++;}
                r.resolvedCases++;
            }
            r.passed=r.resolvedCases==8&&r.resolvedClipReferences==8&&r.resolvedControllerReferences==8&&r.resolvedSpriteReferences==64;r.freshProjectDependencyThenDemoActualImportVerified=r.passed;
        }catch(Exception e){r.error=e.ToString();r.passed=false;}
        File.WriteAllText(cfg.reportPath,JsonUtility.ToJson(r,true));EditorApplication.Exit(r.passed?0:1);
    }
}
