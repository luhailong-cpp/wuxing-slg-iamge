"""Reconcile the frozen official snapshot against the current art manifest by ID."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'records/roster-20261029'
ART = ROOT / 'exports/01-率土之滨/art-review-20261029/generals-manifest.json'
FACTS = SOURCE / 'OFFICIAL_ROSTER_FACTS_20261029.json'
IDENTITIES = SOURCE / 'PRODUCTION_IDENTITY_RECONCILIATION_20261029.json'
CORPUS = SOURCE / 'CORPUS_COVERAGE_LEDGER_20261029.json'
CARD_ART = ROOT / 'exports/01-率土之滨/official-card-art-20261104/card-art-manifest.json'

RECOMMENDED = (
    'ww-p-a803ace56a5c',  # 徐晃
    'ww-p-bd1bcc1072bc',  # 于禁
    'ww-p-fdfa979a0dbc',  # 乐进
    'ww-p-feee693f26dd',  # 朱灵
    'ww-p-0907e758601d',  # 庞德
    'ww-p-15c66f255bef',  # 文聘
    'ww-p-6a5c8e2f7566',  # 李通
    'ww-p-fc77d30af177',  # 黄权
    'ww-p-1ad715230157',  # 曹仁
    'ww-p-07563508cc4b',  # 程昱
    'ww-p-9561f89d16d0',  # 荀攸
    'ww-p-a51d2678b15c',  # 张鲁
    'ww-p-f784cb3f93bc',  # 公孙瓒
    'ww-p-2020bc6050e5',  # 马腾
    'ww-p-767074d82bd2',  # 诸葛瑾
)


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path):
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': sha256(path)}


def write(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n',
                             encoding='utf-8', newline='\n')


def unique_index(rows, key):
    index = {row[key]: row for row in rows}
    if len(index) != len(rows):
        raise ValueError(f'Duplicate {key}')
    return index


def verify_art(people, entities):
    for person in people:
        entity = entities[person['personID']]
        assert entity['personID'] == person['personID']
        assert person['name'] == entity['name']
        assert sha256(ROOT / person['master']) == person['masterSha256']
        assert not person['officialCardVariantsComplete'], 'Check new variant records before building'
        variants = set()
        for asset in person['assets']:
            assert sha256(ROOT / asset['file']) == asset['sha256']
            assert (ROOT / asset['record']).is_file()
            assert asset['variant'] not in variants
            variants.add(asset['variant'])
        assert len(variants) == 5


def verify_card_art(official, card_to_entity, people):
    manifest = read(CARD_ART)
    assert manifest['status'] == 'visually_reviewed_card_art_candidates'
    cards = unique_index(manifest['cards'], 'cardid')
    for view in manifest['reviewViews']:
        assert sha256(ROOT / view['file']) == view['sha256']
        for item in view['sources']:
            assert sha256(ROOT / item['file']) == item['sha256']
    for card_id, card in cards.items():
        row = official[card_id]
        entity = card_to_entity[card_id]
        person = people[entity['personID']]
        assert card['officialName'] == row['name'] and card['variantRaw'] == row['variant']
        assert card['candidatePersonID'] == entity['personID']
        assert card['identityMaster'] == {'file': person['master'], 'sha256': person['masterSha256']}
        master, artwork = card['nativeMaster'], card['artwork']
        generation, derivation = master['generation'], artwork['record']
        for item in (master, artwork, generation, derivation):
            assert sha256(ROOT / item['file']) == item['sha256']
        assert master['sha256'] != person['masterSha256']
        generated = read(ROOT / generation['file'])
        assert generated['file'] == master['file'] and generated['sha256'] == master['sha256']
        assert generated['identity']['personID'] == entity['personID']
        assert generated['identity']['cardIDs'] == [card_id]
        derived = read(ROOT / derivation['file'])
        assert derived['file'] == artwork['file'] and derived['sha256'] == artwork['sha256']
        assert derived['derivedFrom'] == {
            'file': master['file'], 'sha256': master['sha256'],
            'generation': generation['file'], 'generationSha256': generation['sha256'],
        }
    return cards


def scope_for(row):
    if row['officialPublicListPredicatePass']:
        return 'official_public_list'
    if row['isReleaseRaw'] == 1:
        return 'release_marked_outside_public_list'
    return 'unreleased_config_record'


def next_card_action(entity, has_art):
    if entity is None:
        return 'unassigned_in_frozen_reconciliation'
    if entity['cardMatchStatus'] == 'split_by_official_faction_pending_person_match':
        return 'resolve_homonym_with_card_specific_evidence'
    if entity['category'] == '通用兵':
        return 'define_generic_unit_card_art'
    if entity['category'] == '组合':
        return 'define_collective_card_art'
    if entity['category'] == '非三国联动':
        return 'review_special_card_scope'
    if entity['category'] == '待考':
        return 'resolve_card_identity'
    if has_art:
        return 'review_or_produce_card_specific_variant'
    return 'produce_identity_master_then_review_card_variant'


def main():
    facts = read(FACTS)
    official = unique_index(facts['rows'], 'cardid')
    entities = unique_index(read(IDENTITIES)['entities'], 'entityID')
    people = unique_index(read(ART)['people'], 'personID')
    verify_art(people.values(), entities)
    card_to_entity = {}
    names = defaultdict(list)
    for entity in entities.values():
        names[entity['originalName']].append(entity['entityID'])
        for card in entity['cardIds']:
            if card in card_to_entity:
                raise ValueError(f'Multiple existing candidate mappings for card {card}')
            card_to_entity[card] = entity
            if official[card]['name'] != entity['originalName']:
                assert official[card]['name'] == entity['canonicalName']
                assert any(alias['approved'] and alias['name'] == entity['originalName']
                           for alias in entity['aliases'])
        assert set(entity['releaseMarkedCardIds']) == {
            card for card in entity['cardIds'] if official[card]['isReleaseRaw'] == 1
        }
        assert set(entity['publicListCardIds']) == {
            card for card in entity['cardIds'] if official[card]['officialPublicListPredicatePass']
        }

    card_art = verify_card_art(official, card_to_entity, people)
    cards = []
    for card_id, row in official.items():
        assert row['officialPublicListPredicatePass'] == (
            row['name'] != '侍卫' and row['variant']['isSeasonCardRaw'] != 1
            and row['isReleaseRaw'] == 1
        )
        entity = card_to_entity.get(card_id)
        person_id = entity['personID'] if entity else None
        person = people.get(person_id)
        variant = row['variant']
        icon_id = variant['iconHeroIdRaw']
        icon_target = official.get(icon_id)
        art = card_art.get(card_id)
        cards.append({
            'cardid': card_id,
            'sourceArrayIndex': row['sourceArrayIndex'],
            'officialName': row['name'],
            'officialFaction': row['faction'],
            'starsRaw': row['starsRaw'],
            'variantRaw': variant,
            'isReleaseRaw': row['isReleaseRaw'],
            'scope': scope_for(row),
            'sourceDisplayNameCategory': row['displayNameCategory'],
            'candidateEntityID': entity['entityID'] if entity else None,
            'candidatePersonID': person_id,
            'candidateMatchRule': entity['cardMatchStatus'] if entity else None,
            'candidateSourceSpelling': entity['originalName'] if entity else None,
            'identityEvidenceStatus': entity['identityStatus'] if entity else None,
            'masterID': person['id'] if person else None,
            'cardSpecificArtRecord': art,
            'cardSpecificArtStatus': ('verified_card_id_art_candidate' if art
                                      else 'no_card_id_art_record_in_current_manifest'),
            'crossNameIconReference': (
                {'cardid': icon_id, 'officialName': icon_target['name']}
                if icon_target and icon_target['name'] != row['name'] else None
            ),
            'nextAction': ('review_card_specific_art_in_client' if art
                           else next_card_action(entity, person is not None)),
        })

    identity_rows = []
    for entity in entities.values():
        person = people.get(entity['personID'])
        identity_rows.append({
            'entityID': entity['entityID'],
            'personID': entity['personID'],
            'name': entity['name'],
            'sourceName': entity['originalName'],
            'category': entity['category'],
            'identityEvidenceStatus': entity['identityStatus'],
            'identityContext': entity.get('identityContext'),
            'sourceLocators': [
                {key: entry[key] for key in ('sourceUrl', 'sourceSha256', 'revision', 'sourceType', 'locator')
                 if key in entry}
                for entry in entity['source']
            ],
            'cardIds': entity['cardIds'],
            'publicCardIds': entity['publicListCardIds'],
            'releaseMarkedCardIds': entity['releaseMarkedCardIds'],
            'possibleCardMatches': entity.get('possibleCardMatches', []),
            'aliasesWithSourceEvidence': entity['aliases'],
            'sameSourceNameEntityIDs': [key for key in names[entity['originalName']]
                                        if key != entity['entityID']],
            'identityMaster': ({'id': person['id'], 'file': person['master'],
                                'sha256': person['masterSha256'],
                                'verifiedUiDerivatives': len(person['assets'])} if person else None),
            'artStatus': 'verified_identity_master_candidate' if person else 'no_current_identity_master',
        })

    identity_index = unique_index(identity_rows, 'entityID')
    ready = []
    for person_id in RECOMMENDED:
        item = identity_index[person_id]
        if item['identityMaster'] is not None:
            continue
        assert item['publicCardIds'] and item['category'] == '普通人物'
        assert item['identityEvidenceStatus'] in {'primary_index_name_confirmed',
                                                  'primary_heading_and_opening_confirmed'}
        assert not item['sameSourceNameEntityIDs']
        ready.append({
            'personID': person_id,
            'name': item['name'],
            'identityEvidenceStatus': item['identityEvidenceStatus'],
            'sources': item['sourceLocators'],
            'officialPublicCards': [
                {'cardid': cid, 'faction': official[cid]['faction'], 'starsRaw': official[cid]['starsRaw'],
                 'variantRaw': official[cid]['variant']}
                for cid in item['publicCardIds']
            ],
        })

    coverage = {}
    for scope, selected in (
        ('publicList', [card for card in cards if card['scope'] == 'official_public_list']),
        ('releaseMarked', [card for card in cards if card['isReleaseRaw'] == 1]),
        ('unreleased', [card for card in cards if card['isReleaseRaw'] == 0]),
        ('allConfigRecords', cards),
    ):
        coverage[scope] = {
            'cards': len(selected),
            'distinctOfficialDisplayNames': len({card['officialName'] for card in selected}),
            'linkedToCandidateEntity': sum(card['candidateEntityID'] is not None for card in selected),
            'linkedToCurrentMaster': sum(card['masterID'] is not None for card in selected),
            'individualMasterIdentitiesRepresented': len({card['masterID'] for card in selected
                                                           if card['masterID'] is not None}),
            'cardIdSpecificArtRecords': sum(card['cardSpecificArtRecord'] is not None for card in selected),
            'nextActions': dict(Counter(card['nextAction'] for card in selected)),
        }

    for label, count_key in (('publicList', 'publicListRecords'),
                             ('releaseMarked', 'release1Records'),
                             ('unreleased', 'release0Records'),
                             ('allConfigRecords', 'configRecords')):
        assert coverage[label]['cards'] == facts['counts'][count_key]
    corpus = read(CORPUS)
    summary = {
        'sourceSnapshot': '2026-10-29',
        'sourceFiles': [reference(path) for path in (FACTS, IDENTITIES, CORPUS, ART, CARD_ART)],
        'officialConfigSource': facts['sourceChain'][-1],
        'officialPublicListPredicate': facts['publicListPredicate'],
        'coverage': coverage,
        'verifiedCurrentMasters': len(people),
        'verifiedCurrentUi': sum(len(person['assets']) for person in people.values()),
        'reconciliationEntities': len(entities),
        'reconciliationPersonCandidateKeys': sum(row['personID'] is not None for row in identity_rows),
        'originalNameCollisionGroups': {name: ids for name, ids in names.items() if len(ids) > 1},
        'crossNameIconReferences': sum(card['crossNameIconReference'] is not None for card in cards),
        'historicalCorpus': {
            'totalVolumes': corpus['history']['totalVolumes'],
            'indexEntriesRead': corpus['history']['indexEntriesRead'],
            'bodyCensusComplete': corpus['history']['fullVolumeEntityCensusComplete'],
        },
        'novelCorpus': {
            'totalChapters': corpus['novel']['totalChapters'],
            'indexLinksRead': corpus['novel']['indexLinksRead'],
            'bodyCensusComplete': corpus['novel']['fullChapterEntityCensusComplete'],
        },
        'fullRosterComplete': False,
        'liveRosterCoverageConfirmed': False,
        'artAcceptanceComplete': False,
    }
    write('coverage-summary.json', summary)
    write('official-cards-coverage.json', cards)
    write('identity-art-coverage.json', identity_rows)
    write('next-official-historical-masters.json', ready)
    print(json.dumps({'coverage': coverage, 'ready': len(ready),
                      'masters': len(people), 'ui': summary['verifiedCurrentUi']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
