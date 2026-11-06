"""Compose six review images and editable layer recipes from existing art."""
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
GAME = Path('exports/01-率土之滨')
OUT = GAME / 'ui-artonly-20261104'
FONT = GAME / 'fonts/wuxing-ui-20261102/WuxingUI-Regular.ttf'
SIZE = (1280, 720)
INK = '#244638'
MUTED = '#5f6451'
RED = '#a53c24'
LIGHT = '#fff3cd'
BACKGROUND = Path('designs/01-率土之滨/assets/login-background-20261028/login-landscape-v1.png')
REFERENCE = Path('designs/01-率土之滨/ui/troop-correction-20261028/16-historical-generals-five-troops-conscription-ui-v1.png')
STYLES = [Path('designs/mail-ui-v1/01-mail-event.png'), Path('designs/team-ui-v2/team-ui-v2.png')]


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


@lru_cache(maxsize=None)
def provenance(path):
    local = ROOT / path
    records = (Path(str(path) + '.derivation.json'), Path(str(path) + '.generation.json'))
    record = next((r.as_posix() for r in records if (ROOT / r).is_file()), None)
    digest = sha256(local.read_bytes()).hexdigest()
    if record:
        declared = json.loads((ROOT / record).read_text(encoding='utf-8-sig')).get('sha256')
        assert declared == digest, (path, record)
    return {'file': path.as_posix(), 'sha256': digest, 'record': record}


@lru_cache(maxsize=None)
def raster(path):
    with Image.open(ROOT / path) as source:
        return source.convert('RGBA')


@lru_cache(maxsize=None)
def typeface(size):
    return ImageFont.truetype(str(ROOT / FONT), size)


def source(group, key):
    return GAME / group / (key + '.png')


def ui(key):
    return source('runtime-ui-v2', key)


def support(key):
    return source('ui-support-v1', key + '-native')


