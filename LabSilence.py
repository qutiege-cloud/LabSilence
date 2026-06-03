# =============================================================
#  추리 게임
#  Python /     
#  조작: WASD 이동 | 마우스 시점 | [F] 단서 조사 | [Tab] 수사 메뉴
# =============================================================

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()
Text.default_font = 'NotoSansKR-Bold'
window.title = '사건 보고서'
window.borderless = False

# =============================================================
#  단서 데이터
# =============================================================
CLUES = {
    'coffee_cup': {
        'name': '편의점 커피 컵',
        'desc': '실험대 위 버려진 편의점 커피 컵.\n최민호가 매일 사 마시는 브랜드 라벨이 붙어있다.\n→ 퇴근했다는 그가 사건 당일 밤 실험실에 있었음을 시사한다.',
        'location': '실험실', 'collected': False, 'related': '최민호'
    },
    'card_log': {
        'name': '보안카드 재진입 기록',
        'desc': '20시 55분, 최민호의 보조원 카드가\n건물에 재진입한 기록이 발견되었다.\n→ 퇴근했다는 그의 진술과 정면으로 모순이다.',
        'location': '실험실', 'collected': False, 'related': '최민호'
    },
    'pc_log': {
        'name': '독극물 검색 기록',
        'desc': '4층 자료실 PC에서 발견된 독극물 검색 내역.\n검색 시각은 사건 발생 3일 전이다.\n→ 최민호의 계정으로 로그인된 상태에서 검색되었다.',
        'location': '4층 자료실', 'collected': False, 'related': '최민호'
    },
    'circuit_breaker': {
        'name': 'CCTV 분전반 지문',
        'desc': '옥상 CCTV 전원 분전반 손잡이에서\n최민호의 지문이 검출되었다.\n→ 그가 감시를 피하기 위해 직접 CCTV를 차단했다.',
        'location': '옥상', 'collected': False, 'related': '최민호'
    },
    'key_mark': {
        'name': '복사 열쇠 흔적',
        'desc': '독성 물질 보관함에서 발견된 복사 열쇠.\n최민호가 근무 중 몰래 복사한 것으로 추정된다.\n→ 허가 없이 독성 물질에 접근할 수 있었다.',
        'location': '약품창고', 'collected': False, 'related': '최민호'
    },
    'badge': {
        'name': '최민호의 사원증',
        'desc': '약품창고 바닥에 떨어진 사원증.\n\'연구 보조원 최민호\'라고 새겨져 있다.\n→ 범행 중 이 장소에 있었다는 결정적 물리 증거다.',
        'location': '약품창고', 'collected': False, 'related': '최민호'
    },
    'remote_log': {
        'name': '해고 통보 문서',
        'desc': '서버실 프린터에 남아있던 미전달 문서.\n이강현이 최민호를 해고하기로 결정한 인사 처리서다.\n→ 최민호의 범행 동기를 입증하는 결정적 자료다.',
        'location': '서버실', 'collected': False, 'related': '최민호'
    },
    'burned_glove': {
        'name': '증거 인멸 고무장갑',
        'desc': '약품창고 선반 뒤에서 발견된 고무장갑.\n최민호의 DNA가 검출되었다.\n→ 독성 물질 취급 후 도주하며 버린 증거다.',
        'location': '약품창고', 'collected': False, 'related': '최민호'
    },
}

FAKE_CLUES = {
    'receipt':       {'name': '편의점 영수증',      'desc': '피해자 주머니 속 영수증.\n사건 당일 오후 7시 구입.\n→ 사건과 직접 관련이 없다.',              'location': '실험실'},
    'torn_memo':     {'name': '찢어진 메모지',      'desc': '실험 노트에서 찢겨 나온 조각.\n글씨가 흐릿하여 내용 식별 불가.\n→ 의미 있는 단서가 아닌 것 같다.',   'location': '실험실'},
    'lunchbox':      {'name': '점심 도시락 용기',   'desc': '책상 위 버려진 플라스틱 용기.\n→ 누군가 이곳에서 식사를 했다. 사건과 무관.', 'location': '4층 자료실'},
    'old_inventory': {'name': '낡은 재고 목록',     'desc': '수년 전 작성된 약품 재고 문서.\n→ 오래된 기록으로 현재 사건과 무관하다.',    'location': '약품창고'},
    'cigarette_box': {'name': '빈 담배 케이스',     'desc': '옥상 구석에 버려진 담배 케이스.\n→ 특정 인물과 연결할 수 없다.',              'location': '옥상'},
    'old_log':       {'name': '3개월 전 점검 일지', 'desc': '3개월 전 서버 점검 기록.\n→ 현재 사건과 직접적인 연관성이 없다.',           'location': '서버실'},
}

CULPRIT = '최민호'

# 단서 조합 시스템
CLUE_COMBOS = {
    ('cigarette_box', 'circuit_breaker'): {
        'npc': '최민호',
        'unlock_msg': '[ 단서 조합 발견! ]\n옥상 담배 케이스와 CCTV 분전반 지문이 일치합니다.\n최민호가 옥상에서 CCTV를 차단했음을 강하게 압박할 수 있습니다!',
        'pressure_line': '최민호: (당황하며) 그건... 그건 우연이에요!\n담배는 그냥 피운 거고, 분전반은 건드리지 않았어요!',
        'suspicion_boost': 2,
    },
    ('coffee_cup', 'card_log'): {
        'npc': '최민호',
        'unlock_msg': '[ 단서 조합 발견! ]\n실험실 커피 컵과 재진입 기록이 일치합니다.\n최민호가 퇴근 후 돌아왔음을 증명할 수 있습니다!',
        'pressure_line': '최민호: (얼굴이 굳으며) 그... 그 컵은 제 거 아니에요!\n카드 기록도... 오류일 수 있잖아요!',
        'suspicion_boost': 2,
    },
}

# 방별 조사 시간(초)
ROOM_TIMERS = {
    '실험실':     60,
    '4층 자료실': 50,
    '약품창고':   50,
    '옥상':       45,
    '서버실':     55,
}

ROOM_SPAWN = {
    '실험실':     (100, 3, -5),
    '4층 자료실': (-100, 3, -5),
    '약품창고':   (0, 3, 95),
    '옥상':       (0, 3, -95),
    '서버실':     (200, 3, -5),
}

# =============================================================
#  게임 상태
# =============================================================
game_phase        = 'start'
selected_location = None
collected_clues   = []
collected_fakes   = set()
visited_rooms     = set()
explore_timer     = 0.0
room_exiting      = False
talking           = False
notebook_open     = False
accusing          = False

npc_talk_count  = {'정다은': 0, '박지훈': 0, '최민호': 0, '한서윤': 0}
npc_suspicion   = {'정다은': 0, '박지훈': 0, '최민호': 0, '한서윤': 0}
confirmed_lies  = set()   # (npc_name, clue_id) — 모순 발견 처리된 것
shown_clues     = set()   # (npc_name, clue_id) — 의심도 이미 올린 것
unlocked_combos = set()
combo_pressure_ui = []

# =============================================================
#  맵 생성 헬퍼
# =============================================================
def _wall_door_h(cx, z, c, gap=6):
    seg = (20 - gap) / 2
    Entity(model='cube', position=(cx - 10 + seg / 2, 4, z), scale=(seg, 8, 0.5), color=c, collider='box')
    Entity(model='cube', position=(cx + 10 - seg / 2, 4, z), scale=(seg, 8, 0.5), color=c, collider='box')

def _wall_door_v(x, cz, c, gap=6):
    seg = (20 - gap) / 2
    Entity(model='cube', position=(x, 4, cz - 10 + seg / 2), scale=(0.5, 8, seg), color=c, collider='box')
    Entity(model='cube', position=(x, 4, cz + 10 - seg / 2), scale=(0.5, 8, seg), color=c, collider='box')

def make_corridor_h(x1, x2, z0=0, wc=color.dark_gray, fc=color.dark_gray):
    cx = (x1 + x2) / 2
    ln = x2 - x1
    Entity(model='cube', position=(cx, 0.5, z0),  scale=(ln, 1,   6),   color=fc, collider='box')
    Entity(model='cube', position=(cx, 8.5, z0),  scale=(ln, 0.5, 6),   color=wc, collider='box')
    Entity(model='cube', position=(cx, 4,   z0-3), scale=(ln, 8,   0.5), color=wc, collider='box')
    Entity(model='cube', position=(cx, 4,   z0+3), scale=(ln, 8,   0.5), color=wc, collider='box')

def make_corridor_v(z1, z2, x0=0, wc=color.dark_gray, fc=color.dark_gray):
    cz = (z1 + z2) / 2
    ln = z2 - z1
    Entity(model='cube', position=(x0,   0.5, cz), scale=(6,   1,   ln), color=fc, collider='box')
    Entity(model='cube', position=(x0,   8.5, cz), scale=(6,   0.5, ln), color=wc, collider='box')
    Entity(model='cube', position=(x0-3, 4,   cz), scale=(0.5, 8,   ln), color=wc, collider='box')
    Entity(model='cube', position=(x0+3, 4,   cz), scale=(0.5, 8,   ln), color=wc, collider='box')

def make_room(cx, cz, wc=color.dark_gray, fc=color.gray, doors=None):
    doors = doors or set()
    Entity(model='cube', position=(cx, 0.5, cz), scale=(20, 1,   20), color=fc, collider='box')
    Entity(model='cube', position=(cx, 8.5, cz), scale=(20, 0.5, 20), color=wc, collider='box')
    if 'south' in doors: _wall_door_h(cx, cz - 10, wc)
    else: Entity(model='cube', position=(cx, 4, cz - 10), scale=(20, 8, 0.5), color=wc, collider='box')
    if 'north' in doors: _wall_door_h(cx, cz + 10, wc)
    else: Entity(model='cube', position=(cx, 4, cz + 10), scale=(20, 8, 0.5), color=wc, collider='box')
    if 'west' in doors:  _wall_door_v(cx - 10, cz, wc)
    else: Entity(model='cube', position=(cx - 10, 4, cz), scale=(0.5, 8, 20), color=wc, collider='box')
    if 'east' in doors:  _wall_door_v(cx + 10, cz, wc)
    else: Entity(model='cube', position=(cx + 10, 4, cz), scale=(0.5, 8, 20), color=wc, collider='box')

