import pathlib,json,hashlib,datetime,argparse
from PIL import Image,ImageDraw,ImageFont
import numpy as np
R=pathlib.Path('D:/work/wuxing-slg-iamge');B='roster-expansion-20261029-wei1';Q=R/'records'/B;O=R/'exports/01-率土之滨'/B;D=R/'designs/01-率土之滨/characters'/B
ap=argparse.ArgumentParser();ap.add_argument('--replace-existing',action='store_true');args=ap.parse_args()
H=json.loads((Q/'selected-masters-and-crops.json').read_text(encoding='utf-8'))['selections'];NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def ref(p):return {'file':rel(p),'sha256':sha(p)}
def savej(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pm(im,size):return im.convert('RGBa').resize(tuple(size),Image.Resampling.LANCZOS).convert('RGBA')
def alpha(im):
 a=np.array(im.getchannel('A'));b=Image.fromarray(np.uint8(a>16)*255).getbbox()
 return {'range':[int(a.min()),int(a.max())],'alphaZero':int((a==0).sum()),'alphaOne':int((a==1).sum()),'alphaSemi':int(((a>0)&(a<255)).sum()),'alphaOpaque':int((a==255).sum()),'bboxAlpha16':b,'marginsAlpha16':None if b is None else [b[0],b[1],im.width-b[2],im.height-b[3]],'edgeAlpha16Pixels':int((a[0]>16).sum()+(a[-1]>16).sum()+(a[:,0]>16).sum()+(a[:,-1]>16).sum())}
O.mkdir(parents=True,exist_ok=True);assets=[];sources=[];checks=[]
for h in H:
 p=D/f'{h["id"]}-master-v{h["version"]}.png';rp=pathlib.Path(str(p)+'.generation.json');im=Image.open(p).convert('RGBA');gen=json.loads(rp.read_text(encoding='utf-8'));assert sha(p)==gen['sha256'];assert im.size==(1024,1536)
 source={**h,**ref(p),'record':rel(rp),'recordSha256':sha(rp),'sourceSize':list(im.size),'actualModel':gen['actualModel'],'actualQuality':gen['actualQuality'],'alpha':alpha(im),'inspectedOriginal':True};assert source['alpha']['edgeAlpha16Pixels']==0
 sources.append(source);face=im.crop(h['face']);bust=im.crop(h['bust']);variants=[('face-native',face,h['face'],None,None),('bust-native',bust,h['bust'],None,None)]
 for n in (128,256):
  usable=n-n//8;s=min(usable/face.width,usable/face.height);sz=[round(face.width*s),round(face.height*s)];off=[(n-sz[0])//2,(n-sz[1])//2];pic=Image.new('RGBA',(n,n));pic.paste(pm(face,sz),off);variants.append((f'avatar-{n}',pic,h['face'],sz,off))
 pic=Image.new('RGBA',(768,1152));pic.paste(pm(im,[704,1056]),[32,48]);variants.append(('card-full',pic,[0,0,1024,1536],[704,1056],[32,48]))
 for v,pic,box,sz,off in variants:
  fp=O/f'{h["id"]}-{v}.png';assert not fp.exists() or args.replace_existing,fp;pic.save(fp);native=v.endswith('native');warn=['CANDIDATE_NOT_USER_ACCEPTED','NO_ANIMATION_OR_ENGINE_VALIDATION','SOURCE_SOFT_ALPHA_RETAINED']
  if v!='card-full':warn.append('INTENTIONAL_RECTANGULAR_PORTRAIT_CROP_NOT_ISOLATED_HEAD_ART')
  if min(source['alpha']['marginsAlpha16'][0::2])<82 or min(source['alpha']['marginsAlpha16'][1::2])<123:warn.append('ORIGINAL_8_PERCENT_MARGIN_TARGET_NOT_FULLY_MET_NO_ALPHA16_EDGE_CONTACT')
  roi=None
  if sz:
   sx=sz[0]/(box[2]-box[0]);sy=sz[1]/(box[3]-box[1]);roi=[round(off[0]+(h['roi'][0]-box[0])*sx,3),round(off[1]+(h['roi'][1]-box[1])*sy,3),round(off[0]+(h['roi'][2]-box[0])*sx,3),round(off[1]+(h['roi'][3]-box[1])*sy,3)]
  result={**ref(fp),'schemaVersion':1,'createdAtUtc':NOW,'generalId':h['id'],'displayName':h['name'],'variant':v,'width':pic.width,'height':pic.height,'format':'PNG','mode':'RGBA','derivedFrom':[{k:source[k] for k in ('file','sha256','record','recordSha256')}],'operation':'native_rectangle_crop' if native else 'rectangle_crop_premultiplied_Lanczos_downsample_and_transparent_padding','cropBox':box,'resizeTo':sz,'pasteOffsetTopLeft':off,'originalMasterSize':list(im.size),'alphaInspection':alpha(pic),'sourcePixelsExact':native,'resampled':not native,'upscaled':False,'repainted':False,'alphaHygiene':'none','alphaKeyed':False,'alphaThresholdCleared':False,'faceRoiSourceApprox':h['roi'],'faceRoiOutputApprox':roi,'pivotNormalizedBottomLeft':[0.5,0.5],'warnings':warn,'status':'derived_static_UI_candidate','userApproved':False,'clientIntegrated':False,'newGeneratedImage':False};dr=pathlib.Path(str(fp)+'.derivation.json');savej(dr,result);assets.append({**result,'record':rel(dr),'recordSha256':sha(dr)})
  if native:checks.append({'asset':rel(fp),'exactSourceCropRGBA':pic.tobytes()==im.crop(box).tobytes()})
 assert sha(p)==source['sha256']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18);qa=[]
