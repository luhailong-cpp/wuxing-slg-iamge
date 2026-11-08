"""Native crops and honest static-map display variants, without repainting/keying."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image,ImageDraw

ROOT=Path('D:/work/wuxing-slg-iamge')
OUT=ROOT/'exports/01-率土之滨/units'
UNITS=(('infantry','01-dao-infantry-master-v1'),('archer','02-dao-archer-master-v1'),('cavalry','03-dao-cavalry-master-v1'))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f: json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def stats(im):
    a=im.getchannel('A');h=a.histogram()
    edges=[a.crop((0,0,a.width,1)),a.crop((0,a.height-1,a.width,a.height)),a.crop((0,0,1,a.height)),a.crop((a.width-1,0,a.width,a.height))]
    boxes={str(t):a.point(lambda v:255 if v>t else 0).getbbox() for t in (1,16,127)}
    return {'range':a.getextrema(),'zeroPixels':h[0],'alpha1Pixels':h[1],'opaquePixels':h[255],
        'bboxByThreshold':boxes,'edgePixelsAbove1':[sum(v>1 for v in e.get_flattened_data()) for e in edges]}
def main():
    now=datetime.now(timezone.utc).isoformat();OUT.mkdir(parents=True,exist_ok=True)
    qa_dir=ROOT/'work/units-qa-20261027';qa_dir.mkdir(parents=True,exist_ok=True)
    preview=Image.new('RGB',(960,640));draw=ImageDraw.Draw(preview)
    entries=[]
    for column,(name,stem) in enumerate(UNITS):
        source=ROOT/f'designs/01-率土之滨/assets/units/{stem}.png'
        im=Image.open(source);info=stats(im)
        bbox=info['bboxByThreshold']['1']
        if any(info['edgePixelsAbove1']): raise ValueError('Visible source edge touches canvas')
        box=(max(0,bbox[0]-16),max(0,bbox[1]-16),min(im.width,bbox[2]+16),min(im.height,bbox[3]+16))
        crop=im.crop(box);crop_info=stats(crop)
        if any(crop_info['edgePixelsAbove1']): raise ValueError('Visible crop cut')
        relative=source.relative_to(ROOT).as_posix()
        path=OUT/f'{name}-native.png'
        if path.exists(): raise FileExistsError(path)
        crop.save(path)
        anchor=[(bbox[0]+bbox[2])/2-box[0],bbox[3]-box[1]]
        native_record={'schemaVersion':1,'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'derivedAtUtc':now,
            'width':crop.width,'height':crop.height,'mode':'RGBA','format':'PNG','operation':'crop','cropBox':box,
            'derivedFrom':[{'file':relative,'sha256':sha(source),'record':relative+'.generation.json'}],
            'resampled':False,'alphaEdited':False,'art_source':'existing','alphaInspection':crop_info,
            'anchorPxTopLeft':anchor,'anchorNormalizedTopLeft':[anchor[0]/crop.width,anchor[1]/crop.height],
            'anchorStatus':'provisional bottom-center of alpha>1 footprint; no collider/physical scale contract',
            'static':True,'animationFrameCount':0,'userApproved':False,'clientIntegrated':False,
            'status':'static_unit_native_crop_candidate'}
        dump(Path(str(path)+'.derivation.json'),native_record)
        entry={'id':name,'sourceMaster':relative,'sourceMasterSha256':sha(source),'native':native_record['file'],
            'nativeRecord':native_record['file']+'.derivation.json','sourceAlphaInspection':info,
            'sourceSignificantHeightFraction':(bbox[3]-bbox[1])/im.height,'anchorPxTopLeft':anchor,
            'anchorNormalizedTopLeft':native_record['anchorNormalizedTopLeft'],'displayVariants':[]}
        source_margins=[bbox[0],bbox[1],im.width-bbox[2],im.height-bbox[3]]
        entry['sourceMarginsPx']=source_margins
        entry['sourceRequested15PercentMarginMet']=all(v>=im.width*.15 for v in source_margins)
        entry['warnings']=[{'id':'SOURCE_SAFE_MARGIN_BELOW_REQUEST','value':source_margins,
            'threshold':{'minimumEachSidePx':im.width*.15},'file':relative}]
        source_preview=Image.new('RGB',(im.width*2,im.height))
        for bg,color in enumerate(('#f5f0e4','#152b2c')):
            source_preview.paste(Image.alpha_composite(Image.new('RGBA',im.size,color),im).convert('RGB'),(bg*im.width,0))
        source_preview.save(qa_dir/f'{name}-native-light-dark.png')
        for row,body_height in enumerate((64,128)):
            scale=body_height/(bbox[3]-bbox[1]);dimensions=(round(crop.width*scale),round(crop.height*scale))
            small=crop.convert('RGBa').resize(dimensions,Image.Resampling.LANCZOS).convert('RGBA')
            canvas=Image.new('RGBA',(256,256));target_anchor=[128,224]
            offset=(round(target_anchor[0]-anchor[0]*scale),round(target_anchor[1]-anchor[1]*scale))
            if offset[0]<0 or offset[1]<0 or offset[0]+small.width>256 or offset[1]+small.height>256: raise ValueError('Display canvas would clamp')
            canvas.paste(small,offset)
            variant=OUT/f'{name}-{body_height}h.png'
            if variant.exists(): raise FileExistsError(variant)
            canvas.save(variant);rel=variant.relative_to(ROOT).as_posix()
            rec={'schemaVersion':1,'file':rel,'sha256':sha(variant),'derivedAtUtc':now,'width':256,'height':256,
                'mode':'RGBA','format':'PNG','operation':'premultiplied_lanczos_downscale_and_transparent_canvas_registration',
                'derivedFrom':[{'file':native_record['file'],'sha256':native_record['sha256'],'record':native_record['file']+'.derivation.json'}],
                'resampled':True,'scale':scale,'resizedDimensions':dimensions,'pasteOffset':offset,
                'plannedSilhouetteHeightPx':body_height,'anchorPxTopLeft':target_anchor,'anchorNormalizedTopLeft':[.5,.875],
                'nativeDetailClaim':False,'static':True,'animationFrameCount':0,'alphaInspection':stats(canvas),
                'userApproved':False,'clientIntegrated':False,'status':'static_map_unit_display_candidate'}
            dump(Path(str(variant)+'.derivation.json'),rec)
            entry['displayVariants'].append({'file':rel,'record':rel+'.derivation.json','silhouetteHeight':body_height,
                'canvas':[256,256],'anchorPxTopLeft':target_anchor,'anchorNormalizedTopLeft':[.5,.875]})
            for bg,color in enumerate(('#f5f0e4','#152b2c')):
                cell=Image.new('RGBA',(320,160),color)
                # QA displays the canvas without scaling; the top padding is omitted only in preview.
                cell.alpha_composite(canvas,(32,-96))
                x,y=column*320,(row*2+bg)*160;preview.paste(cell.convert('RGB'),(x,y))
                draw.text((x+8,y+8),f'{name} {body_height}px high',fill='#263c37' if bg==0 else '#e7e1ce')
        entries.append(entry)
    preview.save(qa_dir/'units-64-128-light-dark.png')
    manifest={'schemaVersion':1,'createdAtUtc':now,'assetCount':3,'spriteFileCount':9,'nativeCropCount':3,
        'displayDerivativeCount':6,'facing':'south-east','camera':'isometric approximately40degree top-down',
        'static':True,'animationFrameCount':0,'items':entries,'userApproved':False,'clientIntegrated':False,
        'status':'static_unit_candidates_with_provisional_map_registration',
        'limits':['No animation, additional look directions, timing, collider or physical map scale validation.',
            'Display height normalizes whole silhouettes as map tokens; cavalry/infantry physical size ratio is not a game contract.',
            'Raw low-alpha source residue is retained in native crops; only exterior transparent/alpha1 margins are cropped.',
            'All three sources miss the requested15% margin on at least one side; cavalry has the tightest bottom margin. Visible silhouettes remain complete.']}
    dump(OUT/'units-manifest.json',manifest)
    print(json.dumps({'nativeCrops':3,'displayVariants':6,'manifest':(OUT/'units-manifest.json').relative_to(ROOT).as_posix()}))
if __name__=='__main__':main()