def make_box(pos, scale, c):
    Entity(model='cube', position=pos, scale=scale, color=c, collider='box')

def deco(pos, scale, c):
    Entity(model='cube', position=pos, scale=scale, color=c)

# =============================================================
#  맵 배치
# =============================================================
Entity(model='cube', position=(0, 0.5, 0),  scale=(30, 1,   30), color=color.rgb(0.55, 0.55, 0.6), collider='box')
Entity(model='cube', position=(0, 8.5, 0),  scale=(30, 0.5, 30), color=color.dark_gray, collider='box')
for sx, sz in [(15, 9), (15, -9), (-15, 9), (-15, -9)]:
    Entity(model='cube', position=(sx, 4, sz), scale=(1, 8, 12), color=color.dark_gray, collider='box')
for sx, sz in [(9, 15), (-9, 15), (9, -15), (-9, -15)]:
    Entity(model='cube', position=(sx, 4, sz), scale=(12, 8, 1), color=color.dark_gray, collider='box')

# 복도
make_corridor_h(15,  90,  0)
make_corridor_h(-90, -15, 0)
make_corridor_v(15,  90,  0)
make_corridor_v(-90, -15, 0)
make_corridor_h(110, 190, 0)

# 방
make_room( 100,   0, color.rgb(0.25, 0.28, 0.3),  color.rgb(0.72, 0.75, 0.72), {'west', 'east'})
make_room(-100,   0, color.rgb(0.3,  0.28, 0.22), color.rgb(0.82, 0.78, 0.68), {'east'})
make_room(   0, 100, color.rgb(0.2,  0.22, 0.25), color.rgb(0.35, 0.38, 0.4),  {'south'})
make_room(   0,-100, color.rgb(0.3,  0.32, 0.3),  color.rgb(0.5,  0.52, 0.5),  {'north'})
make_room( 200,   0, color.rgb(0.1,  0.1,  0.12), color.rgb(0.18, 0.18, 0.2),  {'west'})

# 복도 입구 잠금문
_DOOR_COLOR = color.rgb(0.28, 0.16, 0.07)
Entity(model='cube', position=( 15, 4,  0), scale=(0.8, 8, 6),   color=_DOOR_COLOR, collider='box')
Entity(model='cube', position=(-15, 4,  0), scale=(0.8, 8, 6),   color=_DOOR_COLOR, collider='box')
Entity(model='cube', position=(  0, 4, 15), scale=(6,   8, 0.8), color=_DOOR_COLOR, collider='box')
Entity(model='cube', position=(  0, 4,-15), scale=(6,   8, 0.8), color=_DOOR_COLOR, collider='box')

for pos, txt in [((15, 8.2, 0), '[잠김]'), ((-15, 8.2, 0), '[잠김]'),
                 ((0, 8.2, 15), '[잠김]'), ((0, 8.2, -15), '[잠김]')]:
    Text(text=txt, position=pos, scale=7, color=color.rgb(0.9, 0.6, 0.1), billboard=True)

# 방 표지판
for pos, txt, c in [
    ((  0, 8,   0), "[ 중앙 홀 ]",    color.white),
    ((100, 9,   0), "[ 실험실 ]",     color.yellow),
    ((-100, 9,  0), "[ 4층 자료실 ]", color.cyan),
    ((  0, 9, 100), "[ 약품창고 ]",   color.orange),
    ((  0, 9,-100), "[ 옥상 ]",       color.lime),
    ((200, 9,   0), "[ 서버실 ]",     color.magenta),
]:
    Text(text=txt, position=pos, scale=12, color=c, billboard=True)

# =============================================================
#  중앙 홀 인테리어
# =============================================================
make_box((7, 2, -12),    (10, 3, 2),  color.rgb(0.6, 0.6, 0.65))
make_box((11.5, 2.5, -9),(2, 4, 4),   color.rgb(0.6, 0.6, 0.65))
deco((7, 3.6, -12),      (9.5, 0.2, 1.8), color.rgb(0.85, 0.85, 0.9))
deco((6, 3.8, -11.5),    (2, 1.5, 0.1),   color.black)
deco((6, 3.8, -11.4),    (1.8, 1.3, 0.05),color.rgb(0, 0.05, 0.2))
for i in range(4):
    x = -11 + i * 3.5
    make_box((x, 1.5, -10), (2.5, 1, 2),   color.rgb(0.6, 0.3, 0.1))
    deco((x, 2.5, -11),     (2.5, 2, 0.3), color.rgb(0.5, 0.25, 0.08))
make_box((0, 5, -14.6),  (10, 5, 0.5), color.rgb(0.4, 0.25, 0.1))
deco((0, 5, -14.3),      (9, 4.2, 0.2),color.rgb(0.9, 0.85, 0.7))
for sx in (-12, 12):
    make_box((sx, 1.5, 12), (1.2, 1, 1.2),  color.rgb(0.35, 0.2, 0.05))
    deco((sx, 2.5, 12),     (0.8, 2.5, 0.8),color.rgb(0.1, 0.5, 0.1))
for x in (-8, 0, 8):
    for z in (-5, 0, 5):
        deco((x, 8.2, z), (4, 0.15, 0.4), color.white)
deco((0, 1.06, 0),   (12, 0.05, 12), color.rgb(0.4, 0.35, 0.6))
make_box((-12, 2, -12),  (3, 3, 3),   color.rgb(0.5, 0.5, 0.55))
deco((-12, 3, -10.5),    (2.5, 1.5, 0.1), color.rgb(0.6, 0.75, 0.8))

# =============================================================
#  실험실 인테리어 (cx=100)
# =============================================================
make_box((100, 3, 8.5),   (18, 1, 2),    color.rgb(0.88, 0.9, 0.92))
deco((100, 1.5, 8.5),     (18, 0.15, 1.8),color.rgb(0.7, 0.72, 0.75))
make_box((92, 1.7, 8.5),  (0.3, 3.5, 2), color.rgb(0.6, 0.6, 0.65))
make_box((108, 1.7, 8.5), (0.3, 3.5, 2), color.rgb(0.6, 0.6, 0.65))
make_box((100, 6.5, 9.3), (18, 0.2, 0.5),color.rgb(0.55, 0.55, 0.6))
for i in range(8):
    x = 92.5 + i * 2.2
    deco((x, 7.0, 9.3), (0.3, 0.7, 0.3),  color.rgb(0.5, 0.85, 0.5))
    deco((x, 7.4, 9.3), (0.25, 0.2, 0.25),color.rgb(0.3, 0.6, 0.3))
make_box((108, 3, 7),     (3, 1, 3.5),   color.white)
deco((108, 3.1, 7),       (1.8, 0.35, 1.8),color.rgb(0.7, 0.82, 0.88))
make_box((103, 3.2, -2),  (10, 1, 2.5),  color.rgb(0.88, 0.9, 0.92))
make_box((98, 3.2, 2),    (8, 1, 2),     color.rgb(0.88, 0.9, 0.92))
make_box((103, 1.7, -2),  (0.3, 3.8, 2.5),color.rgb(0.6, 0.6, 0.65))
make_box((98, 1.7, 2),    (0.3, 3.8, 2), color.rgb(0.6, 0.6, 0.65))
deco((97, 3.7, 2),        (2, 1.5, 0.15),color.black)
deco((97, 3.7, 1.93),     (1.8, 1.3, 0.05),color.rgb(0, 0.05, 0.2))
make_box((100, 3.2, -1),  (8, 1, 3.5),   color.rgb(0.92, 0.92, 0.95))
make_box((96, 1.7, -1),   (0.3, 3.8, 3.5),color.rgb(0.6, 0.6, 0.65))
make_box((104, 1.7, -1),  (0.3, 3.8, 3.5),color.rgb(0.6, 0.6, 0.65))
deco((99.5, 3.9, -1),     (0.7, 1.3, 0.6),color.rgb(0.15, 0.15, 0.15))
deco((99.5, 5.2, -0.7),   (0.4, 0.4, 0.7),color.rgb(0.1, 0.1, 0.1))
make_box((92.5, 4, -6),   (4, 3, 3.5),   color.rgb(0.75, 0.78, 0.82))
deco((92.5, 4.5, -5),     (3.5, 2, 0.15),color.rgb(0.6, 0.75, 0.9))
for sx, sz in [(101, 3.5), (99, -5), (105, 2)]:
    make_box((sx, 1.8, sz), (1, 1.2, 1), color.rgb(0.25, 0.25, 0.45))
make_box((91.5, 3, 4),    (1, 5, 4.5),   color.rgb(0.55, 0.58, 0.62))
make_box((109, 4, -8),    (0.5, 4, 1),   color.rgb(0.8, 0.8, 0.85))
deco((109, 6.2, -8),      (1.5, 0.3, 1.5),color.rgb(0.7, 0.75, 0.8))
for x in (93, 100, 107):
    for z in (0, -5, 5):
        deco((x, 8.2, z), (5, 0.15, 0.4), color.white)

# =============================================================
#  자료실 인테리어 (cx=-100)
# =============================================================
make_box((-100, 4.5,  9.2), (18, 8, 1), color.rgb(0.45, 0.3, 0.12))
make_box((-100, 4.5, -9.2), (18, 8, 1), color.rgb(0.45, 0.3, 0.12))
for sy in (2, 3.5, 5, 6.5):
    deco((-100, sy,  9.0), (17, 0.15, 0.7), color.rgb(0.35, 0.22, 0.08))
    deco((-100, sy, -9.0), (17, 0.15, 0.7), color.rgb(0.35, 0.22, 0.08))
for i in range(9):
    x = -108 + i * 2.0
    for sy in (2.6, 4.1, 5.6):
        deco((x, sy,  9.0), (0.35 + i % 2 * 0.1, 1.0, 0.5), color.rgb(0.15 + i * 0.06, 0.05 + i * 0.02, 0.5 + i * 0.03))
        deco((x, sy, -9.0), (0.35, 0.9, 0.5),                color.rgb(0.5, 0.1 + i * 0.04, 0.1))
