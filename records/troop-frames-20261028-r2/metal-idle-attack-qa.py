import json, hashlib, sys
from pathlib import Path
from PIL import Image
root=Path('D:/work/wuxing-slg-iamge')
rr=root/'records/troop-frames-20261028-r2'
action=sys.argv[1]; version=sys.argv[2] if len(sys.argv)>2 else 'v1'
f=root/f'designs/01-率土之滨/troop-frames-20261028-r2/metal-{action}-se-{version}.png'
im=Image.open(f).convert('RGBA')
a=im.getchannel('A'); hist=a.histogram(); cols=2 if action=='idle' else 3; rows=2
cells=[]
for r in range(rows):
 for c in range(cols):
  box=(round(c*im.width/cols),round(r*im.height/rows),round((c+1)*im.width/cols),round((r+1)*im.height/rows))
  ca=a.crop(box); masks={str(t):ca.point(lambda x:255 if x>t else 0) for t in (0,1,16)}
  bboxes={k:mask.getbbox() for k,mask in masks.items()}
  b=bboxes['16']; ch=ca.height; cw=ca.width
  edge=sum(1 for v in ca.crop((0,0,cw,1)).getdata() if v>16)+sum(1 for v in ca.crop((0,ch-1,cw,ch)).getdata() if v>16)+sum(1 for v in ca.crop((0,0,1,ch)).getdata() if v>16)+sum(1 for v in ca.crop((cw-1,0,cw,ch)).getdata() if v>16)
  cells.append({'index':r*cols+c+1,'box':box,'localBboxByAlphaThreshold':bboxes,'alpha16HeightRatio':None if not b else (b[3]-b[1])/ch,'alpha16BottomRatio':None if not b else b[3]/ch,'alpha16EdgePixelsWithCornerDoubleCount':edge,'rgbaCropSha256':hashlib.sha256(im.crop(box).tobytes()).hexdigest()})
report={'file':str(f.relative_to(root)).replace(chr(92),'/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'nativeSize':im.size,'mode':im.mode,'format':'PNG','alpha':{'zero':hist[0],'one':hist[1],'semi':sum(hist[1:255]),'opaque':hist[255],'min':a.getextrema()[0],'max':a.getextrema()[1]},'grid':{'columns':cols,'rows':rows,'requestedCell':[512,512],'actualExactCell':[im.width/cols,im.height/rows],'rounding':'nearest grid edge'},'cells':cells,'nativeUnmodified':True,'rootPivot':'not manually accepted','formalAnimationApproved':False}
out=rr/f'metal-{action}-{version}-qa.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for name,color in [('light',(240,235,222,255)),('dark',(25,34,41,255))]:
 bg=Image.new('RGBA',im.size,color); bg.alpha_composite(im); bg.convert('RGB').save(rr/f'metal-{action}-{version}-{name}.png')
gen=rr/f'metal-{action}-{version}.generation.json'
if gen.exists():
 rec=json.loads(gen.read_text(encoding='utf-8'));rec.update(width=im.width,height=im.height,format='PNG',mode='RGBA',alpha=report['alpha'],qa=str(out.relative_to(root)).replace(chr(92),'/'));gen.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
