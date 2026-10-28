from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
root=Path('D:/work/wuxing-slg-iamge'); rec=root/'records/troop-frames-20261028-r2'
srcs=[('idle','designs/01-率土之滨/troop-frames-20261028-r2/metal-idle-se-v2.png',2,2),('attack','designs/01-率土之滨/troop-frames-20261028-r2/metal-attack-se-v1.png',2,3),('hurt','designs/01-率土之滨/assets/troop-frames-20261028-r2/metal-hurt-se-v1.png',2,2),('defeat','designs/01-率土之滨/assets/troop-frames-20261028-r2/metal-defeat-se-v1.png',2,3)]
for action,src,rows,cols in srcs:
 im=Image.open(root/src).convert('RGBA');cw=im.width//cols;ch=im.height//rows
 for part in ['head','feet']:
  box=(120,75,510,400) if action=='idle' and part=='head' else (90,30,cw-20,int(ch*.65)) if part=='head' else (100,int(ch*.60),cw-20,ch)
  if part=='feet' and action=='idle':box=(190,375,470,535)
  if part=='feet' and action=='attack':box=(130,330,480,510)
  if part=='feet' and action=='hurt':box=(120,400,570,627)
  if part=='feet' and action=='defeat':box=(100,280,500,512)
  bw=box[2]-box[0];bh=box[3]-box[1];margin=32
  board=Image.new('RGB',(cols*(bw+margin*2),rows*(bh+margin*2)),(240,235,222));d=ImageDraw.Draw(board)
  for i in range(rows*cols):
   c=i%cols;r=i//cols;frame=im.crop((c*cw,r*ch,(c+1)*cw,(r+1)*ch));crop=frame.crop(box)
   tile=Image.new('RGBA',crop.size,(240,235,222,255));tile.alpha_composite(crop)
   ox=c*(bw+margin*2)+margin;oy=r*(bh+margin*2)+margin;board.paste(tile.convert('RGB'),(ox,oy))
   d.text((ox,oy-28),f'{action} {i+1} / source cell pixels',fill=(20,20,20))
   for x in range((box[0]//20+1)*20,box[2],20):
    px=ox+x-box[0];d.line((px,oy,px,oy+bh-1),fill=(191,202,203));d.text((px-7,oy-13),str(x),fill=(20,60,70))
   for y in range((box[1]//20+1)*20,box[3],20):
    py=oy+y-box[1];d.line((ox,py,ox+bw-1,py),fill=(191,202,203));d.text((ox-28,py-4),str(y),fill=(20,60,70))
  board.save(rec/f'metal-ground-{action}-{part}-measure.png')
master=Image.open(root/'designs/01-率土之滨/assets/five-element-troops/01-metal-troop-master-v1.png').convert('RGBA')
bg=Image.new('RGBA',master.size,(240,235,222,255));bg.alpha_composite(master);d=ImageDraw.Draw(bg)
for x in range(100,1254,100):d.line((x,0,x,1254),fill=(180,205,205,255));d.text((x+2,15),str(x),fill=(30,60,60,255))
for y in range(100,1254,100):d.line((0,y,1254,y),fill=(180,205,205,255));d.text((15,y+2),str(y),fill=(30,60,60,255))
bg.convert('RGB').save(rec/'metal-ground-master-measure.png')
print('measurement boards ready')
