import json,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
root=Path('D:/work/wuxing-slg-iamge');rr=root/'records/troop-frames-20261028-r2'
data=json.loads((rr/'metal-ground-registration-measured.json').read_text(encoding='utf-8'))
out=root/'exports/01-率土之滨/troop-frames-20261028-r2/metal-grounded-20-candidate-v1'
if out.exists():raise SystemExit('Refuse existing output directory')
out.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'file':str(p.relative_to(root)).replace(chr(92),'/'),'sha256':sha(p)}
def stats(im):
 a=im.getchannel('A');hist=a.histogram()
 b=a.point(lambda x:255 if x>16 else 0).getbbox()
 return {'size':list(im.size),'alphaZero':hist[0],'alphaOne':hist[1],'alphaSemi':sum(hist[1:255]),'alphaOpaque':hist[255],'alphaNonzero':sum(hist[1:]),'alpha0BBox':a.getbbox(),'alpha16BBox':b,'alpha16Height':b[3]-b[1] if b else 0}
def paste_full(src,canvas,offset):
 x,y=offset
 assert x>=0 and y>=0 and x+src.width<=canvas[0] and y+src.height<=canvas[1],f'Full source rectangle would clip {offset} {src.size} {canvas}'
 dst=Image.new('RGBA',canvas,(0,0,0,0));dst.paste(src,(x,y))
 assert dst.crop((x,y,x+src.width,y+src.height)).tobytes()==src.tobytes(),'Pixel-loss in placement'
 return dst
def shrink(im,s):
 # No threshold, matte/keying, hygiene, crop, component removal or alpha floor.
 size=(round(im.width*s),round(im.height*s))
 return im.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')
def marker_tile(im,pts,rootpoint,background,edge=384):
 bg=Image.new('RGBA',im.size,background);bg.alpha_composite(im);tile=bg.resize((edge,edge),Image.Resampling.LANCZOS).convert('RGB');d=ImageDraw.Draw(tile);fac=edge/im.width
 rx=rootpoint[0]*fac;ry=rootpoint[1]*fac
 d.line((0,ry,edge-1,ry),fill=(65,130,225));d.line((rx,0,rx,edge-1),fill=(110,120,130))
 d.line((rx-5,ry,rx+5,ry),fill=(220,25,35),width=2);d.line((rx,ry-5,rx,ry+5),fill=(220,25,35),width=2)
 pp=[(p[0]*fac,p[1]*fac) for p in pts];d.line((*pp[0],*pp[1]),fill=(50,165,90),width=1)
 for x,y in pp:d.ellipse((x-2,y-2,x+2,y+2),outline=(0,150,50),width=1)
 return tile
