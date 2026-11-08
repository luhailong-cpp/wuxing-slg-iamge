import json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
root=Path('D:/work/wuxing-slg-iamge');rr=root/'records/troop-frames-20261029-r3';sroot=root/'designs/01-率土之滨/assets/troop-frames-20261029-r3'
def runs(values):
 out=[];a=None
 for i,v in enumerate(values):
  if v and a is None:a=i
  if a is not None and (not v or i==len(values)-1):
   end=i if not v else i+1;out.append([a,end]);a=None
 return out
reports={}
for unit in ('fire','earth'):
 for action in ('idle','attack','hurt','defeat'):
  f=sroot/f'{unit}-{action}-se-v1.png';im=Image.open(f).convert('RGBA');a=np.array(im)[:,:,3];cols=2 if action in ('idle','hurt') else 3
  ylo,yhi=(570,690) if im.height==1254 else (480,620)
  yr=runs((a[ylo:yhi]>16).sum(axis=1)==0);yr=[[u+ylo,v+ylo] for u,v in yr]
  rec={'file':str(f.relative_to(root)).replace(chr(92),'/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':list(im.size),'rowTransparentRangesAlpha16':yr,'colTransparentRangesAlpha16':[]}
  # Candidate manual horizontal strip positions for read-only diagnosis.
  cut=640 if im.height==1254 else 560 if action=='defeat' else 520
  for y0,y1 in [(0,cut),(cut,im.height)]:
   cs=[]
   for c in range(1,cols):
    center=round(c*im.width/cols);lo=max(0,center-90);hi=min(im.width,center+100)
    xx=runs((a[y0:y1,lo:hi]>16).sum(axis=0)==0);cs.append([[u+lo,v+lo] for u,v in xx])
   rec['colTransparentRangesAlpha16'].append({'row':[y0,y1],'gapsByColumn':cs})
  reports[unit+'-'+action]=rec
(rr/'fire-earth-registration-gap-diagnosis.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(reports,ensure_ascii=False))