for dx, dz in [(-104, -2.5), (-100, -2.5), (-96, -2.5), (-104, 2.5), (-100, 2.5), (-96, 2.5)]:
    make_box((dx, 2.6, dz),    (3.5, 1, 2.5),   color.rgb(0.65, 0.5, 0.28))
    make_box((dx, 1.7, dz),    (0.2, 3, 2.5),   color.rgb(0.5, 0.4, 0.22))
    deco((dx, 3.7, dz - 0.8),  (2.5, 1.8, 0.1), color.black)
    deco((dx, 3.7, dz - 0.75), (2.3, 1.6, 0.05),color.rgb(0, 0.05, 0.18))
    deco((dx, 3.15, dz + 0.2), (2.0, 0.1, 0.7), color.rgb(0.28, 0.28, 0.28))
    make_box((dx, 1.5, dz + 1.9),(2.2, 1, 2),   color.rgb(0.2, 0.38, 0.6))
    deco((dx, 2.5, dz + 2.8),  (2.2, 2, 0.2),   color.rgb(0.15, 0.3, 0.5))
for z in (-6, 0, 6):
    make_box((-109, 3, z), (1, 5.5, 3.5), color.rgb(0.55, 0.58, 0.6))
make_box((-109, 3, -8.5), (2.5, 2, 2.5), color.rgb(0.7, 0.7, 0.72))
for x in (-107, -100, -93):
    for z in (-4, 0, 4):
        deco((x, 8.2, z), (5, 0.15, 0.5), color.white)

# =============================================================
#  약품창고 인테리어 (cz=100)
# =============================================================
for sz in (93, 98, 103, 108):
    make_box(( 8.5, 4, sz), (1.2, 7.5, 3.5), color.rgb(0.38, 0.4, 0.43))
    make_box((-8.5, 4, sz), (1.2, 7.5, 3.5), color.rgb(0.38, 0.4, 0.43))
    for sy in (1.8, 3.5, 5.2, 6.8):
        deco(( 8.2, sy, sz), (0.8, 0.18, 3.2), color.rgb(0.48, 0.5, 0.53))
        deco((-8.2, sy, sz), (0.8, 0.18, 3.2), color.rgb(0.48, 0.5, 0.53))
        for oz in (-1, 0, 1):
            deco(( 8.2, sy + 0.5, sz + oz), (0.55, 0.75, 0.5),
                 color.rgb(0.7, 0.2, 0.1) if oz == -1 else color.rgb(0.2, 0.5, 0.8))
make_box((5, 4.3, 108.2),  (3.5, 7.5, 2),   color.rgb(0.28, 0.33, 0.38))
deco((5, 4.3, 107.3),      (3.2, 7.2, 0.2), color.rgb(0.22, 0.27, 0.32))
deco((5.8, 4.3, 107.2),    (0.15, 0.5, 0.15),color.yellow)
for bx, bz in [(-3, 93), (3, 93), (0, 96), (-4, 99)]:
    make_box((bx, 2.2, bz), (2.2, 3.5, 2.2), color.rgb(0.28, 0.28, 0.28))
    deco((bx, 4.1, bz),     (2.0, 0.25, 2.0),color.rgb(0.38, 0.38, 0.38))
for z in (95, 100, 105):
    deco((0, 1.08, z), (18, 0.05, 0.3), color.yellow)
for z in (93, 100, 107):
    deco((0, 8.2, z), (5, 0.25, 0.5), color.rgb(0.95, 0.9, 0.7))
make_box((-4, 1.3, 92), (3.5, 0.4, 2.5), color.rgb(0.45, 0.3, 0.1))

# =============================================================
#  옥상 인테리어 (cz=-100)
# =============================================================
deco((0, 1.06, -100), (19, 0.06, 19), color.rgb(0.42, 0.43, 0.42))
for ox, oz in [(-6, -94), (6, -94), (-6, -106), (6, -106)]:
    make_box((ox, 2.2, oz), (3.5, 2.8, 2.2), color.rgb(0.78, 0.8, 0.82))
    deco((ox, 2.5, oz),     (3.2, 1.5, 0.3), color.rgb(0.5, 0.55, 0.6))
make_box((0, 4, -100),     (5.5, 6.5, 5.5), color.rgb(0.38, 0.4, 0.45))
deco((0, 7.4, -100),       (5.2, 0.5, 5.2), color.rgb(0.3, 0.32, 0.37))
make_box((8, 4.5, -108),   (0.4, 9, 0.4),   color.rgb(0.25, 0.25, 0.28))
deco((8, 8.5, -108),       (2.0, 0.3, 0.3), color.rgb(0.2, 0.2, 0.22))
deco((7.2, 8.2, -108),     (0.9, 0.6, 0.5), color.rgb(0.12, 0.12, 0.12))
make_box((5, 4.5, -109.2), (1.8, 3.5, 0.6), color.rgb(0.25, 0.28, 0.3))
deco((5, 4.5, -108.8),     (1.5, 3.2, 0.2), color.rgb(0.2, 0.22, 0.25))
deco((5.5, 4.2, -108.6),   (0.15, 0.5, 0.15),color.rgb(0.8, 0.2, 0.1))
for vx, vz in [(-6, -96), (6, -96), (-6, -104)]:
    make_box((vx, 2.5, vz), (2, 4, 2), color.rgb(0.48, 0.5, 0.52))
make_box((-7, 1.5, -104),  (0.3, 2.5, 0.3), color.rgb(0.5, 0.5, 0.52))
deco((-7, 2.8, -104),      (2.5, 1.8, 0.2), color.rgb(0.7, 0.72, 0.75))
make_box((0, 1.6, -91),    (3, 0.4, 2.5),   color.rgb(0.35, 0.37, 0.4))

# =============================================================
#  서버실 인테리어 (cx=200)
# =============================================================
for rx, rz in [(196, 6), (196, 2), (196, -2), (196, -6),
               (204, 6), (204, 2), (204, -2), (204, -6)]:
    make_box((rx, 4, rz), (2.2, 7.5, 1.8), color.rgb(0.07, 0.07, 0.09))
    side = 0.95 if rx < 200 else -0.95
    for ly in range(7):
        lc = color.lime if ly % 3 != 2 else color.rgb(1.0, 0.5, 0)
        deco((rx + side, ly + 0.8, rz), (0.12, 0.12, 0.8), lc)
    deco((rx, 4, rz - 0.88), (1.8, 6.5, 0.06), color.rgb(0.12, 0.12, 0.16))
make_box((200, 4.5, -3.5), (3.5, 4, 1),   color.rgb(0.1, 0.1, 0.13))
deco((200, 4.5, -3.0),     (3.2, 3.6, 0.2),color.rgb(0.06, 0.06, 0.08))
make_box((200, 2.2, 8.5),  (5, 3.5, 3),   color.rgb(0.12, 0.12, 0.18))
deco((200, 7.6, 0),        (18, 0.2, 1.8), color.rgb(0.28, 0.28, 0.32))
deco((200, 7.9, 4),        (18, 0.7, 2),   color.rgb(0.32, 0.32, 0.36))
deco((200, 7.9, -4),       (18, 0.7, 2),   color.rgb(0.32, 0.32, 0.36))
make_box((191.5, 3.5, 0),  (0.5, 5, 2.5), color.rgb(0.18, 0.18, 0.22))
deco((191.2, 4, 0),        (0.2, 1.2, 0.8),color.rgb(0, 0.6, 0))
for x in (193, 197, 200, 203, 207):
    deco((x, 8.1, 0), (3, 0.15, 0.4), color.rgb(0.8, 0.9, 1.0))

# =============================================================
#  단서 오브젝트
# =============================================================
clue_entities = {}
for key, (pos, scl, c) in {
    'coffee_cup':      ((103.5, 3.9, -2),   (0.4, 0.3, 0.4), color.white),
    'card_log':        (( 97.5, 2.9,  2),   (0.5, 0.4, 0.1), color.cyan),
    'pc_log':          ((-104,  3.8, -2.5), (1.5, 1.0, 0.1), color.blue),
    'circuit_breaker': ((   5,  4,  -107),  (0.8, 1.5, 0.3), color.rgb(0.8, 0.2, 0.1)),
    'key_mark':        ((   5,  4.5,  107), (0.8, 1.0, 0.3), color.rgb(0.9, 0.8, 0.1)),
    'badge':           ((  -1.5,1.65,  95), (0.6, 0.3, 0.1), color.white),
    'remote_log':      (( 200,  4.0,  -3),  (1.5, 1.0, 0.1), color.rgb(0.1, 0.9, 0.3)),
    'burned_glove':    ((   3,  1.5,  97),  (0.5, 0.2, 0.6), color.rgb(0.5, 0.3, 0.1)),
}.items():
    ent = Entity(model='cube', position=pos, scale=scl, color=c, collider='box')
    clue_entities[key] = ent
    Text(text=f"[ {CLUES[key]['name']} ]",
         position=(pos[0], pos[1] + 1, pos[2]),
         scale=5, color=color.yellow, billboard=True)

fake_clue_entities = {}
for fkey, (pos, scl, c) in {
    'receipt':       ((105,  3.7,  8.2), (0.5, 0.1, 0.3), color.rgb(0.9,  0.85, 0.7)),
    'torn_memo':     (( 94,  3.7,  8.0), (0.4, 0.1, 0.3), color.rgb(0.9,  0.9,  0.8)),
    'lunchbox':      ((-96,  3.2,  2.5), (1.0, 0.5, 0.8), color.rgb(0.7,  0.5,  0.3)),
    'old_inventory': ((  -5, 2.0, 98.0), (0.8, 0.5, 0.4), color.rgb(0.8,  0.75, 0.6)),
    'cigarette_box': ((  -6, 1.8,-95.0), (0.5, 0.2, 0.3), color.rgb(0.9,  0.9,  0.85)),
    'old_log':       (( 203, 1.7,  6.0), (1.2, 0.4, 0.8), color.rgb(0.7,  0.65, 0.5)),
}.items():
    ent = Entity(model='cube', position=pos, scale=scl, color=c, collider='box')
    fake_clue_entities[fkey] = ent
    Text(text=f"[ {FAKE_CLUES[fkey]['name']} ]",
         position=(pos[0], pos[1] + 0.8, pos[2]),
         scale=5, color=color.rgb(0.7, 0.7, 0.4), billboard=True)

