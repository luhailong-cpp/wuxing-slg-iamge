from pathlib import Path
from PIL import Image
import json, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path('D:/work/wuxing-slg-iamge')
config=json.loads((root/'config/image-generation.json').read_text(encoding='utf-8-sig'))
for stem in sys.argv[1:]:
 base=root/'records/01-率土之滨'
 req=json.loads((base/(stem+'.tool-request.json')).read_text(encoding='utf-8'))
 receipt=json.loads((base/(stem+'.tool-response.json')).read_text(encoding='utf-8'))
 rel=f'designs/01-率土之滨/characters/{stem}.png'; p=root/rel
 im=Image.open(p); im.verify(); im=Image.open(p)
 assert im.mode=='RGBA', (stem,im.mode)
 a=im.getchannel('A'); h=a.histogram(); box=a.point(lambda v:255 if v>=32 else 0).getbbox()
 margins=[box[0],box[1],im.width-box[2],im.height-box[3]]
 corners=[a.getpixel(pt) for pt in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]]
 digest=hashlib.sha256(p.read_bytes()).hexdigest()
 assert digest==hashlib.sha256(Path(receipt['toolOutputPath']).read_bytes()).hexdigest()
 refs=[]; editing=None
 for ref in req['submittedParameters']['referenced_image_paths']:
  rp=Path(ref); rr=rp.relative_to(root).as_posix()
  if 'mail-ui' in rr: role='首要画风、玉绿米白暖金、圆润道家Q版人物高清手绘参考'
  elif 'team-ui' in rr: role='首要画风和差异化角色完成度参考'
  elif ('02-liu-bei-v1' in rr and stem=='02-liu-bei-v2') or ('11-lv-bu-v1' in rr and stem=='11-lv-bu-v2'):
   role='唯一编辑目标，本角色v1；只修复安全余边和贴边端点'
   editing={'file':rr,'sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'generationRecord':rr+'.generation.json'}
  elif '01-spear-dao-general' in rr: role='同系列完成度与尺度参考；非本图角色身份，不复制脸、衣装或兵器'
  else: role='用户截图，仅角色身份、衣装和持物功能参考；不复制写实脸、画风、UI或场景'
  refs.append({'file':rr,'sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'role':role,'actuallyAttached':True})
 rec={'schemaVersion':1,'file':rel,'sha256':digest,'generatedAt':receipt['callCompletedAt'],'generatedAtBasis':'宿主调用完成时记录的UTC时间；工具未另披露独立图像生成时间','callStartedAt':receipt['callStartedAt'],'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'nativeDimensionsPreserved':True,'resampled':False,'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','resultId':None,'executionCellId':receipt['executionCellId'],'configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':req['submittedParameters']['referenced_image_paths'],'promptFile':f'prompts/01-率土之滨/{stem}.prompt.txt'},'actualModel':None,'actualQuality':None,'evidence':[{'file':f'records/01-率土之滨/{stem}.tool-request.json','field':'submittedParameters'},{'file':f'records/01-率土之滨/{stem}.tool-response.json','fields':['returnedFields','output_hint','callStartedAt','callCompletedAt']},{'sourceImage':receipt['toolOutputPath'],'sha256':digest,'copyHashVerified':True}],'pngMetadataKeys':list(im.info.keys()),'unverifiedReason':'宿主管理，工具未开放model/quality参数，返回字段未披露实际模型与画质；当前可读取PNG元数据未提供可核实版本字段，配置目标不能作为实际版本证据。','prompt':f'prompts/01-率土之滨/{stem}.prompt.txt','references':refs,'assetRole':'完整单角色静态master','alphaInspection':{'mode':'native_alpha','range':list(a.getextrema()),'fullyTransparentPixelCount':h[0],'semiTransparentPixelCount':sum(h[1:255]),'opaquePixelCount':h[255],'canvasCornerAlpha':corners,'thresholdForBounds':32,'bounds':box,'marginsLTRB':margins},'status':'static_master_pending_visual_review','userApproved':False,'animationGenerated':False,'clientIntegrated':False,'plan':'records/01-率土之滨/full-completion-characters-plan.json'}
 if editing: rec['editingTarget']=editing
 (root/(rel+'.generation.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'file':p.name,'size':im.size,'alpha0':h[0],'corners':corners,'margins':margins,'sha256':digest},ensure_ascii=False))

