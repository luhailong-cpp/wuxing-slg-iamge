import json,hashlib,math,sys
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
root=Path('D:/work/wuxing-slg-iamge');rr=root/'records/troop-frames-20261028-r2'
inp=json.loads((rr/'metal-ground-registration-input.json').read_text(encoding='utf-8'))
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def contact(frame,roi):
 a=np.array(frame.getchannel('A')); x0,y0,x1,y1=roi; m=a[y0:y1,x0:x1]>16
 ys,xs=np.where(m)
 if not len(xs):raise ValueError(f'Empty manually selected contact ROI {roi}')
 y=int(ys.max()+y0+1)
 yy,xx=np.where(m & (np.arange(m.shape[0])[:,None]>=int(ys.max())-4))
 point=[round((int(xx.min())+int(xx.max())+1)/2+x0,2),y]
 return {'roi':roi,'contactPoint':point,'solidBounds':[int(xs.min()+x0),int(ys.min()+y0),int(xs.max()+x0+1),y],'roiBottomClearance':y1-y}
data={'schema':'wuxing-slg.manual-ground-registration.v1','input':str((rr/'metal-ground-registration-input.json').relative_to(root)).replace(chr(92),'/'),'inputSha256':h(rr/'metal-ground-registration-input.json'),'master':inp['master'],'registration':inp['registration'],'actions':[]}
for act in inp['actions']:
 source=root/act['source'];im=Image.open(source).convert('RGBA');cw=im.width//act['cols'];ch=im.height//act['rows']
 frames=[];reviews=[]
 for i,rois in enumerate(act['contactRois']):
  c=i%act['cols'];r=i//act['cols'];box=[c*cw,r*ch,(c+1)*cw,(r+1)*ch]
  frame=im.crop(box);cpts=[contact(frame,roi) for roi in rois]
  rawroot=[sum(v['contactPoint'][k] for v in cpts)/len(cpts) for k in (0,1)]
  rroot=[math.floor(v+0.5) for v in rawroot]
  frames.append({'index':i+1,'sourceRect':box,'sourceCellSize':[cw,ch],'contactKind':act['contactKind'][i],'manualRois':rois,'contactMeasurements':cpts,'groundRootExactMidpoint':rawroot,'groundRootInteger':rroot,'registrationRoundingError':[rroot[k]-rawroot[k] for k in (0,1)],'durationMs':act['durationsMs'][i]})
  x0=max(0,min(v[0] for v in rois)-20);y0=max(0,min(v[1] for v in rois)-20);x1=min(cw,max(v[2] for v in rois)+20);y1=min(ch,max(v[3] for v in rois)+20)
  crop=frame.crop((x0,y0,x1,y1));bg=Image.new('RGBA',crop.size,(240,235,222,255));bg.alpha_composite(crop)
  tile=bg.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST).convert('RGB');d=ImageDraw.Draw(tile)
  pts=[((v['contactPoint'][0]-x0)*2,(v['contactPoint'][1]-y0)*2) for v in cpts]
  d.line((*pts[0],*pts[1]),fill=(40,100,240),width=2)
  for px,py in pts:d.ellipse((px-5,py-5,px+5,py+5),outline=(0,145,45),width=2)
  rx=(rroot[0]-x0)*2;ry=(rroot[1]-y0)*2;d.line((rx-7,ry,rx+7,ry),fill=(230,20,30),width=2);d.line((rx,ry-7,rx,ry+7),fill=(230,20,30),width=2)
  title=f'{act["id"]} {i+1}: contacts {cpts[0]["contactPoint"]} {cpts[1]["contactPoint"]}; root {rroot}'
  reviews.append((title,tile))
 width=max(v[1].width for v in reviews);height=sum(v[1].height+28 for v in reviews)
 board=Image.new('RGB',(width,height),(240,235,222));d=ImageDraw.Draw(board);y=0
 for title,tile in reviews:d.text((4,y+5),title,fill=(20,20,20));board.paste(tile,(0,y+28));y+=tile.height+28
 board.save(rr/f'metal-ground-{act["id"]}-contact-review.png')
 srcRecord=act['sourceRecord'] or act['source']+'.generation.json'
 data['actions'].append({**{k:v for k,v in act.items() if k not in ('contactRois','contactKind')},'sourceRecord':srcRecord,'sourceSha256':h(source),'sourceMode':im.mode,'sourceSize':list(im.size),'uniformActionScaleTo180Helmet':180/act['helmetWidth'],'frames':frames})
 # Neutral rigid helmet landmarks, not plume or bbox heights.
 f=im.crop((0,0,cw,ch));left,right=act['helmetWidthLandmarks'];yline={'idle':275,'attack':270,'hurt':330,'defeat':280}[act['id']]
 crop=f.crop((max(0,left-25),max(0,yline-170),min(cw,right+25),min(ch,yline+65)));bg=Image.new('RGBA',crop.size,(240,235,222,255));bg.alpha_composite(crop);tile=bg.convert('RGB');d=ImageDraw.Draw(tile);xx0=max(0,left-25);yy0=max(0,yline-170)
 d.line((left-xx0,yline-yy0,right-xx0,yline-yy0),fill=(220,35,35),width=2)
 for x in (left-xx0,right-xx0):d.line((x,0,x,tile.height),fill=(30,100,210))
 d.text((3,3),f'{act["id"]}: width {right-left} source px',fill=(20,20,20));tile.save(rr/f'metal-ground-{act["id"]}-helmet-review.png')
(rr/'metal-ground-registration-measured.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for a in data['actions']:print(json.dumps({'action':a['id'],'scale':a['uniformActionScaleTo180Helmet'],'roots':[f['groundRootInteger'] for f in a['frames']],'contactY':[ [p['contactPoint'][1] for p in f['contactMeasurements']] for f in a['frames']],'minRoiBottomClearance':min(p['roiBottomClearance'] for f in a['frames'] for p in f['contactMeasurements'])}))
