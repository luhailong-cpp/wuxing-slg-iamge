import json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
R=Path('D:/work/wuxing-slg-iamge');D=R/'designs/01-率土之滨/characters/roster-expansion-20261029-wei1';Q=R/'records/roster-expansion-20261029-wei1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in D.glob('*-master-v*.png'):
 j=Q/(p.stem+'-alpha.json')
 if j.exists() and json.loads(j.read_text(encoding='utf-8'))['sha256']==sha(p):continue
 im=Image.open(p);assert im.mode=='RGBA';a=np.array(im.getchannel('A'));b=Image.fromarray(np.uint8(a>16)*255).getbbox();bb=Image.fromarray(np.uint8(a>1)*255).getbbox();o={'file':p.relative_to(R).as_posix(),'sha256':sha(p),'size':list(im.size),'mode':im.mode,'alphaMinMax':[int(a.min()),int(a.max())],'alphaZero':int((a==0).sum()),'alphaOne':int((a==1).sum()),'semiTransparent':int(((a>0)&(a<255)).sum()),'alphaOpaque':int((a==255).sum()),'bboxAlpha16':b,'marginsAlpha16':[b[0],b[1],im.width-b[2],im.height-b[3]],'bboxAlpha1':bb,'edgeAlpha16Pixels':int((a[0]>16).sum()+(a[-1]>16).sum()+(a[:,0]>16).sum()+(a[:,-1]>16).sum()),'sourcePixelsModified':False,'alphaHygiene':'none','qaViews':[]}
 for label,bg in [('light',(245,239,222,255)),('dark',(28,43,48,255))]:
  cv=Image.new('RGBA',im.size,bg);cv.alpha_composite(im);qp=Q/(p.stem+'-'+label+'.png');cv.save(qp);o['qaViews'].append({'file':qp.relative_to(R).as_posix(),'sha256':sha(qp),'operation':'native size source alpha composite on QA background','backgroundRGBA':bg,'qaOnly':True})
 j.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(o,ensure_ascii=False))