# =============================================================
#  NPC (중앙 홀)
# =============================================================
npc_data_map = {
    '정다은': {
        'entity': None, 'pos': (5, 1, 5), 'color': color.blue,
        'greeting': '정다은: 사건 당일 저는 4층 자료실에서 논문 작업 중이었어요.\n밤늦게까지 있었고, 실험실 쪽은 가지도 않았어요.',
        'alibi_title': '[ 정다은 알리바이 ]',
        'alibi': [
            ('19:50', '자료실 PC 로그인 확인됨'),
            ('20:00', '자료실 체류 — 동료 목격'),
            ('21:30', 'PC 로그오프 후 퇴근'),
            ('??:??', '실험실 이동 흔적 없음'),
        ],
        'clue_response': '정다은: 저는 자료실 밖에 나간 적 없어요. 제가 뭘 알겠어요.',
        'clue_reactions': {
            'coffee_cup': '정다은: 최민호 씨가 그 브랜드 커피 즐겨 마셔요.\n매일 아침 편의점에서 사 오더라고요.',
            'card_log': '정다은: 21시 가까이 재진입 기록이요?\n저는 퇴근도 늦게 했는데, 그 시간에 아무도 못 봤어요.',
            'pc_log': '정다은: 독극물 검색이요? 누구 계정으로요?\n그 자료실 PC는 최민호 씨도 가끔 썼어요.',
            'remote_log': '정다은: 최민호 씨 해고한다고요? 몰랐어요.\n근데 최민호 씨가 얼마 전에 엄청 화났던 적 있어요.',
        },
        'lie_clues': {},
        'reject_lines': [
            '정다은: 저는 정말 모르는 일이에요.',
            '정다은: 더 말씀드릴 게 없어요.',
            '정다은: (고개를 젓는다)',
        ],
    },
    '박지훈': {
        'entity': None, 'pos': (-5, 1, 5), 'color': color.green,
        'greeting': '박지훈: 나는 그날 실험실에서 실험하다가 옥상에서 담배 피우고 들어왔어.\n별거 없어.',
        'alibi_title': '[ 박지훈 알리바이 ]',
        'alibi': [
            ('20:00', '실험실 입실, 실험 가동'),
            ('20:30', '옥상 이동 — 흡연'),
            ('20:45', '실험실 복귀 확인'),
            ('21:00', '실험 종료 후 퇴근'),
        ],
        'clue_response': '박지훈: 그 단서? 나랑은 상관없어.',
        'clue_reactions': {
            'cigarette_box': '박지훈: 응, 내 담배 케이스 맞아.\n그날 옥상에서 피웠거든.',
            'circuit_breaker': '박지훈: 분전반은 나는 건드리지도 않았어.\n최민호가 거기 올라간다는 말 들은 적 있어.',
            'card_log': '박지훈: 21시 재진입 기록이요?\n나는 실험실에서 안 나갔어. 다른 사람이겠지.',
            'coffee_cup': '박지훈: 최민호가 그 브랜드 커피 맨날 마셨잖아.\n실험실에서 마시는 것도 봤어.',
        },
        'lie_clues': {},
        'reject_lines': [
            '박지훈: 나는 할 말 다 했어.',
            '박지훈: (팔짱을 끼며) 더 이상 대답 안 해.',
            '박지훈: (고개를 돌린다)',
        ],
    },
    '최민호': {
        'entity': None, 'pos': (5, 1, -5), 'color': color.orange,
        'greeting': '최민호: 저는 20시에 퇴근했어요! 편의점 영수증도 있다고요.\n절대 아무것도 안 했어요.',
        'alibi_title': '[ 최민호 알리바이 ]',
        'alibi': [
            ('19:45', '실험 보조 완료'),
            ('20:00', '연구소 퇴근 주장'),
            ('20:44', '편의점 영수증 (시간 조작 가능성 ⚠)'),
            ('20:55', '보안카드 재진입 기록 발생 ⚠'),
            ('??:??', '이후 행적 불명 ⚠'),
        ],
        'clue_response': '최민호: (손을 흔들며) 그건 저랑 관계없어요!',
        'clue_reactions': {
            'coffee_cup': '최민호: (당황하며) 그 커피 컵이요? 저... 저는 그날\n편의점 가서 마셨어요. 실험실은 안 갔다고요.',
            'card_log': '최민호: (눈이 흔들리며) 재진입 기록이요?\n그건... 카드 오류일 수 있어요. 자주 그러거든요.',
            'pc_log': '최민호: 독극물 검색이요?! 저는 그런 거\n찾아본 적 없어요. 누가 제 계정으로 한 거예요!',
            'circuit_breaker': '최민호: 분전반 손잡이에 제 지문이요?\n그건... 전에 청소하다가 만진 거예요.',
            'key_mark': '최민호: 복사 열쇠라고요? 저는 열쇠를\n복사한 적 없어요. 오해예요!',
            'badge': '최민호: (얼굴이 창백해지며) 그 사원증이\n왜 거기 있는지 저도... 몰라요.',
            'remote_log': '최민호: (목소리가 떨리며) 그건 그냥 행정 절차예요.\n해고라고요? 그건 몰랐어요.',
            'burned_glove': '최민호: (굳어지며) ...그 장갑은 제 거 아니에요.',
        },
        'lie_clues': {
            'card_log': '최민호: (손이 떨리며) 아니요, 저는 분명히 나갔어요!\n그 기록은... 기록은 잘못된 거예요!',
            'coffee_cup': '최민호: (당황하며 말을 잃고) ...그 컵은——\n아니에요, 저는 실험실에 간 적 없다고요!',
            'badge': '최민호: (후퇴하며) 그건... 예전에 떨어뜨린 거예요.\n범행이랑은 관계없어요!',
            'burned_glove': '최민호: (시선을 피하며) 저는 그 장갑 모릅니다!\n왜 제 DNA가 나온 거죠?!',
        },
        'reject_lines': [
            '최민호: 저는 정말 아무것도 안 했어요. 더 이상 할 말 없어요.',
            '최민호: (자리를 피하려 한다) 변호사 부를게요.',
            '최민호: (묵묵히 고개를 돌린다)',
        ],
    },
    '한서윤': {
        'entity': None, 'pos': (-5, 1, -5), 'color': color.pink,
        'greeting': '한서윤: 저는 그날 서버실에서 야간 점검 중이었어요.\n로그도 남아 있고, 동료도 봤어요. 저는 관계없어요.',
        'alibi_title': '[ 한서윤 알리바이 ]',
        'alibi': [
            ('20:00', '서버실 점검 시작 (로그 확인됨)'),
            ('20:30', '점검 중간 보고서 작성'),
            ('21:00', '점검 종료 기록'),
            ('??:??', '약품창고 접근 흔적 없음'),
        ],
        'clue_response': '한서윤: 저는 그날 서버실 밖에 나간 적 없어요.',
        'clue_reactions': {
            'key_mark': '한서윤: 복사 열쇠요? 저는 원본 열쇠만 갖고 있어요.\n누군가 몰래 복사했다면 큰일이네요.',
            'circuit_breaker': '한서윤: 지문이 최민호 씨 거요? 그건 심각한데요.\n분전반은 보조원이 접근 못하는 구역인데...',
            'badge': '한서윤: 사원증이 약품창고에 있었다고요?\n최민호 씨가 왜 거기 있었던 거죠?',
            'card_log': '한서윤: 20시 55분 재진입이요? 그건 최민호 씨 카드죠?\n그 시간에 거기 있을 이유가 없는데.',
            'remote_log': '한서윤: 최민호 씨 해고 결정이요? 그거라면...\n동기가 되겠네요.',
        },
        'lie_clues': {},
        'reject_lines': [
            '한서윤: 저는 정말 모르는 일이에요.',
            '한서윤: 더 이상 드릴 말씀이 없네요.',
            '한서윤: (단호하게) 저는 결백해요.',
        ],
    },
}

for name, data in npc_data_map.items():
    ent = Entity(model='cube', color=data['color'], scale=(1, 2, 1),
                 position=data['pos'], collider='box')
    data['entity'] = ent
    Text(text=name,
         position=(data['pos'][0], data['pos'][1] + 1.5, data['pos'][2]),
         scale=9, color=data['color'], billboard=True)

# =============================================================
#  플레이어
# =============================================================
player = FirstPersonController()
player.position = (0, 2, -10)
player.speed = 10
player.enabled = False
mouse.locked = False
mouse.visible = True

# =============================================================
#  상시 HUD (게임 플레이 중 항상 표시)
# =============================================================
# z=-0.1 로 설정해 UI 팝업보다 뒤에 위치하되 3D 씬보다는 앞에 오도록 함
hint_label   = Text(parent=camera.ui, text='', position=(0, 0.46),
                    origin=(0, 0), scale=1.0, color=color.yellow, z=-0.1)
status_label = Text(parent=camera.ui, text='', position=(0.55, 0.46),
                    scale=1.0, color=color.cyan, z=-0.1)
timer_label  = Text(parent=camera.ui, text='', position=(0, 0.46),
                    origin=(0, 0), scale=1.1, color=color.white, z=-0.1)

# 대화 창 (하단 고정)
dlg_bg   = Entity(parent=camera.ui, model='quad', scale=(0.88, 0.18),
                  position=(0, -0.4), color=color.black66, z=-0.5, enabled=False)
dlg_text = Text(parent=camera.ui, text='', position=(-0.42, -0.33),
                scale=1.05, color=color.white, z=-0.5, enabled=False)

# UI 그룹 리스트
start_ui      = []
briefing_ui   = []
tab_ui        = []
explore_ui    = []
choice_btns   = []
alibi_ui      = []
accuse_ui     = []
clue_popup_ui     = []
controls_ui       = []
combo_popup_ui    = []
suspicion_ui      = []

# =============================================================
#  유틸리티
# =============================================================
def clear_ui(lst):
    for e in lst:
        try:
            destroy(e)
        except Exception:
            pass
    lst.clear()

