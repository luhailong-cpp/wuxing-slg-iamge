"""Create user review material and record technical checks; no visual approval."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda file: json.loads(file.read_text(encoding='utf-8-sig'))
sha = lambda file: hashlib.sha256(file.read_bytes()).hexdigest()
rel = lambda file: file.relative_to(ROOT).as_posix()
def write(file, value):
    file.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

cfg = read(HERE / 'export-input.json')
output = ROOT / cfg['exportRoot']
manifest_file = output / 'generals-ui-manifest.json'
manifest = read(manifest_file)
board = Image.new('RGB', (144 * len(cfg['characters']), 344))
draw = ImageDraw.Draw(board)
sources = []
for row, (color, ink) in enumerate((('#f1ebdf', '#243c34'), ('#1b282d', '#ece5d2'))):
    draw.rectangle((0, row * 172, board.width, (row + 1) * 172), fill=color)
    for column, person in enumerate(cfg['characters']):
        file = output / f"{person['id']}-avatar-128.png"
        with Image.open(file) as avatar:
            assert avatar.size == (128, 128)
            board.paste(avatar, (column * 144 + 8, row * 172 + 8), avatar)
        draw.text((column * 144 + 8, row * 172 + 144), person['id'], fill=ink)
        if row == 0:
            sources.append({'file': rel(file), 'sha256': sha(file)})
preview = HERE / 'avatars-128-light-dark.png'
board.save(preview)
write(HERE / 'avatars-128-light-dark.png.derivation.json', {
    'file': rel(preview), 'sha256': sha(preview), 'sources': sources,
    'operation': 'Each 128x128 avatar is alpha-composited at exactly 128x128 on light and dark backgrounds; labels are outside the avatar images.',
    'newModelGeneration': False, 'resampled': False})
views = [{'file': rel(HERE / file), 'sha256': sha(HERE / file)} for file in
         ('generals-ui-light.png', 'generals-ui-dark.png', 'avatars-128-light-dark.png')]
review = {
    'status': 'awaiting_user_visual_review', 'passed': False, 'technicalOnly': True,
    'userApproved': False, 'rootVisualReviewPassed': False, 'clientIntegrated': False,
    'modelPreviewInspected': True,
    'recordedAtUtc': datetime.now(timezone.utc).isoformat(),
    'clientDate': '2026-11-11', 'ids': [person['id'] for person in cfg['characters']],
    'views': views,
    'scope': 'Review materials prepared. File integrity checks do not constitute user visual acceptance.',
    'constraints': {'guiAutomationUsed': False, 'computerUseCuaSkyUsed': False,
                    'agentMayApproveVisualsForUser': False},
    'notes': [
        'Three host-generated full-body masters are byte-identical to their host PNGs. Actual model and quality were not disclosed.',
        'Face and bust rectangles were selected from displayed model previews as production crops; their suitability remains for the user to judge.',
        'Source alpha-1, peak-alpha-254 and under-8-percent margin advisories are preserved verbatim in the export manifest.',
        'No animations, additional directions or card-specific visual variants are claimed by this batch.',
        'Do not register this batch with register-reviewed.py because user visual approval is pending.'
    ],
    'warnings': manifest['warnings']}
write(HERE / 'visual-review.json', review)
manifest.update(status='awaiting_user_visual_review', rootVisualReviewPassed=False,
                userApproved=False, clientIntegrated=False, visualFinalAccepted=False,
                technicalOnly=True, technicalVerification='records/' + HERE.name + '/delivery-integrity.json')
write(manifest_file, manifest)
verification = subprocess.run([sys.executable, str(HERE / 'verify-batch.py')], cwd=ROOT,
                              capture_output=True, text=True, encoding='utf-8')
if verification.stderr:
    print(verification.stderr, file=sys.stderr)
result = json.loads(verification.stdout)
result.update(technicalOnly=True, visualAcceptance=False, userApproved=False,
              status='awaiting_user_visual_review',
              checkedAtUtc=datetime.now(timezone.utc).isoformat())
write(HERE / 'delivery-integrity.json', result)
print(json.dumps({'technicalPassed': result['passed'], 'masters': result['checked']['masters'],
                  'ui': result['checked']['assets'], 'warnings': result['warnings'],
                  'visualStatus': review['status'], 'views': views}, ensure_ascii=False, indent=2))
sys.exit(verification.returncode)
