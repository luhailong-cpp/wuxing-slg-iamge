"""Register already copied host images without modifying any PNG or shared index.

Run explicitly after generation. Every response must have a same-stem request and
an existing same-stem PNG in designs/01-率土之滨/characters/<this batch>/.
"""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ART = ROOT / 'designs/01-率土之滨/characters' / HERE.name


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(file):
    return json.loads(file.read_text(encoding='utf-8-sig'))


def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def repository_file(value):
    require(isinstance(value, str) and value, f'Invalid repository path: {value!r}')
    file = Path(value)
    file = (file if file.is_absolute() else ROOT / file).resolve()
    require(file.is_relative_to(ROOT), f'Path escapes this repository: {value}')
    require(file.is_file(), f'Missing repository file: {value}')
    return file


def relative(file):
    return file.resolve().relative_to(ROOT).as_posix()


def prepare(response_file):
    stem = response_file.name.removesuffix('.response.json')
    request_file = HERE / f'{stem}.request.json'
    require(request_file.is_file(), f'Missing request: {request_file.name}')
    request, response = read(request_file), read(response_file)
    require(response.get('actualModel') is None and response.get('actualQuality') is None,
            f'{stem}: actual model/quality are not undisclosed; inspect new metadata before adopting')
    for field in ('callStartedAt', 'callCompletedAt', 'sourceImage', 'resultId'):
        require(response.get(field), f'{stem}: missing response field {field}')
    # This exact host source path is authorized solely for byte verification.
    host_image = Path(response['sourceImage']).resolve()
    require(host_image.is_file(), f'{stem}: missing host output {host_image}')
    master = repository_file(relative(ART / f'{stem}.png'))
    source_sha, master_sha = digest(host_image), digest(master)
    require(source_sha == master_sha, f'{stem}: host output and copied master differ')
    identity = request['identity']
    require(all(identity.get(key) for key in ('id', 'name', 'personID')),
            f'{stem}: incomplete identity')
    references = []
    reference_paths = set()
    for reference in request['references']:
        require(isinstance(reference, dict) and reference.get('file') and reference.get('sha256'),
                f'{stem}: each reference needs a file and SHA256')
        file = repository_file(reference['file'])
        require(digest(file) == reference['sha256'], f'{stem}: reference SHA256 changed: {file}')
        require(reference.get('actuallyAttached') is not False,
                f'{stem}: request includes a reference recorded as unattached')
        references.append(dict(reference))
        reference_paths.add(file)
    submitted = request['submittedParameters']
    submitted_paths = {repository_file(value) for value in submitted.get('referenced_image_paths', [])}
    require(submitted_paths == reference_paths, f'{stem}: submitted references differ from reference records')
    prompt_file = repository_file(request['prompt'])
    if submitted.get('promptFile'):
        require(repository_file(submitted['promptFile']) == prompt_file, f'{stem}: prompt paths differ')
    with Image.open(master) as image:
        require(image.format == 'PNG' and image.mode == 'RGBA', f'{stem}: expected native RGBA PNG')
        width, height = image.size
        alpha = image.getchannel('A')
        histogram = alpha.histogram()
        corners = [alpha.getpixel(point) for point in
                   ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))]
        alpha_inspection = {
            'range': list(alpha.getextrema()),
            'fullyTransparentPixelCount': histogram[0],
            'semiTransparentPixelCount': sum(histogram[1:255]),
            'opaquePixelCount': histogram[255],
            'canvasCornerAlpha': corners,
        }
        metadata_keys = sorted(image.info.keys())
    record = {
        'schemaVersion': 1,
        'file': relative(master),
        'sha256': master_sha,
        'generatedAt': response['callCompletedAt'],
        'generatedAtBasis': 'Observed host call completion time; no separate internal generation time disclosed',
        'callStartedAt': response['callStartedAt'],
        'width': width,
        'height': height,
        'format': 'PNG',
        'mode': 'RGBA',
        'nativeDimensionsPreserved': True,
        'resampled': False,
        'art_source': 'host_image',
        'tool': request.get('tool', 'image_gen.imagegen'),
        'route': 'builtin',
        'resultId': response['resultId'],
        'executionCellId': response.get('executionCellId'),
        'configSnapshot': request['configSnapshot'],
        'configSnapshotBasis': 'actual_request_config_snapshot',
        'submittedParameters': submitted,
        'actualModel': None,
        'actualQuality': None,
        'unverifiedReason': 'Host-managed generation. The tool did not disclose a verifiable actual model or quality for this result. Configuration targets and prompt text are not model evidence.',
        'evidence': [
            {'file': relative(request_file), 'sha256': digest(request_file), 'field': 'submittedParameters'},
            {'file': relative(response_file), 'sha256': digest(response_file),
             'fields': [key for key in ('returnedFields', 'output_hint', 'callStartedAt', 'callCompletedAt',
                                       'resultId', 'sourceImage') if key in response]},
            {'sourceImage': str(host_image), 'sha256': source_sha, 'copyHashVerified': True},
        ],
        'prompt': relative(prompt_file),
        'references': references,
        'pngMetadataKeys': metadata_keys,
        'alphaInspection': alpha_inspection,
        'assetRole': 'historical full-body master',
        'status': 'draft_pending_visual_review',
        'userApproved': False,
        'clientIntegrated': False,
        'identity': identity,
    }
    destination = Path(str(master) + '.generation.json')
    require(destination.resolve().is_relative_to(ART.resolve()), f'{stem}: invalid sidecar destination')
    body = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    if destination.exists():
        require(destination.read_text(encoding='utf-8-sig') == body,
                f'{stem}: existing sidecar differs; refusing to overwrite {destination.name}')
    return destination, body, {'file': relative(master), 'sha256': master_sha,
                               'size': [width, height], 'mode': 'RGBA',
                               'alphaRange': alpha_inspection['range']}


def main():
    responses = sorted(HERE.glob('*.response.json'))
    require(responses, 'No *.response.json files in this batch')
    # Validate the entire set before creating any sidecar.
    prepared = [prepare(file) for file in responses]
    created, reused, details = 0, 0, []
    for destination, body, detail in prepared:
        if destination.exists():
            reused += 1
        else:
            with destination.open('x', encoding='utf-8', newline='\n') as output:
                output.write(body)
            created += 1
        details.append(detail)
    print(json.dumps({'batch': HERE.name, 'createdSidecars': created, 'reusedIdenticalSidecars': reused,
                      'pngFilesModified': 0, 'actualModel': None, 'actualQuality': None,
                      'images': details}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'batch': HERE.name, 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
