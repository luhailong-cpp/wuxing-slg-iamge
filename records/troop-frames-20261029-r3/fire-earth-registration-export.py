import json,hashlib,math,argparse
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path('D:/work/wuxing-slg-iamge'); RR=ROOT/'records/troop-frames-20261029-r3'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p): return {'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def stats(im):
 a=im.getchannel('A');h=a.histogram();b=a.point(lambda v:255 if v>16 else 0).getbbox()
 return {'size':list(im.size),'alphaZero':h[0],'alphaOne':h[1],'alphaSemi':sum(h[1:255]),'alphaOpaque':h[255],'alphaNonzero':sum(h[1:]),'alpha0BBox':a.getbbox(),'alpha16BBox':b,'alpha16Height':b[3]-b[1] if b else 0}
def rounded(x):return math.floor(x+0.5)
def place(im,size,offset):
 x,y=offset;assert 0<=x and 0<=y and x+im.width<=size and y+im.height<=size,(im.size,size,offset)
 out=Image.new('RGBA',(size,size));out.paste(im,offset)
 assert out.crop((x,y,x+im.width,y+im.height)).tobytes()==im.tobytes()
 a=np.array(out.getchannel('A'));assert not (a[0].any() or a[-1].any() or a[:,0].any() or a[:,-1].any())
 return out
def resized(im,size):return im.convert('RGBa').resize((size,size),Image.Resampling.LANCZOS).convert('RGBA')
def board(tiles,cols,bg,labels,path):
 edge=tiles[0].width;w=cols*(edge+8)+8;h=math.ceil(len(tiles)/cols)*(edge+28)+8;o=Image.new('RGB',(w,h),bg);d=ImageDraw.Draw(o)
 for i,t in enumerate(tiles):
  x=8+i%cols*(edge+8);y=8+i//cols*(edge+28);o.paste(t,(x,y));d.text((x,y+edge+3),labels[i],fill=(30,30,30) if bg[0]>100 else (235,235,235))
 o.save(path)
def tile(im,root,points,bg,edge=384,marks=True):
 o=Image.new('RGBA',im.size,(*bg,255));o.alpha_composite(im);o=o.resize((edge,edge),Image.Resampling.LANCZOS).convert('RGB')
 if marks:
  d=ImageDraw.Draw(o);s=edge/im.width;x,y=[v*s for v in root];d.line((0,y,edge-1,y),fill=(50,110,220));d.line((x,0,x,edge-1),fill=(110,120,130));d.line((x-5,y,x+5,y),fill=(230,20,30),width=2);d.line((x,y-5,x,y+5),fill=(230,20,30),width=2)
  if points:
   p=[(v[0]*s,v[1]*s) for v in points];d.line((*p[0],*p[1]),fill=(40,155,80));
   for x,y in p:d.ellipse((x-2,y-2,x+2,y+2),outline=(0,155,70))
 return o
ap=argparse.ArgumentParser();ap.add_argument('--units',nargs='+',choices=['fire','earth'],default=['fire','earth']);ap.add_argument('--replace-existing',action='store_true');args=ap.parse_args()
for unit in args.units:
 ip=RR/f'{unit}-registration-measured.json';data=json.loads(ip.read_text(encoding='utf-8'));out=ROOT/f'exports/01-率土之滨/troop-frames-20261029-r3/{unit}-grounded-candidate-v1'
 if out.exists() and not args.replace_existing:raise SystemExit(f'Refusing existing export {out}')
 if out.exists():
  prior=json.loads((out/'manifest.json').read_text(encoding='utf-8'));assert prior['character']==data['character']
 out.mkdir(parents=True,exist_ok=True)
 master=Image.open(ROOT/data['master']['file']).convert('RGBA');mh=stats(master)['alpha16Height'];msize=rounded(master.width*180/data['master']['helmetWidth']);mnormscale=msize/master.width
 mapFactor=128/(mh*mnormscale)
 mn=resized(master,msize);moff=[512-rounded(v*mnormscale) for v in data['master']['groundRoot']];moff[1]=768-rounded(data['master']['groundRoot'][1]*mnormscale);mnormal=place(mn,1024,moff)
 mMapSize=rounded(msize*mapFactor);mMapScale=mMapSize/master.width;mm=resized(master,mMapSize);mmapoff=[192-rounded(data['master']['groundRoot'][0]*mMapScale),288-rounded(data['master']['groundRoot'][1]*mMapScale)];mmap=place(mm,384,mmapoff)
 mnp=RR/f'{unit}-registration-master-normalized-reference.png';mmp=RR/f'{unit}-registration-master-map-reference.png';mnormal.save(mnp);mmap.save(mmp)
 manifest={'schema':'wuxing-slg.grounded-frame-candidates.v2','status':'technical_registration_candidate_not_user_or_engine_accepted','game':'五行问鼎','character':data['character'],'direction':'SE','userApproved':False,'masterUserApproved':False,'registration':ref(ip),'ownershipEvidence':ref(ROOT/data['ownershipReport']),'exporter':ref(Path(__file__)),'master':{**data['master'],'nativeStats':stats(master),'normalizedScale':mnormscale,'normalizedStats':stats(mnormal),'normalizedReference':ref(mnp),'mapStats':stats(mmap),'mapReference':ref(mmp)},'contract':{'nativeCanvas':[1024,1024],'nativeRoot':[512,768],'normalizedCanvas':[1024,1024],'normalizedRoot':[512,768],'mapCanvas':[384,384],'mapRoot':[192,288],'unityPivot':[0.5,0.25],'sourcePadding':'owned rectangle padded at 0,0 to one shared square per action; original RGBA preserved','nativeOperation':'integer translation only, no resizing, no alpha edits','normalizedOperation':'one uniform scale per action based on neutral rigid helmet width, then integer root translation','helmetTargetPx':180,'mapFactorCommonToUnit':mapFactor,'mapTargetMeaning':'master standing silhouette approximately 128px; poses never individually fitted','mapOperation':'single premultiplied resize from padded original using actual normalized action scale times common unit map factor; integer root translation','alphaHygiene':'none','perFrameFit':False,'resampler':'premultiplied Lanczos','rootMethod':'manually reviewed boot/knee ROIs; bottom support within each ROI; midpoint rounded to integer; contact slope/stance preserved','alphaCaveat':'Native contains every original RGBA byte. Downsampling changes samples and quantizes alpha normally; no alpha-floor deletion, component removal, keying or trimming.'},'actions':[],'notProven':['user approval of identity or final visual','motion smoothness and timing','individual feet do not slide','all generated proportions identical beyond measured neutral helmet width','Unity import or playback'],'warnings':['Faint original alpha haze retained in native; resized alpha can quantize.','SE direction only; walk excluded.','Manual helmet/contact interpretation has artistic measurement uncertainty.']}
 totals={'light':[],'dark':[]};labels=[]
 for act in data['actions']:
  src=Image.open(ROOT/act['source']).convert('RGBA');assert sha(ROOT/act['source'])==act['sha256'];S=act['sourceCanvas'][0];N=rounded(S*180/act['helmetWidth']);s=N/S;M=rounded(S*s*mapFactor);maps=M/S
  ad=out/act['id'];[(ad/k).mkdir(parents=True,exist_ok=True) for k in ('native1024','normalized1024','map128h')]
  rebuild=Image.new('RGBA',src.size);coverage=np.zeros((src.height,src.width),np.uint8);fr=[];qa={'light':[],'dark':[]};alabel=[]
  for f in act['frames']:
   box=f['sourceRect'];im=src.crop(box);rebuild.paste(im,(box[0],box[1]));coverage[box[1]:box[3],box[0]:box[2]]+=1
   padded=Image.new('RGBA',(S,S));padded.paste(im,(0,0));assert padded.crop((0,0,im.width,im.height)).tobytes()==im.tobytes()
   g=f['groundRootInteger'];rawpts=[p['point'] for p in f['contacts']];outputs={};placement={};residual={}
   for kind,size,rootpoint,sz,scale in [('native1024',1024,[512,768],S,1),('normalized1024',1024,[512,768],N,s),('map128h',384,[192,288],M,maps)]:
    content=padded if kind=='native1024' else resized(padded,sz);off=[rootpoint[k]-rounded(g[k]*scale) for k in (0,1)];canvas=place(content,size,off);fp=ad/kind/f'{act["id"]}-{f["index"]:02d}.png';canvas.save(fp)
    outputs[kind]={**ref(fp),**stats(canvas)};pts=[[p[k]*scale+off[k] for k in (0,1)] for p in rawpts];delta=[sum(p[k] for p in pts)/2-rootpoint[k] for k in (0,1)];assert max(map(abs,delta))<=1.1
    residual[kind]=delta;placement[kind]={'sourceSize':[S,S],'resizedSize':[sz,sz],'scale':scale,'integerTranslation':off,'contactPoints':pts,'wholeResizedRectanglePreserved':True}
    if kind=='native1024':assert outputs[kind]['alphaNonzero']==stats(im)['alphaNonzero']
    if kind=='normalized1024':
     for name,bg in [('light',(240,235,222)),('dark',(25,34,41))]:qa[name].append(tile(canvas,rootpoint,pts,bg))
    if kind=='map128h':
     for name,bg in [('light',(240,235,222)),('dark',(25,34,41))]:totals[name].append(tile(canvas,rootpoint,pts,bg,marks=True))
   label=f'{act["id"]} {f["index"]} | {f["durationMs"]} ms';labels.append(label);alabel.append(label)
   fr.append({**f,'sourceCropRgbaSha256':hashlib.sha256(im.tobytes()).hexdigest(),'sourceCropStats':stats(im),'sourcePaddingSize':[S,S],'nativeExactRgbaMatch':True,'placement':placement,'contactMidpointResidual':residual,'outputs':outputs})
  assert rebuild.tobytes()==src.tobytes() and np.all(coverage==1),'Ownership must partition original exactly once'
  for name,bg in [('light',(240,235,222)),('dark',(25,34,41))]:board(qa[name],len(act['cuts']['x'])-1,bg,alabel,RR/f'{unit}-registration-{act["id"]}-{name}-aligned.png')
  ar={k:v for k,v in act.items() if k not in ('frames','manualContactRois')};ar.update(frameCount=len(fr),uniformScaleActual=s,normalizedHelmetWidthPx=act['helmetWidth']*s,mapScaleActual=maps,frames=fr,technicalChecks={'sourceReconstructionExactRGBA':True,'sourceOwnershipExactlyOnce':True,'allNativeExactRGBA':True,'allSourceRectanglesFit':True,'noOutputAlphaEdgeContact':True,'maxNormalizedRootErrorPx':max(max(map(abs,f['contactMidpointResidual']['normalized1024'])) for f in fr)},visualStatus='pending output overview review');manifest['actions'].append(ar)
 for name,bg in [('light',(240,235,222)),('dark',(25,34,41))]:board(totals[name],5,bg,labels,RR/f'{unit}-registration-all-actions-map-{name}.png')
 manifest['counts']={'sourceSheets':4,'animationFrames':20,'native1024PNG':20,'normalized1024PNG':20,'map128hPNG':20,'exportPNG':60,'generatedNewSheetsThisStep':0}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 clips={'character':data['character'],'direction':'SE','status':'candidate_not_playback_accepted','unityPivot':[0.5,0.25],'clips':[{'action':a['id'],'loop':a['loop'],'playback':'forward_once_hold_last' if a['id']=='defeat' else ('forward_loop' if a['loop'] else 'forward_once'),'frames':[{'durationMs':f['durationMs'],'native':f['outputs']['native1024']['file'],'normalized':f['outputs']['normalized1024']['file'],'map128h':f['outputs']['map128h']['file']} for f in a['frames']]} for a in manifest['actions']]}
 (out/'clips.json').write_text(json.dumps(clips,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'README.md').write_text(f'# {unit} SE 四动作技术候选\n\n20 帧，3 规格共 60 PNG；idle 4、attack 6、hurt 4、defeat 6。walk 未纳入。不是新增生图，也不是用户或引擎播放验收。\n\n原图按实际透明间隙划归，所有 RGBA 像素恰好分配一次，native1024 仅整数平移。normalized1024 每动作仅一个按中立头盔宽度登记的比例。接地点为人工确认双靴/双膝的支撑中点；每帧仅移动，不逐帧缩放。map128h 使用共同的母版比例，实际母版轮廓高 {manifest["master"]["mapStats"]["alpha16Height"]} px，跪姿不拉高。\n\n完整来源、SHA、原生 alpha、裁区、坐标、位移和重采样链见 manifest.json；候选时长见 clips.json。保留原生弱 alpha，无抹边、抠色和组件删除。双脚仍可随原画改变间距或斜率，数值根点误差不证明不存在视觉滑步。Unity/FFmpeg/编码未运行。\n',encoding='utf-8')
 print(json.dumps({'unit':unit,'output':str(out),'counts':manifest['counts'],'masterMapHeight':stats(mmap)['alpha16Height'],'maxNormalizedError':max(a['technicalChecks']['maxNormalizedRootErrorPx'] for a in manifest['actions']),'normalizedHeights':{a['id']:[f['outputs']['normalized1024']['alpha16Height'] for f in a['frames']] for a in manifest['actions']}},ensure_ascii=False))
