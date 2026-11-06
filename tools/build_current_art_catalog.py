"""Inventory real files and current direction choices without marking art approved."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
from collections import Counter
from PIL import Image

ROOT = Path('D:/work/wuxing-slg-iamge')
GIT = 'C:/Program Files/Git/cmd/git.exe'
OVERRIDES = {
    2:'02-world-trends-ui-v2.png', 3:'03-five-elements-roster-ui-v3.png',
    13:'phase3-theme/13-five-elements-spell-library-ui-v5.png',
    18:'18-metal-envoy-detail-ui-v2.png',
    19:'19-metal-envoy-recruit-result-ui-v2.png',
    23:'23-metal-envoy-attributes-ui-v2.png',
    24:'24-metal-envoy-troop-types-ui-v2.png', 21:'21-map-march-ui-v4.png', 36:'36-construction-queue-ui-v2.png',
    14:'phase3-theme/14-metal-spell-detail-ui-v3.png',
    15:'phase3-theme/15-five-elements-formation-ui-v3.png',
    16:'phase3-theme/16-five-elements-conscription-ui-v3.png',
    17:'phase3-theme/17-five-elements-battle-report-ui-v4.png',
    33:'33-five-elements-battle-result-ui-v2.png',
    34:'34-metal-envoy-awakening-ui-v2.png',
    35:'35-five-elements-recruit-entry-ui-v3.png',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    names=sorted(set(subprocess.check_output([GIT,'ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode('utf-8').split('\0'))-set(['']))
    images=[]
    errors=[]
    for name in names:
        path=ROOT/name
        if path.suffix.lower() not in ('.png','.jpg','.jpeg','.webp','.gif'): continue
        try:
            with Image.open(path) as im: im.verify()
            with Image.open(path) as im: size=list(im.size);mode=im.mode
        except Exception as exc:
            errors.append({'file':name,'error':'image_decode_failed','type':type(exc).__name__})
            continue
        record=None
        for suffix in ('.generation.json','.derivation.json','.derived.json'):
            candidate=Path(str(path)+suffix)
            if candidate.exists(): record=candidate;break
        entry={'file':name,'sha256':sha(path),'dimensions':size,'mode':mode}
        if record:
            value=read(record)
            entry['record']=record.relative_to(ROOT).as_posix()
            entry['recordHashMatches']=value.get('sha256','').lower()==entry['sha256']
            entry['status']=value.get('status','recorded_derived_preview')
            entry['kind']='generated_native' if record.name.endswith('.generation.json') else 'derived'
            if not entry['recordHashMatches']: errors.append({'file':name,'error':'record_sha256_mismatch'})
        else:
            entry['kind']='reference_or_batch_qa_without_adjacent_record'
        images.append(entry)
    by_name={item['file']:item for item in images}
    ui_dir='designs/01-率土之滨/ui/'
    ui=[]
    for index in range(1,37):
        if index in OVERRIDES:
            name=ui_dir+OVERRIDES[index]
        else:
            candidates=[name for name in by_name if name.startswith(ui_dir+f'{index:02d}-') and name.endswith('-v1.png')]
            if len(candidates)!=1: raise ValueError(f'Unexpected base UI candidates for {index}')
            name=candidates[0]
        if name not in by_name: raise ValueError(f'Current UI not yet complete: {name}')
        usage=('five_elements_redesign_candidate' if index in (2,3,13,14,15,16,17,18,19,23,24,33,34,35) else
            'neutral_static_direction_root_reviewed_rules_and_states_pending' if index in (31,32) else
            'two_bank_bridge_route_visual_repair_candidate_navigation_unverified' if index==21 else
            'resource_icon_repair_candidate_five_elements_rules_still_pending' if index==36 else
            'functional_direction_pending_complete_five_elements_adaptation')
        ui.append({'id':index,'file':name,'sha256':by_name[name]['sha256'],'usage':usage,
            'userApproved':False,'clientIntegrated':False})
    old_char_dir='designs/01-率土之滨/characters/'
    historical=[{'file':name,'sha256':item['sha256'],
        'usage':'excluded_from_five_elements_first_release_requires_genuinely_new_original_design'}
        for name,item in by_name.items() if name.startswith(old_char_dir) and '/' not in name[len(old_char_dir):]
        and not name.split('/')[-1].startswith(('01-','07-'))]
    five=[{'file':name,'sha256':item['sha256'],'status':'original_candidate_pending_user_review_and_margin_contract'}
        for name,item in by_name.items() if name.startswith(old_char_dir+'five-elements/')]
    bundles=[]
    for relative in ('exports/01-率土之滨/map-kit/map-kit-manifest.json','exports/01-率土之滨/fx/fx-manifest.json',
                     'exports/01-率土之滨/five-elements/emblems/emblems-manifest.json','exports/01-率土之滨/units/units-manifest.json',
                     'exports/01-率土之滨/hero-ui-v1/hero-ui-manifest.json',
                     'exports/01-率土之滨/five-elements/skill-icons/skill-icons-manifest.json'):
        manifest=read(ROOT/relative)
        bundles.append({'manifest':relative,'sha256':sha(ROOT/relative),
            'nativeOrCropCount':manifest.get('assetCount',manifest.get('nativeCount')),
            'displayDerivativeCount':manifest.get('displayDerivativeCount',0),
            'animationFrameCount':0,'userApproved':False,'clientIntegrated':False})
    fx_clips=[]
    for asset_id in ('slash-arc','strategy-array','healing-light','buff-cloud','debuff-mist','fire','capture-circle','reward-glow'):
        relative=f'exports/01-率土之滨/fx-animation/{asset_id}/manifest.json'
        path=ROOT/relative
        if not path.exists(): continue
        manifest=read(path)
        frames=manifest.get('frames',[])
        if len(frames)!=8 or len({f['sha256'] for f in frames})!=8:
            errors.append({'file':relative,'error':'expected_eight_unique_actual_frames'})
        for frame in frames:
            name=frame['file']
            if name not in by_name or by_name[name]['sha256']!=frame['sha256']:
                errors.append({'file':name,'error':'animation_manifest_frame_sha_mismatch'})
        fx_clips.append({'id':asset_id,'manifest':relative,'sha256':sha(path),'frameCount':len(frames),
            'durationSeconds':manifest.get('durationSeconds'),'loop':manifest.get('loop'),
            'status':'generated_phase_animation_candidate_pending_motion_and_gameplay_acceptance'})
    value={'schemaVersion':1,'inventoriedAtUtc':datetime.now(timezone.utc).isoformat(),
        'projectRoot':ROOT.as_posix(),'theme':['金','木','水','火','土'],
        'status':'work_in_progress_not_complete_game_art','fullGameArtComplete':False,
        'imageFileCount':len(images),'imageKinds':dict(Counter(i['kind'] for i in images)),
        'currentUiFunctionCount':36,'currentUiDirectionSelection':ui,
        'originalFiveElementsMasterCandidates':five,'historicalCharactersExcludedFromFirstRelease':historical,
        'approvedFirstReleaseCharacters':[], 'staticExportBundles':bundles,
        'totalAnimationFrames':sum(c['frameCount'] for c in fx_clips),'fxAnimationClipCandidates':fx_clips,
        'characterAnimationFrames':0,'clientIntegrated':False,'images':images,'errors':errors,
        'engineTarget':{'name':'Unity','basis':'user_explicit_selection','testedEditorVersion':'6000.6.0f1',
            'actualGameProjectProvided':False,'targetDeviceConfirmed':False},
        'unityPreviewPackageVerification':('records/01-率土之滨/runtime-ui-v2-unity-final-review-20261027.json'
            if (ROOT/'records/01-率土之滨/runtime-ui-v2-unity-final-review-20261027.json').exists()
            else 'records/01-率土之滨/unity-preview-package-verification-20261027.json'),
        'unityFxAnimationPackageVerification':'records/01-率土之滨/unity-fx-animation-package-verification-20261027.json',
        'unityHeroSkillUIPackageVerification':'records/01-率土之滨/hero-skill-ui-final-review-20261027.json',
        'unityFxGPUPlaybackVerification':'records/fx-gpu-playback-v1/final-review.json',
        'unityMapAssemblyVerification':'records/01-率土之滨/map-assembly-v1/unity/verification.json',
        'mapAssemblyManifest':'exports/01-率土之滨/map-assembly-v1/assembly-manifest.json',
        'currentRuntimeUiManifest':('exports/01-率土之滨/runtime-ui-v2/runtime-ui-manifest.json'
            if (ROOT/'exports/01-率土之滨/runtime-ui-v2/runtime-ui-manifest.json').exists()
            else 'exports/01-率土之滨/runtime-ui/runtime-ui-manifest.json'),
        'limits':['All counts are actual files, including historical variants and QA/reference images; these are not counts of approved game resources.',
            'Current direction selection is a production choice, not user approval or final acceptance.',
            'See per-image and per-bundle warnings, margin/alpha limits, recovered receipt gaps and illustrative game values.']}
    destination=ROOT/'records/current-art-catalog-20261027.json'
    write(destination,value)
    print(json.dumps({'catalog':destination.relative_to(ROOT).as_posix(),'images':len(images),
        'imageKinds':value['imageKinds'],'currentUi':len(ui),'originalFiveElements':len(five),
        'excludedHistoricalFiles':len(historical),'errors':errors}))
    if errors: raise SystemExit(1)


if __name__=='__main__': main()
