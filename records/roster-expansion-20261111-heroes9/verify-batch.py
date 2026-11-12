"""Read-only integrity checks for a roster batch; emits JSON and changes no files."""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KINDS = {'face-native', 'bust-native', 'avatar-128', 'avatar-256', 'card-full'}
failures = []
warnings = []
checked = {'masters': 0, 'assets': 0, 'nativeCrops': 0, 'references': 0}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path(value):
    require(isinstance(value, str) and value, f'Invalid local path: {value!r}')
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    require(candidate.is_relative_to(ROOT), f'Path escapes this repository: {value}')
    require(candidate.is_file(), f'Missing file: {value}')
    return candidate


def digest(value):
    return hashlib.sha256(path(value).read_bytes()).hexdigest()


def read(value):
    return json.loads(path(value).read_text(encoding='utf-8-sig'))


def check_hash(value, expected):
    require(digest(value) == expected, f'SHA256 mismatch: {value}')


def check_references(record, owner):
    references = record.get('references', [])
    require(isinstance(references, list), f'{owner}: references must be a list')
    actual = set()
    for reference in references:
        require(isinstance(reference, dict) and 'file' in reference,
                f'{owner}: reference must name a repository file')
        reference_path = path(reference['file'])
        require('sha256' in reference, f'{owner}: missing reference SHA256')
        check_hash(reference['file'], reference['sha256'])
        require(reference.get('actuallyAttached') is not False,
                f'{owner}: a listed reference was not attached')
        actual.add(reference_path)
        checked['references'] += 1
    parameters = record.get('submittedParameters', {})
    submitted = parameters.get('referenced_image_paths') or []
    require(isinstance(submitted, list), f'{owner}: invalid submitted references')
    submitted_paths = {path(value) for value in submitted}
    if submitted_paths:
        require(actual == submitted_paths, f'{owner}: recorded/submitted references differ')
    if parameters.get('promptFile'):
        path(parameters['promptFile'])
    if record.get('prompt') and not parameters.get('prompt'):
        path(record['prompt'])


