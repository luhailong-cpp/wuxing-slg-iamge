"""Save one image request immediately before its separately executed host call."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
names = {'zhang-xiu': '张绣', 'cao-hong': '曹洪', 'jiang-qin': '蒋钦'}
identity_id = sys.argv[1]
name = names[identity_id]
read = lambda file: json.loads(file.read_text(encoding='utf-8-sig'))
sha = lambda file: hashlib.sha256(file.read_bytes()).hexdigest()
rel = lambda file: file.relative_to(ROOT).as_posix()
roster = read(ROOT / 'exports/01-率土之滨/art-review-20261029/generals-manifest.json')
if any(person['name'] == name for person in roster['people']):
    raise ValueError(f'Already in current roster: {name}')
coverage = read(ROOT / 'records/roster-coverage-20261104/identity-art-coverage.json')
identity, = [row for row in coverage if row['name'] == name]
prompt = ROOT / 'prompts/01-率土之滨' / HERE.name / f'{identity_id}-master-v1.prompt.txt'
references = [ROOT / 'designs/mail-ui-v1/01-mail-event.png', ROOT / 'designs/team-ui-v2/team-ui-v2.png']
parameters = {'prompt': prompt.read_text(encoding='utf-8').strip(),
              'referenced_image_paths': [str(file) for file in references], 'transparent_background': True,
              'model': None, 'quality': None}
request = {'startedAt': datetime.now(timezone.utc).isoformat(), 'clientDate': '2026-11-11',
           'configSnapshot': read(ROOT / 'config/image-generation.json'), 'tool': 'image_gen.imagegen',
           'prompt': rel(prompt), 'references': [{'file': rel(file), 'sha256': sha(file),
           'role': 'approved art style reference', 'actuallyAttached': True} for file in references],
           'submittedParameters': parameters,
           'identity': {'id': identity_id, 'name': name, 'personID': identity['personID'],
                        'cardIDs': identity['cardIds'], 'identityEvidenceStatus': identity['identityEvidenceStatus'],
                        'sourceLocators': identity['sourceLocators'],
                        'designNote': 'Original costume interpretation; primary index confirms historical identity, not visual likeness.'}}
destination = HERE / f'{identity_id}-master-v1.request.json'
with destination.open('x', encoding='utf-8', newline='\n') as output:
    output.write(json.dumps(request, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'request': rel(destination), 'prompt': parameters['prompt'], 'startedAt': request['startedAt']}, ensure_ascii=False))
