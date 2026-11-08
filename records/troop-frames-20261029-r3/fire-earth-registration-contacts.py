import json,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
root=Path('D:/work/wuxing-slg-iamge');rr=root/'records/troop-frames-20261029-r3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def contact(im,roi):
 x0,y0,x1,y1=roi;a=np.array(im.getchannel('A'));x1=min(x1,im.width);y1=min(y1,im.height);m=a[y0:y1,x0:x1]>16;ys,xs=np.where(m)
 if not len(xs):raise ValueError(f'Empty contact ROI {roi}')
 bottom=int(ys.max());yy,xx=np.where(m & (np.arange(m.shape[0])[:,None]>=bottom-4))
 return {'manualRoi':roi,'effectiveRoi':[x0,y0,x1,y1],'point':[(int(xx.min())+int(xx.max())+1)/2+x0,bottom+y0+1],'bottomClearance':y1-bottom-y0-1}
for unit in ('fire','earth'):
 ip=rr/f'{unit}-registration-input.json';data=json.loads(ip.read_text(encoding='utf-8'));data['inputSha256']=sha(ip);data['master']['sha256']=sha(root/data['master']['file'])
 for act in data['actions']:
  src=Image.open(root/act['source']).convert('RGBA');act['sourceRecord']=act['source']+'.generation.json';act['sourceRecordSha256']=sha(root/act['sourceRecord']);reviews=[]
  for f,rois,kind,duration in zip(act['frames'],act['manualContactRois'],act['contactKind'],act['durationMs']):
   im=src.crop(f['sourceRect']);pts=[contact(im,roi) for roi in rois];exact=[sum(v['point'][k] for v in pts)/2 for k in (0,1)];gr=[math.floor(v+0.5) for v in exact];f.update(contacts=pts,groundRootExact=exact,groundRootInteger=gr,contactKind=kind,durationMs=duration)
   x0=max(0,min(v[0] for v in rois)-12);x1=min(im.width,max(v[2] for v in rois)+12);y0=max(0,min(v[1] for v in rois)-12);y1=min(im.height,max(v[3] for v in rois)+12)
   crop=im.crop((x0,y0,x1,y1));bg=Image.new('RGBA',crop.size,(240,235,222,255));bg.alpha_composite(crop);tile=bg.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST).convert('RGB');d=ImageDraw.Draw(tile)
   pp=[((v['point'][0]-x0)*2,(v['point'][1]-y0)*2) for v in pts];d.line((*pp[0],*pp[1]),fill=(45,110,220),width=2)
   for x,y in pp:d.ellipse((x-4,y-4,x+4,y+4),outline=(0,145,40),width=2)
   rx=(gr[0]-x0)*2;ry=(gr[1]-y0)*2;d.line((rx-6,ry,rx+6,ry),fill=(220,20,30),width=2);d.line((rx,ry-6,rx,ry+6),fill=(220,20,30),width=2)
   title=f'{unit} {act["id"]} {f["index"]}: {pts[0]["point"]} {pts[1]["point"]} => {gr}'
   reviews.append((title,tile))
  w=max(t.width for _,t in reviews);h=sum(t.height+24 for _,t in reviews);board=Image.new('RGB',(w,h),(240,235,222));dd=ImageDraw.Draw(board);yy=0
  for title,t in reviews:dd.text((4,yy+4),title,fill=(20,20,20));board.paste(t,(0,yy+24));yy+=t.height+24
  board.save(rr/f'{unit}-registration-{act["id"]}-contact-review.png')
  im=src.crop(act['frames'][0]['sourceRect']);left,right=act['helmetWidthLandmarks'];yl=({'idle':300,'attack':235,'hurt':315,'defeat':250} if unit=='fire' else {'idle':320,'attack':270,'hurt':360,'defeat':300})[act['id']]
  box=(max(0,left-20),max(0,yl-220),min(im.width,right+20),min(im.height,yl+65));cr=im.crop(box);bg=Image.new('RGBA',cr.size,(240,235,222,255));bg.alpha_composite(cr);dd=ImageDraw.Draw(bg)
  for x in (left,right):xx=x-box[0];dd.line((xx,0,xx,cr.height),fill=(35,110,220,255))
  dd.line((left-box[0],yl-box[1],right-box[0],yl-box[1]),fill=(220,25,35,255),width=2);dd.text((3,3),f'{unit} {act["id"]} width={right-left}',fill=(15,15,15,255));bg.convert('RGB').save(rr/f'{unit}-registration-{act["id"]}-helmet-review.png')
 (rr/f'{unit}-registration-measured.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'unit':unit,'roots':{a['id']:[f['groundRootInteger'] for f in a['frames']] for a in data['actions']},'minRoiBottomClearance':min(p['bottomClearance'] for a in data['actions'] for f in a['frames'] for p in f['contacts'])}))