def saveqa(name,im,inputs,op):
 p=Q/name;im.save(p);r={**ref(p),'qaOnly':True,'operation':op,'sourceImages':[{'file':a['file'],'sha256':a['sha256']} for a in inputs],'font':'local QA only: Microsoft YaHei; font file not distributed'};savej(pathlib.Path(str(p)+'.derivation.json'),r);qa.append(r)
for label,bg in [('light',(245,239,222,255)),('dark',(28,43,48,255))]:
 textcolor=(90,60,30,255) if label=='light' else (240,230,195,255);cv=Image.new('RGBA',(900,920),bg);dr=ImageDraw.Draw(cv)
 for i,h in enumerate(H):
  x=i%3*300;y=i//3*460;dr.text((x+8,y+5),h['name']+' / '+h['id'],font=font,fill=textcolor)
  for v,dy in [('avatar-128',34),('avatar-256',185)]:
   a=next(a for a in assets if a['generalId']==h['id'] and a['variant']==v);im=Image.open(R/a['file']);cv.alpha_composite(im,(x+(300-im.width)//2,y+dy))
 saveqa('avatars-'+label+'.png',cv,[a for a in assets if a['variant'].startswith('avatar')],{'type':'composite_with_labels','assetDisplayScale':1,'backgroundRGBA':bg})
 cv=Image.new('RGBA',(900,980),bg);dr=ImageDraw.Draw(cv)
 for i,h in enumerate(H):
  x=i%3*300;y=i//3*490;dr.text((x+8,y+6),h['name'],font=font,fill=textcolor);a=next(a for a in assets if a['generalId']==h['id'] and a['variant']=='card-full');cv.alpha_composite(pm(Image.open(R/a['file']),[288,432]),(x+6,y+40))
 saveqa('cards-'+label+'.png',cv,[a for a in assets if a['variant']=='card-full'],{'type':'full_card_overview','assetDisplayScale':0.375,'backgroundRGBA':bg})
 for h in H:
  aa=[a for a in assets if a['generalId']==h['id'] and a['variant'].endswith('native')];pics=[Image.open(R/a['file']) for a in aa];cv=Image.new('RGBA',(sum(p.width for p in pics)+60,max(p.height for p in pics)+65),bg);dr=ImageDraw.Draw(cv);x=20
  for a,im in zip(aa,pics):dr.text((x,10),h['name']+' '+a['variant'],font=font,fill=textcolor);cv.alpha_composite(im,(x,50));x+=im.width+20
  saveqa(h['id']+'-native-'+label+'.png',cv,aa,{'type':'native_rectangular_portrait_QA','assetDisplayScale':1,'backgroundRGBA':bg})
m={'schemaVersion':1,'createdAtUtc':NOW,'scope':'six historical persons, one original master each -> thirty UI derivatives; official card variants not fully covered','status':'static_candidates_pending_final_visual_review','generalCount':6,'selectedMasterCount':6,'assetCount':30,'variantCounts':{v:6 for v in ('face-native','bust-native','avatar-128','avatar-256','card-full')},'avatarContainers':[[128,128],[256,256]],'cardContainer':[768,1152],'sources':sources,'assets':assets,'qa':qa,'userApproved':False,'clientIntegrated':False,'animationIncluded':False,'masterPixelsChangedByDerivation':False,'selectedSourceRequirement':'no effective alpha16 edge contact','notComplete':['all official card variants','all Three Kingdoms personalities','character animation','Unity import','user visual acceptance']}
savej(O/'generals-ui-manifest.json',m);savej(Q/'pixel-validation.json',{'nativeCropChecks':checks,'all12NativeCropsRGBAExact':all(c['exactSourceCropRGBA'] for c in checks),'selectedMasterHashRecheckCount':6,'derivedAssetCount':len(assets),'sourceAlpha16EdgeContacts':[s['alpha']['edgeAlpha16Pixels'] for s in sources]});print(json.dumps({'assetCount':len(assets),'qaCount':len(qa),'output':rel(O),'nativeCropsExact':all(c['exactSourceCropRGBA'] for c in checks),'avatar128FaceWidth':{a['generalId']:a['faceRoiOutputApprox'][2]-a['faceRoiOutputApprox'][0] for a in assets if a['variant']=='avatar-128'}},ensure_ascii=False))
