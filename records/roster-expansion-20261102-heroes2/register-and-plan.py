"""Verify this fixed batch, register candidates, and prepare a separate Unity plan."""
import json, hashlib, pathlib, datetime
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parents[2]
UNITY=pathlib.Path('D:/work/wuxing-slg-unity')
BATCH='roster-expansion-20261102-heroes2'
RECORD=ROOT/'records'/BATCH
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

manifest_path=ROOT/'exports/01-率土之滨'/BATCH/'generals-ui-manifest.json'
manifest=read(manifest_path)
assert len(manifest['sources'])==12 and len(manifest['assets'])==60
ids={
'tai-shi-ci':'ww-p-5ebeefca3947','huang-gai':'ww-p-d18659ca51e8',
'cheng-pu':'ww-p-b27da4aa9648','han-dang':'ww-p-4ae012a298a8',
'zhou-tai':'ww-p-f99e9da04bab','ling-tong':'ww-p-f4b3c8e434cb',
'zhang-zhao':'ww-p-08f9961349aa','gu-yong':'ww-p-a7aea0703420',
'fa-zheng':'ww-p-15f2c2ccb097','zhong-hui':'ww-p-b6da1d6b1f5b',
'wen-yang':'ww-p-bdb3cb354ad6','zhang-he':'ww-p-b88bff48909d'}
for s in manifest['sources']:
    assert sha(ROOT/s['source'])==s['sha256']
    assert sha(ROOT/s['generation'])==s['generationSha256']
for a in manifest['assets']:
    assert sha(ROOT/a['file'])==a['sha256']
    assert sha(ROOT/a['record'])==a['recordSha256']
manifest['rootVisualReviewPassed']=True
manifest['status']='source_and_60_UI_candidates_root_reviewed; Unity pending; user final acceptance pending'
write(manifest_path,manifest)
review={'checkedAtUtc':stamp(),'sourceMasterCount':12,'uiDerivativeCount':60,
        'rootVisualReviewPassed':True,'userFinalAccepted':False,
        'views':[{'file':str((RECORD/f).relative_to(ROOT)).replace('\\','/'),'sha256':sha(RECORD/f)} for f in ['twelve-generals-ui-light.png','twelve-generals-ui-dark.png']],
        'corrections':['cheng-pu, zhang-he and wen-yang face crop windows exclude disconnected weapon edge fragments'],
        'notes':['Native alpha, alpha1 and max254 retained without thresholding; all source/derivation hashes checked.',
                 'Twelve complete identities remain candidates; official card variants and full roster are incomplete.'],
        'manifestSha256':sha(manifest_path),'warningCount':len(manifest['warnings'])}
write(RECORD/'visual-review.json',review)

global_path=ROOT/'exports/01-率土之滨/art-review-20261029/generals-manifest.json'
g=read(global_path)
g['people']=[p for p in g['people'] if p['batch']!=BATCH]
assert len(g['people'])==60
for s in manifest['sources']:
    assert not any(p['personID']==ids[s['id']] or p['id']==s['id'] for p in g['people'])
    g['people'].append({'id':s['id'],'name':s['name'],'personID':ids[s['id']],'batch':BATCH,
        'master':s['source'],'masterSha256':s['sha256'],
        'sourceManifest':str(manifest_path.relative_to(ROOT)).replace('\\','/'),
        'assets':[{k:a[k] for k in ['variant','file','sha256','record']} for a in manifest['assets'] if a['personId']==s['id']],
        'officialCardVariantsComplete':False,'visualFinalAccepted':False,'clientIntegrated':False})
g.update(createdAt=stamp(),scope='72 identity-master candidates: prior12 plus new60; full roster and variants incomplete',assetCount=360,clientIntegrated=False,integrationScope='Prior300 imported; this batch60 pending Unity validation')
write(global_path,g)
data_path=global_path.parent/'data.js'
raw=data_path.read_text(encoding='utf-8').strip()
data=json.loads(raw.removeprefix('window.ART_REVIEW_DATA=').removesuffix(';'))
data['generals']=g
data_path.write_text('window.ART_REVIEW_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
html=global_path.parent/'index.html'
text=html.read_text(encoding='utf-8').replace('新增 48 人','新增 60 人')
option='<option value="'+BATCH+'">本批新增 12 人</option>'
if option not in text:text=text.replace('<option value="new">',option+'<option value="new">')
html.write_text(text,encoding='utf-8')

plan={'batch':BATCH,'artRoot':str(ROOT).replace('\\','/'),'assetRoot':'Assets/WuxingHeroBatches/'+BATCH,
      'expectedPng':60,'reportPath':'Docs/ArtImport/heroes2-validation-20261102.json',
      'scenePath':'Assets/Project/Scenes/Heroes2Review20261102.unity',
      'captureReportPath':'Docs/ArtImport/heroes2-gpu-20261102.json',
      'captureDirectory':'Docs/ArtImport/QA/Heroes2_20261102',
      'fontPath':'Assets/Project/Fonts/WuxingUI-Regular.ttf',
      'fontProbe':'金木水火土 招募 武将 同盟 战报 邮件 返回 确认 取消 出征 队伍 资源',
      'heroes':[{'id':s['id'],'name':s['name']} for s in manifest['sources']],
      'allNames':[p['name'] for p in g['people']],'fontFiles':[],'assets':[]}
for f in ['WuxingUI-Regular.ttf','OFL.txt','font-provenance.json','README.md']:
    path=ROOT/'exports/01-率土之滨/fonts/wuxing-ui-20261102'/f
    plan['fontFiles'].append({'source':str(path.relative_to(ROOT)).replace('\\','/'),'destination':'Assets/Project/Fonts/'+f,'sha256':sha(path)})
for a in manifest['assets']:
    im=Image.open(ROOT/a['file']).convert('RGBA')
    bottom=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    plan['assets'].append({'source':a['file'],'destination':plan['assetRoot']+'/'+pathlib.Path(a['file']).name,
       'sha256':a['sha256'],'pixelSha256':hashlib.sha256(bottom.tobytes()).hexdigest(),
       'alphaSha256':hashlib.sha256(bottom.getchannel('A').tobytes()).hexdigest(),
       'width':im.width,'height':im.height,'kind':'sprite','id':a['personId'],'variant':a['variant'],
       'pivotX':.5,'pivotY':.5,'ppu':128})
path=UNITY/'Docs/ArtImport/Pending/20261102-heroes2/plan.json'
write(path,plan)
write(UNITY/'Docs/ArtImport/hero-library-batches.json',{'plans':[str(path.relative_to(UNITY)).replace('\\','/')]})
write(RECORD/'registration.json',{'createdAtUtc':stamp(),'masterPeople':72,'uiDerivatives':360,'unityPendingPng':60,'planSha256':sha(path),'checks':'12 source +12 generation +60 derived +60 derivation record hashes matched','fullGameArtComplete':False})
print(json.dumps({'people':72,'ui':360,'plan':str(path),'sourceHashesChecked':144},ensure_ascii=True))