def show_hint(msg, dur=3):
    hint_label.text = msg
    invoke(lambda: setattr(hint_label, 'text', ''), delay=dur)

def set_dlg(msg):
    dlg_bg.enabled = True
    dlg_text.enabled = True
    dlg_text.text = msg

def hide_dlg():
    dlg_bg.enabled = False
    dlg_text.enabled = False
    dlg_text.text = ''

def update_status():
    status_label.text = f'단서 {len(collected_clues)}/{len(CLUES)}'

# =============================================================
#  시작 화면
# =============================================================
def show_start_screen():
    global game_phase
    game_phase = 'start'
    player.enabled = False
    mouse.locked = False
    mouse.visible = True
    clear_ui(start_ui)
    clear_ui(controls_ui)

    bg    = Entity(parent=camera.ui, model='quad', scale=(3, 2),
                   color=color.rgba(0, 0, 0, 0.98), z=-1)
    title = Text(parent=camera.ui, text='사건 보고서',
                 position=(0, 0.33), origin=(0, 0),
                 scale=4.2, color=color.rgb(0.88, 0.08, 0.08), z=-1)
    sub   = Text(parent=camera.ui, text='Crime Scene Investigation',
                 position=(0, 0.22), origin=(0, 0),
                 scale=1.6, color=color.rgb(0.45, 0.45, 0.5), z=-1)
    sep   = Entity(parent=camera.ui, model='quad', scale=(0.65, 0.004),
                   position=(0, 0.17), color=color.rgb(0.5, 0.05, 0.05), z=-1)
    intro = Text(parent=camera.ui, text='',
                 position=(0, 0.06), origin=(0, 0),
                 scale=1.35, color=color.rgb(0.8, 0.8, 0.8), z=-1)

    lines = [
        '2026년 5월 14일,  밤 10시.',
        '한 화학 연구원이 연구실에서 숨진 채 발견되었다.',
        '현장에는 강한 몸싸움의 흔적이 남아 있다.',
        '',
        '당신은 사건을 담당하게 된 형사이다.',
    ]
    acc = []
    t = 0.8
    for line in lines:
        acc.append(line)
        snap = '\n'.join(acc)
        def setter(txt=snap):
            intro.text = txt
        invoke(setter, delay=t)
        t += 1.3

    def show_btns():
        b1 = Button(parent=camera.ui, text='  게임 시작  ',
                    scale=(0.26, 0.072), position=(0, -0.27),
                    color=color.rgb(0.65, 0.08, 0.08), z=-1)
        b2 = Button(parent=camera.ui, text='  조작법 확인  ',
                    scale=(0.26, 0.072), position=(0, -0.37),
                    color=color.rgb(0.25, 0.25, 0.3), z=-1)
        b3 = Button(parent=camera.ui, text='  종  료  ',
                    scale=(0.22, 0.065), position=(0, -0.46),
                    color=color.rgb(0.15, 0.15, 0.18), z=-1)
        b1.on_click = show_briefing
        b2.on_click = show_controls_screen
        b3.on_click = application.quit
        start_ui.extend([b1, b2, b3])

    invoke(show_btns, delay=t + 0.4)
    start_ui.extend([bg, title, sub, sep, intro])


def show_controls_screen():
    """조작법 팝업 — 시작 화면 위에 독립 레이어로 표시"""
    clear_ui(controls_ui)

    # z=-2 로 시작 화면(z=-1)보다 앞에 렌더링
    bg  = Entity(parent=camera.ui, model='quad', scale=(0.72, 0.56),
                 color=color.rgba(0, 0, 0, 0.97), z=-2)
    ttl = Text(parent=camera.ui, text='[ 조작법 ]',
               position=(0, 0.22), origin=(0, 0),
               scale=2.0, color=color.yellow, z=-2)
    txt = Text(parent=camera.ui,
               text=(
                   'W / A / S / D   —  이동\n'
                   '마우스           —  시점 변경\n'
                   'F                —  단서 조사 / 상호작용\n'
                   'Tab              —  수사 메뉴 (방 이동 + 수첩)\n'
                   'ESC              —  메뉴 닫기'
               ),
               position=(-0.27, 0.10), scale=1.25,
               color=color.white, z=-2)
    btn = Button(parent=camera.ui, text='닫기',
                 scale=(0.18, 0.065), position=(0, -0.19), z=-2)

    def close_controls():
        clear_ui(controls_ui)

    btn.on_click = close_controls
    controls_ui.extend([bg, ttl, txt, btn])


# =============================================================
#  브리핑
# =============================================================
def show_briefing():
    global game_phase
    game_phase = 'briefing'
    clear_ui(start_ui)
    clear_ui(controls_ui)

    bg   = Entity(parent=camera.ui, model='quad', scale=(3, 2),
                  color=color.rgba(0, 0, 0, 0.97), z=-1)
    ttl  = Text(parent=camera.ui, text='━━  사건 브리핑  ━━',
                position=(0, 0.37), origin=(0, 0),
                scale=2.1, color=color.rgb(0.85, 0.7, 0.1), z=-1)
    info = Text(parent=camera.ui,
                text=(
                    '피해자:      이강현\n'
                    '직업:        수석 화학 연구원\n'
                    '사건 장소:   연구소 실험실\n'
                    '사건 시각:   2026-05-14  22:00\n'
                ),
                position=(-0.34, 0.22), scale=1.3, color=color.white, z=-1)
    div  = Entity(parent=camera.ui, model='quad', scale=(0.82, 0.004),
                  position=(0, 0.10), color=color.rgb(0.4, 0.4, 0.45), z=-1)
    sttl = Text(parent=camera.ui, text='[ 현재 확보된 용의자 ]',
                position=(-0.32, 0.07), scale=1.3, color=color.cyan, z=-1)
    sus  = Text(parent=camera.ui,
                text=(
                    '• 정다은  —  연구원 (피해자 동료)\n'
                    '• 박지훈  —  연구원 (피해자 동료)\n'
                    '• 최민호  —  연구 보조원\n'
                    '• 한서윤  —  관리팀장'
                ),
                position=(-0.32, -0.07), scale=1.25, color=color.light_gray, z=-1)
    note = Text(parent=camera.ui,
                text='※ 5개 현장을 모두 조사한 후 범인을 지목할 수 있습니다.\n   단 한 번의 기회이며, 틀리면 추리 실패로 게임이 종료됩니다.',
                position=(0, -0.27), origin=(0, 0),
                scale=0.88, color=color.rgb(0.8, 0.6, 0.2), z=-1)
    btn  = Button(parent=camera.ui, text='수사 시작  →',
                  scale=(0.28, 0.072), position=(0, -0.38),
                  color=color.rgb(0.6, 0.08, 0.08), z=-1)
    btn.on_click = start_investigation
    briefing_ui.extend([bg, ttl, info, div, sttl, sus, note, btn])


# =============================================================
#  수사 시작 (중앙 홀)
# =============================================================
def start_investigation():
    global game_phase
    game_phase = 'investigating'
    clear_ui(briefing_ui)
    player.position = (0, 2, -10)
    player.enabled = True
    mouse.locked = True
    mouse.visible = False
    update_status()
    show_hint('용의자들을 조사하거나 [Tab]으로 현장에 이동하세요.', dur=7)


# =============================================================
#  현장 이동
# =============================================================
def travel_to_room(name):
    global game_phase, selected_location, explore_timer, room_exiting
    if name in visited_rooms:
        show_hint(f'{name} — 이미 조사 완료된 장소입니다.')
        return
    game_phase = 'exploring'
    selected_location = name
    explore_timer = float(ROOM_TIMERS[name])
    room_exiting = False
    player.position = ROOM_SPAWN[name]
    player.enabled = True
    mouse.locked = True
    mouse.visible = False
    update_status()
    _show_explore_hud()
    show_hint(f'{name} 진입 — [F] 단서 조사  [Tab] 메뉴', dur=4)


def _show_explore_hud():
    clear_ui(explore_ui)
    lbl = Text(parent=camera.ui, text=f'[ {selected_location} ]',
               position=(-0.62, 0.46), scale=1.0,
               color=color.rgb(0.9, 0.7, 0.2), z=-0.1)
    explore_ui.append(lbl)


def end_exploration():
    global game_phase
    game_phase = 'investigating'
    visited_rooms.add(selected_location)
    clear_ui(explore_ui)
    timer_label.text = ''
    player.position = (0, 2, -10)
    player.enabled = True
    mouse.locked = True
    mouse.visible = False
    show_hint('탐색 완료. 수사를 계속하거나 [Tab]으로 다른 현장을 이동하세요.', dur=6)


def force_exit_room():
    global room_exiting
    room_exiting = False
    timer_label.color = color.white
    end_exploration()
    show_hint(f'{selected_location} — 탐색 시간이 종료되었습니다.', dur=4)


