"""Build a static human-review package from existing art; no art generation or approval."""
import datetime
import hashlib
import html
import json
import os
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPORTS = ROOT / 'exports/01-率土之滨'
FONT = EXPORTS / 'fonts/wuxing-ui-20261102/WuxingUI-Regular.ttf'
BATCHES = [f'roster-expansion-20261111-heroes{i}' for i in (7, 8, 9, 10, 11)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def local(value):
    path = (ROOT / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
    require(path.is_relative_to(ROOT), f'Outside repository: {value}')
    require(path.is_file(), f'Input not ready: {value}')
    return path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.resolve().relative_to(ROOT).as_posix()


def url(path):
    return quote(os.path.relpath(path, HERE).replace('\\', '/'), safe='/._-~')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    font = ImageFont.truetype(str(local(FONT)), 28)
    small_font = ImageFont.truetype(str(FONT), 15)
    groups = []
    people = []
    for batch in BATCHES:
        manifest_path = local(EXPORTS / batch / 'generals-ui-manifest.json')
        manifest = read(manifest_path)
        require(manifest['generalCount'] == 3 and manifest['assetCount'] == 15,
                f'{batch}: expected 3 masters and 15 UI assets')
        require(manifest.get('userApproved') is False, f'{batch}: expected user approval pending')
        previews = [local(ROOT / 'records' / batch / f'generals-ui-{tone}.png') for tone in ('light', 'dark')]
        group = {'batch': batch, 'manifest': relative(manifest_path), 'manifestSha256': sha(manifest_path),
                 'status': 'awaiting_user_visual_review', 'userApproved': False,
                 'warnings': manifest.get('warnings', []), 'people': [],
                 'previewFiles': [{'file': relative(path), 'sha256': sha(path)} for path in previews]}
        for index, source in enumerate(manifest['sources']):
            master = local(source['source'])
            require(sha(master) == source['sha256'], f"Source hash mismatch: {source['id']}")
            generation = local(source['generation'])
            require(sha(generation) == source['generationSha256'], f"Generation record hash mismatch: {source['id']}")
            assets = [asset for asset in manifest['assets'] if asset['personId'] == source['id']]
            require(len(assets) == 5, f"Five UI variants required: {source['id']}")
            for asset in assets:
                require(sha(local(asset['file'])) == asset['sha256'], f"Asset hash mismatch: {asset['file']}")
                require(sha(local(asset['record'])) == asset['recordSha256'], f"Derivation hash mismatch: {asset['record']}")
            card = next(asset for asset in assets if asset['variant'] == 'card-full')
            avatar = next(asset for asset in assets if asset['variant'] == 'avatar-128')
            with Image.open(local(card['file'])) as image:
                require(image.mode == 'RGBA' and image.size == (768, 1024), f"Card format: {card['file']}")
            with Image.open(local(avatar['file'])) as image:
                require(image.mode == 'RGBA' and image.size == (128, 128), f"Avatar format: {avatar['file']}")
            person = {'id': source['id'], 'name': source['name'], 'batch': batch,
                      'status': 'awaiting_user_visual_review', 'userApproved': False,
                      'source': {'file': relative(master), 'sha256': sha(master)},
                      'card': {'file': card['file'], 'sha256': card['sha256']},
                      'avatar128': {'file': avatar['file'], 'sha256': avatar['sha256']},
                      'summaryGrid': {'column': BATCHES.index(batch), 'row': index}}
            group['people'].append(person)
            people.append(person)
        groups.append(group)
    require(len(people) == 15 and len({person['id'] for person in people}) == 15, 'Expected 15 distinct people')
    outputs = []
    for tone, bg, ink, subtle in [('light', '#f1ebdf', '#243c34', '#586a60'),
                                  ('dark', '#1b282d', '#ece5d2', '#c3bda9')]:
        board = Image.new('RGB', (1200, 1095), bg)
        draw = ImageDraw.Draw(board)
        operations = []
        for person in people:
            x, y = person['summaryGrid']['column'] * 240, person['summaryGrid']['row'] * 365
            path = local(person['card']['file'])
            with Image.open(path) as source:
                image = source.convert('RGBa').resize((216, 288), Image.Resampling.LANCZOS).convert('RGBA')
            board.paste(image, (x + 12, y + 6), image)
            draw.text((x + 120, y + 298), person['name'], font=font, fill=ink, anchor='mt')
            draw.text((x + 120, y + 335), '待用户审核', font=small_font, fill=subtle, anchor='mt')
            operations.append({'source': person['card'], 'operation': 'uniform premultiplied-alpha Lanczos resize for review only',
                               'sourceSize': [768, 1024], 'previewSize': [216, 288], 'offset': [x + 12, y + 6],
                               'scale': 0.28125, 'sourceModified': False})
        output = HERE / f'summary-{tone}.png'
        board.save(output)
        derivative = {'file': relative(output), 'sha256': sha(output), 'format': 'PNG', 'mode': 'RGB',
                      'size': [1200, 1095], 'purpose': 'QA contact sheet for user visual review',
                      'newModelGeneration': False, 'artModified': False, 'userApproved': False,
                      'background': bg, 'layout': {'columns': 5, 'rows': 3, 'cell': [240, 365], 'order': 'one batch per column'},
                      'font': {'file': relative(FONT), 'sha256': sha(FONT), 'nameSize': 28, 'labelSize': 15},
                      'derivedFrom': operations}
        save(Path(str(output) + '.derivation.json'), derivative)
        outputs.append({'file': relative(output), 'sha256': sha(output), 'record': relative(Path(str(output) + '.derivation.json'))})
    cards_html = []
    for group in groups:
        items = []
        for person in group['people']:
            master = local(person['source']['file'])
            card = local(person['card']['file'])
            avatar = local(person['avatar128']['file'])
            items.append(f'''<article class="hero"><div class="hero-preview"><a href="{url(card)}"><img src="{url(card)}" alt="{html.escape(person['name'])}完整卡面" width="768" height="1024" loading="lazy"></a></div><div class="hero-body"><h3>{html.escape(person['name'])}</h3><span class="status">待用户审核</span><div class="links"><a href="{url(master)}">原生母图</a><a href="{url(card)}">完整卡面</a><a href="{url(avatar)}">128 头像</a></div><img class="avatar" src="{url(avatar)}" alt="{html.escape(person['name'])}128像素头像" width="128" height="128" loading="lazy"></div></article>''')
        light = local(group['previewFiles'][0]['file'])
        dark = local(group['previewFiles'][1]['file'])
        num = group['batch'].split('heroes')[-1]
        cards_html.append(f'''<section class="batch"><div class="batch-title"><h2>第 {num} 批</h2><p><a href="{url(light)}">本批浅底预览</a><a href="{url(dark)}">本批深底预览</a><a href="{url(local(group['manifest']))}">来源与技术提示</a></p></div><div class="grid">{''.join(items)}</div></section>''')
    html_body = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>五行问鼎 · 15 名武将人工审核</title>
<style>
@font-face{font-family:WuxingUI;src:url("FONT_URL") format("truetype");font-display:swap}*{box-sizing:border-box}body{margin:0;background:#eee7d8;color:#253b33;font-family:WuxingUI,"Microsoft YaHei",sans-serif;line-height:1.65}main{max-width:1120px;padding:30px 20px 70px;margin:auto}header{padding:22px 26px;background:#faf6eb;border:1px solid #c6b58d;border-radius:18px}h1{font-size:clamp(25px,4vw,36px);line-height:1.3;margin:0 0 10px}h2{margin:0;font-size:25px}h3{font-size:25px;margin:0 0 6px}p{margin:8px 0}a{color:#226a59;text-underline-offset:3px}a:focus-visible{outline:3px solid #be873f;outline-offset:4px}nav{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px}ol{padding-left:24px}li+li{margin-top:4px}.note{font-size:15px;color:#5b6255}.batch{margin-top:30px}.batch-title{display:flex;justify-content:space-between;align-items:baseline;gap:15px;flex-wrap:wrap;margin:0 0 13px}.batch-title p{display:flex;gap:16px;flex-wrap:wrap;font-size:15px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.hero{overflow:hidden;border:1px solid #c6b58d;border-radius:14px;background:#faf6eb}.hero-preview{background:#e6decd;padding:12px}.hero-preview img{display:block;width:100%;height:310px;object-fit:contain}.hero-body{padding:16px}.status{display:inline-block;border:1px solid #b39967;border-radius:20px;padding:2px 10px;font-size:14px;background:#f0e5c8;color:#715624}.links{display:flex;gap:15px;flex-wrap:wrap;margin-top:13px;font-size:15px}.avatar{display:block;max-width:128px;margin-top:12px;background:#e6decd;border-radius:10px}.footer{margin-top:28px;border-top:1px solid #c6b58d;padding-top:14px;font-size:14px;color:#5b6255}@media(max-width:700px){main{padding:18px 12px 40px}header{padding:18px}.grid{grid-template-columns:1fr}.hero-preview img{height:340px}.batch-title{display:block}}
</style></head><body><main><header><h1>五行问鼎 · 15 名武将人工审核</h1><p>本页汇总本次 5 批新作。当前均为<strong>待用户视觉审核</strong>，技术检查不代表画面已通过。</p><ol><li><strong>画风与辨识：</strong>是否保持道家 Q 版手绘，人物面容、服饰和持物是否容易区分。</li><li><strong>肢体与持物：</strong>请查看双手、双脚、武器、冠饰和衣摆是否完整、自然。</li><li><strong>浅深边缘：</strong>请分别查看浅底与深底预览，确认透明边缘和头像裁切是否合适。</li></ol><nav><a href="summary-light.png">15 人浅底总览</a><a href="summary-dark.png">15 人深底总览</a><a href="summary-metadata.json">文件与技术记录</a></nav><p class="note">可按姓名指出“可用”或需要修改的位置。原生图与各类导出均保留；头像、半身是有意裁切。没有动作播放、GUI 控制或自动视觉通过。</p></header>GROUPS<div class="footer">此页只读取本仓库已有 PNG。模型与质量未披露的字段保持 null；原生低透明度像素、alpha 峰值与边距提示记录在各批清单中。整款游戏、动作和客户端验收仍未完成。</div></main></body></html>
'''.replace('FONT_URL', url(FONT)).replace('GROUPS', ''.join(cards_html))
    html_file = HERE / 'index.html'
    html_file.write_text(html_body, encoding='utf-8', newline='\n')
    metadata = {'createdAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'product': '五行问鼎', 'status': 'awaiting_user_visual_review', 'userApproved': False,
                'rootVisualReviewPassed': False, 'technicalOnly': True, 'guiAutomationUsed': False,
                'scope': '15 existing generated identity masters and their 75 UI derivatives, grouped for user review',
                'peopleCount': 15, 'uiAssetsChecked': 75,
                'technicalChecks': {'existingSourceAndAssetHashes': True, 'cardRgba768x1024': True,
                                    'avatarRgba128x128': True, 'localReferencesOnly': True},
                'visualAcceptance': 'User review pending. No model or automatic acceptance.',
                'summaryImages': outputs, 'index': {'file': relative(html_file), 'sha256': sha(html_file)},
                'groups': groups}
    save(HERE / 'summary-metadata.json', metadata)
    print(json.dumps({'people': 15, 'uiAssetsChecked': 75, 'status': metadata['status'],
                      'outputs': [relative(html_file)] + [item['file'] for item in outputs]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
