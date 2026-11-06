"""Compose the authored pass supply route from tracked source art."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from math import ceil, dist
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
EXPORTS = ROOT / 'exports/01-率土之滨'
OUT = EXPORTS / 'map-artonly-20261104'
RECORDS = Path(__file__).resolve().parent
VIEWPORT = (1254, 706)
GROUND_CROP = (0, 240, 1254, 946)
ROAD_NW = (283, 207)
ROAD_SE = (976, 595)
ROUTE = [ROAD_NW, (289, 227), (299, 241), (319, 249), (348, 253), (419, 283), ROAD_SE]
REVIEW_FEET = [('metal', (494, 325)), ('wood', (694, 437))]

# Coordinates are source top-left x/y, or render top-left x/y as named.
# Scale is applied uniformly and rounded to the nearest integer raster size.
LAYERS = [
    ('grass', 'world-terrain-20261101/grass-native.png', (0, 0), 1, 'ground'),
    ('supply-road', 'map-connectors-20261028-r2/02-stone-road-decal-v1.png', (176, 80), .58, 'paving'),
    ('north-woods', 'map-kit/terrain/woodland.png', (46, 22), .61, 'props'),
    ('pass-gate', 'map-kit/buildings/city-gate.png', (154, 42), .68, 'props'),
    ('east-hills', 'map-kit/terrain/mountains.png', (947, 21), .72, 'props'),
    ('quarry', 'map-kit/terrain/quarry.png', (789, 47), .51, 'props'),
    ('north-field', 'map-kit/terrain/wheat-field.png', (601, 106), .58, 'props'),
    ('east-field', 'map-kit/terrain/wheat-field.png', (794, 174), .57, 'props'),
    ('west-woods', 'map-kit/terrain/woodland.png', (5, 244), .72, 'props'),
    ('west-field', 'map-kit/terrain/wheat-field.png', (231, 328), .65, 'props'),
    ('sawmill', 'map-kit/buildings/workshop.png', (496, 384), .60, 'props'),
    ('depot', 'map-kit/buildings/warehouse.png', (985, 394), .72, 'props'),
    ('south-woods', 'map-kit/terrain/woodland.png', (290, 480), .77, 'props'),
    ('south-field', 'map-kit/terrain/wheat-field.png', (649, 516), .70, 'props'),
]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def save_record(path, record):
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')


def compose():
    canvas = Image.new('RGBA', VIEWPORT)
    inputs = []
    for name, asset, origin, scale, layer in LAYERS:
        path = EXPORTS / asset
        sidecar = path.with_name(path.name + '.derivation.json')
        source_info = json.loads(sidecar.read_text(encoding='utf-8-sig'))
        actual_digest = digest(path)
        if actual_digest != source_info['sha256']:
            raise ValueError(f'Source hash mismatch: {path}')
        with Image.open(path) as image:
            native = image.convert('RGBA')
        sprite = native.crop(GROUND_CROP) if layer == 'ground' else native
        if scale != 1:
            sprite = sprite.resize(tuple(round(n * scale) for n in sprite.size), Image.Resampling.LANCZOS)
        alpha = sprite.getchannel('A')
        content = alpha.point(lambda value: 255 if value > 16 else 0).getbbox()
        if not content:
            raise ValueError(f'No visible content: {path}')
        bounds = tuple(value + origin[index % 2] for index, value in enumerate(content))
        if bounds[0] < 0 or bounds[1] < 0 or bounds[2] > VIEWPORT[0] or bounds[3] > VIEWPORT[1]:
            raise ValueError(f'Visible placement outside frame: {name} {bounds}')
        canvas.alpha_composite(sprite, origin)
        inputs.append({
            'id': name,
            'layer': layer,
            'file': relative(path),
            'sha256': actual_digest,
            'derivationRecord': relative(sidecar),
            'nativeSizePx': native.size,
            'cropPx': GROUND_CROP if layer == 'ground' else None,
            'scale': scale,
            'sizePx': sprite.size,
            'topLeftPx': origin,
            'visibleBoundsAlphaAbove16Px': bounds,
        })
    if canvas.getchannel('A').getextrema() != (255, 255):
        raise ValueError('Ground must cover the full viewport')
    return canvas, inputs


def pavement_sample(canvas):
    # A swatch majority tolerates narrow mortar lines. The apron route bends
    # around the gate's decorative footing before it reaches the road center.
    colors = []
    for start, end in zip(ROUTE, ROUTE[1:]):
        intervals = ceil(dist(start, end) / 5)
        for i in range(intervals + 1):
            ratio = i / intervals
            x, y = (round(a + ratio * (b - a)) for a, b in zip(start, end))
            swatch = canvas.crop((x - 3, y - 3, x + 4, y + 4))
            stone_like = sum(r > 138 and r - g in range(0, 56) and b > 100 for r, g, b, _ in swatch.get_flattened_data())
            colors.append({'pointPx': [x, y], 'pavementLikePixels': stone_like, 'samplePixels': 49})
    failed = [entry for entry in colors if entry['pavementLikePixels'] < 25]
    if failed:
        raise ValueError(f'Review road swatch continuity failed: {failed}')
    return colors


def review_render(canvas):
    render = canvas.copy()
    manifest_path = EXPORTS / 'five-troop-frames-20261029/manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    source_root = manifest['commonRootTopLeft']
    overlays = []
    for unit, foot in REVIEW_FEET:
        frame = next(row for row in manifest['assets'] if row['unit'] == unit and row['action'] == 'idle' and row['index'] == 1)
        path = ROOT / frame['file']
        if digest(path) != frame['sha256']:
            raise ValueError(f'Troop frame hash mismatch: {path}')
        scale = .5
        with Image.open(path) as source:
            sprite = source.convert('RGBA').resize((192, 192), Image.Resampling.LANCZOS)
        position = tuple(round(a - b * scale) for a, b in zip(foot, source_root))
        render.alpha_composite(sprite, position)
        overlays.append({
            'id': unit,
            'file': frame['file'],
            'sha256': frame['sha256'],
            'manifest': relative(manifest_path),
            'sourceSizePx': manifest['commonCanvas'],
            'sourceRootPx': source_root,
            'displayScale': scale,
            'topLeftPx': position,
            'footPx': foot,
        })

    font_path = EXPORTS / 'fonts/wuxing-ui-20261102/WuxingUI-Regular.ttf'
    font = ImageFont.truetype(str(font_path), 18)
    draw = ImageDraw.Draw(render)
    for center, name, position in [
        (ROAD_NW, '关门接缝', (317, 169)),
        (ROAD_SE, '粮道终点', (997, 628)),
    ]:
        x, y = center
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill='#f6e4ac', outline='#174941', width=2)
        draw.text(position, name, font=font, fill='#173f36', stroke_width=2, stroke_fill='#f9f2db')

    proof = RECORDS / 'pass-supply-road-placement-proof.png'
    render.convert('RGB').save(proof, optimize=True)
    return {
        'file': relative(proof),
        'sha256': digest(proof),
        'canvasPx': VIEWPORT,
        'art_source': 'existing',
        'operation': 'Place two original idle poses at their map foot anchors and annotate the two road terminals for review.',
        'labelsFont': {'file': relative(font_path), 'sha256': digest(font_path)},
        'troopOverlays': overlays,
    }


def main():
    canvas, inputs = compose()
    samples = pavement_sample(canvas)
    out = OUT / 'pass-supply-road.png'
    canvas.convert('RGB').save(out, optimize=True)
    metadata = {
        'schema': 'wuxing.map.art-assembly.v1',
        'file': relative(out),
        'sha256': digest(out),
        'canvasPx': VIEWPORT,
        'pixelFormat': 'RGB',
        'art_source': 'existing',
        'route': 'derived_cropped_ground_and_layered_existing_sprites',
        'operation': 'Native opaque ground crop, uniform Lanczos downscale of placed overlays, alpha compositing in recorded order.',
        'createdAtUtc': datetime.now(timezone.utc).isoformat(),
        'origin': 'top-left',
        'worldContract': 'records/quarter-world-20261030/world-scope-contract.json',
        'scope': 'One pass supply road art scene at a landscape review scale.',
        'newModelImages': 0,
        'sourcePixelsModifiedOnDisk': False,
        'derivedFrom': inputs,
        'routeGuide': {
            'id': 'pass-gate-to-supply-road-end',
            'centerlinePx': ROUTE,
            'gateApronOverlaysRoad': True,
            'roadPortsSource': 'exports/01-率土之滨/map-connectors-20261028-r2/ports-provisional.json',
            'depotAccess': 'Roadside placement. The paved route ends beside the depot. Yard path and collision remain to be authored.',
            'worldCellAssignment': None,
        },
        'fullGameMapComplete': False,
        'userFinalAccepted': False,
    }
    save_record(out.with_suffix('.png.derivation.json'), metadata)
    proof = review_render(canvas)
    proof['derivedFrom'] = [{'file': relative(out), 'sha256': digest(out)}]
    proof['roadCenterlineCheck'] = {
        'method': 'Sample 7×7 swatches across the authored road centerline. Warm stone-like RGB in at least 25 of 49 pixels, including at the gate apron seam.',
        'passed': True,
        'sampleCount': len(samples),
        'minPavementLikePixels': min(row['pavementLikePixels'] for row in samples),
        'samples': samples,
        'collisionChecked': False,
    }
    save_record(RECORDS / 'pass-supply-road-placement-proof.png.derivation.json', proof)


if __name__ == '__main__':
    main()