# =============================================================
#  Tab 수사 메뉴 (방 이동 + 수첩)
# =============================================================
def open_tab_menu():
    global notebook_open
    notebook_open = True
    player.enabled = False
    mouse.locked = False
    mouse.visible = True
    clear_ui(tab_ui)

    # 배경 및 타이틀
    bg   = Entity(parent=camera.ui, model='quad', scale=(0.96, 0.82),
                  position=(0, 0.04), color=color.black90, z=-1)
    ttl  = Text(parent=camera.ui, text='[ 수사 메뉴 ]',
                position=(0, 0.40), origin=(0, 0),
                scale=1.8, color=color.yellow, z=-1)
    divl = Entity(parent=camera.ui, model='quad', scale=(0.003, 0.72),
                  position=(0.01, 0.04), color=color.rgb(0.4, 0.4, 0.5), z=-1)
    tab_ui.extend([bg, ttl, divl])

    # 왼쪽: 현장 이동
    left_title = Text(parent=camera.ui, text='── 현장 이동 ──',
                      position=(-0.36, 0.32), scale=1.2, color=color.cyan, z=-1)
    tab_ui.append(left_title)

    for i, (rname, rtime) in enumerate(ROOM_TIMERS.items()):
        py = 0.22 - i * 0.115
        is_cur = (game_phase == 'exploring' and selected_location == rname)
        is_vis = rname in visited_rooms
        if is_cur:
            bc  = color.rgb(0.55, 0.45, 0.08)
            lbl = f'★ {rname}  [조사 중]'
            en  = False
        elif is_vis:
            bc  = color.rgb(0.2, 0.2, 0.22)
            lbl = f'✓ {rname}  [완료]'
            en  = False
        else:
            bc  = color.rgb(0.12, 0.35, 0.15)
            lbl = f'{rname}  ({rtime}초)'
            en  = True
        btn = Button(parent=camera.ui, text=lbl,
                     scale=(0.40, 0.068), position=(-0.24, py), color=bc, z=-1)
        if en and game_phase == 'investigating':
            def make_travel(n=rname):
                def handler():
                    close_tab_menu()
                    travel_to_room(n)
                return handler
            btn.on_click = make_travel()
        tab_ui.append(btn)

    if game_phase == 'exploring':
        exit_btn = Button(parent=camera.ui, text='탐색 종료 →',
                          scale=(0.40, 0.068), position=(-0.24, -0.28),
                          color=color.rgb(0.5, 0.1, 0.1), z=-1)
        exit_btn.on_click = lambda: (close_tab_menu(), end_exploration())
        tab_ui.append(exit_btn)

    # 오른쪽: 수첩
    right_title = Text(parent=camera.ui, text='── 형사 수첩 ──',
                       position=(0.26, 0.32), scale=1.2, color=color.orange, z=-1)
    clue_count  = Text(parent=camera.ui, text=f'수집: {len(collected_clues)}/{len(CLUES)}',
                       position=(0.26, 0.24), scale=1.0, color=color.cyan, z=-1)
    tab_ui.extend([right_title, clue_count])

    if not collected_clues:
        no_clue = Text(parent=camera.ui, text='단서 없음',
                       position=(0.12, 0.12), scale=1.0, color=color.gray, z=-1)
        tab_ui.append(no_clue)
    else:
        for i, cid in enumerate(collected_clues[:5]):
            c  = CLUES[cid]
            py = 0.16 - i * 0.10
            name_lbl = Text(parent=camera.ui, text=f'◆ {c["name"]}',
                            position=(0.12, py), scale=0.95, color=color.orange, z=-1)
            desc_lbl = Text(parent=camera.ui,
                            text=f'   {c["desc"].split(chr(10))[0]}',
                            position=(0.12, py - 0.035), scale=0.78,
                            color=color.light_gray, z=-1)
            tab_ui.extend([name_lbl, desc_lbl])

    all_rooms_done = len(visited_rooms) >= len(ROOM_TIMERS)
    if game_phase == 'investigating':
        if all_rooms_done:
            accuse_btn = Button(parent=camera.ui, text='▶ 범인 지목  [최후의 1번]',
                                scale=(0.38, 0.068), position=(0.27, -0.28),
                                color=color.red, z=-1)
            accuse_btn.on_click = lambda: (close_tab_menu(), open_accusation())
            tab_ui.append(accuse_btn)
        else:
            remaining_rooms = len(ROOM_TIMERS) - len(visited_rooms)
            lock_lbl = Text(parent=camera.ui,
                            text=f'▷ 범인 지목 잠김\n   현장 {remaining_rooms}곳 조사 후 해금',
                            position=(0.27, -0.28), scale=0.85, color=color.gray, z=-1)
            tab_ui.append(lock_lbl)

    close_btn = Button(parent=camera.ui, text='닫기  [Tab]',
                       scale=(0.22, 0.055), position=(0, -0.38), z=-1)
    close_btn.on_click = close_tab_menu
    tab_ui.append(close_btn)


def close_tab_menu():
    global notebook_open
    notebook_open = False
    clear_ui(tab_ui)
    if game_phase in ('exploring', 'investigating'):
        player.enabled = True
        mouse.locked = True
        mouse.visible = False


# =============================================================
#  단서 수집
# =============================================================
def collect_clue(clue_id):
    clue = CLUES[clue_id]
    if clue['collected']:
        show_hint(f'이미 수집: {clue["name"]}')
        return
    clue['collected'] = True
    collected_clues.append(clue_id)
    clue_entities[clue_id].color = color.gray
    update_status()
    _check_combos()
    open_clue_popup(clue_id)


def open_clue_popup(clue_id):
    global talking
    talking = True
    mouse.locked = False
    mouse.visible = True
    player.enabled = False
    clear_ui(clue_popup_ui)

    clue  = CLUES[clue_id]
    bg    = Entity(parent=camera.ui, model='quad', scale=(0.72, 0.42),
                   position=(0, 0.02), color=color.black90, z=-2)
    title = Text(parent=camera.ui,
                 text=f'★ 단서 발견!  {clue["name"]}',
                 position=(-0.31, 0.18), scale=1.3, color=color.yellow, z=-2)
    loc   = Text(parent=camera.ui,
                 text=f'발견 위치: {clue["location"]}',
                 position=(-0.31, 0.11), scale=1.0, color=color.cyan, z=-2)
    desc  = Text(parent=camera.ui,
                 text=clue['desc'],
                 position=(-0.31, 0.03), scale=0.95, color=color.white, z=-2)
    remaining = 3 - len(collected_clues)
    total_msg = '범인 지목 가능!' if len(collected_clues) >= 3 else f'단서 {remaining}개 더 필요'
    total = Text(parent=camera.ui,
                 text=f'[수첩 {len(collected_clues)}/{len(CLUES)}]  {total_msg}',
                 position=(-0.31, -0.10), scale=0.9,
                 color=color.lime if len(collected_clues) >= 3 else color.gray, z=-2)

    def close_popup():
        clear_ui(clue_popup_ui)
        end_dialogue()

    btn = Button(parent=camera.ui, text='확인 [F]',
                 scale=(0.18, 0.055), position=(0, -0.17), z=-2)
    btn.on_click = close_popup
    clue_popup_ui.extend([bg, title, loc, desc, total, btn])


def collect_fake_clue(fkey):
    if fkey in collected_fakes:
        show_hint('이미 확인한 물건입니다.')
        return
    collected_fakes.add(fkey)
    _check_combos()
    _open_fake_popup(fkey)


def _open_fake_popup(fkey):
    global talking
    talking = True
    mouse.locked = False
    mouse.visible = True
    player.enabled = False
    clear_ui(clue_popup_ui)

    clue = FAKE_CLUES[fkey]
    bg   = Entity(parent=camera.ui, model='quad', scale=(0.68, 0.34),
                  position=(0, 0.02), color=color.black90, z=-2)
    ttl  = Text(parent=camera.ui, text=f'◇ {clue["name"]}',
                position=(-0.28, 0.13), scale=1.25,
                color=color.rgb(0.7, 0.7, 0.7), z=-2)
    note = Text(parent=camera.ui, text='[ 사건과 무관한 물품 ]',
                position=(-0.28, 0.07), scale=1.0, color=color.gray, z=-2)
    desc = Text(parent=camera.ui, text=clue['desc'],
                position=(-0.28, -0.01), scale=0.95,
                color=color.light_gray, z=-2)

    def close_popup():
        clear_ui(clue_popup_ui)
        end_dialogue()

    btn = Button(parent=camera.ui, text='확인 [F]',
                 scale=(0.18, 0.055), position=(0, -0.13), z=-2)
    btn.on_click = close_popup
    clue_popup_ui.extend([bg, ttl, note, desc, btn])


# =============================================================
#  NPC 대화
# =============================================================
current_npc = ''


def start_npc_dialogue(name):
    global talking, current_npc
    talking = True
    current_npc = name
    mouse.locked = False
    mouse.visible = True
    player.enabled = False

    npc_talk_count[name] += 1
    count = npc_talk_count[name]

    if count >= 4:
        reject_list = npc_data_map[name]['reject_lines']
        idx = min(count - 4, len(reject_list) - 1)
        set_dlg(reject_list[idx])
        show_npc_choices(name)
    else:
        set_dlg(npc_data_map[name]['greeting'])
        show_npc_choices(name)


def show_npc_choices(name):
    clear_ui(choice_btns)
    has_clues = len(collected_clues) > 0
    susp = npc_suspicion[name]
    if susp == 0:
        susp_str, susp_c = '의심도: 없음', color.gray
    elif susp <= 2:
        susp_str, susp_c = f'의심도: ●{"●" * (susp-1)}{"○" * (3-susp)}  주목', color.yellow
    elif susp <= 4:
        susp_str, susp_c = f'의심도: ●●{"●" * (susp-2)}{"○" * (4-susp)}  의심', color.orange
    else:
        susp_str, susp_c = '의심도: ●●●●●  고도 의심', color.red

    # 버튼 및 의심도 — 대화창(y≈-0.33) 위에 배치
    susp_lbl = Text(parent=camera.ui, text=susp_str,
                    position=(0, -0.10), origin=(0, 0), scale=1.0, color=susp_c, z=-1)
    b1 = Button(parent=camera.ui, text='알리바이 묻기',
                scale=(0.26, 0.060), position=(-0.15, -0.19), z=-1)
    b2 = Button(parent=camera.ui, text='단서 제시하기',
                scale=(0.26, 0.060), position=(0.15, -0.19),
                color=color.orange if has_clues else color.gray, z=-1)
    b3 = Button(parent=camera.ui, text='대화 종료',
                scale=(0.17, 0.054), position=(0.43, -0.10), z=-1)
    b1.on_click = lambda: show_alibi(name)
    b2.on_click = (lambda: show_clue_choice(name, 0)) if has_clues else (lambda: show_hint('수집한 단서가 없습니다.'))
    b3.on_click = end_dialogue
    choice_btns.extend([susp_lbl, b1, b2, b3])

    # 단서 조합 압박 버튼 — 대화창 위에 배치
    for combo_key, combo_data in CLUE_COMBOS.items():
        if combo_data['npc'] == name and combo_key in unlocked_combos:
            bp = Button(parent=camera.ui, text='★ 단서 조합으로 압박하기',
                        scale=(0.36, 0.058), position=(0, -0.27),
                        color=color.rgb(0.7, 0.1, 0.5), z=-1)
            bp.on_click = lambda cd=combo_data, n=name: _do_combo_pressure(cd, n)
            choice_btns.append(bp)
            break


