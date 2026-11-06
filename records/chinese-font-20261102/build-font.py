"""Create an OFL-licensed, renamed static UI font; never use system fonts."""
from pathlib import Path
import sys,json,hashlib,urllib.request,datetime

ROOT=Path(__file__).resolve().parents[2]
CLIENT=Path('D:/work/wuxing-slg-unity')
sys.path.insert(0,str(CLIENT/'Logs/Tools/fonttools'))
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset

HERE=Path(__file__).resolve().parent
OUT=ROOT/'exports/01-率土之滨/fonts/wuxing-ui-20261102'
CACHE=CLIENT/'Logs/Downloads/NotoSansSC'
OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'wuxing-art-font-preparation'})
    with urllib.request.urlopen(req,timeout=120) as response:return response.read()
def sha(b):return hashlib.sha256(b).hexdigest()
lock=HERE/'upstream-lock.json'
if lock.exists():
    upstream=json.loads(lock.read_text(encoding='utf-8'))
else:
    commits=json.loads(get('https://api.github.com/repos/google/fonts/commits?path=ofl/notosanssc&per_page=1'))
    commit=commits[0]['sha']
    base='https://raw.githubusercontent.com/google/fonts/'+commit+'/ofl/notosanssc/'
    upstream={'repository':'https://github.com/google/fonts','commit':commit,
              'fontUrl':base+'NotoSansSC%5Bwght%5D.ttf','licenseUrl':base+'OFL.txt'}
    lock.write_text(json.dumps(upstream,indent=2)+'\n',encoding='utf-8')
font_file=CACHE/'NotoSansSC-variable.ttf'
if not font_file.exists():font_file.write_bytes(get(upstream['fontUrl']))
license_file=OUT/'OFL.txt'
if not license_file.exists():license_file.write_bytes(get(upstream['licenseUrl']))
font=TTFont(font_file,recalcTimestamp=False)
font_source_hash=sha(font_file.read_bytes())
source_version=font['name'].getDebugName(5)
available=set(font.getBestCmap())
required=set(range(0x20,0x7f))
# All GB2312 Han characters, plus every current sourced roster name and UI probe.
for hi in range(0xb0,0xf8):
    for lo in range(0xa1,0xff):
        try:required.update(map(ord,bytes([hi,lo]).decode('gb2312')))
        except UnicodeDecodeError:pass
queue=json.loads((ROOT/'records/roster-20261029/PRODUCTION_QUEUE_20261029.json').read_text(encoding='utf-8'))
names=sorted({x['name'] for x in queue['queue']})
probe='五行问鼎 · 人物美术检查 金木水火土 招募 武将 同盟 战报 邮件 返回 确认 取消 出征 队伍 资源 铜钱 木材 铁矿 石料 粮食 主城 建造 升级 技能 兵力 体力 待机 攻击 受击 战败 行走 全部 在线 离线'
required.update(map(ord,''.join(names)+probe))
required.discard(10);required.discard(13)
missing=sorted(required-available)
if missing:raise ValueError('Upstream font lacks required codepoints: '+','.join(f'U+{cp:04X}' for cp in missing))
requested=required.copy()
corpus_records=[]
for directory in ['docs','records','prompts']:
    for p in (ROOT/directory).rglob('*'):
        if not p.is_file() or p.suffix not in ['.json','.md','.txt'] or 'publication-local' in p.parts:continue
        if p.stat().st_size>2_000_000:continue
        try:text=p.read_text(encoding='utf-8')
        except UnicodeDecodeError:continue
        requested.update(cp for cp in map(ord,text) if cp in available)
        corpus_records.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())})
instantiateVariableFont(font,{'wght':400},inplace=True)
options=subset.Options();options.name_IDs=['*'];options.name_languages=['*'];options.name_legacy=True
sub=subset.Subsetter(options=options);sub.populate(unicodes=sorted(requested));sub.subset(font)
# Modified font uses a project-specific primary name; retain upstream copyright/OFL.
names_by_id={1:'Wuxing UI',2:'Regular',3:'WuxingUI-Regular-'+font_source_hash[:12],
             4:'Wuxing UI Regular',6:'WuxingUI-Regular',16:'Wuxing UI',17:'Regular'}
for record in font['name'].names:
    if record.nameID in names_by_id:record.string=names_by_id[record.nameID].encode(record.getEncoding(),errors='replace')
out=OUT/'WuxingUI-Regular.ttf';font.save(out)
check=TTFont(out);final_cmap=set(check.getBestCmap());assert required<=final_cmap
assert check['name'].getDebugName(1)=='Wuxing UI'
unicode_file=HERE/'glyphs.txt';unicode_file.write_text(''.join(chr(cp) for cp in sorted(requested)),encoding='utf-8')
receipt={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source':upstream,'upstreamFontSha256':font_source_hash,'upstreamVersion':source_version,
    'license':'SIL Open Font License 1.1','licenseSha256':sha(license_file.read_bytes()),
    'sourceReservedFontName':'Source','modifiedPrimaryFamily':'Wuxing UI',
    'operation':'instantiate variable wght=400; retain required glyphs and available corpus glyphs; rename primary family; preserve copyright and OFL',
    'file':out.relative_to(ROOT).as_posix(),'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,
    'requiredCodepoints':len(required),'subsetCodepoints':len(final_cmap),'requiredMissing':[],
    'rosterNamesCovered':len(names),'glyphList':'records/chinese-font-20261102/glyphs.txt',
    'corpusFiles':corpus_records,'sourceFontFromSystem':False,'newModelGeneration':False,
    'unityGlyphChecked':False,'userChatOrUnseenFutureTextCoverageClaimed':False}
(HERE/'font-provenance.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'font-provenance.json').write_text(json.dumps({k:v for k,v in receipt.items() if k!='corpusFiles'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'README.md').write_text('# 五行问鼎中文UI字体\n\nWuxing UI Regular是Noto Sans SC的400字重静态子集，保留原版权与SIL OFL1.1，主字体名已改为Wuxing UI。上游固定commit和SHA见font-provenance.json。覆盖GB2312汉字、当前研究队列人物名及制作文本所需字符；未承诺任意未来输入或全球所有语言。不是系统字体，也不是AI生成图像。字体单独按OFL分发，项目其他素材没有因此增加统一许可证。\n',encoding='utf-8')
print(json.dumps({k:receipt[k] for k in ['file','bytes','requiredCodepoints','subsetCodepoints','rosterNamesCovered','requiredMissing']},ensure_ascii=True))
