from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
root=Path('D:/work/wuxing-slg-iamge');rr=root/'records/troop-frames-20261029-r3';spec=json.loads((rr/'fire-earth-registration-ownership-input.json').read_text(encoding='utf-8'))
report={}
for unit,us in spec.items():
 ma=Image.open(root/us['master']).convert('RGBA');b=ma.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
 report[unit]={'masterAlpha16Bbox':b,'masterAlpha16Height':b[3]-b[1],'actions':{}}
 for action,cut in us['actions'].items():
  p=root/f'designs/01-率土之滨/assets/troop-frames-20261029-r3/{unit}-{action}-se-v1.png';im=Image.open(p).convert('RGBA');a=np.array(im)[:,:,3];xs=cut['x'];ys=[0,cut['y'],im.height];cols=len(xs)-1
  crossing=[{'axis':'y','line':cut['y'],'alpha16In2pxBand':int((a[cut['y']-1:cut['y']+1]>16).sum())}]+[{'axis':'x','line':x,'alpha16In2pxBand':int((a[:,x-1:x+1]>16).sum())} for x in xs[1:-1]]
  assert all(c['alpha16In2pxBand']==0 for c in crossing),crossing
  reassembled=Image.new('RGBA',im.size);tiles=[];frames=[]
  maxdim=max(max(xs[i+1]-xs[i] for i in range(cols)),ys[1],ys[2]-ys[1])
  for row in range(2):
   for col in range(cols):
    rect=[xs[col],ys[row],xs[col+1],ys[row+1]];fr=im.crop(rect);reassembled.paste(fr,(rect[0],rect[1]));idx=row*cols+col+1
    bbox=fr.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();crop=[max(0,bbox[0]+60),max(0,bbox[3]-155),min(fr.width,bbox[2]+8),min(fr.height,bbox[3]+22)]
    # Fixed local source pixel coordinates are shown; this crop is QA only.
    cr=fr.crop(crop);bg=Image.new('RGBA',cr.size,(240,235,222,255));bg.alpha_composite(cr);tile=bg.convert('RGB');d=ImageDraw.Draw(tile)
    for x in range((crop[0]//25+1)*25,crop[2],25):xx=x-crop[0];d.line((xx,0,xx,tile.height),fill=(190,205,205));d.text((xx+1,2),str(x),fill=(20,45,55))
    for y in range((crop[1]//25+1)*25,crop[3],25):yy=y-crop[1];d.line((0,yy,tile.width,yy),fill=(190,205,205));d.text((2,yy+1),str(y),fill=(20,45,55))
    tiles.append((f'{unit}-{action} {idx} local; sourceRect={rect}',tile))
    frames.append({'index':idx,'sourceRect':rect,'ownedSize':list(fr.size),'sourceCanvas':[maxdim,maxdim],'alpha16Bbox':bbox})
  assert reassembled.tobytes()==im.tobytes(),'Ownership is not exact source partition'
  w=max(t.width for _,t in tiles);h=max(t.height for _,t in tiles);board=Image.new('RGB',(cols*(w+8)+8,2*(h+32)+8),(240,235,222));d=ImageDraw.Draw(board)
  for i,(title,tile) in enumerate(tiles):x=8+(i%cols)*(w+8);y=8+(i//cols)*(h+32);d.text((x,y),title,fill=(20,20,20));board.paste(tile,(x,y+24))
  board.save(rr/f'{unit}-registration-{action}-feet-grid.png')
  report[unit]['actions'][action]={'source':str(p.relative_to(root)).replace(chr(92),'/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sourceSize':list(im.size),'sourceCanvas':[maxdim,maxdim],'cuts':{'x':xs,'y':ys},'crossingChecks':crossing,'exactSourcePartition':True,'frames':frames}
  # Ownership lines on composed sheet for manual confirmation.
  bg=Image.new('RGBA',im.size,(240,235,222,255));bg.alpha_composite(im);dd=ImageDraw.Draw(bg)
  for x in xs[1:-1]:dd.line((x,0,x,im.height),fill=(40,110,220,255),width=2)
  dd.line((0,cut['y'],im.width,cut['y']),fill=(40,110,220,255),width=2)
  bg.convert('RGB').save(rr/f'{unit}-registration-{action}-ownership.png')
(rr/'fire-earth-registration-ownership-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({u:{'masterAlpha16Height':v['masterAlpha16Height'],'actions':{a:{'canvas':d['sourceCanvas'],'crossingChecks':d['crossingChecks']} for a,d in v['actions'].items()}} for u,v in report.items()}))
