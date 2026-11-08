"""Register the visually reviewed art batch in the shared roster and preview."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


RECORDS = Path(__file__).resolve().parent
ROOT = RECORDS.parents[1]
BATCH = RECORDS.name
EXPORTS = ROOT / 'exports/01-率土之滨'
REVIEW = EXPORTS / 'art-review-20261029'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def main():
    stamp = datetime.now(timezone.utc).isoformat()
    review = read(RECORDS / 'visual-review.json')
    for sheet in review['views']:
        assert digest(ROOT / sheet['file']) == sheet['sha256']
    assert review['passed']
    source_path = EXPORTS / BATCH / 'generals-ui-manifest.json'
    source_manifest = read(source_path)
    roster_path = REVIEW / 'generals-manifest.json'
    roster = read(roster_path)
    people = [p for p in roster['people'] if p['batch'] != BATCH]
    people_ids = {p['personID'] for p in people}
    assert len(people) == len(people_ids)
    new_people = []
    for source in source_manifest['sources']:
        assert digest(ROOT / source['source']) == source['sha256']
        assert digest(ROOT / source['generation']) == source['generationSha256']
        identity = read(ROOT / source['generation'])['identity']
        assert identity['id'] == source['id'] and identity['name'] == source['name']
        assert identity['personID'] not in people_ids
        people_ids.add(identity['personID'])
        assets = [a for a in source_manifest['assets'] if a['personId'] == source['id']]
        assert {a['variant'] for a in assets} == {'card-full', 'face-native', 'bust-native', 'avatar-128', 'avatar-256'}
        for asset in assets:
            assert digest(ROOT / asset['file']) == asset['sha256']
            assert digest(ROOT / asset['record']) == asset['recordSha256']
        new_people.append({'id': source['id'], 'name': source['name'], 'personID': identity['personID'],
                           'batch': BATCH, 'master': source['source'], 'masterSha256': source['sha256'],
                           'sourceManifest': rel(source_path),
                           'assets': [{k: a[k] for k in ('variant', 'file', 'sha256', 'record')} for a in assets],
                           'officialCardVariantsComplete': False, 'visualFinalAccepted': False, 'clientIntegrated': False})
    assert set(review['ids']) == {p['id'] for p in new_people}
    people += new_people
    for person in people:
        assert digest(ROOT / person['master']) == person['masterSha256']
        for asset in person['assets']:
            assert digest(ROOT / asset['file']) == asset['sha256']
            assert (ROOT / asset['record']).is_file()
    asset_count = sum(len(p['assets']) for p in people)
    source_manifest.update(rootVisualReviewPassed=True, status='source and UI candidates visually reviewed')
    write(source_path, source_manifest)
    roster.update(people=people, createdAt=stamp, assetCount=asset_count, clientIntegrated=False,
                  scope=f'{len(people)} identity-master candidates with five UI variants each. Full roster incomplete.',
                  integrationScope='Previously integrated people retain their flags. Latest batch is art production only.')
    write(roster_path, roster)
    js_path = REVIEW / 'data.js'
    js_data = json.loads(js_path.read_text(encoding='utf-8').strip().removeprefix('window.ART_REVIEW_DATA=').removesuffix(';'))
    js_data['generals'] = roster
    js_path.write_text('window.ART_REVIEW_DATA=' + json.dumps(js_data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8', newline='\n')
    page = REVIEW / 'index.html'
    html = page.read_text(encoding='utf-8')
    import re
    html = re.sub(r'人物库 · \d+', f'人物库 · {len(people)}', html)
    html = re.sub(r'(<option value="new">)新增 \d+ 人', rf'\g<1>新增 {len(people)-12} 人', html)
    option = f'<option value="{BATCH}">本批新增 {len(new_people)} 人</option>'
    if option not in html:
        html = html.replace('<option value="all">全部批次</option>', '<option value="all">全部批次</option>' + option)
    page.write_text(html, encoding='utf-8', newline='\n')
    overlay_path = ROOT / 'records/roster-20261029/CURRENT_PRODUCTION_OVERLAY_20261102.json'
    overlay = read(overlay_path)
    overlay.update(updatedAtUtc=stamp, masterPeople=len(people), uiDerivatives=asset_count)
    new_ids = {p['id'] for p in new_people}
    overlay['entries'] = [p for p in overlay['entries'] if p['id'] not in new_ids]
    overlay['entries'] += [{k: p[k] for k in ('id', 'name', 'personID', 'master', 'masterSha256')}
                           | {'uiDerivativeCount': 5, 'unityUiImported': False,
                              'status': 'master_and_UI_candidates_reviewed', 'officialCardVariantsComplete': False,
                              'userFinalAccepted': False} for p in new_people]
    write(overlay_path, overlay)
    print(json.dumps({'people': len(people), 'ui': asset_count, 'newPeople': len(new_people)}, ensure_ascii=True))


if __name__ == '__main__':
    main()