master=Image.open(root/data['master']['file']).convert('RGBA');mastats=stats(master)
masterScale=180/data['master']['helmetWidth'];mresize=shrink(master,masterScale);masterActualScale=mresize.width/master.width
# Shared master comparator uses visually known ground midpoint only for QA.
mroot=[700,1160];mpoint=[round(v*masterActualScale) for v in mroot];moffset=[512-mpoint[0],768-mpoint[1]]
masterNorm=paste_full(mresize,(1024,1024),moffset);masterMap=shrink(masterNorm,0.375)
masterNorm.save(rr/'metal-ground-master-scale-reference.png');masterMap.save(rr/'metal-ground-master-scale-reference-128h.png')
manifest={'schema':'wuxing-slg.grounded-frame-candidates.v1','status':'technical_registration_candidate_not_user_or_engine_accepted','game':'五行问鼎','character':'troop-metal','direction':'SE','userApproved':False,'masterUserApproved':False,'sourceRegistration':ref(rr/'metal-ground-registration-measured.json'),'master':{**data['master'],'sha256':sha(root/data['master']['file']),'nativeStats':mastats,'uniformScale':masterActualScale,'qaReference':ref(rr/'metal-ground-master-scale-reference.png'),'mapReference':ref(rr/'metal-ground-master-scale-reference-128h.png'),'normalizedStats':stats(masterNorm),'mapStats':stats(masterMap)},'contract':{'nativeCanvas':[1024,1024],'nativeRoot':[512,768],'nativeOperation':'whole source cell with integer translation only; exact RGBA bytes retained','sharedHelmetWidthTargetPx':180,'normalCanvas':[1024,1024],'normalRoot':[512,768],'scalePerActionOnly':True,'perFrameFit':False,'resampler':'premultiplied Lanczos; no explicit alpha deletion or cleaning','alphaCaveat':'Original alpha is bit-for-bit preserved in native1024 frames. Downsampling changes samples/quantizes alpha normally; there is no alpha threshold edit, crop or removed component. The entire resized source rectangle is pasted and checked.','mapCanvas':[384,384],'mapRoot':[192,288],'mapScaleFromNormal':0.375,'map128hMeaning':'approximately 128px master standing silhouette; pose heights remain natural, knees/crouch never expanded','rootMethod':'manual boot/knee contact ROIs -> two contact points -> integer-rounded midpoint; each grounded frame registered separately','groundRootProofScope':'contact midpoint aligns; foot articulation/stance width are not redrawn'},'actions':[],'notProven':['user visual acceptance','motion smoothness and timing','individual foot immobility (stance width and contact-line slope can change)','consistent generated proportions beyond measured helmet width','Unity playback/import']}
allMapTiles=[]
for act in data['actions']:
 ad=out/act['id'];ad.mkdir();[(ad/n).mkdir() for n in ('native1024','normalized1024','map128h')]
 src=Image.open(root/act['source']).convert('RGBA');want=act['uniformActionScaleTo180Helmet'];cw=act['frames'][0]['sourceCellSize'][0]
 targetSize=round(cw*want);s=targetSize/cw;fr=[];qaLight=[];qaDark=[];mapTiles=[]
 for item in act['frames']:
  i=item['index'];frame=src.crop(item['sourceRect']);g=item['groundRootInteger'];offset=[512-g[0],768-g[1]]
  native=paste_full(frame,(1024,1024),offset);nf=ad/'native1024'/f'{act["id"]}-{i:02d}.png';native.save(nf)
  resized=shrink(frame,s);transformed=[round(g[0]*s),round(g[1]*s)];off=[512-transformed[0],768-transformed[1]]
  normal=paste_full(resized,(1024,1024),off);pf=ad/'normalized1024'/f'{act["id"]}-{i:02d}.png';normal.save(pf)
  mp=shrink(normal,0.375);mf=ad/'map128h'/f'{act["id"]}-{i:02d}.png';mp.save(mf)
  contactPts=[p['contactPoint'] for p in item['contactMeasurements']];nativePts=[[p[0]+offset[0],p[1]+offset[1]] for p in contactPts]
  normPts=[[p[0]*s+off[0],p[1]*s+off[1]] for p in contactPts]
  normMid=[sum(p[k] for p in normPts)/2 for k in (0,1)];residual=[normMid[0]-512,normMid[1]-768]
  assert max(abs(v) for v in residual)<=1.1,'Root residual exceeds integer placement bound'
  rawStats=stats(frame);ns=stats(native);ps=stats(normal);ms=stats(mp)
  assert ns['alphaNonzero']==rawStats['alphaNonzero'],'native alpha loss'
  for asset in (native,normal,mp):
   aa=np.array(asset.getchannel('A'));assert not (aa[0].any() or aa[-1].any() or aa[:,0].any() or aa[:,-1].any()),'alpha reaches output edge'
  fr.append({**item,'sourceCropRgbaSha256':hashlib.sha256(frame.tobytes()).hexdigest(),'nativeTranslation':offset,'nativeFullSourceRectanglePreserved':True,'nativeExactRgbaMatch':True,'native':{**ref(nf),**ns},'actionUniformScale':s,'resizedSourceSize':list(resized.size),'normalizedTranslation':off,'normalizedContactPoints':normPts,'normalizedContactMidpointResidualFromRoot':residual,'normalizedFullResizedRectanglePreserved':True,'normalized':{**ref(pf),**ps},'map128h':{**ref(mf),**ms},'mapContactMidpointResidualFromRoot':[v*0.375 for v in residual]})
  qaLight.append(marker_tile(normal,normPts,[512,768],(240,235,222,255)))
  qaDark.append(marker_tile(normal,normPts,[512,768],(25,34,41,255)))
  # Display full map128h canvas at actual resolution, no magnification.
  tile=Image.new('RGBA',mp.size,(240,235,222,255));tile.alpha_composite(mp);d=ImageDraw.Draw(tile);d.line((0,288,383,288),fill=(50,110,210,255));d.line((188,288,196,288),fill=(230,20,30,255),width=2)
  mapTiles.append(tile.convert('RGB'));allMapTiles.append((act['id'],i,tile.convert('RGB')))
 for name,tiles in [('light',qaLight),('dark',qaDark),('map128h',mapTiles)]:
  cols=act['cols'];rows=act['rows'];board=Image.new('RGB',(cols*392+8,rows*410+8),(240,235,222) if name!='dark' else (25,34,41));d=ImageDraw.Draw(board)
  for j,tile in enumerate(tiles):x=8+(j%cols)*392;y=8+(j//cols)*410;board.paste(tile,(x,y));d.text((x,y+387),f'{act["id"]} {j+1} | {act["durationsMs"][j]} ms | grounded root',fill=(30,30,30) if name!='dark' else (225,225,225))
  board.save(rr/f'metal-ground-{act["id"]}-{name}-aligned.png')
 actionResult={k:v for k,v in act.items() if k!='frames'};actionResult.update(uniformScaleRequested=want,uniformScaleActual=s,normalizedHelmetWidthPx=act['helmetWidth']*s,frameCount=len(fr),frames=fr,technicalChecks={'nativeExactRgbaAllFrames':True,'allSourceRectanglesFit':True,'allNormalizedRectanglesFit':True,'noOutputAlphaEdgeContact':True,'maximumRootMidpointErrorPx':max(max(abs(v) for v in f['normalizedContactMidpointResidualFromRoot']) for f in fr)},visualStatus='pending aligned review')
 manifest['actions'].append(actionResult)
manifest['counts']={'generatedNativeSheetsInThisStep':0,'sourceSheets':4,'animationFrames':20,'native1024Png':20,'normalized1024Png':20,'map128hPng':20,'exportPngTotal':60}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(out),'counts':manifest['counts'],'masterMapHeight':manifest['master']['mapStats']['alpha16Height'],'actions':[{'id':a['id'],'scale':a['uniformScaleActual'],'helmetWidth':a['normalizedHelmetWidthPx'],'maxRootError':a['technicalChecks']['maximumRootMidpointErrorPx'],'normalizedHeights':[f['normalized']['alpha16Height'] for f in a['frames']]} for a in manifest['actions']]},ensure_ascii=False))
