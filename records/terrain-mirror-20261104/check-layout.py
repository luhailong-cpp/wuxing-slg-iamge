"""Verify the terrain placement contract and render a static review proof."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
KIT = 'designs/01-率土之滨/maps/world-terrain-20261104-kit'
MATERIALS = {'water': '8fe5738235250cb66dabf0b4b52b73b6cd63e9c9601864b8a2ad92dc14e4f8fc',
             'earth': '1b2d0a5c118519e667ddda055660f5ac3d0609c648985bf47758b72a7697aeee'}


def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def verify(material, expected_hash):
    file = ROOT / KIT / (material + '-v1.png')
    assert digest(file) == expected_hash
    source = Image.open(file).convert('RGBA')
    assert source.size == (1254, 1254) and source.getchannel('A').getextrema() == (255, 255)
    native = np.asarray(source)
    width, height = source.size
    review = Image.new('RGBA', (width * 4, height * 4))
    for row in range(4):
        for column in range(4):
            tile = native
            if column % 2:
                tile = tile[:, ::-1]
            if row % 2:
                tile = tile[::-1]
            review.paste(Image.fromarray(tile), (column * width, row * height))

    combined = np.asarray(review)
    x_join_max = max(int(np.abs(combined[:, x].astype(int) - combined[:, x - 1]).max())
                     for x in range(width, 4 * width, width))
    y_join_max = max(int(np.abs(combined[y].astype(int) - combined[y - 1]).max())
                     for y in range(height, 4 * height, height))
    assert (x_join_max, y_join_max) == (0, 0)
    proof = HERE / (material + '-layout-review.png')
    review.convert('RGB').resize((1000, 1000), Image.Resampling.LANCZOS).save(proof)
    return {
        'material': material, 'source': file.relative_to(ROOT).as_posix(), 'sourceSha256': expected_hash,
        'sourceSize': list(source.size), 'preview': proof.relative_to(ROOT).as_posix(),
        'previewSha256': digest(proof), 'checkedJoinsPerAxis': 3, 'maximumDifferenceRGBA': [x_join_max, y_join_max],
        'previewOperation': '4x4 instance placement with alternating UV flips, Lanczos review downscale only',
    }


if __name__ == '__main__':
    results = [verify(name, digest_value) for name, digest_value in MATERIALS.items()]
    (HERE / 'pixel-check.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8', newline='\n')
