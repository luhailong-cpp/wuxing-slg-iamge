"""Register technically valid art candidates while preserving user review as pending.

Usage: python records/production-20261111/register-candidates.py --batch BATCH
Run serially from this repository. This command never grants visual acceptance.
"""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPORTS = ROOT / 'exports/01-率土之滨'
REVIEW = EXPORTS / 'art-review-20261029'
PENDING = 'awaiting_user_visual_review'
KINDS = {'card-full', 'face-native', 'bust-native', 'avatar-128', 'avatar-256'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe(value, exists=True):
    path = Path(value)
    path = (path if path.is_absolute() else ROOT / path).resolve()
    require(path.is_relative_to(ROOT), f'Path escapes this repository: {value}')
    if exists:
        require(path.is_file(), f'Missing file: {value}')
    return path


def read(path):
    return json.loads(safe(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(safe(path).read_bytes()).hexdigest()


def rel(path):
    return safe(path, exists=False).relative_to(ROOT).as_posix()


def serialized(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def write(path, value):
    safe(path, exists=False).write_text(serialized(value), encoding='utf-8', newline='\n')


def unique(rows, key, owner):
    index = {row[key]: row for row in rows}
    require(len(index) == len(rows), f'{owner}: duplicate {key}')
    return index


def verify_hash(path, expected):
    require(digest(path) == expected, f'SHA256 mismatch: {path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    batch = args.batch
    require(re.fullmatch(r'roster-expansion-\d{8}-heroes\d+', batch), 'Unexpected batch directory name')
    records = ROOT / 'records' / batch
    visual_path = records / 'visual-review.json'
    visual = read(visual_path)
    require(visual.get('status') == PENDING, 'Visual status must await user review')
    require(visual.get('userApproved') is False and visual.get('passed') is False,
            'This path requires explicitly pending user approval and passed=false')
    require(visual.get('technicalOnly') is True, 'Visual record must identify technical-only scope')
    for view in visual['views']:
        verify_hash(view['file'], view['sha256'])
    verifier = safe(records / 'verify-batch.py')
    verification = subprocess.run([sys.executable, str(verifier)], cwd=ROOT, capture_output=True,
                                  text=True, encoding='utf-8')
    require(verification.returncode == 0, 'Fresh technical verifier failed: ' + verification.stdout + verification.stderr)
    technical = json.loads(verification.stdout)
    require(technical.get('passed') is True, 'Fresh technical verification did not pass')
    require(technical.get('readOnly') is True, 'Expected a read-only batch verifier')

    source_path = EXPORTS / batch / 'generals-ui-manifest.json'
    source_manifest = read(source_path)
    require(source_manifest.get('userApproved') is False, 'Source manifest must remain unapproved')
    require(source_manifest.get('clientIntegrated') is False, 'This path cannot reset an integrated batch')
    sources = source_manifest['sources']
    unique(sources, 'id', 'batch sources')
    require(technical['checked']['masters'] == len(sources), 'Technical master count mismatch')
    require(technical['checked']['assets'] == len(sources) * 5, 'Technical UI count mismatch')
    require(set(visual['ids']) == {item['id'] for item in sources}, 'Visual review identities mismatch')
    roster_path = REVIEW / 'generals-manifest.json'
    roster = read(roster_path)
    existing_by_person = unique(roster['people'], 'personID', 'shared roster')
    existing_by_id = unique(roster['people'], 'id', 'shared roster')
    replacements = {}
    for source in sources:
        verify_hash(source['source'], source['sha256'])
        verify_hash(source['generation'], source['generationSha256'])
        generated = read(source['generation'])
        require(safe(generated['file']) == safe(source['source']) and generated['sha256'] == source['sha256'],
                'Generation record image mismatch')
        identity = generated['identity']
        require(identity['id'] == source['id'] and identity['name'] == source['name'], 'Source identity mismatch')
        person_id = identity['personID']
        require(person_id not in replacements, 'Duplicate batch personID')
        old = existing_by_person.get(person_id)
        if old:
            require(old['batch'] == batch and old['id'] == source['id'],
                    f'PersonID already belongs to another batch: {person_id}')
            require(not old.get('clientIntegrated') and not old.get('userApproved') and not old.get('visualFinalAccepted'),
                    'Refusing to reset an integrated or approved person')
        same_id = existing_by_id.get(source['id'])
        require(same_id is None or (same_id['batch'] == batch and same_id['personID'] == person_id),
                f'Character id conflicts with another person: {source["id"]}')
        assets = [item for item in source_manifest['assets'] if item['personId'] == source['id']]
        require(len(assets) == 5 and {item['variant'] for item in assets} == KINDS, 'Five UI variants required')
        for asset in assets:
            verify_hash(asset['file'], asset['sha256'])
            verify_hash(asset['record'], asset['recordSha256'])
        replacement = copy.deepcopy(old) if old else {}
        replacement.update({
            'id': source['id'], 'name': source['name'], 'personID': person_id, 'batch': batch,
            'master': source['source'], 'masterSha256': source['sha256'], 'sourceManifest': rel(source_path),
            'assets': [{key: asset[key] for key in ('variant', 'file', 'sha256', 'record')} for asset in assets],
            'status': PENDING, 'technicalVerificationPassed': True,
            'userApproved': False, 'userFinalAccepted': False, 'visualFinalAccepted': False,
            'rootVisualReviewPassed': False, 'clientIntegrated': False, 'officialCardVariantsComplete': False,
        })
        replacements[person_id] = replacement
    old_batch_ids = {person['personID'] for person in roster['people'] if person['batch'] == batch}
    require(old_batch_ids.issubset(replacements), 'Current source set would drop an existing batch person')
    people = [replacements.get(person['personID'], person) for person in roster['people']]
    people.extend(person for person_id, person in replacements.items() if person_id not in existing_by_person)
    unique(people, 'personID', 'result roster')
    unique(people, 'id', 'result roster')
    # Verify retained files while leaving all historical entry fields unchanged.
    for person in people:
        verify_hash(person['master'], person['masterSha256'])
        for asset in person['assets']:
            verify_hash(asset['file'], asset['sha256'])
            safe(asset['record'])
    stamp = datetime.now(timezone.utc).isoformat()
    asset_count = sum(len(person['assets']) for person in people)
    roster.update(people=people, updatedAtUtc=stamp, assetCount=asset_count, clientIntegrated=False,
                  scope=f'{len(people)} identity-master candidates with five UI variants each. Full roster incomplete.',
                  integrationScope='Historical entry flags are preserved. New candidates await user visual review.')
    js_path = REVIEW / 'data.js'
    js_text = safe(js_path).read_text(encoding='utf-8').strip()
    require(js_text.startswith('window.ART_REVIEW_DATA=') and js_text.endswith(';'), 'Unexpected data.js wrapper')
    js_data = json.loads(js_text.removeprefix('window.ART_REVIEW_DATA=').removesuffix(';'))
    js_data['generals'] = roster
    page = REVIEW / 'index.html'
    html = safe(page).read_text(encoding='utf-8')
    require('<option value="all">全部批次</option>' in html, 'Missing batch selector insertion point')
    html = re.sub(r'人物库 · \d+', f'人物库 · {len(people)}', html)
    html = re.sub(r'(<option value="new">)新增 \d+ 人', rf'\g<1>新增 {len(people) - 12} 人', html)
    option = f'<option value="{batch}">本批候选 {len(replacements)} 人（待审核）</option>'
    pattern = rf'<option value="{re.escape(batch)}">.*?</option>'
    html = re.sub(pattern, option, html) if re.search(pattern, html) else html.replace(
        '<option value="all">全部批次</option>', '<option value="all">全部批次</option>' + option)
    overlay_path = ROOT / 'records/roster-20261029/CURRENT_PRODUCTION_OVERLAY_20261102.json'
    overlay = read(overlay_path)
    unique(overlay['entries'], 'personID', 'production overlay')
    overlay_ids = unique(overlay['entries'], 'id', 'production overlay')
    for person_id, person in replacements.items():
        old = overlay_ids.get(person['id'])
        require(old is None or old['personID'] == person_id, 'Overlay character id conflict')
    overlay_replacements = {}
    old_overlay = {entry['personID']: entry for entry in overlay['entries']}
    for person_id, person in replacements.items():
        entry = copy.deepcopy(old_overlay.get(person_id, {}))
        entry.update({key: person[key] for key in ('id', 'name', 'personID', 'batch', 'master', 'masterSha256')})
        entry.update(uiDerivativeCount=5, unityUiImported=False, status=PENDING,
                     technicalVerificationPassed=True, officialCardVariantsComplete=False,
                     userApproved=False, userFinalAccepted=False, visualFinalAccepted=False,
                     rootVisualReviewPassed=False)
        overlay_replacements[person_id] = entry
    entries = [overlay_replacements.get(entry['personID'], entry) for entry in overlay['entries']]
    entries.extend(entry for person_id, entry in overlay_replacements.items() if person_id not in old_overlay)
    overlay.update(updatedAtUtc=stamp, masterPeople=len(people), uiDerivatives=asset_count, entries=entries)
    receipt_path = records / 'candidate-registration.json'
    source_manifest.update(status=PENDING, userApproved=False, rootVisualReviewPassed=False,
                           visualFinalAccepted=False, clientIntegrated=False, technicalOnly=True,
                           technicalVerificationPassed=True, candidateRegistrationReceipt=rel(receipt_path))
    # Every validation precedes shared file writes. Run batches serially.
    write(source_path, source_manifest)
    write(roster_path, roster)
    js_path.write_text('window.ART_REVIEW_DATA=' + json.dumps(js_data, ensure_ascii=False, separators=(',', ':')) + ';\n',
                       encoding='utf-8', newline='\n')
    page.write_text(html, encoding='utf-8', newline='\n')
    write(overlay_path, overlay)
    receipt = {'registeredAtUtc': stamp, 'batch': batch, 'status': PENDING, 'userApproved': False,
               'visualAcceptanceGranted': False, 'technicalVerification': technical,
               'visualReview': {'file': rel(visual_path), 'sha256': digest(visual_path)},
               'sourceManifest': {'file': rel(source_path), 'sha256': digest(source_path)},
               'batchPeople': len(replacements), 'totalPeople': len(people), 'totalUI': asset_count,
               'sharedOutputs': [{'file': rel(file), 'sha256': digest(file)}
                                 for file in (roster_path, js_path, page, overlay_path)]}
    write(receipt_path, receipt)
    print(json.dumps({'batch': batch, 'candidatePeople': len(replacements), 'totalPeople': len(people),
                      'totalUI': asset_count, 'status': PENDING, 'userApproved': False,
                      'receipt': rel(receipt_path)}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
