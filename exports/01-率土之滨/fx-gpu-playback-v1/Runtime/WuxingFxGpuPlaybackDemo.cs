using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using System.Security.Cryptography;
using UnityEngine;

// Existing clips are evaluated by real Animator Normal updates in PlayMode.
// The caller owns lifetime cleanup; the original nonlooping clips hold frame07.
public sealed class WuxingFxGpuPlaybackDemo : MonoBehaviour
{
    [Serializable] public class FxCase {
        public string id, clipPath; public AnimationClip clip;
        public RuntimeAnimatorController controller; public Sprite[] expectedSprites;
        public string[] framePaths; public int canvasWidth, canvasHeight;
        public Vector2 sourceAnchorTopLeft;
    }
    [Serializable] public class Config {
        public string projectRoot, package, sourceIndex, localRawOutput, reportPath, outputDemoPackage, bootstrapReport;
    }
    [Serializable] public class Sample {
        public string effect, background, localRawCapture, sha256, observedSpritePath;
        public int captureOrdinal, unityFrameCount, observedFrameIndex, expectedFrameIndex, pixelsDifferentFromBackground;
        public double gameElapsedSeconds, realtimeElapsedSeconds, animatorClipTimeSeconds;
        public float unityDeltaTime, animatorNormalizedTime;
        public bool rendererEnabled, animatorEnabled, callerCleared, transformAndScaleFixed, matchesClockExpectedFrame;
        public Vector3 position, localScale; public Vector2 projectedAnchorPixel, spritePivot, spriteRectSize;
    }
    [Serializable] public class Baseline { public string background, localRawCapture, sha256; public Color32 pixel; }
    [Serializable] public class EffectResult {
        public string id, clipPath; public float clipLength;
        public int[] observedFrameOrder; public bool ordered00To07, anchorAndScaleFixed, allClearCapturesEqualBackground, lastVisibleFrameIs07;
        public double firstCallerClearGameSeconds, animatorTimeAtClearSeconds;
        public int visibleCaptures, clearedCaptures;
    }
    [Serializable] public class Report {
        public string schema="wuxing.fx_actual_gpu_playmode_capture.v1", startedAtUtc, completedAtUtc, unityVersion;
        public string graphicsDeviceType, graphicsDeviceName, graphicsDeviceVersion, colorSpace, error;
        public bool playMode, graphicsEnabled, passed, performanceBenchmark=false, clientIntegrated=false, finalSmoothnessApproved=false;
        public int captureFramerate=60, capturesPerEffectPerBackground, captureWidth=512, captureHeight=512;
        public float cameraOrthographicSize=6.4f, pixelsPerUnit=100;
        public string clockPolicy="Time.captureFramerate60 fixes Unity game delta; Animator Normal automatically advances. Wall clock differs and is logged. No sprite assignment per sampled phase.";
        public string rawPolicy="Complete raw GPU PNG sequence is local work QA, intentionally unpublished; selected native captures and derived MP4/montages are published separately.";
        public string lifecyclePolicy="Caller hides renderer, disables Animator and clears Sprite at game elapsed >=0.8; source clip alone does not disappear.";
        public List<Baseline> baselines=new List<Baseline>(); public List<Sample> samples=new List<Sample>();
        public List<EffectResult> effects=new List<EffectResult>();
    }
    private sealed class Actor { public FxCase fx; public GameObject go; public Animator animator; public SpriteRenderer renderer; public bool cleared; public double clearGame=-1, clearClip=-1; }
    public FxCase[] effects;
    private Config config; private Report report; private List<Actor> actors=new List<Actor>();
    private Camera cameraQA; private RenderTexture target; private Texture2D readback;
    private Dictionary<string,Color32[]> baselinePixels=new Dictionary<string,Color32[]>();
    private double startGame, startReal; private bool ready, finished; private int ordinal;
    private readonly string[] bgNames={"light","dark"};
    private readonly Color32[] bgColors={new Color32(245,239,222,255),new Color32(28,43,48,255)};
    private static string Hash(byte[] b) { using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(b)).Replace("-","").ToLowerInvariant(); }
    private string Portable(string path) { var p=path.Replace('\\','/');var root=config.projectRoot.Replace('\\','/').TrimEnd('/')+"/";return p.StartsWith(root,StringComparison.OrdinalIgnoreCase)?p.Substring(root.Length):p; }
    private void Awake() { Time.captureFramerate=60;Time.timeScale=1;QualitySettings.vSyncCount=0;Application.targetFrameRate=60; }
    private IEnumerator Start() {
        yield return null; // Let the fixed capture game clock settle before actors begin.
        try { Initialize(); } catch(Exception e) { Fail(e); }
    }
    private void Initialize() {
        var args=Environment.GetCommandLineArgs();int p=Array.IndexOf(args,"-fxGpuConfig");
        config=p>=0?JsonUtility.FromJson<Config>(File.ReadAllText(args[p+1])):new Config { projectRoot=Path.GetFullPath("."),localRawOutput=Path.GetFullPath("FxGpuPlaybackOutput/Raw"),reportPath=Path.GetFullPath("FxGpuPlaybackOutput/playback.json") };
        report=new Report { startedAtUtc=DateTime.UtcNow.ToString("o"),unityVersion=Application.unityVersion,playMode=Application.isPlaying,graphicsEnabled=SystemInfo.graphicsDeviceType!=UnityEngine.Rendering.GraphicsDeviceType.Null,graphicsDeviceType=SystemInfo.graphicsDeviceType.ToString(),graphicsDeviceName=SystemInfo.graphicsDeviceName,graphicsDeviceVersion=SystemInfo.graphicsDeviceVersion,colorSpace=QualitySettings.activeColorSpace.ToString() };
        if(!report.graphicsEnabled || args.Contains("-nographics"))throw new NotSupportedException("Real graphics device required; GPU playback is not verified");
        if(effects==null || effects.Length!=8)throw new InvalidDataException("Expected8 actual source clips");
        Directory.CreateDirectory(config.localRawOutput);
        var cg=new GameObject("ActualGpuCaptureCamera");cameraQA=cg.AddComponent<Camera>();cameraQA.enabled=false;
        cameraQA.transform.position=new Vector3(0,0,-10);cameraQA.orthographic=true;cameraQA.orthographicSize=6.4f;cameraQA.aspect=1;
        cameraQA.clearFlags=CameraClearFlags.SolidColor;cameraQA.allowHDR=false;cameraQA.allowMSAA=false;
        target=new RenderTexture(512,512,24,RenderTextureFormat.ARGB32,RenderTextureReadWrite.sRGB);target.antiAliasing=1;target.Create();cameraQA.targetTexture=target;
        readback=new Texture2D(512,512,TextureFormat.RGBA32,false,false);
        for(int b=0;b<2;b++) {
            cameraQA.cullingMask=0;cameraQA.backgroundColor=bgColors[b];var bytes=RenderPixels();
            var path=Path.Combine(config.localRawOutput,"baseline-"+bgNames[b]+".png");File.WriteAllBytes(path,bytes);
            baselinePixels[bgNames[b]]=readback.GetPixels32();report.baselines.Add(new Baseline{background=bgNames[b],localRawCapture=Portable(path),sha256=Hash(bytes),pixel=baselinePixels[bgNames[b]][0]});
        }
        for(int n=0;n<effects.Length;n++) {
            var f=effects[n];if(f.clip==null||f.controller==null||f.expectedSprites.Length!=8)throw new InvalidDataException("Missing source references "+f.id);
            var go=new GameObject("FX-"+f.id);go.layer=12+n;go.transform.position=Vector3.zero;go.transform.localScale=Vector3.one;
            var sr=go.AddComponent<SpriteRenderer>();sr.sharedMaterial=new Material(Shader.Find("Sprites/Default"));sr.color=Color.white;
            var an=go.AddComponent<Animator>();an.runtimeAnimatorController=f.controller;an.updateMode=AnimatorUpdateMode.Normal;an.cullingMode=AnimatorCullingMode.AlwaysAnimate;an.applyRootMotion=false;an.speed=1;
            an.Rebind();an.Play("Play",0,0);an.Update(0); // Initial binding only; subsequent phases are automatic Normal updates.
            actors.Add(new Actor{fx=f,go=go,animator=an,renderer=sr});
            foreach(var bg in bgNames)Directory.CreateDirectory(Path.Combine(config.localRawOutput,f.id,bg));
        }
        startGame=Time.timeAsDouble-Time.deltaTime;startReal=Time.realtimeSinceStartupAsDouble;ready=true;
    }
    private byte[] RenderPixels() {
        var old=RenderTexture.active;
        try { cameraQA.Render();RenderTexture.active=target;readback.ReadPixels(new Rect(0,0,512,512),0,0,false);readback.Apply(false,false);return readback.EncodeToPNG(); }
        finally { RenderTexture.active=old; }
    }
    private void LateUpdate() {
        if(!ready||finished)return;
        try {
            double elapsed=Time.timeAsDouble-startGame;
            for(int n=0;n<actors.Count;n++) {
                var a=actors[n];var state=a.animator.GetCurrentAnimatorStateInfo(0);double clipTime=state.normalizedTime*a.fx.clip.length;
                if(!a.cleared && elapsed>=.8-0.000001) { a.clearGame=elapsed;a.clearClip=clipTime;a.cleared=true;a.renderer.enabled=false;a.animator.enabled=false;a.renderer.sprite=null; }
                int observed=Array.IndexOf(a.fx.expectedSprites,a.renderer.sprite);
                for(int b=0;b<2;b++) {
                    cameraQA.cullingMask=1<<a.go.layer;cameraQA.backgroundColor=bgColors[b];var bytes=RenderPixels();var pixels=readback.GetPixels32();var basePixels=baselinePixels[bgNames[b]];int changed=0;
                    for(int k=0;k<pixels.Length;k++)if(pixels[k].r!=basePixels[k].r||pixels[k].g!=basePixels[k].g||pixels[k].b!=basePixels[k].b||pixels[k].a!=basePixels[k].a)changed++;
                    var path=Path.Combine(config.localRawOutput,a.fx.id,bgNames[b],"frame-"+ordinal.ToString("D4")+".png");File.WriteAllBytes(path,bytes);
                    var pivot=a.renderer.sprite==null?Vector2.zero:a.renderer.sprite.pivot;var size=a.renderer.sprite==null?Vector2.zero:a.renderer.sprite.rect.size;
                    var v=cameraQA.WorldToViewportPoint(a.go.transform.position);int expected=Mathf.Clamp(Mathf.FloorToInt((float)(clipTime+0.000005)/.1f),0,7);
                    report.samples.Add(new Sample{effect=a.fx.id,background=bgNames[b],localRawCapture=Portable(path),sha256=Hash(bytes),captureOrdinal=ordinal,unityFrameCount=Time.frameCount,observedFrameIndex=observed,expectedFrameIndex=expected,observedSpritePath=observed<0?"":a.fx.framePaths[observed],gameElapsedSeconds=elapsed,realtimeElapsedSeconds=Time.realtimeSinceStartupAsDouble-startReal,animatorClipTimeSeconds=clipTime,unityDeltaTime=Time.deltaTime,animatorNormalizedTime=state.normalizedTime,rendererEnabled=a.renderer.enabled,animatorEnabled=a.animator.enabled,callerCleared=a.cleared,position=a.go.transform.position,localScale=a.go.transform.localScale,projectedAnchorPixel=new Vector2(v.x*512,(1-v.y)*512),spritePivot=pivot,spriteRectSize=size,pixelsDifferentFromBackground=changed,transformAndScaleFixed=a.go.transform.position==Vector3.zero&&a.go.transform.localScale==Vector3.one,matchesClockExpectedFrame=a.cleared||observed==expected});
                }
            }
            ordinal++;if(ordinal>=60)Finish();
        }catch(Exception e){Fail(e);}
    }
    private void Finish() {
        foreach(var a in actors) {
            var ss=report.samples.Where(s=>s.effect==a.fx.id&&s.background=="light").ToArray();var visible=ss.Where(s=>!s.callerCleared).ToArray();var order=new List<int>();foreach(var x in visible)if(order.Count==0||order[order.Count-1]!=x.observedFrameIndex)order.Add(x.observedFrameIndex);
            var clears=report.samples.Where(s=>s.effect==a.fx.id&&s.callerCleared).ToArray();
            report.effects.Add(new EffectResult{id=a.fx.id,clipPath=a.fx.clipPath,clipLength=a.fx.clip.length,observedFrameOrder=order.ToArray(),ordered00To07=order.SequenceEqual(Enumerable.Range(0,8)),anchorAndScaleFixed=ss.All(s=>s.transformAndScaleFixed&&s.projectedAnchorPixel==new Vector2(256,256)),lastVisibleFrameIs07=visible.Length>0&&visible[visible.Length-1].observedFrameIndex==7,allClearCapturesEqualBackground=clears.Length>0&&clears.All(s=>s.pixelsDifferentFromBackground==0&&!s.rendererEnabled&&s.observedFrameIndex==-1),firstCallerClearGameSeconds=a.clearGame,animatorTimeAtClearSeconds=a.clearClip,visibleCaptures=visible.Length,clearedCaptures=clears.Length/2});
        }
        report.capturesPerEffectPerBackground=ordinal;report.passed=report.graphicsEnabled&&report.effects.Count==8&&report.effects.All(x=>x.ordered00To07&&x.anchorAndScaleFixed&&x.lastVisibleFrameIs07&&x.allClearCapturesEqualBackground&&x.firstCallerClearGameSeconds>=.7999&&x.firstCallerClearGameSeconds<.817);
        SaveAndStop();
    }
    private void Fail(Exception e) { if(report==null)report=new Report();report.error=e.ToString();report.passed=false;SaveAndStop(); }
    private void SaveAndStop() {
        finished=true;report.completedAtUtc=DateTime.UtcNow.ToString("o");
        if(config==null)config=new Config{reportPath=Path.GetFullPath("FxGpuPlaybackOutput/error.json")};
        Directory.CreateDirectory(Path.GetDirectoryName(config.reportPath));File.WriteAllText(config.reportPath,JsonUtility.ToJson(report,true));Time.captureFramerate=0;
        #if UNITY_EDITOR
        UnityEditor.SessionState.SetBool("WuxingFxGpuPlaybackDone",true);UnityEditor.EditorApplication.isPlaying=false;
        #endif
    }
}