def show_alibi(name):
    clear_ui(alibi_ui)
    data = npc_data_map[name]
    rows = data['alibi']
    h = 0.07 * (len(rows) + 1) + 0.16
    bg  = Entity(parent=camera.ui, model='quad', scale=(0.62, h),
                 position=(0, 0.06), color=color.black66, z=-2)
    ttl = Text(parent=camera.ui, text=data['alibi_title'],
               position=(-0.27, 0.06 + h / 2 - 0.045),
               scale=1.25, color=color.yellow, z=-2)
    hd  = Text(parent=camera.ui, text='시간         행동',
               position=(-0.27, 0.06 + h / 2 - 0.09),
               scale=1.0, color=color.cyan, z=-2)
    alibi_ui.extend([bg, ttl, hd])

    sy = 0.06 + h / 2 - 0.09
    for i, (t, a) in enumerate(rows):
        suspicious = any(x in a for x in ['⚠', '불명', '잔류', '원격', '유일'])
        row_lbl = Text(parent=camera.ui,
                       text=f'{t:<7}  {a}',
                       position=(-0.27, sy - 0.07 * (i + 1)),
                       scale=0.92,
                       color=color.red if suspicious else color.white, z=-2)
        alibi_ui.append(row_lbl)

    cb = Button(parent=camera.ui, text='닫기',
                scale=(0.15, 0.052), position=(0, 0.06 - h / 2 + 0.032), z=-2)
    cb.on_click = lambda: (clear_ui(alibi_ui), show_npc_choices(name))
    alibi_ui.append(cb)


_CLUE_PAGE_SIZE = 4

