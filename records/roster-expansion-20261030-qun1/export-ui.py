import json, hashlib, datetime
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
cfg = json.loads((HERE / 'export-input.json').read_text(encoding='utf-8'))
ROOT = Path(cfg['projectRoot'])
OUT = ROOT / cfg['exportRoot']
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rel = lambda p: Path(p).relative_to(ROOT).as_posix()

def stats(im):
    a = im.getchannel('A')
    hist = a.histogram()
    solid = a.point(lambda x: 255 if x > 16 else 0)
    edge = [sum(v > 16 for v in a.crop(b).getdata()) for b in
            [(0, 0, im.width, 1), (im.width-1, 0, im.width, im.height),
             (0, im.height-1, im.width, im.height), (0, 0, 1, im.height)]]
    return {'size': list(im.size), 'alphaRange': list(a.getextrema()),
            'alphaOne': hist[1], 'alphaZero': hist[0],
            'solidBBoxAbove16': solid.getbbox(), 'solidEdgePixelsTRBL': edge}

def contained(im, size, pad):
    scale = min((size[0]-2*pad)/im.width, (size[1]-2*pad)/im.height)
    dims = (round(im.width*scale), round(im.height*scale))
    small = im.convert('RGBa').resize(dims, Image.Resampling.LANCZOS).convert('RGBA')
    pos = ((size[0]-dims[0])//2, (size[1]-dims[1])//2)
    out = Image.new('RGBA', size)
    out.paste(small, pos)
    return out, {'uniformScale': scale, 'resizedSize': dims, 'offset': pos,
                 'resampler': 'premultiplied Lanczos', 'alphaThresholdEdit': False}

manifest = {'schemaVersion': 1, 'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'scope': 'Four original Daoist chibi identity masters to 20 UI derivatives',
            'newGeneratedImagesInThisScript': 0, 'generalCount': len(cfg['characters']),
            'sources': [], 'assets': [], 'warnings': [],
            'userApproved': False, 'clientIntegrated': False, 'variantsFulfilled': False}
for item in cfg['characters']:
    p = ROOT / item['source']
    im = Image.open(p)
    if im.mode != 'RGBA':
        raise ValueError(f'{p.name}: expected native RGBA')
    source = {**item, 'sha256': sha(p), 'generation': item['source']+'.generation.json', 'stats': stats(im)}
    source['generationSha256'] = sha(ROOT / source['generation'])
    manifest['sources'].append(source)
    face, bust = im.crop(item['faceBox']), im.crop(item['bustBox'])
    variants = [('face-native', face, {'crop': item['faceBox'], 'resampled': False}),
                ('bust-native', bust, {'crop': item['bustBox'], 'resampled': False})]
    for sz in (128, 256):
        out, transform = contained(face, (sz, sz), round(sz*.04))
        variants.append((f'avatar-{sz}', out, {'crop': item['faceBox'], **transform}))
    full, transform = contained(im, (768, 1024), 32)
    variants.append(('card-full', full, {'crop': [0, 0, im.width, im.height], **transform}))
    for kind, out, transform in variants:
        dest = OUT / f"{item['id']}-{kind}.png"
        if dest.exists() and Image.open(dest).tobytes() != out.tobytes():
            raise FileExistsError(dest)
        out.save(dest)
        record = {'file': rel(dest), 'sha256': sha(dest), 'derivedFrom': {
            'file': item['source'], 'sha256': source['sha256'], 'generation': source['generation']},
            'operation': transform, 'newModelGeneration': False, 'nativeDimensionsClaim': kind.endswith('native'),
            'alphaNote': 'Native rectangular crops preserve RGBA exactly. Resizes normally resample/quantize alpha; no threshold cleanup.'}
        record_path = Path(str(dest)+'.derivation.json')
        record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        manifest['assets'].append({'personId': item['id'], 'displayName': item['name'], 'variant': kind,
                                   'file': rel(dest), 'sha256': record['sha256'], 'record': rel(record_path),
                                   'recordSha256': sha(record_path), 'stats': stats(out)})
        if kind.endswith('native') and out.tobytes() != im.crop(transform['crop']).tobytes():
            raise ValueError('Native crop RGBA mismatch')
    st = source['stats']
    if st['alphaOne']:
        manifest['warnings'].append({'id': 'SOURCE_ALPHA1_RETAINED', 'file': item['source'],
                                     'value': st['alphaOne'], 'threshold': 0})
    if st['alphaRange'][1] < 255:
        manifest['warnings'].append({'id': 'SOURCE_MAX_ALPHA_BELOW255', 'file': item['source'],
                                     'value': st['alphaRange'][1], 'threshold': 255})
    bb = st['solidBBoxAbove16']
    margins = [bb[0]/im.width, bb[1]/im.height, (im.width-bb[2])/im.width, (im.height-bb[3])/im.height]
    if min(margins) < .08:
        manifest['warnings'].append({'id': 'SOURCE_MARGIN_UNDER8PCT', 'file': item['source'],
                                     'value': margins, 'threshold': .08,
                                     'handling': 'Full original source retained; padded card derivative does not repair native detail.'})

manifest['assetCount'] = len(manifest['assets'])
manifest['nativeCropRgbaChecked'] = True
manifest['status'] = 'awaiting_root_visual_review'
manifest['warnings'].append({'id': 'INTENTIONAL_PORTRAIT_WINDOW', 'value': True, 'threshold': False,
                             'scope': 'face/bust/avatar are portrait crops; use card-full for entire body and props'})
(OUT / 'generals-ui-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
qa_derivations = []
for bg, color, ink in [('light', '#f1ebdf', '#243c34'), ('dark', '#1b282d', '#ece5d2')]:
    board = Image.new('RGB', (960, 570), color)
    d = ImageDraw.Draw(board)
    for i, item in enumerate(cfg['characters']):
        p = OUT / f"{item['id']}-card-full.png"
        card = Image.open(p).convert('RGBa').resize((216, 288), Image.Resampling.LANCZOS).convert('RGBA')
        board.paste(card, ((i%4)*240+12, (i//4)*570), card)
        av = Image.open(OUT / f"{item['id']}-avatar-256.png")
        av = av.convert('RGBa').resize((220, 220), Image.Resampling.LANCZOS).convert('RGBA')
        board.paste(av, ((i%4)*240+10, (i//4)*570+310), av)
        d.text(((i%4)*240+10, (i//4)*570+545), item['id'], fill=ink)
    p = HERE / f'four-generals-ui-{bg}.png'
    board.save(p)
    qa_derivations.append({'file': rel(p), 'sha256': sha(p), 'operation': 'QA contact sheet; uniform preview downscale over solid background',
                           'sources': [{'file': a['file'], 'sha256': a['sha256']} for a in manifest['assets'] if a['variant'] in ['card-full','avatar-256']]})
(HERE / 'qa-derivations.json').write_text(json.dumps(qa_derivations, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'sources': len(cfg['characters']), 'derivatives': len(manifest['assets']), 'warnings': len(manifest['warnings']),
                  'manifest': rel(OUT / 'generals-ui-manifest.json')}, ensure_ascii=False))
