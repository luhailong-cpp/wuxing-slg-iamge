"""Export existing native skill art; crop, downscale and pad only, never repaint or clear alpha."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path('D:/work/wuxing-slg-iamge')
SOURCE='designs/01-率土之滨/assets/five-elements/five-elements-skill-icons-v1.png'
OUT=Path('exports/01-率土之滨/five-elements/skill-icons')
BOXES=[('metal','金',(0,0,512,496)),('wood','木',(512,0,1024,512)),('water','水',(1024,0,1536,512)),('fire','火',(0,496,512,1024)),('earth','土',(512,512,1024,1024))]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def info(im):
 a=np.array(im.getchannel('A'));b=Image.fromarray(np.uint8(a>16)*255).getbbox()
 edges=np.concatenate([a[0,:],a[-1,:],a[:,0],a[:,-1]])
 return {'range':[int(a.min()),int(a.max())],'faintAlpha1Pixels':int((a==1).sum()),'edgeAbove1':int((edges>1).sum()),'edgeAbove16':int((edges>16).sum()),'bboxAbove16':b,'marginAbove16':min(b[0],b[1],im.width-b[2],im.height-b[3]) if b else None}
def main():
 now=datetime.now(timezone.utc).isoformat();src=ROOT/SOURCE;digest=sha(src)
 rec=json.loads(Path(str(src)+'.generation.json').read_text(encoding='utf-8-sig'))
 if rec['sha256']!=digest:raise ValueError('Source mismatch')
 sheet=Image.open(src);a=np.array(sheet.getchannel('A'));cover=np.zeros(a.shape,dtype=np.uint8)
 (ROOT/OUT).mkdir(parents=True,exist_ok=True)
 items=[];preview=Image.new('RGB',(1000,720));draw=ImageDraw.Draw(preview)
 for col,(name,label,box) in enumerate(BOXES):
  x0,y0,x1,y1=box;cover[y0:y1,x0:x1]+=1
  crop=sheet.crop(box);qa=info(crop)
  if qa['edgeAbove1']:raise ValueError(f'Visible crop edge: {name}')
  path=ROOT/OUT/(name+'-native.png')
  if path.exists():raise FileExistsError(path)
  crop.save(path);rel=path.relative_to(ROOT).as_posix()
  side={'schemaVersion':1,'file':rel,'sha256':sha(path),'derivedAtUtc':now,'width':crop.width,'height':crop.height,'format':'PNG','mode':'RGBA','operation':'manual_ownership_rectangle_crop','cropBox':box,'resampled':False,'alphaModified':False,'art_source':'existing','derivedFrom':[{'file':SOURCE,'sha256':digest,'record':SOURCE+'.generation.json'}],'alphaInspection':qa,'userApproved':False,'clientIntegrated':False,'status':'candidate_skill_icon_pending_user_review'}
  dump(Path(str(path)+'.derived.json'),side);entry={'element':name,'label':label,'native':rel,'nativeRecord':rel+'.derived.json','displayVariants':[]}
  for row,size in enumerate([32,64,128]):
   b=qa['bboxAbove16'];scale=size*.78/max(b[2]-b[0],b[3]-b[1]);dims=tuple(max(1,round(v*scale)) for v in crop.size)
   scaled=crop.convert('RGBa').resize(dims,Image.Resampling.LANCZOS).convert('RGBA');canvas=Image.new('RGBA',(size,size));offset=((size-dims[0])//2,(size-dims[1])//2);canvas.paste(scaled,offset)
   p=ROOT/OUT/f'{name}-{size}.png'
   if p.exists():raise FileExistsError(p)
   canvas.save(p);r=p.relative_to(ROOT).as_posix();q=info(canvas)
   d={'schemaVersion':1,'file':r,'sha256':sha(p),'derivedAtUtc':now,'width':size,'height':size,'format':'PNG','mode':'RGBA','operation':'premultiplied_alpha_lanczos_downscale_then_center_padding','sourceScale':scale,'resizedDimensions':dims,'pasteOffset':offset,'resampled':True,'alphaCleaned':False,'nativeDetailClaim':False,'art_source':'existing','derivedFrom':[{'file':rel,'sha256':side['sha256'],'record':rel+'.derived.json'}],'alphaInspection':q,'userApproved':False,'clientIntegrated':False,'status':'display_size_candidate'}
   dump(Path(str(p)+'.derived.json'),d);entry['displayVariants'].append({'size':size,'file':r,'record':r+'.derived.json'})
   for bg,color in enumerate(['#f5f0e4','#152b2c']):
    tile=Image.new('RGBA',(200,100),color);tile.alpha_composite(canvas,((200-size)//2,(100-size)//2 if size<=64 else -14))
    # 128px previews use a 160-high cell below separately; no deliverable art altered.
    if size==128:
     tile=Image.new('RGBA',(200,160),color);tile.alpha_composite(canvas,((200-size)//2,22))
    yy=(0 if row==0 else 200 if row==1 else 400)+bg*(100 if row<2 else 160)
    preview.paste(tile.convert('RGB'),(col*200,yy))
    draw.text((col*200+6,yy+5),f'{name} {size}px',fill='#263c37' if bg==0 else '#e7e1ce')
  items.append(entry)
 lost=int(((a>1)&(cover==0)).sum());overlap=int(((a>1)&(cover>1)).sum())
 if lost or overlap:raise ValueError('Ownership lost or duplicated above alpha1')
 raw=json.loads((ROOT/'work/skill-icons-v1/raw-qc/sheet-qc.json').read_text(encoding='utf-8-sig'))
 manifest={'schemaVersion':1,'createdAtUtc':now,'assetType':'five_candidate_element_skill_icons','source':SOURCE,'sourceSha256':digest,'nativeCount':5,'displayDerivativeCount':15,'animationFrames':0,'items':items,'rawSheetQc':raw,'manualOwnership':{'gridUsedForFinalCrop':False,'reason':'Fire faint leading edge begins at source y511, so first-column split moved from512 to496 within clear alpha<=1 band y479..510. Other columns retain512 cell split.','allSourcePixelsAbove1CoveredExactlyOnce':True,'uncoveredAbove1':lost,'overlapAbove1':overlap,'alphaModified':False,'sixthCellMaxAlpha':int(a[512:,1024:].max())},'warnings':['Generated subjects exceed requested320px silhouette and96px cell margins; native icons remain candidates.','Native faint alpha1 residue retained; empty sixth cell contains259 alpha1 pixels.','Grid fire top margin4px above16 and earth12px: manual crop fixes fire clipping ownership but not original safe-frame compliance.','32px detail is condensed; use64px or larger for primary skill display.'],'userApproved':False,'clientIntegrated':False,'status':'candidate_exports_with_raw_qc_warnings'}
 dump(ROOT/OUT/'skill-icons-manifest.json',manifest);(ROOT/'work/skill-icons-v1').mkdir(parents=True,exist_ok=True);preview.save(ROOT/'work/skill-icons-v1/skill-icons-light-dark.png')
 print(json.dumps({'native':5,'display':15,'lostAbove1':lost,'overlapAbove1':overlap,'manifest':(OUT/'skill-icons-manifest.json').as_posix(),'rawStatus':raw['status']}))
if __name__=='__main__':main()

