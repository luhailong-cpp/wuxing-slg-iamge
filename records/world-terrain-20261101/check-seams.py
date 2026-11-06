import json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
src = ROOT / 'designs/01-率土之滨/maps/world-terrain-20261101/grass-seamless-v1.png'
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.float32)
dx = float(np.abs(a[:,1:]-a[:,:-1]).mean())
dy = float(np.abs(a[1:]-a[:-1]).mean())
seam_x = float(np.abs(a[:,0]-a[:,-1]).mean())
seam_y = float(np.abs(a[0]-a[-1]).mean())
result = {'schemaVersion':1, 'source':src.relative_to(ROOT).as_posix(),
          'sha256':hashlib.sha256(src.read_bytes()).hexdigest(), 'nativeSize':list(im.size),
          'horizontal':{'edgeMeanAbsRgb':seam_x,'interiorMeanAbsRgb':dx,'ratio':seam_x/max(dx,.001)},
          'vertical':{'edgeMeanAbsRgb':seam_y,'interiorMeanAbsRgb':dy,'ratio':seam_y/max(dy,.001)},
          'thresholdRatio':2.0, 'numericSeamPassed':max(seam_x/max(dx,.001),seam_y/max(dy,.001))<=2,
          'visualReviewPassed':False, 'nativeSourcePixelsModified':False, 'warning':[]}
if im.size != (1024,1024):
    result['warning'].append({'id':'NATIVE_SIZE_DIFFERS_FROM_PROMPT','value':list(im.size),'threshold':[1024,1024]})
if not result['numericSeamPassed']:
    result['warning'].append({'id':'REPEAT_EDGE_DISCONTINUITY','value':[seam_x/max(dx,.001),seam_y/max(dy,.001)],'threshold':2.0})
tile = Image.new('RGB',(im.width*3,im.height*3))
for y in range(3):
    for x in range(3):tile.paste(im,(x*im.width,y*im.height))
tile.crop((im.width-256,im.height-256,im.width+256,im.height+256)).save(HERE/'repeat-join-native.png')
overview = tile.resize((1254,1254),Image.Resampling.LANCZOS)
overview.save(HERE/'repeat-3x3-overview.png')
result['qaDerivations']=[{'file':'records/world-terrain-20261101/repeat-join-native.png','operation':'512x512 exact pixel crop across the horizontal/vertical repeat junction'},
                         {'file':'records/world-terrain-20261101/repeat-3x3-overview.png','operation':'QA repeat overview downscale only; not native detail'}]
previous=HERE/'seam-review.json'
if previous.exists():
    old=json.loads(previous.read_text(encoding='utf-8'))
    if old.get('sha256')==result['sha256']:
        result['visualReviewPassed']=old.get('visualReviewPassed',False)
        if 'visualReview' in old:result['visualReview']=old['visualReview']
        result['warning']+= [x for x in old.get('warning',[]) if x not in result['warning']]
(HERE/'seam-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
