import json,hashlib,ast
from pathlib import Path
from PIL import Image,ImageDraw
root=Path('D:/work/wuxing-slg-iamge');rr=root/'records/troop-frames-20261028-r2';out=root/'exports/01-率土之滨/troop-frames-20261028-r2/metal-grounded-20-candidate-v1'
# Parse only: no Python bytecode compilation or execution of reusable exporter.
ast.parse((rr/'metal-grounded-frames-export-reusable.py').read_text(encoding='utf-8'))
m=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
crop=(85,140,300,316);cw=crop[2]-crop[0];ch=crop[3]-crop[1]
for name,bg in [('light',(240,235,222,255)),('dark',(25,34,41,255))]:
 board=Image.new('RGB',(7*(cw+10)+10,4*(ch+36)+10),bg[:3]);d=ImageDraw.Draw(board)
 for row,action in enumerate(m['actions']):
  items=[('MASTER',rr/'metal-ground-master-scale-reference-128h.png')]+[(str(f['index'])+' / '+str(f['durationMs'])+'ms',root/f['map128h']['file']) for f in action['frames']]
  for col,(label,p) in enumerate(items):
   im=Image.open(p).convert('RGBA');bb=im.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox()
   assert crop[0]<=bb[0] and crop[1]<=bb[1] and crop[2]>=bb[2] and crop[3]>=bb[3],f'QA crop cuts subject: {p} {bb}'
   tile=Image.new('RGBA',im.size,bg);tile.alpha_composite(im);tile=tile.crop(crop).convert('RGB')
   x=10+col*(cw+10);y=10+row*(ch+36);board.paste(tile,(x,y))
   ry=y+288-crop[1];rx=x+192-crop[0];d.line((x,ry,x+cw-1,ry),fill=(60,125,215));d.line((rx-3,ry,rx+3,ry),fill=(225,35,30),width=2)
   d.text((x,y+ch+5),action['id']+' | '+label,fill=(25,25,25) if name=='light' else (230,230,230))
 board.save(rr/f'metal-grounded-20-overview-{name}.png')
print('Reusable exporter syntax parsed; both 20-frame overviews generated with common QA crop.')
