from pathlib import Path
from PIL import Image
import json, hashlib, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path('D:/work/wuxing-slg-iamge'); base=root/'records/01-率土之滨'; char=root/'designs/01-率土之滨/characters'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
names={'02-liu-bei-v2':'刘备','03-cao-cao-v1':'曹操','04-sun-quan-v1':'孙权','05-zhao-yun-v1':'赵云','06-zhuge-liang-v1':'诸葛亮','07-tutorial-guide-v1':'引导少女','08-guan-yu-v1':'关羽','09-zhang-fei-v1':'张飞','10-zhou-yu-v1':'周瑜','11-lv-bu-v2':'吕布','12-diao-chan-v1':'貂蝉','13-hua-tuo-v1':'华佗','14-huang-yue-ying-v1':'黄月英'}
old={'02-liu-bei-v1':'02-liu-bei-v2','11-lv-bu-v1':'11-lv-bu-v2'}; rows=[]
for stem in list(names)+list(old):
 p=char/(stem+'.png'); recpath=char/(stem+'.png.generation.json')
 rec=json.loads(recpath.read_text(encoding='utf-8')); req=json.loads((base/(stem+'.tool-request.json')).read_text(encoding='utf-8')); rsp=json.loads((base/(stem+'.tool-response.json')).read_text(encoding='utf-8'))
 im=Image.open(p); im.verify(); im=Image.open(p)
 assert im.mode=='RGBA' and im.size==(1024,1536)
 a=im.getchannel('A'); hist=a.histogram(); box=a.point(lambda v:255 if v>=32 else 0).getbbox()
 margins=[box[0],box[1],im.width-box[2],im.height-box[3]]
 corners=[a.getpixel(pt) for pt in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]]
 sha=hashlib.sha256(p.read_bytes()).hexdigest(); assert rec['sha256']==sha
 assert req['submittedParameters']['prompt'].strip()==(root/rec['prompt']).read_text(encoding='utf-8-sig').strip()
 for ref in rec['references']:
  rp=root/ref['file']; assert rp.is_file() and hashlib.sha256(rp.read_bytes()).hexdigest()==ref['sha256']
 assert hist[0]>0
 theme='original_guide_pending_wuxing_identity_review' if stem.startswith('07-') else 'historical_identity_candidate_requires_original_wuxing_redesign'
 warnings=[]
 if min(margins)<80: warnings.append('安全余边未达到原提示的8–10%目标；不能把提示要求当作已实现。')
 if max(corners)>0: warnings.append('画布角落存在alpha=1微量半透明像素；未处理。')
 if stem in old: warnings.append('端点贴边旧候选，已有构图修订；保留溯源，不用于首发。')
 if stem=='11-lv-bu-v2': warnings.append('完整原tool output_hint与完成时间未跨上下文保存；缺失字段为null，使用源文件路径/哈希/文件时间补证。')
 rec['status']='legacy_direction_candidate_not_release'; rec['userApproved']=False
 rec['themeCorrection']={'receivedAt':'2026-10-27','userDirection':'金木水火土主题；率土之滨仅功能参考','disposition':theme,'renameOnlyForbidden':True,'releaseEligible':False}
 rec['visualReview']={'file':'records/01-率土之滨/full-completion-characters-review.json','viewedInHost':True,'observed':'已实际查看静态图；用户方向已纠正，此检查不等于形象验收。','warnings':warnings}
 if stem in old: rec['supersededForFramingBy']=f'designs/01-率土之滨/characters/{old[stem]}.png'
 if stem=='11-lv-bu-v2':
  rec['generatedAtBasis']='工具完成时间未保留，generatedAt为null；源文件时间仅作附加证据。'; rec['receiptRecoveryGap']=True; rec['sourceFileLastWriteUtc']=rsp['sourceFileLastWriteUtc']
 recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 rows.append({'stem':stem,'file':p.relative_to(root).as_posix(),'name':names.get(stem,'刘备' if stem.startswith('02') else '吕布'),'size':list(im.size),'mode':im.mode,'sha256':sha,'alphaZeroPixels':hist[0],'cornerAlpha':corners,'alpha32MarginsLTRB':margins,'role':'旧方向修订前稿' if stem in old else '旧方向较完整候选','themeDisposition':theme,'userApproved':False,'releaseEligible':False,'animationGenerated':False,'warnings':warnings,'filePromptRequestRefsHashVerified':True,'visualInspectionPerformed':True,'toolReceiptComplete':stem!='11-lv-bu-v2'})
planpath=base/'full-completion-characters-plan.json'; plan=json.loads(planpath.read_text(encoding='utf-8'))
for group in ['characters','additionalWorkingBaseline']:
 for c in plan.get(group,[]):
  original=c['stem']; revised=old.get(original,original)
  c['status']='generated_legacy_direction_candidate_not_release'; c['lastCandidate']=f'designs/01-率土之滨/characters/{revised}.png'; c['fiveElementsRedesignRequired']=original!='07-tutorial-guide-v1'; c['wuxingIdentityReviewRequired']=True
