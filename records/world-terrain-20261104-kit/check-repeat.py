"""Measure native repeats and render visual proof without changing the tiles."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BATCH = HERE.name
DESIGNS = ROOT / 'designs/01-率土之滨/maps' / BATCH
EXPORTS = ROOT / 'exports/01-率土之滨' / BATCH
THRESHOLD = 2.0


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


for source in sorted(DESIGNS.glob('*-v[12].png')):
    record = Path(str(source) + '.generation.json')
    generated = json.loads(record.read_text(encoding='utf-8'))
    source_hash = digest(source)
    assert generated['sha256'] == source_hash
    image = Image.open(source).convert('RGBA')
    w, h = image.size
    rgb = np.asarray(image, dtype=np.float32)[:, :, :3]
    horizontal = float(np.abs(rgb[:, 0] - rgb[:, -1]).mean())
    vertical = float(np.abs(rgb[0] - rgb[-1]).mean())
    x_ratio = horizontal / max(float(np.abs(np.diff(rgb, axis=1)).mean()), .001)
    y_ratio = vertical / max(float(np.abs(np.diff(rgb, axis=0)).mean()), .001)
    opaque = image.getchannel('A').getextrema() == (255, 255)
    warnings = []
    if (w, h) != (1024, 1024):
        warnings.append({'id': 'NATIVE_SIZE_DIFFERS_FROM_PROMPT', 'value': [w, h], 'threshold': [1024, 1024], 'file': rel(source)})
    checks = {'square': w == h, 'opaque': opaque, 'seamRatioPassed': max(x_ratio, y_ratio) <= THRESHOLD}
    if not checks['seamRatioPassed']:
        warnings.append({'id': 'REPEAT_EDGE_DISCONTINUITY', 'value': [x_ratio, y_ratio], 'threshold': THRESHOLD, 'file': rel(source)})
    tile = Image.new('RGB', (w * 3, h * 3))
    for y in range(3):
        for x in range(3):
            tile.paste(image, (x * w, y * h))
    review = HERE / f'{source.stem}-repeat-3x3.png'
    tile.resize((1008, 1008), Image.Resampling.LANCZOS).save(review)
    join = HERE / f'{source.stem}-junction-native.png'
    tile.crop((w - 220, h - 220, w + 220, h + 220)).save(join)
    report = {'checkedAtUtc': datetime.now(timezone.utc).isoformat(), 'source': rel(source), 'sourceSha256': source_hash,
              'generation': rel(record), 'nativeSize': [w, h], 'checks': checks,
              'horizontalRatio': x_ratio, 'verticalRatio': y_ratio, 'threshold': THRESHOLD,
              'visualReviewPassed': None, 'warnings': warnings,
              'qa': [{'file': rel(review), 'sha256': digest(review), 'operation': '3x3 repeat then downscale for QA'},
                     {'file': rel(join), 'sha256': digest(join), 'operation': 'exact native RGB repeat junction crop'}]}
    report_path = HERE / f'{source.stem}-review.json'
    if report_path.is_file():
        previous = json.loads(report_path.read_text(encoding='utf-8'))
        if previous['sourceSha256'] == source_hash:
            for key in ['visualReviewPassed', 'visualNotes']:
                if key in previous:
                    report[key] = previous[key]
    if all(checks.values()) and report['visualReviewPassed'] is True:
        EXPORTS.mkdir(parents=True, exist_ok=True)
        export = EXPORTS / source.name
        shutil.copyfile(source, export)
        assert digest(export) == source_hash
        report['export'] = rel(export)
        write(EXPORTS / (source.name + '.derivation.json'), {'file': rel(export), 'sha256': source_hash,
              'derivedFrom': {'file': rel(source), 'sha256': source_hash, 'generation': rel(record)},
              'operation': 'byte-identical copy', 'nativeSize': [w, h], 'newModelGeneration': False})
    write(report_path, report)
    print(json.dumps({'name': source.stem, 'checks': checks, 'ratios': [x_ratio, y_ratio],
                      'review': report['visualReviewPassed'], 'export': report.get('export')}, ensure_ascii=True))
