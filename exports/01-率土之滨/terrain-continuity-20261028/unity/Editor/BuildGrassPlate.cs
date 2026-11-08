using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
public static class BuildGrassPlate {
 [Serializable] public class Config { public string exportRoot,package,report,sourceHash; }
 [Serializable] public class Report { public string mode,unityVersion,error,file,sha256,guid,packageHash,completedAt; public bool passed,sourceHashMatches,importMatches,clientIntegrated=false,playModeTested=false,actualGPUCameraRender=false,seamlessTilingVerified=false; public int spriteCount,prefabCount,width,height; public Vector2 pivot; public string[] notes; }
 static Config C; static Report R; static bool imported;
 static string Hash(string p) { using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(File.ReadAllBytes(p))).Replace("-","").ToLowerInvariant(); }
 static void Load(bool roundtrip) { var a=Environment.GetCommandLineArgs(); C=JsonUtility.FromJson<Config>(File.ReadAllText(a[Array.IndexOf(a,"-terrainConfig")+1]));R=new Report{mode=roundtrip?"fresh_project_import":"source_build",unityVersion=Application.unityVersion}; }
 public static void Build(){Run(false);} public static void Roundtrip(){Run(true);}
 static void Finish(){R.completedAt=DateTime.UtcNow.ToString("o");Directory.CreateDirectory(Path.GetDirectoryName(C.report));File.WriteAllText(C.report,JsonUtility.ToJson(R,true));EditorApplication.Exit(R.passed?0:1);}
 static void Run(bool roundtrip){try {
 Load(roundtrip);
 if(roundtrip&&!imported){AssetDatabase.importPackageCompleted+=name=>{imported=true;EditorApplication.delayCall+=()=>Run(true);};AssetDatabase.importPackageFailed+=(name,err)=>{R.error=err;Finish();};AssetDatabase.ImportPackage(C.package,false);return;}
 AssetDatabase.Refresh();string p=C.exportRoot+"/continuous-grass-plate-native.png";
 if(!roundtrip){var imp=(TextureImporter)AssetImporter.GetAtPath(p);imp.textureType=TextureImporterType.Sprite;imp.spriteImportMode=SpriteImportMode.Single;imp.spritePixelsPerUnit=100;imp.textureCompression=TextureImporterCompression.Uncompressed;imp.mipmapEnabled=false;imp.npotScale=TextureImporterNPOTScale.None;imp.alphaSource=TextureImporterAlphaSource.FromInput;imp.alphaIsTransparency=true;imp.maxTextureSize=2048;imp.isReadable=true;var st=new TextureImporterSettings();imp.ReadTextureSettings(st);st.spriteAlignment=(int)SpriteAlignment.Center;st.spritePivot=new Vector2(.5f,.5f);st.spriteMeshType=SpriteMeshType.FullRect;imp.SetTextureSettings(st);imp.SaveAndReimport();var g=new GameObject("ContinuousGrassPlate");var renderer=g.AddComponent<SpriteRenderer>();renderer.sprite=AssetDatabase.LoadAssetAtPath<Sprite>(p);renderer.sortingOrder=-100;PrefabUtility.SaveAsPrefabAsset(g,C.exportRoot+"/ContinuousGrassPlate.prefab");UnityEngine.Object.DestroyImmediate(g);AssetDatabase.SaveAssets();}
 var sp=AssetDatabase.LoadAssetAtPath<Sprite>(p);var ti=(TextureImporter)AssetImporter.GetAtPath(p);var settings=new TextureImporterSettings();ti.ReadTextureSettings(settings);var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(C.exportRoot+"/ContinuousGrassPlate.prefab");var sr=prefab==null?null:prefab.GetComponent<SpriteRenderer>();
 R.file=p;R.sha256=Hash(p);R.guid=AssetDatabase.AssetPathToGUID(p);R.width=(int)sp.rect.width;R.height=(int)sp.rect.height;R.pivot=sp.pivot;R.sourceHashMatches=R.sha256==C.sourceHash;R.importMatches=R.width==1774&&R.height==887&&(sp.pivot-new Vector2(887,443.5f)).magnitude<.01f&&sp.pixelsPerUnit==100&&ti.textureCompression==TextureImporterCompression.Uncompressed&&!ti.mipmapEnabled&&ti.npotScale==TextureImporterNPOTScale.None&&settings.spriteMeshType==SpriteMeshType.FullRect&&sp.border==Vector4.zero&&sr!=null&&sr.sprite==sp&&sr.sortingOrder==-100&&ti.alphaSource==TextureImporterAlphaSource.FromInput;R.spriteCount=1;R.prefabCount=1;if(!R.sourceHashMatches||!R.importMatches)throw new Exception("source or import mismatch");if(!roundtrip)AssetDatabase.ExportPackage(C.exportRoot,C.package,ExportPackageOptions.Recurse);R.packageHash=Hash(C.package);R.passed=true;R.notes=new[]{"One continuous native grass plate, not a seamless tile.3x3 visual seam test failed.","No city or troop pixels are copied into this package; they appear only in static QA composition.","No navigation, GPU, PlayMode or production-client integration claimed."};
 }catch(Exception e){if(R==null)R=new Report();R.error=e.ToString();R.passed=false;}Finish();}
}