plan['themeCorrection']={'date':'2026-10-27','direction':'用户明确金木水火土；率土之滨仅功能参考','generationStopped':True,'inFlightCalls':0,'historicalIdentityCandidatesAreNotRelease':True,'renameOnlyForbidden':True}
plan['scopeNote']='该13位是已停止的旧方向工作名单；12位历史身份必须重新设计为五行原创，不可仅改名。引导少女需五行身份审查。均为静态候选，不含动画或首发验收。'
planpath.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doctor=json.loads((base/'full-completion-characters-doctor.json').read_text(encoding='utf-8'))
review={'schemaVersion':1,'closedAt':now,'scope':'13位旧方向角色；共15张本批PNG（含刘备/吕布各一张修订前稿）。01原创持枪道将为此前已存在素材，不计入本批。','currentDirection':'金木水火土五行原创游戏，道家Q版高清手绘；率土之滨只参考功能。','generationStopped':True,'inFlightCalls':0,'themeStatus':'historical_candidates_not_release','userApproved':False,'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主工具无model/quality参数且未披露实际版本；配置目标GPT Image 2.5/max不作为实际已锁定证据。','images':rows,'runtimeDiagnostics':{'source':'records/01-率土之滨/full-completion-characters-doctor.json','warningsAndFailuresVerbatim':[c for c in doctor['checks'] if c['status'] in ['WARN','FAIL']],'staticInspectionRoute':'专用Python+Pillow只读尺寸/alpha/hash，不程序绘图','optionalMissingCapabilitiesUsed':False},'notCompleted':['金木水火土原创角色名单与视觉身份设计','所有历史角色的五行原创重绘','用户形象验收','导出余边、alpha角落微量像素清理','头像与阵营图标接入','动作与动画','引擎集成与客户端验收'],'evidenceGap':['11-lv-bu-v2已返回且已落盘，源文件哈希已比对；完整原始output_hint、准确完成时间未恢复，均未编造。']}
(base/'full-completion-characters-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
table='\n'.join('| '+r['name']+' | '+r['stem']+'.png | '+('待五行身份审查' if r['stem'].startswith('07-') else '历史身份，须五行原创重设计')+' |' for r in rows if r['stem'] not in old)
doc=f'''# 角色制作交接 — 2026-10-27

项目根：D:/work/wuxing-slg-iamge。本窗口已停止生成，无在途生图或修图调用。未操作 Git，未承诺已上传。

## 首要方向修正

用户明确游戏主题是 **金木水火土**；率土之滨只提供功能参考。画法仍以邮件与组队主参考为准，保持道家 Q 版高清手绘。

本批误沿三国身份制作的历史人物仅保留为旧方向候选，不是正式首发，不代表用户已验收。必须设计新的五行身份、服装、法器和辨识特征后重新生成；不得旧图改名后冒称五行原创新图。引导少女虽非历史身份，也尚未完成五行世界观审查。

designs/01-率土之滨 为旧制作分类，不证明游戏正式名称；此交接未重命名、移动或删除资产。

## 已落盘

角色目录：designs/01-率土之滨/characters/。以下13位较完整候选都是原生 **1024×1536 RGBA PNG**，含实际 alpha=0 像素，无放大。每张独立宿主 image_gen 生成，只是静态 master，不含动画。

| 原工作身份 | 较完整候选文件 | 状态 |
|---|---|---|
{table}

另保留：
- 02-liu-bei-v1.png：右剑端点贴边，后有 v2。保留来源链，非首发。
- 11-lv-bu-v1.png：右羽尖贴边，后有 v2。保留来源链，非首发。
- 01-spear-dao-general-v1.png：此前已存在的原创持枪道将，本批未改；是否纳入五行正式角色待新窗口审查。

本批共15张 PNG、13个候选身份。两张 v2 是AI构图修订，不是程序透明补边。

## 在途与证据

- 在途调用 **0**。最后返回的吕布 v2 已原样复制回项目，源文件与落盘哈希一致；实际查看双羽冠与方天戟完整入画。
- 提示词：prompts/01-率土之滨/<stem>.prompt.txt。
- 请求/返回记录：records/01-率土之滨/<stem>.tool-request.json、.tool-response.json。
- 每张PNG旁 .png.generation.json 有配置快照、尺寸、哈希、参考图及哈希、alpha检查和候选状态。
- 总检查：records/01-率土之滨/full-completion-characters-review.json。
- 工作计划已标记停止：records/01-率土之滨/full-completion-characters-plan.json。
- 吕布 v2 临时返回未跨上下文保留：完整 output_hint 与准确完成时间未恢复，记录为 null。源输出路径、开始时间、cell=28、文件时间与哈希有证据；不把文件时间冒称生成完成时间。
- 配置目标 GPT Image 2.5 / max；工具无model/quality参数且未披露版本质量，实际字段均为null，不能声称显式锁定型号。

## 检查与未完

已实际查看本批静态图。多数候选主要四肢与持物完整，余边并非全部达到提示的8–10%；部分角落有alpha=1微量半透明像素。详细数值见 review 与 sidecar。未程序绘图、未擦除、未重采样。方向被纠正后，此检查只验证旧候选文件，不等于正式接入或用户通过。

新窗口先做：
1. 读根AGENTS、最新交接、模型策略和风格规范，实际查看两张UI主参考。
2. 建立金木水火土原创身份名单及视觉差异，再做新图。
3. 历史候选排除正式首发引用，不能只换名字。可保留画法完成度供人工分析。
4. 审查引导助手的五行身份、服装和法器。
5. 用户验收后再做头像、动作、动画、atlas及客户端导出，目前均未完成。
6. 正式使用任何候选前再处理余边与角落alpha、复核；当前未做删稿清理。

未改父README、全项目统计或Git。公开仓上传由根窗口统一处理。
'''
(root/'docs/HANDOFF_CHARACTERS_20261027.md').write_text(doc,encoding='utf-8')
print(json.dumps({'handoff':'docs/HANDOFF_CHARACTERS_20261027.md','review':'records/01-率土之滨/full-completion-characters-review.json','newBatchPngs':len(rows),'candidateIdentities':len(names),'allPngPromptRequestReferenceHashesVerified':True,'inFlight':0,'historyThemeCandidatesNotRelease':12,'guideNeedsWorldReview':1},ensure_ascii=False))