class Composition:
    def __init__(self):
        self.canvas = Image.new('RGBA', SIZE)
        self.layers = []
        self.sources = {}

    def picture(self, path, x, y, width=None, *, role, cover=False):
        original = raster(path)
        if cover:
            layer = ImageOps.fit(original, SIZE, method=Image.Resampling.LANCZOS)
        elif width is not None and width != original.width:
            assert width < original.width, (path, width, original.width)
            layer = original.resize((width, round(original.height * width / original.width)), Image.Resampling.LANCZOS)
        else:
            layer = original
        box = [x, y, x + layer.width, y + layer.height]
        assert 0 <= box[0] < box[2] <= SIZE[0] and 0 <= box[1] < box[3] <= SIZE[1], box
        self.canvas.alpha_composite(layer, (x, y))
        self.sources[path.as_posix()] = provenance(path)
        self.layers.append({'kind': 'image', 'role': role, 'source': path.as_posix(), 'sourceSize': list(original.size), 'boxXYXY': box,
                            'operation': 'cover downscale with centered crop' if cover else ('proportional downscale' if layer is not original else 'native size composite')})

    def label(self, x, y, value, size, *, color=INK, anchor='lm', role, max_width=None):
        font = typeface(size)
        draw = ImageDraw.Draw(self.canvas)
        box = draw.textbbox((x, y), value, font=font, anchor=anchor)
        assert 0 <= box[0] < box[2] <= SIZE[0] and 0 <= box[1] < box[3] <= SIZE[1], (value, box)
        assert max_width is None or box[2] - box[0] <= max_width, (value, box, max_width)
        missing = font.getmask('\u0378')
        for ch in set(value) - {' '}:
            mask = font.getmask(ch)
            assert (mask.size, bytes(mask)) != (missing.size, bytes(missing)), (value, ch)
        draw.text((x, y), value, font=font, anchor=anchor, fill=color)
        self.layers.append({'kind': 'text', 'role': role, 'value': value, 'position': [x, y], 'anchor': anchor,
                            'font': FONT.as_posix(), 'sizePx': size, 'fill': color, 'glyphBoundsXYXY': list(box)})

    def button(self, x, y, value, skin, role, *, width=218, size=19):
        self.picture(ui(skin), x - width // 2, y - round(width * 204 / 500 / 2), width, role=role)
        color = LIGHT if skin == 'button-primary-normal' else INK
        if skin.endswith('disabled'):
            color = '#413e36'
        self.label(x + round(width / 72), y, value, size, color=color, anchor='mm', role=role + '文字', max_width=width * .57)


def row(c, hero, unit, position, y, current, target, adjustable, completed_add=0):
    active = target > current
    row_skin = 'card-row-selected' if active else 'card-row-normal'
    c.picture(ui(row_skin), 208, y - 88, 453, role=position + '卡片')
    hero_id, hero_name = hero
    unit_id, unit_name = unit
    c.picture(source('generals-ui-v1', hero_id + '-avatar-256'), 280, y - 41, 82, role=position + '武将头像')
    c.label(371, y - 21, position, 16, color=MUTED, role=position + '阵位')
    c.label(371, y + 9, hero_name, 26, role=position + '武将名')
    c.picture(source('five-element-troops-v1', unit_id + '-icon128'), 444, y - 42, 38, role=position + '兵种图标')
    c.label(488, y - 23, unit_name, 17, role=position + '兵种')
    c.label(444, y + 12, '兵力', 16, color=MUTED, role=position + '兵力标签')
    c.label(488, y + 12, f'{current} → {target}', 21, role=position + '兵力数值', max_width=127)
    added_label = f'已补 +{completed_add}' if completed_add else f'本次 +{target - current}'
    c.label(443, y + 36, added_label, 15, color=MUTED, role=position + '新增数值')
    if adjustable:
        minus_skin = 'button-secondary-normal' if active else 'button-secondary-disabled'
        c.button(538, y + 35, '-', minus_skin, position + '减少兵力', width=52, size=16)
        c.button(581, y + 35, '+', 'button-primary-normal', position + '增加兵力', width=52, size=16)


STATE_INPUT = {
    'idle': {'title': '待设置', 'counts': [480, 560, 480, 560], 'heldGrain': 1600, 'heldCoins': 800, 'cta': '确认征兵', 'enabled': False},
    'amount_changed': {'title': '数量已调整', 'counts': [480, 560, 680, 660], 'heldGrain': 1600, 'heldCoins': 800, 'cta': '确认征兵', 'enabled': True},
    'resources_insufficient': {'title': '粮草不足', 'counts': [480, 560, 980, 860], 'heldGrain': 1600, 'heldCoins': 800, 'cta': '粮草不足', 'enabled': False},
    'recruiting': {'title': '征兵中', 'counts': [480, 560, 680, 660], 'heldGrain': 1600, 'heldCoins': 800, 'cta': '取消征兵', 'enabled': True},
    'cancel_confirm': {'title': '取消确认', 'counts': [480, 560, 680, 660], 'heldGrain': 1600, 'heldCoins': 800, 'cta': '取消征兵', 'enabled': True},
    'complete': {'title': '征兵完成', 'counts': [680, 660, 680, 660], 'completedAdds': [200, 100], 'heldGrain': 400, 'heldCoins': 500, 'cta': '完成', 'enabled': True},
}


def compose(state, scenario):
    c = Composition()
    old_a, old_b, new_a, new_b = scenario['counts']
    added = new_a + new_b - old_a - old_b
    cost_grain, cost_coins = added * 4, added
    running = state in {'recruiting', 'cancel_confirm'}
    complete = state == 'complete'
    shortage = max(0, cost_grain - scenario['heldGrain'])
    completed_a, completed_b = scenario.get('completedAdds', (0, 0))
    c.picture(BACKGROUND, 0, 0, role='山城背景', cover=True)
    c.picture(ui('panel-main'), 167, 76, role='征兵主面板')
    c.label(657, 150, '征 兵', 34, color=LIGHT, anchor='mm', role='主标题')
    c.label(640, 202, '第一部队', 17, color=MUTED, anchor='mm', role='部队名称')
    c.picture(support('close'), 1015, 136, 58, role='关闭')
    c.label(437, 229, '兵力配置', 22, anchor='mm', role='配兵标题')
    row(c, ('liu-bei', '刘备'), ('metal', '金兵'), '大营', 303, old_a, new_a, not running and not complete, completed_a)
    row(c, ('zhao-yun', '赵云'), ('wood', '木兵'), '中军', 435, old_b, new_b, not running and not complete, completed_b)
    c.picture(ui('panel-detail'), 710, 216, 310, role='征兵信息面板')
    c.label(865, 263, scenario['title'], 23, anchor='mm', color=LIGHT, role='当前状态', max_width=168)

    if running:
        c.picture(ui('icon-timer'), 756, 306, 39, role='计时图标')
        c.label(808, 324, '剩余时间', 17, color=MUTED, role='计时标题')
        c.label(865, 368, '00:03:24', 36, anchor='mm', role='倒计时')
        c.label(865, 421, f'将补充 {added:,} 兵力', 19, anchor='mm', role='征兵增量')
    elif complete:
        c.picture(source('ui-state-kit-20261028-r2', 'illustration-confirm'), 816, 295, 104, role='完成插画')
        c.label(865, 415, f'已补充 {completed_a + completed_b:,} 兵力', 20, anchor='mm', role='完成增量')
        c.label(865, 448, f'总兵力 {old_a + old_b:,}', 17, color=MUTED, anchor='mm', role='完成后兵力')
    else:
        c.picture(ui('icon-grain'), 748, 303, 42, role='粮草图标')
        c.label(796, 321, '粮草', 17, role='粮草名称')
        c.label(965, 321, f'{cost_grain:,} / {scenario["heldGrain"]:,}', 19,
                color=RED if shortage else INK, anchor='rm', role='粮草需求和持有量', max_width=128)
        c.picture(ui('icon-coin'), 748, 346, 42, role='铜钱图标')
        c.label(796, 366, '铜钱', 17, role='铜钱名称')
        c.label(965, 366, f'{cost_coins:,} / {scenario["heldCoins"]:,}', 19, anchor='rm', role='铜钱需求和持有量', max_width=128)
        c.picture(ui('icon-timer'), 750, 389, 38, role='时间图标')
        c.label(796, 407, '耗时', 17, role='耗时名称')
        duration = f'{added // 3600:02}:{added // 60 % 60:02}:{added % 60:02}' if added else '—'
        c.label(965, 407, duration, 19, anchor='rm', role='耗时示例', max_width=128)
        c.label(865, 445, f'还差 {shortage:,} 粮草' if shortage else ('需求 / 持有' if added else '请先调整目标兵力'),
                16, color=RED if shortage else MUTED, anchor='mm', role='消耗说明')

    action_skin = 'button-primary-normal' if scenario['enabled'] and not running else 'button-secondary-normal'
    if not scenario['enabled']:
        action_skin = 'button-primary-disabled'
    c.button(864, 496, scenario['cta'], action_skin, '征兵操作')
    c.button(334, 540, '返回配兵', 'button-secondary-normal', '返回配兵', width=198, size=17)
    c.label(550, 540, f'总兵力 {old_a + old_b:,}' if complete else f'总兵力 {old_a + old_b:,} → {new_a + new_b:,}',
            21, anchor='mm', role='总兵力预览', max_width=254)

    if state == 'cancel_confirm':
        overlay = Image.new('RGBA', SIZE, (19, 29, 23, 151))
        c.canvas.alpha_composite(overlay)
        c.layers.append({'kind': 'color', 'role': '确认层背景遮罩', 'boxXYXY': [0, 0, *SIZE], 'rgba': [19, 29, 23, 151]})
        c.picture(ui('panel-confirm'), 356, 150, role='取消征兵确认框')
        c.label(641, 222, '取消征兵', 28, color=LIGHT, anchor='mm', role='确认框标题')
        c.label(640, 317, '要取消当前征兵吗？', 28, anchor='mm', role='确认提示')
        c.label(640, 365, '取消后将停止这次征兵。', 19, color=MUTED, anchor='mm', role='取消后果')
        c.button(523, 442, '继续征兵', 'button-secondary-normal', '保留征兵')
        c.button(756, 442, '确认取消', 'button-primary-normal', '确认取消')

    assert c.canvas.getchannel('A').getextrema() == (255, 255)
    assert c.layers[0]['role'] == '山城背景'
    return c


def main():
    target = ROOT / OUT
    target.mkdir(exist_ok=True, parents=True)
    states = []
    for state, scenario in STATE_INPUT.items():
        composition = compose(state, scenario)
        output = OUT / (state.replace('_', '-') + '.png')
        composition.canvas.convert('RGB').save(ROOT / output, optimize=True)
        info = {'id': state, 'title': scenario['title'], 'preview': provenance(output), 'size': list(SIZE), 'mode': 'RGB',
                'exampleInput': scenario, 'derivedFrom': list(composition.sources.values()), 'layers': composition.layers}
        states.append(info)
    write_json(target / 'manifest.json', {
        'schemaVersion': 1,
        'builtAtUtc': datetime.now(timezone.utc).isoformat(),
        'game': '五行问鼎',
        'feature': '征兵',
        'stateMatrixScreenId': 16,
        'stateMatrixSource': provenance(Path('records/production-20261028/ui-state-matrix.json')),
        'artSource': 'existing',
        'operation': 'existing raster layers and separately rendered text composited into a landscape review image',
        'layoutReference': provenance(REFERENCE),
        'styleReferences': [provenance(p) for p in STYLES],
        'font': {**provenance(FONT), 'license': provenance(GAME / 'fonts/wuxing-ui-20261102/OFL.txt')},
        'previewSize': list(SIZE),
        'previewStateCount': len(states),
        'visualReviewRecord': 'records/ui-artonly-20261104/visual-review.json',
        'states': states,
        'newModelImages': 0,
        'clientIntegrated': False,
        'userAccepted': False,
        'limits': ['Review composition at one landscape size', 'Fixed example data and unit types',
                   'Live quantity inputs, dynamic progress, resource settlement, reserve system and other display ratios require follow-up'],
    })


if __name__ == '__main__':
    main()
