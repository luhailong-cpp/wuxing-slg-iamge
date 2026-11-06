"""Crop inspected icon ownership regions and make explicit display-size derivatives.

No drawing, alpha cleanup, keying, upscaling, or source modification occurs.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

from PIL import Image, ImageDraw

ROOT = Path('D:/work/wuxing-slg-iamge')
SOURCE = Path('designs/01-率土之滨/assets/five-elements/five-elements-emblems-sheet-v1.png')
OUT = Path('exports/01-率土之滨/five-elements/emblems')
ITEMS = [
    ('metal', '金', (32, 48, 502, 528)),
    ('wood', '木', (528, 56, 1010, 512)),
    ('water', '水', (1100, 60, 1495, 520)),
    ('fire', '火', (80, 528, 495, 1000)),
    ('earth', '土', (528, 574, 1060, 974)),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def alpha_info(im):
    a = im.getchannel('A')
    h = a.histogram()
    edges = [a.crop((0,0,a.width,1)), a.crop((0,a.height-1,a.width,a.height)),
             a.crop((0,0,1,a.height)), a.crop((a.width-1,0,a.width,a.height))]
    return {'range': a.getextrema(), 'zeroPixels': h[0], 'opaquePixels': h[255],
        'edgePixelsAbove1': [sum(v>1 for v in edge.get_flattened_data()) for edge in edges],
        'bboxAbove16': a.point(lambda v:255 if v>16 else 0).getbbox()}


def main():
    now = datetime.now(timezone.utc).isoformat()
    source = ROOT / SOURCE
    record = json.loads(Path(str(source) + '.generation.json').read_text(encoding='utf-8-sig'))
    digest = sha(source)
    if digest != record['sha256']:
        raise ValueError('Source hash mismatch')
    sheet = Image.open(source)
    if sheet.mode != 'RGBA':
        raise ValueError('Expected native alpha')
    out = ROOT / OUT
    out.mkdir(parents=True, exist_ok=True)
    preview = Image.new('RGB', (800, 960))
    draw = ImageDraw.Draw(preview)
    exported = []
    for column, (name, label, box) in enumerate(ITEMS):
        crop = sheet.crop(box)
        native_path = out / f'{name}-native.png'
        if native_path.exists():
            raise FileExistsError(native_path)
        info = alpha_info(crop)
        if any(info['edgePixelsAbove1']):
            raise ValueError(f'Visible edge crosses ownership: {name}')
        crop.save(native_path)
        native_rel = native_path.relative_to(ROOT).as_posix()
        native_record = {
            'schemaVersion': 1, 'file': native_rel, 'sha256': sha(native_path),
            'derivedAtUtc': now, 'format': 'PNG', 'mode': 'RGBA',
            'width': crop.width, 'height': crop.height, 'art_source': 'existing',
            'operation': 'crop', 'cropBox': box, 'resampled': False,
            'derivedFrom': [{'file': SOURCE.as_posix(), 'sha256': digest,
                'record': SOURCE.as_posix() + '.generation.json'}],
            'alphaInspection': info, 'anchor': {'type': 'ui_center', 'pixel': [crop.width/2,crop.height/2]},
            'status': 'candidate_static_icon_pending_user_review', 'userApproved': False,
            'clientIntegrated': False,
            'limitations': ['Native alpha is preserved, including faint alpha=1 source residue.',
                'Not a 15%-safe-frame master; manual ownership review confirms complete visible silhouette.'],
        }
        dump(Path(str(native_path) + '.derived.json'), native_record)
        entry = {'element': name, 'label': label, 'native': native_rel,
            'nativeRecord': native_rel + '.derived.json', 'displayVariants': []}
        bbox = info['bboxAbove16']
        for row, size in enumerate((32,64,128)):
            scale = size * .80 / max(bbox[2]-bbox[0], bbox[3]-bbox[1])
            if scale >= 1:
                raise ValueError('Display derivative would upscale')
            dimensions = (max(1,round(crop.width*scale)),max(1,round(crop.height*scale)))
            resized = crop.convert('RGBa').resize(dimensions, Image.Resampling.LANCZOS).convert('RGBA')
            canvas = Image.new('RGBA', (size,size))
            offset = ((size-dimensions[0])//2,(size-dimensions[1])//2)
            canvas.paste(resized, offset)
            path = out / f'{name}-{size}.png'
            if path.exists():
                raise FileExistsError(path)
            canvas.save(path)
            rel = path.relative_to(ROOT).as_posix()
            derivative = {
                'schemaVersion': 1, 'file': rel, 'sha256': sha(path), 'derivedAtUtc': now,
                'width': size, 'height': size, 'format': 'PNG', 'mode': 'RGBA',
                'operation': 'premultiplied_alpha_lanczos_downscale_and_center_on_transparent_canvas',
                'resampled': True, 'nativeDetailClaim': False,
                'sourceScale': scale, 'resizedDimensions': dimensions, 'pasteOffset': offset,
                'derivedFrom': [{'file': native_rel, 'sha256': native_record['sha256'],
                    'record': native_rel+'.derived.json'}],
                'anchor': {'type': 'ui_center', 'pixel': [size/2,size/2]},
                'alphaInspection': alpha_info(canvas), 'art_source': 'existing',
                'status': 'display_derivative_pending_client_validation', 'userApproved': False,
                'clientIntegrated': False,
            }
            dump(Path(str(path)+'.derived.json'), derivative)
            entry['displayVariants'].append({'size': size, 'file': rel, 'record': rel+'.derived.json'})
            for background, color in enumerate(('#f5f0e4','#152b2c')):
                cell = Image.new('RGBA',(160,160),color)
                cell.alpha_composite(canvas,((160-size)//2,(160-size)//2))
                x,y = column*160,(row*2+background)*160
                preview.paste(cell.convert('RGB'),(x,y))
                draw.text((x+8,y+8),f'{name} {size}px',fill='#263c37' if background==0 else '#e7e1ce')
        exported.append(entry)
    qc_path = ROOT/'work/five-elements-icons/spill-expect5-v1/sheet-qc.json'
    qc = json.loads(qc_path.read_text(encoding='utf-8'))
    manifest = {
        'schemaVersion': 1, 'createdAtUtc': now, 'assetType': 'five_static_element_emblems',
        'source': SOURCE.as_posix(), 'sourceSha256': digest, 'nativeCount': 5,
        'displayDerivativeCount': 15, 'animations': 0, 'framesPerIcon': 1,
        'items': exported, 'userApproved': False, 'clientIntegrated': False,
        'status': 'visually_reviewed_candidate_exports_with_recorded_warnings',
        'rawSheetQc': {k:qc[k] for k in ('schema','check','status','method','checks','params')},
        'manualOwnership': {'allVisibleSubjectPixelsCoveredAbove1': True,
            'crossingVisibleEdgesAbove1': 0, 'sixthCellIntentionallyEmpty': True,
            'alphaModified': False, 'keyed': False,
            'reviewBasis': 'Actual light/dark composite and manually inspected native ownership rectangles; no largest-component filtering.'},
    }
    dump(out/'emblems-manifest.json',manifest)
    preview.save(ROOT/'work/five-elements-icons/32-64-128-light-dark.png')
    print(json.dumps({'native':5,'displayDerivatives':15,'manifest':(OUT/'emblems-manifest.json').as_posix(),
        'rawQcStatus':qc['status'],'warnings':[c['id'] for c in qc['checks'] if c['status']=='warn']}))


if __name__ == '__main__':
    main()
