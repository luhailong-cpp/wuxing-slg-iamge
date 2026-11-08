"""Export distinct roster-card artwork and render a base-versus-variant review."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BATCH = HERE.name
GAME = '01-率土之滨'
MASTERS = ROOT / 'designs' / GAME / 'characters' / BATCH
OUTPUT = ROOT / 'exports' / GAME / BATCH
BASES = ROOT / 'exports' / GAME / 'roster-expansion-20261104-heroes4'
FACTS = ROOT / 'records/roster-20261029/OFFICIAL_ROSTER_FACTS_20261029.json'
CARDS = {100585: 'cao-ren', 100787: 'cheng-yu'}
SIZE = (768, 1024)
PAD = 32


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def reference(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def resize(image, size):
    return image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')


def export_card(card, official):
    source = MASTERS / f'card-{card}-master-v1.png'
    source_ref = reference(source)
    generation = source.with_suffix('.png.generation.json')
    generation_ref = reference(generation)
    generated = read(generation)
    identity = generated['identity']
    if (generated['file'] != source_ref['file'] or generated['sha256'] != source_ref['sha256']
            or identity['cardIDs'] != [card] or identity['name'] != official['name']):
        raise ValueError(f'Generation record does not match official card {card}')
    identity_ref = next(ref for ref in generated['references']
                        if ref['role'] == 'approved identity continuity reference')
    if reference(ROOT / identity_ref['file'])['sha256'] != identity_ref['sha256']:
        raise ValueError(f'Identity reference has changed for card {card}')

    image = Image.open(source)
    alpha = image.getchannel('A')
    solid_box = alpha.point(lambda value: 255 if value > 16 else 0).getbbox()
    if image.mode != 'RGBA' or image.size != (generated['width'], generated['height']) or solid_box is None:
        raise ValueError(f'Expected visible native RGBA master for card {card}')
    left, top, right, bottom = solid_box
    width, height = image.size
    margins = [left, top, width - right, height - bottom]
    if min(margins) <= 0:
        raise ValueError(f'Silhouette touches native edge for card {card}')
    crop = (max(0, left - 24), max(0, top - 24), min(width, right + 24), min(height, bottom + 24))
    trimmed = image.crop(crop)
    scale = min((SIZE[0] - 2 * PAD) / trimmed.width, (SIZE[1] - 2 * PAD) / trimmed.height)
    scaled_size = (round(trimmed.width * scale), round(trimmed.height * scale))
    offset = ((SIZE[0] - scaled_size[0]) // 2, (SIZE[1] - scaled_size[1]) // 2)
    result = Image.new('RGBA', SIZE)
    result.paste(resize(trimmed, scaled_size), offset)
    destination = OUTPUT / f'card-{card}-artwork.png'
    if destination.exists() and Image.open(destination).tobytes() != result.tobytes():
        raise FileExistsError(destination)
    result.save(destination)
    art_ref = reference(destination)
    record = destination.with_suffix('.png.derivation.json')
    write(record, {
        **art_ref,
        'derivedFrom': {**source_ref, 'generation': generation_ref['file'], 'generationSha256': generation_ref['sha256']},
        'operation': {
            'crop': crop,
            'cropBasis': 'alpha above 16 plus up to 24 native pixels on each edge',
            'uniformScale': scale,
            'resizedSize': scaled_size,
            'offset': offset,
            'resampler': 'premultiplied Lanczos',
            'alphaThresholdEdit': False,
        },
        'newModelGeneration': False,
        'nativeDimensionsClaim': False,
    })
    return {
        'cardid': card,
        'officialName': official['name'],
        'variantRaw': official['variant'],
        'candidatePersonID': identity['personID'],
        'identityMaster': {key: identity_ref[key] for key in ('file', 'sha256')},
        'nativeMaster': {**source_ref, 'generation': generation_ref},
        'nativeAlpha': {'range': alpha.getextrema(), 'onePixelCount': alpha.histogram()[1],
                        'visibleBBoxAbove16': solid_box, 'visibleMarginsLTRB': margins},
        'artwork': {**art_ref, 'record': reference(record), 'size': SIZE, 'mode': result.mode,
                    'alphaRange': result.getchannel('A').getextrema(), 'alphaBBox': result.getchannel('A').getbbox()},
    }


def render_reviews(cards):
    views = []
    for name, bg, ink in [('light', '#f1ebdf', '#243c34'), ('dark', '#1b282d', '#ece5d2')]:
        board = Image.new('RGBA', (1152, 426), bg)
        pen = ImageDraw.Draw(board)
        sources = []
        for index, item in enumerate(cards):
            card = item['cardid']
            pair = [BASES / f'{CARDS[card]}-card-full.png', ROOT / item['artwork']['file']]
            for side, path in enumerate(pair):
                x = index * 576 + side * 288
                board.alpha_composite(resize(Image.open(path), (288, 384)), (x, 0))
                label = f'{CARDS[card]} base' if side == 0 else f"{item['variantRaw']['seasonRaw']} {card}"
                pen.text((x + 16, 397), label, fill=ink)
                sources.append(reference(path))
        path = HERE / f'card-variants-{name}.png'
        board.convert('RGB').save(path)
        views.append({**reference(path), 'sources': sources,
                      'operation': 'Composited base and variant artwork at uniform preview scale on solid background'})
    return views


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    official = {row['cardid']: row for row in read(FACTS)['rows']}
    cards = [export_card(card, official[card]) for card in CARDS]
    views = render_reviews(cards)
    review = HERE / 'visual-review.json'
    manifest = {'schemaVersion': 1, 'scope': 'Original character artwork indexed by archived official card ID',
                'status': 'awaiting_visual_review', 'cards': cards, 'reviewViews': views}
    if review.is_file():
        visual = read(review)
        if (visual['passed'] is not True or visual['cardids'] != list(CARDS)
                or visual['views'] != [{key: view[key] for key in ('file', 'sha256')} for view in views]):
            raise ValueError('The visual review does not match these card exports')
        manifest['status'] = 'verified_card_specific_art_candidates'
        manifest['visualReview'] = reference(review)
    write(OUTPUT / 'card-art-manifest.json', manifest)


if __name__ == '__main__':
    main()