def run():
    cfg = read((HERE / 'export-input.json').as_posix())
    manifest = read(f"{cfg['exportRoot']}/generals-ui-manifest.json")
    people = cfg['characters']
    require(len({p['id'] for p in people}) == len(people), 'Duplicate batch character id')
    require(len({p['source'] for p in people}) == len(people), 'Duplicate batch master path')
    require(manifest['generalCount'] == len(people), 'Manifest general count mismatch')
    require(manifest['assetCount'] == len(people) * 5, 'Manifest asset count mismatch')
    sources = {s['id']: s for s in manifest['sources']}
    require(len(sources) == len(manifest['sources']) == len(people), 'Duplicate/missing manifest source')
    require(set(sources) == {p['id'] for p in people}, 'Manifest source ids differ from input')
    person_ids = set()
    batch_ids = {p['id'] for p in people}
    for person in people:
        identity_id = person['id']
        source = sources[identity_id]
        require(source['source'] == person['source'], f'{identity_id}: source path mismatch')
        source_path = path(person['source'])
        check_hash(person['source'], source['sha256'])
        check_hash(source['generation'], source['generationSha256'])
        generation = read(source['generation'])
        require(path(generation['file']) == source_path, f'{identity_id}: generation path mismatch')
        require(generation['sha256'] == source['sha256'], f'{identity_id}: generation image SHA mismatch')
        identity = generation['identity']
        require(identity['id'] == identity_id and identity['name'] == person['name'],
                f'{identity_id}: generation identity mismatch')
        require(identity['personID'] not in person_ids, 'Duplicate batch personID')
        person_ids.add(identity['personID'])
        check_references(generation, source['generation'])
        for evidence in generation.get('evidence', []):
            if evidence.get('file'):
                evidence_path = path(evidence['file'])
                if evidence_path.suffix == '.json' and evidence_path.name.endswith('.request.json'):
                    check_references(read(evidence['file']), evidence['file'])
        with Image.open(source_path) as image:
            require(image.mode == 'RGBA', f'{identity_id}: source is not native RGBA')
            require(image.size == (generation['width'], generation['height']),
                    f'{identity_id}: recorded source dimensions mismatch')
            require(image.format == 'PNG', f'{identity_id}: source is not PNG')
            low, high = image.getchannel('A').getextrema()
            require(low == 0 and high > 16, f'{identity_id}: source lacks transparent/visible alpha')
            assets = [a for a in manifest['assets'] if a['personId'] == identity_id]
            require(len(assets) == 5 and {a['variant'] for a in assets} == KINDS,
                    f'{identity_id}: five distinct UI variants required')
            for asset in assets:
                kind = asset['variant']
                check_hash(asset['file'], asset['sha256'])
                check_hash(asset['record'], asset['recordSha256'])
                derivation = read(asset['record'])
                require(path(derivation['file']) == path(asset['file']), f'{kind}: derivation file mismatch')
                require(derivation['sha256'] == asset['sha256'], f'{kind}: derivation SHA mismatch')
                require(path(derivation['derivedFrom']['file']) == source_path,
                        f'{kind}: derivation source mismatch')
                require(derivation['derivedFrom']['sha256'] == source['sha256'],
                        f'{kind}: derivation source SHA mismatch')
                require(path(derivation['derivedFrom']['generation']) == path(source['generation']),
                        f'{kind}: derivation generation record mismatch')
                require(derivation['newModelGeneration'] is False, f'{kind}: invalid generation claim')
                with Image.open(path(asset['file'])) as exported:
                    require(exported.mode == 'RGBA' and exported.format == 'PNG',
                            f'{kind}: export must be RGBA PNG')
                    require(list(exported.size) == asset['stats']['size'], f'{kind}: stats dimensions mismatch')
                    if kind in ('face-native', 'bust-native'):
                        box = person['faceBox' if kind == 'face-native' else 'bustBox']
                        require(derivation['operation']['crop'] == box, f'{kind}: crop mismatch')
                        require(0 <= box[0] < box[2] <= image.width and 0 <= box[1] < box[3] <= image.height,
                                f'{kind}: crop outside source')
                        expected = image.crop(box)
                        require(exported.size == expected.size and exported.tobytes() == expected.tobytes(),
                                f'{kind}: native RGBA pixels changed')
                        checked['nativeCrops'] += 1
                    else:
                        expected_size = (768, 1024) if kind == 'card-full' else (int(kind.split('-')[1]),) * 2
                        require(exported.size == expected_size, f'{kind}: incorrect target dimensions')
                    require(exported.getchannel('A').getextrema()[0] == 0, f'{kind}: alpha background lost')
                checked['assets'] += 1
        checked['masters'] += 1
    roster = read('exports/01-率土之滨/art-review-20261029/generals-manifest.json')
    require(len({p['personID'] for p in roster['people']}) == len(roster['people']),
            'Shared roster already contains duplicate personIDs')
    for person in roster['people']:
        if person['personID'] in person_ids:
            require(person['batch'] == HERE.name and person['id'] in batch_ids,
                    f"Batch personID conflicts with existing roster: {person['personID']}")
    warnings.extend(manifest.get('warnings', []))
    visual = HERE / 'visual-review.json'
    if visual.is_file():
        review = read(visual.as_posix())
        require(set(review['ids']) == batch_ids, 'Visual review character ids mismatch')
        for view in review['views']:
            check_hash(view['file'], view['sha256'])
    else:
        warnings.append({'id': 'VISUAL_REVIEW_NOT_RECORDED', 'value': True})


try:
    run()
except Exception as error:
    failures.append(str(error))
print(json.dumps({'batch': HERE.name, 'readOnly': True, 'passed': not failures,
                  'checked': checked, 'warnings': warnings, 'failures': failures}, ensure_ascii=False, indent=2))
sys.exit(1 if failures else 0)
