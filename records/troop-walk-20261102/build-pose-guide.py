from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib

HERE=Path(__file__).resolve().parent
im=Image.new('RGB',(1536,1024),'#f6f3e9');d=ImageDraw.Draw(im)
# Reference geometry only; never deliver these lines as game art.
# The second row reverses which depth leg leads, preserving facing.
legs=[
    ([(266,296),(280,354),(305,418)],[(249,291),(235,344),(220,384)]),
    ([(266,301),(265,359),(273,407)],[(249,296),(278,340),(277,375)]),
    ([(266,293),(245,344),(232,390)],[(249,288),(280,340),(294,390)]),
    ([(266,296),(238,344),(220,384)],[(249,291),(280,354),(305,418)]),
    ([(266,296),(278,340),(277,375)],[(249,301),(265,359),(273,407)]),
    ([(266,288),(280,340),(294,390)],[(249,293),(245,344),(232,390)]),
]
names=['NEAR contact / FAR back','NEAR support / FAR passing','NEAR push / FAR advancing',
       'FAR contact / NEAR back','FAR support / NEAR passing','FAR push / NEAR advancing']
for i,(near,far) in enumerate(legs):
    ox=(i%3)*512;oy=(i//3)*512
    d.rectangle((ox+64,oy+50,ox+448,oy+452),outline='#c3bead',width=2)
    d.line((ox+160,oy+360,ox+352,oy+437),fill='#969a94',width=2)
    d.ellipse((ox+193,oy+71,ox+319,oy+197),outline='#73756b',width=3)
    d.line((ox+256,oy+197,ox+256,oy+292),fill='#73756b',width=9)
    d.line((ox+249,oy+291,ox+266,oy+296),fill='#73756b',width=8)
    for points,color in [(far,'#3977bf'),(near,'#df7c22')]:
        pts=[(x+ox,y+oy) for x,y in points]
        d.line(pts,fill=color,width=12)
        x,y=pts[-1];d.polygon([(x-10,y-6),(x+19,y-1),(x+23,y+6),(x-11,y+6)],fill=color)
    d.text((ox+65,oy+468),str(i+1)+' '+names[i],fill='#222222')
d.text((12,12),'REFERENCE ONLY | orange=NEAR, blue=FAR | do not paint labels, colors or skeleton',fill='#222222')
out=HERE/'six-phase-pose-guide.png';im.save(out)
(HERE/'six-phase-pose-guide.json').write_text(json.dumps({'role':'code-drawn motion planning reference, not game art',
    'file':'records/troop-walk-20261102/six-phase-pose-guide.png','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
    'layout':[3,2],'canvas':[1536,1024],'phaseNames':names,'nearFarLegCoordinates':legs,
    'frameCount':6,'loop':True,'durationMsEach':100,'acceptedGameFrames':0},indent=2)+'\n',encoding='utf-8')
print('Saved six-phase pose reference; no generated game frames')