def show_clue_choice(name, page=0):
    clear_ui(choice_btns)
    set_dlg(npc_data_map[name]['clue_response'])

    total  = len(collected_clues)
    start  = page * _CLUE_PAGE_SIZE
    end    = min(start + _CLUE_PAGE_SIZE, total)
    visible = collected_clues[start:end]
    pages  = max(1, (total + _CLUE_PAGE_SIZE - 1) // _CLUE_PAGE_SIZE)

    hdr = Text(parent=camera.ui,
               text=f'제시할 단서 선택  ({page+1}/{pages})',
               position=(0, 0.22), origin=(0, 0),
               scale=0.95, color=color.cyan, z=-1)
    choice_btns.append(hdr)

    # 단서 버튼 — y=0.16부터 아래로 (최대 y=-0.08 정도, 대화창 위)
    for i, cid in enumerate(visible):
        def make_handler(k, n):
            def handler():
                _present_clue_to_npc(n, k)
            return handler
        b = Button(parent=camera.ui, text=CLUES[cid]['name'],
                   scale=(0.52, 0.054),
                   position=(0, 0.16 - i * 0.064), z=-1)
        b.on_click = make_handler(cid, name)
        choice_btns.append(b)

    nav_y = 0.16 - len(visible) * 0.064 - 0.010

    # 이전 / 다음 페이지 버튼
    if pages > 1:
        if page > 0:
            pb = Button(parent=camera.ui, text='◀ 이전',
                        scale=(0.14, 0.050), position=(-0.10, nav_y), z=-1,
                        color=color.rgb(0.3, 0.3, 0.4))
            pb.on_click = lambda p=page: show_clue_choice(name, p - 1)
            choice_btns.append(pb)
        if end < total:
            nb = Button(parent=camera.ui, text='다음 ▶',
                        scale=(0.14, 0.050), position=(0.10, nav_y), z=-1,
                        color=color.rgb(0.3, 0.3, 0.4))
            nb.on_click = lambda p=page: show_clue_choice(name, p + 1)
            choice_btns.append(nb)
        nav_y -= 0.062

    back = Button(parent=camera.ui, text='← 뒤로',
                  scale=(0.18, 0.054), position=(0, nav_y), z=-1)
    back.on_click = lambda: show_npc_choices(name)
    choice_btns.append(back)


def _present_clue_to_npc(name, clue_id):
    data = npc_data_map[name]
    lie_clues = data.get('lie_clues', {})
    reactions = data.get('clue_reactions', {})
    key = (name, clue_id)
    first_time = key not in shown_clues

    if clue_id in lie_clues and key not in confirmed_lies:
        confirmed_lies.add(key)
        shown_clues.add(key)
        npc_suspicion[name] = min(npc_suspicion[name] + 2, 5)
        set_dlg(f'[ 모순 발견! ]\n{lie_clues[clue_id]}')
    elif clue_id in reactions:
        if first_time:
            shown_clues.add(key)
            npc_suspicion[name] = min(npc_suspicion[name] + 1, 5)
        set_dlg(reactions[clue_id])
    else:
        set_dlg(f'{name}: (단서를 보며 굳은 표정)\n  ...그 단서는 처음 보는군요.')

    show_npc_choices(name)


def _do_combo_pressure(combo_data, name):
    npc_suspicion[name] = min(npc_suspicion[name] + combo_data['suspicion_boost'], 5)
    set_dlg(combo_data['pressure_line'])
    show_npc_choices(name)


def _check_combos():
    for combo_key, combo_data in CLUE_COMBOS.items():
        if combo_key in unlocked_combos:
            continue
        fake_id, real_id = combo_key
        if fake_id in collected_fakes and real_id in collected_clues:
            unlocked_combos.add(combo_key)
            _show_combo_popup(combo_data['unlock_msg'])
            return


def _show_combo_popup(msg):
    global talking
    talking = True
    mouse.locked = False
    mouse.visible = True
    player.enabled = False
    clear_ui(combo_popup_ui)

    bg = Entity(parent=camera.ui, model='quad', scale=(0.72, 0.28),
                position=(0, 0.1), color=color.rgba(0.1, 0, 0.2, 0.95), z=-2)
    ttl = Text(parent=camera.ui, text=msg,
               position=(-0.32, 0.19), scale=1.05, color=color.rgb(1, 0.8, 0.2), z=-2)

    def close_combo():
        clear_ui(combo_popup_ui)
        end_dialogue()

    btn = Button(parent=camera.ui, text='확인 [F]',
                 scale=(0.18, 0.055), position=(0, -0.04), z=-2)
    btn.on_click = close_combo
    combo_popup_ui.extend([bg, ttl, btn])


def end_dialogue():
    global talking
    talking = False
    player.enabled = True
    mouse.locked = True
    mouse.visible = False
    hide_dlg()
    clear_ui(choice_btns)
    clear_ui(alibi_ui)
    clear_ui(clue_popup_ui)
    clear_ui(combo_popup_ui)


# =============================================================
#  범인 지목
# =============================================================
def open_accusation():
    global accusing
    accusing = True
    player.enabled = False
    mouse.locked = False
    mouse.visible = True
    clear_ui(accuse_ui)

    bg  = Entity(parent=camera.ui, model='quad', scale=(0.88, 0.70),
                 position=(0, 0.02), color=color.black90, z=-1)
    ttl = Text(parent=camera.ui, text='[ 범인을 지목하라 ]',
               position=(0, 0.30), origin=(0, 0), scale=1.6, color=color.red, z=-1)
    warn = Text(parent=camera.ui,
                text='⚠  이것은 단 한 번의 기회입니다.  ⚠\n지목 후에는 되돌릴 수 없습니다.',
                position=(0, 0.20), origin=(0, 0), scale=1.0, color=color.yellow, z=-1)
    sub = Text(parent=camera.ui,
               text='수집한 모든 단서를 토대로, 진범을 지목하십시오.',
               position=(0, 0.12), origin=(0, 0), scale=0.95, color=color.white, z=-1)
    accuse_ui.extend([bg, ttl, warn, sub])

    for name, pos, nc in zip(
        ['정다은', '박지훈', '최민호', '한서윤'],
        [(-0.2, 0.02), (0.2, 0.02), (-0.2, -0.10), (0.2, -0.10)],
        [color.blue, color.green, color.orange, color.pink]
    ):
        def make_accuse(n=name):
            def handler():
                show_result(n)
            return handler
        b = Button(parent=camera.ui, text=name,
                   scale=(0.28, 0.078), position=pos, color=nc, z=-1)
        b.on_click = make_accuse()
        accuse_ui.append(b)


def close_accusation():
    global accusing
    accusing = False
    clear_ui(accuse_ui)


def show_result(name):
    clear_ui(accuse_ui)
    correct = (name == CULPRIT)

    bg = Entity(parent=camera.ui, model='quad', scale=(0.96, 0.88),
                position=(0, 0.02), color=color.black90, z=-1)
    accuse_ui.append(bg)

    if correct:
        culprit_clues = [c for c in collected_clues if CLUES[c].get('related') == '최민호']
        lies_caught   = sum(1 for (n, _) in confirmed_lies if n == '최민호')
        combo_found   = bool(unlocked_combos)

        if len(culprit_clues) >= 5 and lies_caught >= 2:
            grade, grade_c = '★★★  완벽한 수사  ★★★', color.yellow
            grade_msg = '모든 결정적 증거를 확보하고 거짓말까지 현장에서 간파했습니다.\n이 사건은 법정에서 반드시 유죄가 됩니다.'
        elif len(culprit_clues) >= 3 or combo_found:
            grade, grade_c = '★★☆  우수한 수사  ★★☆', color.cyan
            grade_msg = '충분한 증거로 범인을 특정했습니다.\n유죄 입증에는 무리가 없습니다.'
        else:
            grade, grade_c = '★☆☆  가까스로 해결  ★☆☆', color.orange
            grade_msg = '범인은 맞췄지만 증거가 부족합니다.\n법정에서 무죄 판결이 날 수도 있습니다.'

        ttl = Text(parent=camera.ui, text='★  추리 성공!  범인은 최민호였다.',
                   position=(0, 0.37), origin=(0, 0), scale=1.4, color=color.yellow, z=-1)
        g_lbl = Text(parent=camera.ui, text=grade,
                     position=(0, 0.29), origin=(0, 0), scale=1.1, color=grade_c, z=-1)
        g_desc = Text(parent=camera.ui, text=grade_msg,
                      position=(0, 0.22), origin=(0, 0), scale=0.88, color=color.light_gray, z=-1)
        body = Text(parent=camera.ui,
                    text=(
                        '범행 동기: 이강현이 최민호를 해고하려 했고,\n'
                        '           이 사실을 알게 된 최민호가 범행을 결심했다.\n\n'
                        '범행 과정\n'
                        '  ① 옥상 CCTV 분전반을 직접 조작해 감시 차단\n'
                        '  ② 퇴근한 척 편의점에 들렀다가 건물에 재진입\n'
                        '  ③ 몰래 복사한 열쇠로 약품창고 독성 물질 반출\n'
                        '  ④ 실험실 침입 → 독성 물질 주입 → 도주\n\n'
                        f'수집 증거: {len(culprit_clues)}/8개  |  거짓말 간파: {lies_caught}회  |  단서 조합: {"발견" if combo_found else "미발견"}'
                    ),
                    position=(-0.44, 0.12), scale=0.88, color=color.white, z=-1)
        accuse_ui.extend([ttl, g_lbl, g_desc, body])
        btn_text, btn_color = '수사 완료 — 게임 종료', color.lime
    else:
        missed = [cid for cid in CLUES if CLUES[cid].get('related') == '최민호' and cid not in collected_clues]
        missed_info = {
            'coffee_cup': (
                '실험실',
                '편의점 커피 컵',
                '"최민호가 즐겨 마시는 브랜드 → 실험실에 있었다"\n'
                '   퇴근했다는 진술이 처음부터 거짓이었음을 눈치챘어야 했다.'
            ),
            'card_log': (
                '실험실',
                '보안카드 재진입 기록',
                '"20:55 최민호 카드 재진입 = 퇴근 진술이 거짓"\n'
                '   재진입 이후 행방이 불명이므로, 그를 첫 번째 용의자로 의심했어야 했다.'
            ),
            'pc_log': (
                '4층 자료실',
                '독극물 검색 기록',
                '"사건 3일 전 최민호 계정으로 독극물 검색 → 사전 계획"\n'
                '   우발이 아닌 계획 범행임을, 그리고 계획한 사람이 최민호임을 추론했어야 했다.'
            ),
            'circuit_breaker': (
                '옥상',
                'CCTV 분전반 지문',
                '"분전반 손잡이의 지문 = 최민호가 직접 CCTV를 껐다"\n'
                '   감시 카메라를 끈 사람이 범인이고, 그게 최민호임을 연결했어야 했다.'
            ),
            'key_mark': (
                '약품창고',
                '복사 열쇠',
                '"무단 복사 열쇠 = 누군가 미리 독성 물질 접근을 준비했다"\n'
                '   사전에 열쇠를 복사할 수 있었던 내부 인물을 추적했어야 했다.'
            ),
            'badge': (
                '약품창고',
                '최민호의 사원증',
                '"약품창고 바닥에 최민호 사원증 → 그가 거기 있었다"\n'
                '   현장에 남겨진 물리 증거로, 그의 진술이 거짓임을 확인했어야 했다.'
            ),
            'remote_log': (
                '서버실',
                '해고 통보 문서',
                '"이강현이 최민호를 해고할 예정이었다 → 범행 동기"\n'
                '   동기 없는 살인은 없다. 이 문서가 왜 존재하는지 물었어야 했다.'
            ),
            'burned_glove': (
                '약품창고',
                '증거 인멸 고무장갑',
                '"최민호 DNA 검출 → 독성 물질 다루고 버린 장갑"\n'
                '   범인은 증거를 지우려 했고, 그 행위 자체가 최민호를 특정한다.'
            ),
        }

        ttl = Text(parent=camera.ui,
                   text=f'✗  추리 실패.  {name}은(는) 범인이 아니었다.',
                   position=(0, 0.38), origin=(0, 0), scale=1.15, color=color.red, z=-1)
        real = Text(parent=camera.ui,
                    text='진범은  최민호  였습니다.',
                    position=(0, 0.30), origin=(0, 0), scale=1.1, color=color.orange, z=-1)
        why = Text(parent=camera.ui,
                   text=(
                       '최민호는 이강현에게 해고 통보를 받을 것을 미리 알고\n'
                       'CCTV를 직접 차단한 뒤 재진입해 독성 물질로 범행을 저질렀다.'
                   ),
                   position=(0, 0.22), origin=(0, 0), scale=0.90, color=color.white, z=-1)
        accuse_ui.extend([ttl, real, why])

        if missed:
            sep = Entity(parent=camera.ui, model='quad', scale=(0.88, 0.003),
                         position=(0, 0.15), color=color.rgb(0.5, 0.3, 0.1), z=-1)
            accuse_ui.append(sep)
            miss_hdr = Text(parent=camera.ui,
                            text=f'놓친 단서  ({len(missed)}개)  —  이것을 발견했다면 최민호를 의심할 수 있었다:',
                            position=(-0.44, 0.12), scale=0.85, color=color.yellow, z=-1)
            accuse_ui.append(miss_hdr)

            for j, mid in enumerate(missed[:3]):
                loc, clue_name, think = missed_info.get(mid, ('?', mid, ''))
                m_txt = Text(parent=camera.ui,
                             text=f'◆ [{loc}]  {clue_name}\n   {think}',
                             position=(-0.44, 0.05 - j * 0.135),
                             scale=0.80, color=color.light_gray, z=-1)
                accuse_ui.append(m_txt)
        btn_text, btn_color = '게임 종료', color.rgb(0.5, 0.1, 0.1)

    def finish():
        clear_ui(accuse_ui)
        application.quit()

    btn = Button(parent=camera.ui, text=btn_text,
                 scale=(0.3, 0.065), position=(0, -0.35),
                 color=btn_color, z=-1)
    btn.on_click = finish
    accuse_ui.append(btn)


# =============================================================
#  입력 처리
# =============================================================
def input(key):
    global talking, notebook_open, accusing

    if game_phase in ('start', 'briefing'):
        return

    # Tab: 수사 메뉴 토글
    if key == 'tab':
        if not talking and not accusing:
            if notebook_open:
                close_tab_menu()
            else:
                open_tab_menu()
        return

    # ESC: 현재 열린 UI 닫기 (범인 지목 화면은 ESC로 닫을 수 없음)
    if key == 'escape':
        if notebook_open:
            close_tab_menu()
        elif talking:
            end_dialogue()
        elif accusing:
            show_hint('범인을 반드시 지목해야 합니다. 되돌릴 수 없습니다.', dur=2)
        elif game_phase == 'exploring':
            open_tab_menu()
        return

    # F / 마우스 클릭 이외의 키는 무시
    if key not in ('f', 'left mouse down'):
        return

    # UI가 열려 있을 때 F로 팝업 확인 버튼 클릭
    if talking or notebook_open or accusing:
        if key == 'f':
            for popup in (clue_popup_ui, combo_popup_ui):
                if popup:
                    for e in popup:
                        if isinstance(e, Button):
                            e.on_click()
                            return
        return

    # 중앙 홀: NPC 상호작용
    if game_phase == 'investigating':
        for name, data in npc_data_map.items():
            ent = data['entity']
            if ent is None:
                continue
            if mouse.hovered_entity == ent or (key == 'f' and distance(player.position, ent.position) < 4):
                if distance(player.position, ent.position) < 4:
                    start_npc_dialogue(name)
                else:
                    show_hint(f'{name}에게 더 가까이 가세요.')
                return

    # 현장 탐색: 단서 상호작용
    if game_phase == 'exploring':
        for cid, ent in clue_entities.items():
            if mouse.hovered_entity == ent or (key == 'f' and distance(player.position, ent.position) < 3):
                if distance(player.position, ent.position) < 3:
                    if CLUES[cid]['location'] == selected_location:
                        collect_clue(cid)
                    else:
                        show_hint('이 단서는 다른 구역에 있습니다.')
                else:
                    show_hint(f'[{CLUES[cid]["name"]}] — 더 가까이 가서 조사하세요.')
                return

        for fkey, ent in fake_clue_entities.items():
            if mouse.hovered_entity == ent or (key == 'f' and distance(player.position, ent.position) < 3):
                if distance(player.position, ent.position) < 3:
                    if FAKE_CLUES[fkey]['location'] == selected_location:
                        collect_fake_clue(fkey)
                    else:
                        show_hint('이 물건은 다른 구역에 있습니다.')
                else:
                    show_hint(f'[{FAKE_CLUES[fkey]["name"]}] — 더 가까이 가서 조사하세요.')
                return


# =============================================================
#  매 프레임 업데이트
# =============================================================
def update():
    global explore_timer, room_exiting

    if game_phase in ('start', 'briefing'):
        return
    if talking or notebook_open or accusing:
        return

    if game_phase == 'exploring':
        explore_timer -= time.dt
        remaining = max(0, int(explore_timer))
        timer_label.color = color.red if remaining <= 10 else color.white
        timer_label.text  = f'남은 시간:  {remaining}초'

        if explore_timer <= 0 and not room_exiting:
            room_exiting = True
            timer_label.text = '⏰  시간 종료!'
            invoke(force_exit_room, delay=1.5)

        # 근접 단서 힌트
        for cid, ent in clue_entities.items():
            if (distance(player.position, ent.position) < 2.8
                    and not CLUES[cid]['collected']
                    and CLUES[cid]['location'] == selected_location):
                hint_label.text = f'[F]  {CLUES[cid]["name"]}  조사하기'
                return
        for fkey, ent in fake_clue_entities.items():
            if (distance(player.position, ent.position) < 2.8
                    and fkey not in collected_fakes
                    and FAKE_CLUES[fkey]['location'] == selected_location):
                hint_label.text = f'[F]  {FAKE_CLUES[fkey]["name"]}  조사하기'
                return

    elif game_phase == 'investigating':
        timer_label.text = ''
        for name, data in npc_data_map.items():
            if data['entity'] is None:
                continue
            if distance(player.position, data['entity'].position) < 3.5:
                hint_label.text = f'[F]  {name}에게 말 걸기'
                return

    hint_label.text = ''


# =============================================================
show_start_screen()
app.run()
