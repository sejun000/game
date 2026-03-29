import random
import time
import os
import sys
import json

# 📢 Colab 전용 사운드
try:
    from IPython.display import Audio, display
    IS_COLAB = True
except ImportError:
    IS_COLAB = False

# ==========================================
# TUI 유틸리티 (색깔 기반)
# ==========================================
class C:
    """ANSI 색상 코드"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"

class TUI:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def title(text):
        """제목 출력"""
        print(f"\n{C.BOLD}{C.CYAN}═══ {text} ═══{C.RESET}")

    @staticmethod
    def subtitle(text):
        """소제목 출력"""
        print(f"{C.YELLOW}── {text} ──{C.RESET}")

    @staticmethod
    def box(title, content_lines, width=60):
        """박스 형태로 출력 (간소화)"""
        print(f"\n{C.BOLD}{C.CYAN}[ {title} ]{C.RESET}")
        for line in content_lines:
            print(f"  {line}")
        return ""

    @staticmethod
    def display_width(s):
        """한글 포함 문자열의 표시 너비 계산"""
        width = 0
        for c in str(s):
            if ord(c) > 127:
                width += 2
            else:
                width += 1
        return width

    @staticmethod
    def pad(text, width):
        """한글 포함 문자열 패딩"""
        display_len = TUI.display_width(text)
        return str(text) + " " * max(0, width - display_len)

    @staticmethod
    def table(headers, rows, col_widths=None):
        """테이블 형태로 출력 (색깔 기반)"""
        if not col_widths:
            col_widths = [12] * len(headers)

        def pad_cell(text, width):
            display_len = TUI.display_width(str(text))
            padding = width - display_len
            return str(text) + " " * max(0, padding)

        lines = []
        # 헤더
        header_str = f"{C.BOLD}{C.CYAN}"
        header_str += " | ".join([pad_cell(h, w) for h, w in zip(headers, col_widths)])
        header_str += C.RESET
        lines.append(header_str)
        lines.append(C.GRAY + "-" * (sum(col_widths) + 3 * (len(headers)-1)) + C.RESET)

        # 행들
        for row in rows:
            cells = [pad_cell(c, w) for c, w in zip(row, col_widths)]
            lines.append(" | ".join(cells))

        return "\n".join(lines)

    @staticmethod
    def progress_bar(current, maximum, width=20, fill="█", empty="░"):
        """진행 바"""
        ratio = min(1.0, max(0, current / maximum)) if maximum > 0 else 0
        filled = int(width * ratio)
        return fill * filled + empty * (width - filled)

    @staticmethod
    def status_line(label, value, max_val=None, width=50):
        """상태 라인"""
        if max_val:
            bar = TUI.progress_bar(value, max_val, 15)
            return f"{label}: {bar} {value}/{max_val}"
        return f"{label}: {value}"


class SoundManager:
    def play(self, filename, autoplay=True):
        if os.path.exists(filename) and IS_COLAB:
            display(Audio(filename, autoplay=autoplay))
        else:
            self._print_text_fx(filename)

    def _print_text_fx(self, filename):
        if "attack" in filename: print("   [챙!]", end="")
        elif "fire" in filename: print("   [화르륵!]", end="")
        elif "crit" in filename: print("   [쿠광!!]", end="")
        elif "heal" in filename: print("   [뾰로롱]", end="")
        elif "magic" in filename: print("   [띠링]", end="")
        elif "double" in filename: print("   [슉!]", end="")
        elif "buff" in filename: print("   [우오오!]", end="")
        elif "debuff" in filename: print("   [야이..@!]", end="")

sound_mgr = SoundManager()

# ==========================================
# 장수 대사 시스템
# ==========================================
class HeroDialogue:
    # 장수별 대사 (공격, 피격, 승리, 패배, 스킬)
    DIALOGUES = {
        # 촉
        "관우": {
            "attack": ["의를 저버린 자여, 받아라!", "청룡언월도의 무게를 알겠느냐!"],
            "hurt": ["크윽... 이 정도는!", "아직이다...!"],
            "win": ["하늘이 정의의 편이로다.", "의로운 자는 반드시 이긴다."],
            "skill": ["천하의 관운장이 간다!"]
        },
        "장비": {
            "attack": ["으아아아!! 덤벼라!!", "이 장익덕님이 상대다!!"],
            "hurt": ["끄아악! 아프잖아!!", "이 정도론 안 죽어!!"],
            "win": ["크하하하! 약하구만!!", "다음엔 더 센 놈 데려와!"],
            "skill": ["우오오오오!!"]
        },
        "제갈량": {
            "attack": ["계책대로군요.", "하늘의 뜻을 읽었습니다."],
            "hurt": ["이것도 계산 안이오...", "허나 아직 수가 있소."],
            "win": ["모든 것은 예상대로.", "지략이 무력을 이기는 법."],
            "skill": ["동남풍이여, 불어라!"]
        },
        "조운": {
            "attack": ["상산 조자룡, 참상하겠다!", "내 창을 막을 자 누구냐!"],
            "hurt": ["크윽...!", "아직 쓰러질 수 없다!"],
            "win": ["주군을 위해!", "이것이 상산의 무예!"],
            "skill": ["만 명이 와도 뚫는다!"]
        },
        "마초": {
            "attack": ["서량의 전사가 왔다!", "아버지의 원수!"],
            "hurt": ["끄윽...", "물러서지 않는다!"],
            "win": ["서량 마씨의 무예!", "원수는 반드시 갚는다!"],
            "skill": ["돌격!!"]
        },
        # 위
        "하후돈": {
            "attack": ["내 눈을 가져간 대가를 치러라!", "맹장 하후돈이다!"],
            "hurt": ["이 정도 상처쯤이야!", "눈 하나로도 충분하다!"],
            "win": ["이것이 조씨 가문의 힘!", "위나라 만세!"],
            "skill": ["눈알이든 뭐든 가져가라!"]
        },
        "장료": {
            "attack": ["합비의 장료가 간다!", "오나라 놈들, 덤벼라!"],
            "hurt": ["아직이다!", "물러서지 않겠다!"],
            "win": ["이것이 위나라의 무장!", "합비는 지킨다!"],
            "skill": ["800으로 10만을 막는다!"]
        },
        "사마의": {
            "attack": ["허허, 예상대로군.", "제갈량, 오늘은 내가 이긴다."],
            "hurt": ["흥, 이것도 계산 안이야.", "서두르지 마라..."],
            "win": ["인내가 승리를 부르는 법.", "하하, 결국 내 뜻대로."],
            "skill": ["공명이여, 이번엔 어쩔 텐가?"]
        },
        "순욱": {
            "attack": ["계책을 쓰겠습니다.", "승상을 위하여."],
            "hurt": ["크윽...", "물러서지 않겠습니다."],
            "win": ["충신은 두 마음이 없습니다.", "위나라를 위해."],
            "skill": ["이것이 왕좌의 책략!"]
        },
        # 오
        "주유": {
            "attack": ["적벽의 불길을 기억하라!", "주공근이 간다!"],
            "hurt": ["크윽... 공명 때문이야!", "아직 끝나지 않았다!"],
            "win": ["강동의 미주가 이겼도다!", "적벽의 영웅이다!"],
            "skill": ["동풍이여! 불어라!"]
        },
        "손책": {
            "attack": ["소패왕이 간다!", "강동의 호랑이다!"],
            "hurt": ["으윽!", "이 정도론!"],
            "win": ["천하는 내 것!", "소패왕의 무예다!"],
            "skill": ["강동 땅은 내가 지킨다!"]
        },
        "육손": {
            "attack": ["계책이 있습니다.", "서두르지 마십시오."],
            "hurt": ["예상 범위입니다.", "아직 수가 있습니다."],
            "win": ["인내가 승리를 부릅니다.", "이릉의 불길처럼."],
            "skill": ["때를 기다렸습니다!"]
        },
        "감녕": {
            "attack": ["방울소리가 들리냐!", "금범 감녕이다!"],
            "hurt": ["끄윽!", "아직이야!"],
            "win": ["해적왕의 무예다!", "100명으로 충분하다!"],
            "skill": ["야습이다! 돌격!"]
        }
    }

    # 기본 대사 (등록 안 된 장수용)
    DEFAULT = {
        "attack": ["하아앗!", "받아라!"],
        "hurt": ["크윽!", "으윽..."],
        "win": ["이겼다!", "승리다!"],
        "skill": ["필살!"]
    }

    @staticmethod
    def get(hero_name, situation):
        """장수 대사 가져오기"""
        dialogues = HeroDialogue.DIALOGUES.get(hero_name, HeroDialogue.DEFAULT)
        lines = dialogues.get(situation, HeroDialogue.DEFAULT.get(situation, [""]))
        return random.choice(lines)

    @staticmethod
    def say(hero_name, situation):
        """대사 출력"""
        line = HeroDialogue.get(hero_name, situation)
        print(f'     💬 "{line}"')


# ==========================================
# 장수별 스킬 시스템
# ==========================================
class HeroSkills:
    # 스킬 정의: {id: {name, mp, type, desc, formula}}
    SKILLS = {
        "attack": {"name": "공격", "mp": 0, "type": "physical", "desc": "기본 공격", "icon": "⚔️"},
        "fire": {"name": "화계", "mp": 20, "type": "magic", "desc": "화염 공격+화상", "icon": "🔥"},
        "thunder": {"name": "낙뢰", "mp": 50, "type": "magic", "desc": "강력한 번개", "icon": "⚡"},
        "confuse": {"name": "혼란", "mp": 30, "type": "magic", "desc": "적 기절", "icon": "💫"},
        "heal": {"name": "치유", "mp": 30, "type": "support", "desc": "HP 회복", "icon": "💊"},
        "rally": {"name": "격려", "mp": 40, "type": "support", "desc": "능력치 상승", "icon": "💪"},
        "taunt": {"name": "욕설", "mp": 40, "type": "debuff", "desc": "적 능력 하락", "icon": "🤬"},
        "rest": {"name": "휴식", "mp": 0, "type": "support", "desc": "MP 회복", "icon": "💤"},
        "support": {"name": "지원", "mp": 30, "type": "support", "desc": "병력→HP", "icon": "🚩"},
        "charge": {"name": "돌격", "mp": 35, "type": "physical", "desc": "무력+민첩 공격", "icon": "🐎"},
        "combo": {"name": "연환계", "mp": 45, "type": "hybrid", "desc": "무력+지력 공격", "icon": "🌀"},
        "arrow": {"name": "난사", "mp": 25, "type": "physical", "desc": "연속 공격", "icon": "🏹"},
        "defend": {"name": "철벽", "mp": 30, "type": "support", "desc": "방어력 상승", "icon": "🛡️"},
        "poison": {"name": "독계", "mp": 35, "type": "magic", "desc": "독 상태이상", "icon": "☠️"},
        "inspire": {"name": "고무", "mp": 50, "type": "support", "desc": "아군 전체 버프", "icon": "📯"},
        "drill": {"name": "조련", "mp": 35, "type": "support", "desc": "민첩/운 대폭 상승", "icon": "🎯"},
        # ===== 군주 전용 사기 스킬 =====
        # 조조
        "conquer": {"name": "패도", "mp": 80, "type": "ultimate", "desc": "천하를 호령하는 일격", "icon": "👑"},
        "ambition": {"name": "천하포무", "mp": 100, "type": "ultimate", "desc": "모든 적 섬멸", "icon": "🌑"},
        # 유비
        "virtue": {"name": "인덕", "mp": 80, "type": "ultimate", "desc": "아군 전원 완전회복", "icon": "☀️"},
        "oath": {"name": "도원결의", "mp": 100, "type": "ultimate", "desc": "불멸의 결속", "icon": "🍑"},
        # 손권
        "eastern": {"name": "강동패업", "mp": 80, "type": "ultimate", "desc": "연속 강타", "icon": "🌊"},
        "redcliff": {"name": "적벽대화", "mp": 100, "type": "ultimate", "desc": "전장을 불태우다", "icon": "🔱"},
        # 여포
        "musou": {"name": "무쌍", "mp": 70, "type": "ultimate", "desc": "천하무쌍의 일격", "icon": "💀"},
        "sky_pierce": {"name": "천하무적", "mp": 100, "type": "ultimate", "desc": "방천화극의 폭풍", "icon": "🔱"},
        # ===== 유명 장수 사기 스킬 =====
        # 관우
        "dragon_blade": {"name": "청룡언월", "mp": 80, "type": "ultimate", "desc": "청룡도의 일섬", "icon": "🐉"},
        "righteous": {"name": "의리천추", "mp": 100, "type": "ultimate", "desc": "의로운 분노 폭발", "icon": "⚔️"},
        # 장비
        "roar": {"name": "장판파후", "mp": 80, "type": "ultimate", "desc": "적 전체 기절", "icon": "🗣️"},
        # 제갈량
        "wind_fire": {"name": "칠성단", "mp": 80, "type": "ultimate", "desc": "동남풍 소환", "icon": "🌪️"},
        "bagua": {"name": "팔진도", "mp": 100, "type": "ultimate", "desc": "적 전체 혼란+피해", "icon": "☯️"},
        # 조운
        "changban": {"name": "장판돌파", "mp": 80, "type": "ultimate", "desc": "만군 속 돌파", "icon": "🏇"},
        # 사마의
        "patience": {"name": "인고지책", "mp": 80, "type": "ultimate", "desc": "HP회복+상대디버프", "icon": "🦊"},
        "dark_scheme": {"name": "음모", "mp": 100, "type": "ultimate", "desc": "독+화상+혼란", "icon": "🕷️"},
        # 주유
        "fire_attack": {"name": "화공", "mp": 80, "type": "ultimate", "desc": "적 전체 대화염", "icon": "🔥"},
        "genius": {"name": "미주영재", "mp": 100, "type": "ultimate", "desc": "완벽한 전략", "icon": "🎭"},
        # 광역 스킬
        "fire_all": {"name": "화염진", "mp": 60, "type": "magic_aoe", "desc": "적 전체 화염", "icon": "🔥"},
        "thunder_all": {"name": "뇌격진", "mp": 70, "type": "magic_aoe", "desc": "적 전체 낙뢰", "icon": "⚡"},
        "arrow_rain": {"name": "화시우", "mp": 50, "type": "physical_aoe", "desc": "적 전체 화살비", "icon": "🏹"},
        # ===== 다중 타겟 스킬 (2~3명) =====
        "twin_strike": {"name": "쌍격", "mp": 40, "type": "physical_multi", "desc": "적 2명 공격", "icon": "⚔️"},
        "triple_arrow": {"name": "삼연시", "mp": 45, "type": "physical_multi", "desc": "적 3명 화살", "icon": "🏹"},
        "chain_fire": {"name": "연화", "mp": 50, "type": "magic_multi", "desc": "적 2명 화염", "icon": "🔥"},
        "chain_thunder": {"name": "연뢰", "mp": 55, "type": "magic_multi", "desc": "적 2명 번개", "icon": "⚡"},
        "mass_confuse": {"name": "군혼", "mp": 60, "type": "debuff_multi", "desc": "적 2명 혼란", "icon": "💫"},
        "mass_poison": {"name": "독운", "mp": 55, "type": "debuff_multi", "desc": "적 2명 중독", "icon": "☠️"},
        # ===== 다중 회복/버프 스킬 =====
        "group_heal": {"name": "집단치유", "mp": 80, "type": "heal_multi", "desc": "아군 2명 회복", "icon": "💚"},
        "mass_heal": {"name": "대회복", "mp": 100, "type": "heal_all", "desc": "아군 전체 회복", "icon": "💖"},
        "duo_rally": {"name": "쌍격려", "mp": 50, "type": "buff_multi", "desc": "아군 2명 버프", "icon": "💪"},
        "trio_rally": {"name": "삼군격려", "mp": 65, "type": "buff_multi", "desc": "아군 3명 버프", "icon": "📣"},
        "war_drum": {"name": "전고", "mp": 70, "type": "buff_all", "desc": "아군 전체 공격력↑", "icon": "🥁"},
        "iron_wall": {"name": "철벽진", "mp": 70, "type": "buff_all", "desc": "아군 전체 방어력↑", "icon": "🛡️"},
        # ===== 추가 사기 스킬 =====
        # 황충
        "old_glory": {"name": "노장불사", "mp": 80, "type": "ultimate", "desc": "HP회복+치명타 대폭 상승", "icon": "🏹"},
        # 하후돈
        "eye_fury": {"name": "독안의분노", "mp": 80, "type": "ultimate", "desc": "눈을 뽑아 적 공포", "icon": "👁️"},
        # 장료
        "hefei": {"name": "합비의용", "mp": 80, "type": "ultimate", "desc": "800명으로 10만 압도", "icon": "⚔️"},
        # 순욱
        "kings_path": {"name": "왕좌지책", "mp": 80, "type": "ultimate", "desc": "아군 전체 대버프", "icon": "👑"},
        # 육손
        "yiling": {"name": "이릉화공", "mp": 80, "type": "ultimate", "desc": "적 전체 화염폭풍", "icon": "🔥"},
        # 손책
        "little_conqueror": {"name": "소패왕", "mp": 80, "type": "ultimate", "desc": "단일 대상 초강타", "icon": "🐯"},
        # 감녕
        "night_raid": {"name": "백기야습", "mp": 80, "type": "ultimate", "desc": "100기 야습 공격", "icon": "🌙"},
        # 마초
        "revenge": {"name": "복수의창", "mp": 80, "type": "ultimate", "desc": "아버지의 원한", "icon": "🔱"},
        # ===== 추가 사기 스킬 =====
        # 방통
        "linked_strategy": {"name": "연환계책", "mp": 80, "type": "ultimate", "desc": "적 전체 이동봉쇄+화상", "icon": "⛓️"},
        # 강유
        "northern_expedition": {"name": "북벌", "mp": 80, "type": "ultimate", "desc": "승상의 뜻을 이어", "icon": "🏔️"},
        # 위연
        "betrayal_strike": {"name": "반골의일격", "mp": 80, "type": "ultimate", "desc": "반역의 힘", "icon": "💀"},
        # 조인
        "iron_defense": {"name": "철옹성", "mp": 80, "type": "ultimate", "desc": "아군 방어 극대화", "icon": "🏰"},
        # 곽가
        "ten_victories": {"name": "십승십패", "mp": 80, "type": "ultimate", "desc": "완벽한 분석", "icon": "📜"},
        # 허저
        "naked_fury": {"name": "나체결투", "mp": 80, "type": "ultimate", "desc": "광전사 모드", "icon": "💢"},
        # 전위
        "last_stand": {"name": "최후의저항", "mp": 80, "type": "ultimate", "desc": "죽어서도 싸운다", "icon": "⚰️"},
        # 서황
        "fancheng": {"name": "번성대첩", "mp": 80, "type": "ultimate", "desc": "관우를 꺾은 무예", "icon": "⚔️"},
        # 장합
        "qishan": {"name": "기산방어", "mp": 80, "type": "ultimate", "desc": "철벽 방어진", "icon": "🛡️"},
        # 태사자
        "duel_master": {"name": "일기토", "mp": 80, "type": "ultimate", "desc": "손책과의 결투", "icon": "🤺"},
        # 여몽
        "white_robe": {"name": "백의도강", "mp": 80, "type": "ultimate", "desc": "은밀한 습격", "icon": "👻"},
        # 노숙
        "alliance": {"name": "손유동맹", "mp": 80, "type": "ultimate", "desc": "동맹의 힘", "icon": "🤝"},
        # 황개
        "fire_ship": {"name": "고육지책", "mp": 80, "type": "ultimate", "desc": "화선 돌격", "icon": "🚢"},
        # 주태
        "bodyguard": {"name": "호위무쌍", "mp": 80, "type": "ultimate", "desc": "주군을 위해", "icon": "🛡️"},
        # 능통
        "revenge_blade": {"name": "부친복수", "mp": 80, "type": "ultimate", "desc": "감녕에 대한 분노", "icon": "😤"},
        # ===== 남만 스킬 =====
        # 맹획
        "seven_capture": {"name": "칠종칠금", "mp": 100, "type": "ultimate", "desc": "불굴의 의지", "icon": "🐘"},
        "savage_king": {"name": "남만왕", "mp": 80, "type": "ultimate", "desc": "맹수군단 소환", "icon": "👑"},
        # 축융
        "flying_blade": {"name": "비도술", "mp": 50, "type": "magic_multi", "desc": "비도 연발", "icon": "🗡️"},
        "beast_queen": {"name": "맹수여왕", "mp": 80, "type": "ultimate", "desc": "맹수+화공", "icon": "🔥"},
        # 올돌골
        "rattan_armor": {"name": "등갑병", "mp": 60, "type": "buff_all", "desc": "불침투 갑옷", "icon": "🛡️"},
        "immortal_body": {"name": "불사지신", "mp": 100, "type": "ultimate", "desc": "죽음을 거부", "icon": "💀"},
        # 아회남
        "poison_fog": {"name": "독안개", "mp": 70, "type": "magic_aoe", "desc": "독안개 살포", "icon": "☠️"},
        # 동도나
        "beast_charge": {"name": "맹수돌격", "mp": 60, "type": "physical_aoe", "desc": "코끼리 돌격", "icon": "🐘"},
    }

    # 장수별 스킬셋 (attack은 기본)
    HERO_SKILLS = {
        # ===== 군주 (사기 스킬 보유) =====
        "조조": ["attack", "charge", "rally", "inspire", "war_drum", "conquer", "ambition", "rest"],
        "유비": ["attack", "rally", "heal", "inspire", "group_heal", "virtue", "oath", "rest"],
        "손권": ["attack", "charge", "inspire", "defend", "iron_wall", "eastern", "redcliff", "rest"],
        # ===== 촉 (사기 스킬 + 다중 타겟) =====
        "관우": ["attack", "charge", "rally", "drill", "twin_strike", "dragon_blade", "righteous", "rest"],
        "장비": ["attack", "taunt", "charge", "twin_strike", "roar", "rest"],
        "제갈량": ["attack", "fire", "thunder", "confuse", "heal", "chain_fire", "mass_heal", "wind_fire", "bagua", "rest"],
        "조운": ["attack", "charge", "combo", "defend", "drill", "twin_strike", "changban", "rest"],
        "황충": ["attack", "arrow", "rally", "drill", "triple_arrow", "arrow_rain", "old_glory", "rest"],
        "마초": ["attack", "charge", "taunt", "twin_strike", "revenge", "rest"],
        "방통": ["attack", "fire", "confuse", "heal", "chain_fire", "group_heal", "mass_heal", "fire_all", "linked_strategy", "rest"],
        "강유": ["attack", "combo", "confuse", "rally", "drill", "chain_thunder", "trio_rally", "northern_expedition", "rest"],
        "위연": ["attack", "charge", "taunt", "twin_strike", "betrayal_strike", "rest"],
        "법정": ["attack", "confuse", "poison", "mass_poison", "mass_confuse", "rest"],
        # ===== 위 (사기 스킬 + 다중 타겟) =====
        "하후돈": ["attack", "charge", "rally", "taunt", "twin_strike", "eye_fury", "rest"],
        "조인": ["attack", "defend", "rally", "drill", "iron_wall", "duo_rally", "iron_defense", "rest"],
        "순욱": ["attack", "confuse", "heal", "inspire", "group_heal", "mass_heal", "trio_rally", "kings_path", "rest"],
        "곽가": ["attack", "confuse", "poison", "mass_poison", "mass_confuse", "ten_victories", "rest"],
        "허저": ["attack", "charge", "taunt", "twin_strike", "naked_fury", "rest"],
        "장료": ["attack", "charge", "arrow", "rally", "drill", "triple_arrow", "arrow_rain", "hefei", "rest"],
        "사마의": ["attack", "fire", "thunder", "confuse", "poison", "chain_thunder", "patience", "dark_scheme", "rest"],
        "전위": ["attack", "charge", "defend", "twin_strike", "last_stand", "rest"],
        "서황": ["attack", "charge", "arrow", "drill", "triple_arrow", "fancheng", "rest"],
        "장합": ["attack", "defend", "combo", "drill", "twin_strike", "iron_wall", "qishan", "rest"],
        "하후연": ["attack", "charge", "arrow", "drill", "triple_arrow", "rest"],  # 기병장
        "우금": ["attack", "defend", "rally", "drill", "iron_wall", "rest"],  # 방어 전문
        "악진": ["attack", "charge", "rally", "twin_strike", "rest"],  # 선봉장
        "이전": ["attack", "combo", "rally", "defend", "duo_rally", "rest"],  # 균형형
        "조홍": ["attack", "charge", "defend", "twin_strike", "rest"],  # 돌격형
        "조창": ["attack", "charge", "taunt", "twin_strike", "rest"],  # 맹장형
        "문빙": ["attack", "defend", "arrow", "rally", "triple_arrow", "rest"],  # 궁병장
        "등애": ["attack", "confuse", "fire", "combo", "chain_fire", "mass_confuse", "rest"],  # 지략가
        "종회": ["attack", "confuse", "poison", "fire", "mass_poison", "mass_confuse", "rest"],  # 모사
        "정욱": ["attack", "confuse", "poison", "heal", "mass_poison", "group_heal", "rest"],  # 책사
        "순유": ["attack", "confuse", "heal", "inspire", "group_heal", "trio_rally", "rest"],  # 책사
        "만총": ["attack", "defend", "rally", "drill", "iron_wall", "duo_rally", "rest"],  # 수비장
        "방덕": ["attack", "charge", "taunt", "twin_strike", "rest"],  # 맹장
        "조진": ["attack", "charge", "defend", "rally", "twin_strike", "rest"],  # 균형형
        "채양": ["attack", "charge", "rally", "rest"],  # 일반 무장
        "이각": ["attack", "charge", "taunt", "rest"],  # 서량 무장
        "곽사": ["attack", "charge", "arrow", "rest"],  # 서량 무장
        "화흠": ["attack", "heal", "confuse", "group_heal", "rest"],  # 문관
        "유엽": ["attack", "confuse", "heal", "inspire", "group_heal", "rest"],  # 문관
        # ===== 오 (사기 스킬 + 다중 타겟) =====
        "주유": ["attack", "fire", "thunder", "confuse", "inspire", "chain_fire", "fire_attack", "genius", "rest"],
        "육손": ["attack", "fire", "confuse", "defend", "drill", "chain_fire", "fire_all", "yiling", "rest"],
        "손책": ["attack", "charge", "rally", "taunt", "twin_strike", "little_conqueror", "rest"],
        "태사자": ["attack", "arrow", "charge", "drill", "triple_arrow", "arrow_rain", "duel_master", "rest"],
        "감녕": ["attack", "charge", "arrow", "taunt", "twin_strike", "night_raid", "rest"],
        "여몽": ["attack", "combo", "confuse", "drill", "mass_confuse", "white_robe", "rest"],
        "노숙": ["attack", "heal", "inspire", "group_heal", "mass_heal", "trio_rally", "alliance", "rest"],
        "황개": ["attack", "fire", "charge", "chain_fire", "fire_all", "fire_ship", "rest"],
        "주태": ["attack", "defend", "charge", "iron_wall", "bodyguard", "rest"],
        "능통": ["attack", "arrow", "combo", "triple_arrow", "revenge_blade", "rest"],
        "정보": ["attack", "charge", "defend", "rally", "twin_strike", "rest"],  # 노장
        "한당": ["attack", "charge", "arrow", "twin_strike", "rest"],  # 노장
        "장흠": ["attack", "arrow", "charge", "triple_arrow", "rest"],  # 궁병장
        "반장": ["attack", "charge", "taunt", "twin_strike", "rest"],  # 무장
        "서성": ["attack", "defend", "combo", "rally", "iron_wall", "rest"],  # 방어장
        "정봉": ["attack", "charge", "arrow", "drill", "triple_arrow", "rest"],  # 맹장
        "주환": ["attack", "combo", "defend", "rally", "twin_strike", "rest"],  # 균형형
        "주연": ["attack", "defend", "fire", "rally", "chain_fire", "rest"],  # 방어형
        "손환": ["attack", "charge", "rally", "defend", "rest"],  # 손씨 일족
        "장소": ["attack", "confuse", "heal", "inspire", "group_heal", "mass_heal", "rest"],  # 대문관
        "고옹": ["attack", "heal", "inspire", "rally", "group_heal", "trio_rally", "rest"],  # 문관
        "육항": ["attack", "fire", "confuse", "defend", "chain_fire", "fire_all", "rest"],  # 육손 아들
        "손상향": ["attack", "charge", "arrow", "rally", "triple_arrow", "rest"],  # 궁수
        "제갈근": ["attack", "confuse", "heal", "inspire", "group_heal", "trio_rally", "rest"],  # 문관
        "손견": ["attack", "charge", "rally", "taunt", "twin_strike", "rest"],  # 호랑이
        "오경": ["attack", "charge", "defend", "rest"],  # 일반 무장
        "전종": ["attack", "combo", "rally", "twin_strike", "rest"],  # 일반 무장
        "동습": ["attack", "defend", "arrow", "triple_arrow", "rest"],  # 일반 무장
        "하제": ["attack", "charge", "rally", "rest"],  # 일반 무장
        # ===== 재야 장수 =====
        "여포": ["attack", "charge", "combo", "taunt", "twin_strike", "musou", "sky_pierce", "rest"],  # 최강의 무장
        "진궁": ["attack", "confuse", "poison", "fire", "mass_poison", "mass_confuse", "rest"],  # 여포의 책사
        "장수": ["attack", "charge", "arrow", "twin_strike", "rest"],
        "장임": ["attack", "defend", "charge", "rally", "iron_wall", "rest"],
        "엄안": ["attack", "defend", "rally", "drill", "duo_rally", "rest"],  # 노장
        "서서": ["attack", "confuse", "heal", "inspire", "group_heal", "mass_heal", "rest"],  # 책사
        "화타": ["attack", "heal", "inspire", "group_heal", "mass_heal", "rest"],  # 명의
        # ===== 남만 =====
        "맹획": ["attack", "charge", "taunt", "rally", "twin_strike", "savage_king", "seven_capture", "rest"],  # 남만왕
        "축융": ["attack", "fire", "charge", "flying_blade", "beast_queen", "rest"],  # 맹획 부인
        "올돌골": ["attack", "defend", "charge", "rattan_armor", "immortal_body", "rest"],  # 등갑병 대장
        "아회남": ["attack", "poison", "confuse", "mass_poison", "poison_fog", "rest"],  # 독 전문가
        "동도나": ["attack", "charge", "rally", "twin_strike", "beast_charge", "rest"],  # 맹수 조련사
    }

    # 기본 스킬셋 (등록 안 된 장수용)
    DEFAULT_SKILLS = ["attack", "rally", "heal", "rest"]

    @staticmethod
    def get_skills(hero_name):
        """장수의 스킬 목록 반환"""
        return HeroSkills.HERO_SKILLS.get(hero_name, HeroSkills.DEFAULT_SKILLS)

    @staticmethod
    def get_skill_info(skill_id):
        """스킬 정보 반환"""
        return HeroSkills.SKILLS.get(skill_id, {"name": "???", "mp": 0, "type": "physical", "desc": "???", "icon": "?"})

    @staticmethod
    def pad_korean(text, width):
        """한글 포함 문자열 패딩"""
        display_len = sum(2 if ord(c) > 127 else 1 for c in text)
        return text + " " * max(0, width - display_len)

    @staticmethod
    def show_skills(hero_name, current_mp):
        """장수의 사용 가능한 스킬 표시 (색깔 기반)"""
        skills = HeroSkills.get_skills(hero_name)
        print(f"\n{C.BOLD}{C.CYAN}[ {hero_name} 스킬 ]{C.RESET}")
        for i, skill_id in enumerate(skills):
            info = HeroSkills.get_skill_info(skill_id)
            mp_str = f"MP{info['mp']:02d}" if info['mp'] > 0 else "무료"
            usable = current_mp >= info['mp']
            skill_name = HeroSkills.pad_korean(info['name'], 6)
            skill_desc = HeroSkills.pad_korean(info['desc'], 12)
            if usable:
                print(f"  {C.GREEN}{i+1}.{C.RESET} {info['icon']}{skill_name} {C.YELLOW}({mp_str}){C.RESET} {skill_desc}")
            else:
                print(f"  {C.GRAY}{i+1}. {info['icon']}{skill_name} ({mp_str}) {skill_desc} [MP부족]{C.RESET}")
        return skills

    @staticmethod
    def show_enemy_skills(hero_name):
        """적 장수의 스킬 목록 표시 (전투 정보용)"""
        skills = HeroSkills.get_skills(hero_name)
        skill_names = []
        for skill_id in skills:
            info = HeroSkills.get_skill_info(skill_id)
            skill_names.append(f"{info['icon']}{info['name']}")
        return " / ".join(skill_names)


# ==========================================
# 이벤트 시스템
# ==========================================
class EventSystem:
    EVENTS = [
        {"id": "locust", "name": "메뚜기 떼 습격", "icon": "🦗", "chance": 8,
         "desc": "메뚜기 떼가 농작물을 휩쓸었습니다!", "effect": "food", "value": -0.3},
        {"id": "rebellion", "name": "민란 발생", "icon": "🔥", "chance": 6,
         "desc": "백성들이 반란을 일으켰습니다!", "effect": "troops", "value": -0.2},
        {"id": "plague", "name": "역병 창궐", "icon": "☠️", "chance": 5,
         "desc": "역병이 돌아 병사들이 쓰러집니다...", "effect": "troops", "value": -0.15},
        {"id": "harvest", "name": "풍년", "icon": "🌾", "chance": 12,
         "desc": "올해는 대풍년입니다!", "effect": "food", "value": 0.25},
        {"id": "merchant", "name": "대상 방문", "icon": "🐪", "chance": 10,
         "desc": "서역의 대상이 방문하여 교역합니다.", "effect": "gold", "value": 0.2},
        {"id": "volunteer", "name": "의용군 합류", "icon": "⚔️", "chance": 8,
         "desc": "뜻을 함께할 의용군이 찾아왔습니다!", "effect": "troops", "value": 0.15},
        {"id": "drought", "name": "가뭄", "icon": "☀️", "chance": 7,
         "desc": "극심한 가뭄으로 농업 생산이 감소합니다.", "effect": "agri", "value": -15},
        {"id": "flood", "name": "홍수", "icon": "🌊", "chance": 6,
         "desc": "대홍수로 농지가 침수되었습니다!", "effect": "food", "value": -0.25},
        {"id": "desertion", "name": "탈영", "icon": "🏃", "chance": 5,
         "desc": "일부 병사들이 탈영했습니다...", "effect": "troops", "value": -0.1},
        {"id": "treasure", "name": "보물 발견", "icon": "💎", "chance": 4,
         "desc": "고대의 보물을 발견했습니다!", "effect": "gold", "value": 3000},
        {"id": "betrayal", "name": "장수 이탈", "icon": "💔", "chance": 3,
         "desc": "충성도 낮은 장수가 떠났습니다!", "effect": "hero_leave", "value": 0},
        {"id": "recruit", "name": "인재 영입", "icon": "🎓", "chance": 5,
         "desc": "떠돌이 무장이 합류를 청합니다!", "effect": "hero_join", "value": 0},
    ]

    @staticmethod
    def roll_event():
        """이벤트 발생 체크 (매 턴 30% 확률로 이벤트 발생)"""
        if random.randint(1, 100) > 30:
            return None

        # 가중치 기반 이벤트 선택
        total = sum(e["chance"] for e in EventSystem.EVENTS)
        roll = random.randint(1, total)

        cumulative = 0
        for event in EventSystem.EVENTS:
            cumulative += event["chance"]
            if roll <= cumulative:
                return event
        return None

    @staticmethod
    def apply_event(event, target):
        """이벤트 효과 적용 (target: 성 또는 세력)"""
        effect = event["effect"]
        value = event["value"]
        result = {"applied": True, "detail": ""}

        if effect == "food":
            # 성 기반: 군량
            supply_key = '군량' if '군량' in target else '쌀'
            if supply_key in target:
                if isinstance(value, float):
                    change = int(target[supply_key] * abs(value))
                    if value < 0:
                        target[supply_key] = max(0, target[supply_key] - change)
                        result["detail"] = f"군량 -{change}"
                    else:
                        target[supply_key] += change
                        result["detail"] = f"군량 +{change}"

        elif effect == "gold":
            # 금은 세력 단위
            if '금' in target:
                if isinstance(value, float):
                    change = int(target["금"] * abs(value))
                    if value < 0:
                        target["금"] = max(0, target["금"] - change)
                        result["detail"] = f"금 -{change}"
                    else:
                        target["금"] += change
                        result["detail"] = f"금 +{change}"
                else:
                    target["금"] += int(value)
                    result["detail"] = f"금 +{int(value)}"
            else:
                result["applied"] = False
                result["detail"] = "금 변동 없음"

        elif effect == "troops":
            # 성 기반: 병력
            if '병력' in target:
                change = int(target["병력"] * abs(value))
                if value < 0:
                    target["병력"] = max(100, target["병력"] - change)
                    result["detail"] = f"병력 -{change}"
                else:
                    target["병력"] += change
                    result["detail"] = f"병력 +{change}"

        elif effect == "agri":
            # 성 기반: 농업
            if '농업' in target:
                target["농업"] = max(10, target["농업"] + int(value))
                result["detail"] = f"농업 {int(value):+d}"

        elif effect == "hero_leave":
            # 성 기반: 장수 이탈
            heroes = target.get("장수", [])
            low_loyalty = [h for h in heroes if h["충성"] < 50]
            if low_loyalty and len(heroes) > 1:
                leaving = random.choice(low_loyalty)
                target["장수"].remove(leaving)
                leaving["충성"] = 50
                result["leaving_hero"] = leaving
                result["detail"] = f"{leaving['이름']} 이탈! (재야로 이동)"
            else:
                result["applied"] = False
                result["detail"] = "충성스러운 장수들이라 이탈자 없음"

        elif effect == "hero_join":
            # 새 장수 합류 - 성에 배치
            new_hero = {
                "이름": random.choice(["장각", "관평", "주창", "마대", "장포", "왕평", "요화", "마량"]),
                "무력": random.randint(70, 88),
                "지력": random.randint(60, 85),
                "매력": random.randint(60, 80),
                "통솔": random.randint(65, 85),
                "민첩": random.randint(65, 90),
                "운": random.randint(60, 85),
                "충성": random.randint(60, 80),
                "hp": 0, "max_hp": 0, "mp": 100, "max_mp": 100,
                "burn": 0, "stun": 0, "buff": 0, "debuff": 0,
                "부상": 0,
                "원소속": 0
            }
            if '장수' in target:
                target["장수"].append(new_hero)
            result["new_hero"] = new_hero
            result["detail"] = f"{new_hero['이름']} 합류! (무력:{new_hero['무력']} 통솔:{new_hero['통솔']})"

        return result


# ==========================================
# 데이터 & 유틸리티
# ==========================================
def get_valid_input(prompt, min_val, max_val):
    while True:
        try:
            val = input(prompt)
            if val.lower() == 'exit': return -1
            if not val.strip(): continue
            num = int(val)
            if min_val <= num <= max_val: return num
            print(f"  ⚠ {min_val}~{max_val} 사이 숫자를 입력하세요.")
        except ValueError: print("  ⚠ 숫자만 입력해주세요.")

def create_heroes(faction_idx):
    # (이름, 무력, 지력, 매력, 통솔, is_lord)
    # 군주는 첫번째, 스탯 최강
    base_data = {
        1: [("조조",88,96,95,98,True), ("하후돈",94,70,80,88,False), ("조인",88,85,82,90,False), ("순욱",30,98,92,75,False), ("곽가",25,99,88,70,False), ("허저",97,20,60,72,False), ("장료",93,82,85,92,False), ("사마의",40,99,90,88,False), ("전위",96,30,65,70,False), ("서황",91,75,72,85,False), ("장합",90,78,70,85,False), ("하후연",93,65,72,86,False), ("우금",85,72,68,82,False), ("악진",89,55,65,78,False), ("이전",82,78,75,80,False), ("조홍",84,60,70,75,False), ("조창",95,35,60,72,False), ("문빙",86,70,72,78,False), ("등애",78,92,65,88,False), ("종회",72,95,80,85,False), ("정욱",45,94,68,72,False), ("순유",40,96,82,78,False), ("만총",75,85,78,82,False), ("방덕",94,45,70,76,False), ("조진",82,75,72,80,False), ("채양",80,40,50,65,False), ("이각",82,35,30,60,False), ("곽사",81,38,32,58,False), ("화흠",70,82,85,75,False), ("유엽",35,88,80,70,False)],
        2: [("유비",75,78,100,92,True), ("관우",98,82,95,95,False), ("장비",99,40,70,80,False), ("제갈량",35,100,98,92,False), ("조운",97,88,96,90,False), ("황충",94,65,80,78,False), ("마초",96,50,75,82,False), ("방통",32,98,70,75,False), ("강유",90,92,85,88,False), ("위연",92,60,50,80,False)],
        3: [("손권",82,88,92,95,True), ("주유",80,97,96,94,False), ("육손",75,96,92,90,False), ("손책",94,78,92,88,False), ("태사자",95,68,80,82,False), ("감녕",96,65,74,78,False), ("여몽",85,92,82,86,False), ("노숙",50,94,90,80,False), ("황개",88,70,82,76,False), ("주태",92,50,75,74,False), ("능통",90,55,72,76,False), ("정보",86,68,78,82,False), ("한당",85,55,70,75,False), ("장흠",84,50,68,72,False), ("반장",82,45,55,70,False), ("서성",83,72,70,78,False), ("정봉",91,65,68,80,False), ("주환",87,78,72,82,False), ("주연",84,75,70,80,False), ("손환",80,70,75,78,False), ("장소",40,95,92,80,False), ("고옹",35,92,95,78,False), ("육항",78,94,85,88,False), ("손상향",85,65,92,72,False), ("제갈근",45,90,88,75,False), ("손견",94,72,88,90,False), ("오경",70,45,60,65,False), ("전종",78,60,65,70,False), ("동습",76,70,68,72,False), ("하제",72,58,55,68,False)],
        4: [("맹획",92,35,80,75,True), ("축융",88,45,85,72,False), ("올돌골",95,20,60,70,False), ("아회남",78,55,70,68,False), ("동도나",85,40,65,66,False)]
    }
    heroes = []
    for name, war, intell, charm, lead, is_lord in base_data[faction_idx]:
        agi = random.randint(60, 99)
        luck = random.randint(60, 99)
        if name in ["조운", "마초", "감녕", "장료", "손책", "여포"]: agi = min(100, agi + 10)
        if name in ["관우", "조조", "유비", "손권"]: luck = min(100, luck + 10)

        # 군주는 특별 스탯 보너스 + MP 200
        mp_max = 200 if is_lord else 100

        heroes.append({
            "이름": name, "무력": war, "지력": intell, "매력": charm,
            "통솔": lead, "민첩": agi, "운": luck,
            "충성": 100 if is_lord else random.randint(70, 95),  # 군주는 충성 100
            "hp": 0, "max_hp": 0, "mp": mp_max, "max_mp": mp_max,
            "burn": 0, "stun": 0, "buff": 0, "debuff": 0,
            "부상": 0,  # 부상 상태 (0이면 정상, 양수면 남은 월 수)
            "원소속": faction_idx,  # 원래 소속 세력 (포로/재야용)
            "is_lord": is_lord  # 군주 여부
        })
    return heroes


# ==========================================
# 게임 메인 클래스
# ==========================================
class Game:
    def __init__(self):
        self.year = 200  # 시작 연도
        self.month = 1   # 시작 월
        self.day = 1     # 시작 일 (1, 11, 21)
        self.actions_left = 3  # 월별 남은 행동 횟수
        self.acted_heroes = []  # 이번 달 행동한 장수 목록
        self.factions = {}
        self.player_id = 1
        self.free_heroes = []  # 재야 장수 목록
        self.prisoners = {}    # 포로 목록 {세력id: [장수들]}
        self.alliances = {}    # 동맹 목록 {세력id: {"대상": 상대세력id, "남은개월": int}}
        self.castles = {}      # 성 목록 {성이름: {...}}

    def setup(self):
        TUI.clear()
        sound_mgr.play("bgm_main.mp3")

        title_art = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     ⚔️  삼 국 지 : 패 왕 의  길  ⚔️                  ║
    ║                                                       ║
    ║         Three Kingdoms: Path of the Conqueror         ║
    ║                    [ v2.0 TUI Edition ]               ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
        """
        print(title_art)

        print(TUI.table(
            ["번호", "군주", "세력", "난이도"],
            [
                ["1", "조조", "위(魏)", "★☆☆ Easy"],
                ["2", "유비", "촉(蜀)", "★★★ Hard"],
                ["3", "손권", "오(吳)", "★★☆ Normal"],
                ["4", "맹획", "남만(南蠻)", "★★★ Hard"]
            ],
            [6, 8, 12, 14]
        ))

        self.player_id = get_valid_input("\n  군주를 선택하세요 (1~4): ", 1, 4)

        # 세력 초기화 (금만 세력 단위로 관리)
        self.factions[1] = {"이름":"조조", "금":5000}
        self.factions[2] = {"이름":"유비", "금":1500}
        self.factions[3] = {"이름":"손권", "금":3000}
        self.factions[4] = {"이름":"맹획", "금":1000}

        # 장수 생성
        wei_heroes = create_heroes(1)   # 조조군 10명
        shu_heroes = create_heroes(2)   # 유비군 10명
        wu_heroes = create_heroes(3)    # 손권군 10명
        nanman_heroes = create_heroes(4) # 맹획군 5명

        # 성 초기화 (13성)
        self.castles = {
            # === 조조(위) 6성 ===
            "허창": {
                "소속": 1, "수도": True,
                "장수": [wei_heroes[0], wei_heroes[3], wei_heroes[4], wei_heroes[7], wei_heroes[18], wei_heroes[19], wei_heroes[20], wei_heroes[21], wei_heroes[28], wei_heroes[29]],  # 조조, 순욱, 곽가, 사마의, 등애, 종회, 정욱, 순유, 화흠, 유엽
                "병력": 5000, "군량": 3000, "농업": 150, "상업": 150,
                "인접": ["낙양", "업", "진류"]
            },
            "낙양": {
                "소속": 1, "수도": False,
                "장수": [wei_heroes[1], wei_heroes[5], wei_heroes[10], wei_heroes[11], wei_heroes[16], wei_heroes[23]],  # 하후돈, 허저, 장합, 하후연, 조창, 방덕
                "병력": 3000, "군량": 2000, "농업": 120, "상업": 120,
                "인접": ["허창", "완성"]
            },
            "업": {
                "소속": 1, "수도": False,
                "장수": [wei_heroes[2], wei_heroes[12], wei_heroes[13], wei_heroes[24]],  # 조인, 우금, 악진, 조진
                "병력": 2500, "군량": 1500, "농업": 100, "상업": 100,
                "인접": ["허창", "서주"]
            },
            "서주": {
                "소속": 1, "수도": False,
                "장수": [wei_heroes[6], wei_heroes[14], wei_heroes[22]],  # 장료, 이전, 만총
                "병력": 2500, "군량": 1000, "농업": 80, "상업": 100,
                "인접": ["업", "건업"]
            },
            "완성": {
                "소속": 1, "수도": False,
                "장수": [wei_heroes[9], wei_heroes[15], wei_heroes[17]],  # 서황, 조홍, 문빙
                "병력": 2000, "군량": 1000, "농업": 80, "상업": 80,
                "인접": ["낙양", "한중"]
            },
            "진류": {
                "소속": 1, "수도": False,
                "장수": [wei_heroes[8], wei_heroes[25], wei_heroes[26], wei_heroes[27]],  # 전위, 채양, 이각, 곽사
                "병력": 1500, "군량": 500, "농업": 60, "상업": 60,
                "인접": ["허창"]
            },
            # === 유비(촉) 2성 ===
            "성도": {
                "소속": 2, "수도": True,
                "장수": [shu_heroes[0], shu_heroes[3], shu_heroes[4], shu_heroes[5], shu_heroes[7], shu_heroes[8]],  # 유비, 제갈량, 조운, 황충, 방통, 강유
                "병력": 3000, "군량": 2000, "농업": 100, "상업": 100,
                "인접": ["한중", "남중"]
            },
            "한중": {
                "소속": 2, "수도": False,
                "장수": [shu_heroes[1], shu_heroes[2], shu_heroes[6], shu_heroes[9]],  # 관우, 장비, 마초, 위연
                "병력": 2500, "군량": 1500, "농업": 80, "상업": 60,
                "인접": ["성도", "완성", "장사"]
            },
            # === 손권(오) 4성 ===
            "건업": {
                "소속": 3, "수도": True,
                "장수": [wu_heroes[0], wu_heroes[1], wu_heroes[7], wu_heroes[20], wu_heroes[21], wu_heroes[23], wu_heroes[24]],  # 손권, 주유, 노숙, 장소, 고옹, 손상향, 제갈근
                "병력": 4000, "군량": 2500, "농업": 120, "상업": 140,
                "인접": ["시상", "서주"]
            },
            "시상": {
                "소속": 3, "수도": False,
                "장수": [wu_heroes[3], wu_heroes[4], wu_heroes[11], wu_heroes[12], wu_heroes[25]],  # 손책, 태사자, 정보, 한당, 손견
                "병력": 2500, "군량": 1500, "농업": 100, "상업": 100,
                "인접": ["건업", "장사"]
            },
            "장사": {
                "소속": 3, "수도": False,
                "장수": [wu_heroes[2], wu_heroes[6], wu_heroes[10], wu_heroes[17], wu_heroes[18], wu_heroes[22]],  # 육손, 여몽, 능통, 주환, 주연, 육항
                "병력": 2000, "군량": 1000, "농업": 80, "상업": 80,
                "인접": ["시상", "여릉", "한중", "남중"]
            },
            "여릉": {
                "소속": 3, "수도": False,
                "장수": [wu_heroes[5], wu_heroes[8], wu_heroes[9], wu_heroes[13], wu_heroes[14], wu_heroes[15], wu_heroes[16], wu_heroes[19], wu_heroes[26], wu_heroes[27], wu_heroes[28], wu_heroes[29]],  # 감녕, 황개, 주태, 장흠, 반장, 서성, 정봉, 손환, 오경, 전종, 동습, 하제
                "병력": 1500, "군량": 800, "농업": 60, "상업": 60,
                "인접": ["장사"]
            },
            # === 맹획(남만) 1성 ===
            "남중": {
                "소속": 4, "수도": True,
                "장수": nanman_heroes,  # 전원 (맹획, 축융, 올돌골, 아회남, 동도나)
                "병력": 8000, "군량": 4000, "농업": 100, "상업": 50,
                "인접": ["성도", "장사"]
            }
        }

        # 포로 목록 초기화
        for fid in self.factions:
            self.prisoners[fid] = []

        # 재야 장수 초기화 (어느 세력에도 속하지 않은 인재들)
        self.free_heroes = [
            {"이름":"여포","무력":100,"지력":25,"통솔":70,"민첩":95,"운":40,"매력":45,"충성":50,"원소속":0,"is_lord":False,"부상":0},
            {"이름":"진궁","무력":45,"지력":96,"통솔":80,"민첩":65,"운":55,"매력":78,"충성":50,"원소속":0,"is_lord":False,"부상":0},
            {"이름":"장수","무력":90,"지력":55,"통솔":75,"민첩":80,"운":60,"매력":62,"충성":50,"원소속":0,"is_lord":False,"부상":0},
            {"이름":"장임","무력":88,"지력":60,"통솔":78,"민첩":72,"운":65,"매력":70,"충성":50,"원소속":0,"is_lord":False,"부상":0},
            {"이름":"엄안","무력":85,"지력":68,"통솔":82,"민첩":55,"운":70,"매력":80,"충성":50,"원소속":0,"is_lord":False,"부상":0},
            {"이름":"서서","무력":45,"지력":92,"통솔":72,"민첩":68,"운":80,"매력":82,"충성":50,"원소속":0,"is_lord":False,"부상":0},
            {"이름":"화타","무력":20,"지력":90,"통솔":50,"민첩":60,"운":85,"매력":95,"충성":50,"원소속":0,"is_lord":False,"부상":0},
        ]

        TUI.clear()

    def get_player(self): return self.factions[self.player_id]

    # === 성 시스템 헬퍼 함수 ===
    def get_faction_castles(self, faction_id):
        """세력이 보유한 성 목록 반환"""
        return {name: data for name, data in self.castles.items() if data['소속'] == faction_id}

    def get_faction_castle_count(self, faction_id):
        """세력의 성 개수 (영토) 반환"""
        return len(self.get_faction_castles(faction_id))

    def get_faction_total_troops(self, faction_id):
        """세력의 총 병력 반환"""
        return sum(c['병력'] for c in self.castles.values() if c['소속'] == faction_id)

    def get_faction_total_supply(self, faction_id):
        """세력의 총 군량 반환"""
        return sum(c['군량'] for c in self.castles.values() if c['소속'] == faction_id)

    def get_faction_heroes(self, faction_id):
        """세력의 모든 장수 반환"""
        heroes = []
        for castle in self.castles.values():
            if castle['소속'] == faction_id:
                heroes.extend(castle['장수'])
        return heroes

    def get_castle_by_hero(self, hero_name):
        """장수가 있는 성 이름 반환"""
        for castle_name, castle in self.castles.items():
            for h in castle['장수']:
                if h['이름'] == hero_name:
                    return castle_name
        return None

    def get_adjacent_enemy_castles(self, castle_name):
        """인접한 적 성 목록 반환"""
        castle = self.castles[castle_name]
        my_faction = castle['소속']
        enemy_castles = []
        for adj_name in castle['인접']:
            if self.castles[adj_name]['소속'] != my_faction:
                enemy_castles.append(adj_name)
        return enemy_castles

    def get_adjacent_friendly_castles(self, castle_name):
        """인접한 아군 성 목록 반환"""
        castle = self.castles[castle_name]
        my_faction = castle['소속']
        friendly_castles = []
        for adj_name in castle['인접']:
            if self.castles[adj_name]['소속'] == my_faction:
                friendly_castles.append(adj_name)
        return friendly_castles

    def save_game(self, slot=1, silent=False):
        """게임 저장"""
        save_data = {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "actions_left": self.actions_left,
            "acted_heroes": self.acted_heroes,
            "factions": self.factions,
            "player_id": self.player_id,
            "free_heroes": self.free_heroes,
            "prisoners": self.prisoners,
            "alliances": self.alliances,
            "castles": self.castles
        }
        filename = f"sam_save_{slot}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            if not silent:
                print(f"\n  💾 슬롯 {slot}에 저장 완료! ({filename})")
                print(f"     {self.get_date_string()} - {self.factions[self.player_id]['이름']}군")
                time.sleep(1)
            return True
        except Exception as e:
            if not silent:
                print(f"\n  ❌ 저장 실패: {e}")
            return False

    def auto_save(self):
        """매 턴 자동 저장 (슬롯 0)"""
        self.save_game(slot=0, silent=True)

    def load_game(self, slot=1):
        """게임 로드"""
        filename = f"sam_save_{slot}.json"
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            self.year = save_data["year"]
            self.month = save_data["month"]
            self.day = save_data["day"]
            self.actions_left = save_data["actions_left"]
            self.acted_heroes = save_data["acted_heroes"]
            # factions의 키를 정수로 변환
            self.factions = {int(k): v for k, v in save_data["factions"].items()}
            self.player_id = save_data["player_id"]
            self.free_heroes = save_data["free_heroes"]
            # prisoners의 키를 정수로 변환
            self.prisoners = {int(k): v for k, v in save_data["prisoners"].items()}
            self.alliances = {int(k): v for k, v in save_data["alliances"].items()} if save_data["alliances"] else {}
            # castles 로드
            self.castles = save_data.get("castles", {})
            print(f"\n  📂 슬롯 {slot} 로드 완료!")
            print(f"     {self.get_date_string()} - {self.factions[self.player_id]['이름']}군")
            time.sleep(1)
            return True
        except FileNotFoundError:
            print(f"\n  ❌ 저장 파일이 없습니다. ({filename})")
            return False
        except Exception as e:
            print(f"\n  ❌ 로드 실패: {e}")
            return False

    def show_save_slots(self, show_auto=False):
        """저장 슬롯 목록 표시"""
        print("\n┌─────────── 저장 슬롯 ───────────┐")
        # 자동 저장 슬롯 (로드 시에만 표시)
        if show_auto:
            filename = "sam_save_0.json"
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    date_str = f"{data['year']}년 {data['month']}월 {data['day']}일"
                    faction_name = data['factions'][str(data['player_id'])]['이름']
                    print(f"│  0. [자동] {faction_name}군 - {date_str}│")
                except:
                    print(f"│  0. [자동] (손상된 파일)          │")
            else:
                print(f"│  0. [자동] (비어있음)             │")
        for slot in range(1, 4):
            filename = f"sam_save_{slot}.json"
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    date_str = f"{data['year']}년 {data['month']}월 {data['day']}일"
                    faction_name = data['factions'][str(data['player_id'])]['이름']
                    print(f"│  {slot}. {faction_name}군 - {date_str}  │")
                except:
                    print(f"│  {slot}. (손상된 파일)              │")
            else:
                print(f"│  {slot}. (비어있음)                 │")
        print("└─────────────────────────────────┘")

    def get_date_string(self):
        """현재 날짜 문자열 반환"""
        return f"{self.year}년 {self.month}월 {self.day}일"

    def show_status(self):
        """현재 상태 표시"""
        pl = self.get_player()
        my_castles = self.get_faction_castles(self.player_id)
        total_troops = self.get_faction_total_troops(self.player_id)
        total_supply = self.get_faction_total_supply(self.player_id)
        total_heroes = len(self.get_faction_heroes(self.player_id))

        print(f"\n{'═' * 70}")
        print(f"  📜 {pl['이름']}의 천하통일기 - {self.get_date_string()}")
        print(f"  📅 이번 달 남은 행동: {self.actions_left}회")
        print(f"{'═' * 70}")

        # 세력 총괄 현황
        resources = [
            f"💰 금: {pl['금']:,}",
            f"🌾 총 군량: {total_supply:,}",
            f"⚔️ 총 병력: {total_troops:,}",
            f"🏰 보유 성: {len(my_castles)}개",
            f"👥 총 장수: {total_heroes}명"
        ]
        print(TUI.box("세력 총괄", resources, 68))

        # 보유 성 목록
        print(f"\n  🏯 보유 성 목록:")
        print(f"  {'─' * 66}")
        print(f"  {'성명':<8} {'병력':>8} {'군량':>8} {'농업':>6} {'상업':>6} {'장수':>6}  인접 적성")
        print(f"  {'─' * 66}")
        for castle_name, castle in my_castles.items():
            mark = "★" if castle['수도'] else " "
            hero_count = len(castle['장수'])
            enemy_adj = self.get_adjacent_enemy_castles(castle_name)
            enemy_str = ", ".join(enemy_adj) if enemy_adj else "-"
            print(f"  {mark}{castle_name:<7} {castle['병력']:>8,} {castle['군량']:>8,} {castle['농업']:>6} {castle['상업']:>6} {hero_count:>6}명  {enemy_str}")
        print(f"  {'─' * 66}")

        # 동맹 정보
        my_alliance = self.alliances.get(self.player_id)
        if my_alliance:
            ally_name = self.factions[my_alliance['대상']]['이름']
            print(f"  🤝 동맹: {ally_name}군 (남은 기간: {my_alliance['남은개월']}개월)")

    def show_commands(self):
        """명령어 메뉴"""
        print("\n┌──────────────────── 명 령 ────────────────────┐")
        print("│  1.농업   2.상업   3.포상   4.징병   5.전쟁  │")
        print("│  6.계략   7.정보   8.등용   9.외교   10.이동 │")
        print("│  11.저장  12.로드  0.종료                    │")
        print("└──────────────────────────────────────────────┘")

    def select_hero(self, msg, allow_injured=True, check_acted=True, mark_acted=True):
        """장수 선택 (전체 세력 장수 중 선택)
        allow_injured=False: 부상 장수 선택 불가
        check_acted=True: 이번 달 행동한 장수 선택 불가
        mark_acted=True: 선택 후 행동한 것으로 표시
        """
        my_heroes = self.get_faction_heroes(self.player_id)
        print(f"\n{'─' * 70}")
        print(f"  📋 장수 선택 - {msg}")
        print(f"{'─' * 70}")

        headers = ["#", "이름", "무력", "지력", "통솔", "민첩", "운", "충성", "상태"]
        rows = []
        available = []
        for i, h in enumerate(my_heroes):
            status = "정상"
            can_select = True

            if h.get('부상', 0) > 0:
                status = f"부상({h['부상']}월)"
                if not allow_injured:
                    can_select = False

            if check_acted and h['이름'] in self.acted_heroes:
                status = "행동완료"
                can_select = False

            rows.append([
                str(i+1), h['이름'],
                str(h['무력']), str(h['지력']), str(h['통솔']),
                str(h['민첩']), str(h['운']),
                str(h['충성']), status
            ])

            if can_select:
                available.append(i+1)

        print(TUI.table(headers, rows, [3, 8, 5, 5, 5, 5, 5, 5, 10]))

        if len(available) == 0:
            print("  ❌ 선택 가능한 장수가 없습니다!")
            return None

        while True:
            idx = get_valid_input("  번호 선택: ", 1, len(my_heroes))
            if idx in available:
                hero = my_heroes[idx-1]
                if mark_acted:
                    self.acted_heroes.append(hero['이름'])
                return hero
            else:
                h = my_heroes[idx-1]
                if h.get('부상', 0) > 0:
                    print(f"  ⚠ {h['이름']}은(는) 부상 중입니다.")
                elif h['이름'] in self.acted_heroes:
                    print(f"  ⚠ {h['이름']}은(는) 이번 달 이미 행동했습니다.")

    def get_battle_stats(self, hero):
        w = hero['무력']
        i = hero['지력']
        if hero['buff'] > 0: w *= 1.15; i *= 1.15
        if hero['debuff'] > 0: w = max(0, w * 0.85); i = max(0, i * 0.85)
        return int(w), int(i)

    def calc_crit(self, base_val, luck, is_heal=False):
        chance = luck / 4.0
        is_crit = random.random() * 100 < chance

        variation = random.randint(int(base_val * -0.1), int(base_val * 0.1))
        final_val = base_val + variation

        if is_crit:
            final_val = int(final_val * 1.5)
            msg = "✨ 대박!" if is_heal else "⚡ 치명타!"
            sound_mgr.play("sfx_crit.wav")
            return final_val, True, msg
        return final_val, False, ""

    def get_double_chance(self, agi):
        return agi / 4.0

    def pad_kr(self, text, width):
        """한글 포함 문자열 패딩"""
        display_len = sum(2 if ord(c) > 127 else 1 for c in str(text))
        return str(text) + " " * max(0, width - display_len)

    def get_state_icons(self, h):
        """상태이상 아이콘 반환"""
        s = ""
        if h.get('buff', 0) > 0: s += f"{C.GREEN}↑{h['buff']}{C.RESET}"
        if h.get('debuff', 0) > 0: s += f"{C.RED}↓{h['debuff']}{C.RESET}"
        if h.get('burn', 0) > 0: s += f"{C.RED}🔥{C.RESET}"
        if h.get('stun', 0) > 0: s += f"{C.YELLOW}💫{C.RESET}"
        if h.get('poison', 0) > 0: s += f"{C.MAGENTA}☠{C.RESET}"
        if h.get('defend_buff', 0) > 0: s += f"{C.CYAN}🛡{C.RESET}"
        return s if s else ""

    def hp_color(self, hp, max_hp):
        """HP 비율에 따른 색상"""
        ratio = hp / max_hp if max_hp > 0 else 0
        if ratio > 0.5: return C.GREEN
        elif ratio > 0.25: return C.YELLOW
        else: return C.RED

    def show_battle_status_3v3(self, my_party, enemy_party, turn, current_actor=None):
        """3vs3 전투 상태 표시"""
        print(f"\n{C.BOLD}{C.CYAN}═══════════════ BATTLE Turn {turn} ═══════════════{C.RESET}")

        # 아군 표시
        print(f"{C.BLUE}【 아 군 】{C.RESET}")
        for i, h in enumerate(my_party):
            if h['hp'] <= 0:
                print(f"  {C.GRAY}{i+1}. {h['이름']} [전사]{C.RESET}")
                continue
            hp_bar = TUI.progress_bar(h['hp'], h['max_hp'], 12)
            hp_col = self.hp_color(h['hp'], h['max_hp'])
            state = self.get_state_icons(h)
            marker = f"{C.YELLOW}▶{C.RESET}" if current_actor and current_actor['이름'] == h['이름'] else " "
            print(f" {marker}{i+1}. {self.pad_kr(h['이름'], 6)} HP:{hp_col}{hp_bar}{int(h['hp']):>5}{C.RESET} MP:{h['mp']:>3} 민:{h['민첩']:>2} {state}")

        print(f"{C.GRAY}{'─' * 55}{C.RESET}")

        # 적군 표시
        print(f"{C.RED}【 적 군 】{C.RESET}")
        for i, h in enumerate(enemy_party):
            if h['hp'] <= 0:
                print(f"  {C.GRAY}{i+1}. {h['이름']} [전사]{C.RESET}")
                continue
            hp_bar = TUI.progress_bar(h['hp'], h['max_hp'], 12)
            hp_col = self.hp_color(h['hp'], h['max_hp'])
            state = self.get_state_icons(h)
            marker = f"{C.RED}▶{C.RESET}" if current_actor and current_actor['이름'] == h['이름'] else " "
            print(f" {marker}{i+1}. {self.pad_kr(h['이름'], 6)} HP:{hp_col}{hp_bar}{int(h['hp']):>5}{C.RESET} MP:{h['mp']:>3} 민:{h['민첩']:>2} {state}")

        print(f"{C.CYAN}{'═' * 55}{C.RESET}")

    def select_target(self, enemy_party, skill_type="single", target_count=1):
        """타겟 선택 (플레이어용)"""
        alive = [(i, h) for i, h in enumerate(enemy_party) if h['hp'] > 0]
        if not alive:
            return None

        if skill_type == "all":
            print(f"  {C.YELLOW}▶ 전체 대상 스킬{C.RESET}")
            return [h for _, h in alive]

        if skill_type == "multi":
            count = min(target_count, len(alive))
            print(f"  {C.YELLOW}▶ 다중 대상 스킬 ({count}명){C.RESET}")
            if len(alive) <= count:
                return [h for _, h in alive]
            # 플레이어가 직접 선택
            targets = []
            for t in range(count):
                print(f"\n  {C.CYAN}▶ {t+1}번째 대상 선택:{C.RESET}")
                remaining = [(i, h) for i, h in alive if h not in targets]
                for idx, h in remaining:
                    hp_pct = int(h['hp'] / h['max_hp'] * 100)
                    state = self.get_state_icons(h)
                    print(f"    {idx+1}. {h['이름']} (HP:{hp_pct}%) {state}")
                while True:
                    choice = get_valid_input("    타겟: ", 1, len(enemy_party))
                    sel = enemy_party[choice-1]
                    if sel['hp'] > 0 and sel not in targets:
                        targets.append(sel)
                        break
                    print("    ⚠ 선택 불가 대상입니다.")
            return targets

        print(f"\n  {C.YELLOW}▶ 타겟 선택:{C.RESET}")
        for idx, h in alive:
            hp_pct = int(h['hp'] / h['max_hp'] * 100)
            state = self.get_state_icons(h)
            print(f"    {idx+1}. {h['이름']} (HP:{hp_pct}%) {state}")

        while True:
            choice = get_valid_input("    타겟: ", 1, len(enemy_party))
            if enemy_party[choice-1]['hp'] > 0:
                return enemy_party[choice-1]
            print("    ⚠ 이미 전사한 대상입니다.")

    def select_ally_target(self, my_party, actor, skill_type="single", target_count=1):
        """아군 타겟 선택 (회복/버프용)"""
        alive = [(i, h) for i, h in enumerate(my_party) if h['hp'] > 0]
        if not alive:
            return None

        if skill_type == "all":
            print(f"  {C.GREEN}▶ 아군 전체 대상{C.RESET}")
            return [h for _, h in alive]

        if skill_type == "multi":
            count = min(target_count, len(alive))
            print(f"  {C.GREEN}▶ 아군 다중 대상 ({count}명){C.RESET}")
            if len(alive) <= count:
                return [h for _, h in alive]
            # 플레이어가 직접 선택
            targets = []
            for t in range(count):
                print(f"\n  {C.CYAN}▶ {t+1}번째 아군 선택:{C.RESET}")
                remaining = [(i, h) for i, h in alive if h not in targets]
                for idx, h in remaining:
                    hp_pct = int(h['hp'] / h['max_hp'] * 100)
                    state = self.get_state_icons(h)
                    marker = "(본인)" if h['이름'] == actor['이름'] else ""
                    print(f"    {idx+1}. {h['이름']} (HP:{hp_pct}%) {state} {marker}")
                while True:
                    choice = get_valid_input("    대상: ", 1, len(my_party))
                    sel = my_party[choice-1]
                    if sel['hp'] > 0 and sel not in targets:
                        targets.append(sel)
                        break
                    print("    ⚠ 선택 불가 대상입니다.")
            return targets

        print(f"\n  {C.GREEN}▶ 아군 타겟 선택:{C.RESET}")
        for idx, h in alive:
            hp_pct = int(h['hp'] / h['max_hp'] * 100)
            state = self.get_state_icons(h)
            marker = "(본인)" if h['이름'] == actor['이름'] else ""
            print(f"    {idx+1}. {h['이름']} (HP:{hp_pct}%) {state} {marker}")

        while True:
            choice = get_valid_input("    대상: ", 1, len(my_party))
            if my_party[choice-1]['hp'] > 0:
                return my_party[choice-1]
            print("    ⚠ 선택 불가 대상입니다.")

    def get_state_icons(self, h):
        """상태이상 아이콘 문자열 반환"""
        icons = []
        if h.get('burn', 0) > 0: icons.append(f"🔥{h['burn']}")
        if h.get('poison', 0) > 0: icons.append(f"☠️{h['poison']}")
        if h.get('stun', 0) > 0: icons.append(f"💫{h['stun']}")
        if h.get('buff', 0) > 0: icons.append(f"💪{h['buff']}")
        if h.get('debuff', 0) > 0: icons.append(f"🔽{h['debuff']}")
        if h.get('defend_buff', 0) > 0: icons.append(f"🛡️{h['defend_buff']}")
        if h.get('oath_protect', 0) > 0: icons.append(f"🍑{h['oath_protect']}")
        return ' '.join(icons) if icons else ''

    def show_battle_status_3v3(self, my_party, enemy_party, turn, current_actor=None):
        """3vs3 전투 상태 표시"""
        print(f"\n{C.YELLOW}{'═' * 60}{C.RESET}")
        print(f"  {C.WHITE}턴 {turn}{C.RESET}")
        print(f"{C.YELLOW}{'═' * 60}{C.RESET}")

        # 아군
        print(f"  {C.BLUE}◆ 아 군 ◆{C.RESET}")
        for h in my_party:
            if h['hp'] <= 0:
                print(f"    💀 {h['이름']} (전사)")
                continue
            hp_pct = int(h['hp'] / h['max_hp'] * 100)
            hp_bar = '█' * (hp_pct // 10) + '░' * (10 - hp_pct // 10)
            hp_col = C.GREEN if hp_pct > 50 else (C.YELLOW if hp_pct > 25 else C.RED)
            marker = f"{C.CYAN}▶{C.RESET}" if current_actor and h['이름'] == current_actor['이름'] else " "
            state = self.get_state_icons(h)
            print(f"  {marker} {self.pad_kr(h['이름'], 6)} HP:{hp_col}{hp_bar}{int(h['hp']):>5}{C.RESET} MP:{h['mp']:>3} {state}")

        print(f"  {C.CYAN}{'─' * 50}{C.RESET}")

        # 적군
        print(f"  {C.RED}◆ 적 군 ◆{C.RESET}")
        for h in enemy_party:
            if h['hp'] <= 0:
                print(f"    💀 {h['이름']} (전사)")
                continue
            hp_pct = int(h['hp'] / h['max_hp'] * 100)
            hp_bar = '█' * (hp_pct // 10) + '░' * (10 - hp_pct // 10)
            hp_col = C.GREEN if hp_pct > 50 else (C.YELLOW if hp_pct > 25 else C.RED)
            state = self.get_state_icons(h)
            print(f"    {self.pad_kr(h['이름'], 6)} HP:{hp_col}{hp_bar}{int(h['hp']):>5}{C.RESET} MP:{h['mp']:>3} {state}")

        print(f"{C.YELLOW}{'═' * 60}{C.RESET}")

    def show_battle_status(self, p, e, turn):
        """전투 상태 표시 (색깔 기반) - 호환성 유지"""
        p_war, p_int = self.get_battle_stats(p)
        e_war, e_int = self.get_battle_stats(e)

        p_crit = int(p['운']/4.0)
        p_dbl = int(p['민첩']/4.0)
        e_crit = int(e['운']/4.0)
        e_dbl = int(e['민첩']/4.0)

        print(f"\n{C.BOLD}{C.CYAN}═══ BATTLE Turn {turn} ═══{C.RESET}")

        # 아군
        p_hp_bar = TUI.progress_bar(p['hp'], p['max_hp'], 15)
        p_mp_bar = TUI.progress_bar(p['mp'], p['max_mp'], 8, "▓", "░")
        p_hp_col = self.hp_color(p['hp'], p['max_hp'])
        print(f"{C.BLUE}▶ {p['이름']}{C.RESET} {self.get_state_icons(p)}")
        print(f"  HP: {p_hp_col}{p_hp_bar} {int(p['hp']):>5}/{p['max_hp']}{C.RESET}")
        print(f"  MP: {C.CYAN}{p_mp_bar} {p['mp']:>3}/{p['max_mp']}{C.RESET}  무:{p_war} 지:{p_int} [치명{p_crit}% 연격{p_dbl}%]")

        print(f"{C.GRAY}{'─' * 50}{C.RESET}")

        # 적군
        e_hp_bar = TUI.progress_bar(e['hp'], e['max_hp'], 15)
        e_mp_bar = TUI.progress_bar(e['mp'], e['max_mp'], 8, "▓", "░")
        e_hp_col = self.hp_color(e['hp'], e['max_hp'])
        print(f"{C.RED}▶ {e['이름']}{C.RESET} {self.get_state_icons(e)}")
        print(f"  HP: {e_hp_col}{e_hp_bar} {int(e['hp']):>5}/{e['max_hp']}{C.RESET}")
        print(f"  MP: {C.CYAN}{e_mp_bar} {e['mp']:>3}/{e['max_mp']}{C.RESET}  무:{e_war} 지:{e_int} [치명{e_crit}% 연격{e_dbl}%]")
        enemy_skills = HeroSkills.show_enemy_skills(e['이름'])
        print(f"  {C.GRAY}스킬: {enemy_skills}{C.RESET}")

    def calc_defense(self, target):
        """통솔력 + 방어버프 기반 방어력 계산 (데미지 감소율 %)"""
        base_def = int(target['통솔'] * 0.4)
        # 철벽 방어 버프시 추가 방어력
        if target.get('defend_buff', 0) > 0:
            base_def += int(target['통솔'] * 0.3)
        return min(60, base_def)  # 최대 60% 감소

    def apply_damage(self, target, base_damage, attacker_luck=50):
        """방어력 적용하여 최종 데미지 계산 및 적용"""
        defense_rate = self.calc_defense(target)
        damage_reduction = base_damage * defense_rate / 100
        final_damage = max(1, int(base_damage - damage_reduction))
        damage, is_crit, msg = self.calc_crit(final_damage, attacker_luck)
        target['hp'] -= damage
        # 도원결의 불멸 효과: HP 1 이하로 안 떨어짐
        if target.get('oath_protect', 0) > 0 and target['hp'] <= 0:
            target['hp'] = 1
            msg += f" {C.YELLOW}[도원결의!]{C.RESET}"
        return damage, is_crit, msg, defense_rate

    def execute_battle(self, my_party, enemy_party, is_defense=False, my_faction=None, enemy_faction=None, from_castle=None, target_castle=None):
        """3vs3 전투 실행 - 민첩 기반 행동 순서
        Returns: (승리여부, 아군부상자, 적군부상자, 아군포로, 적군포로)
        from_castle: 아군 출발 성 (공격시) 또는 방어 성 (방어시)
        target_castle: 적군 성
        """
        TUI.clear()  # 전투 화면 시작
        sound_mgr.play("bgm_battle.mp3")
        turn = 1
        my_injured = []      # 아군 부상자
        enemy_injured = []   # 적군 부상자
        my_captured = []     # 아군 포로 (적에게 잡힘)
        enemy_captured = []  # 적군 포로 (아군에게 잡힘)

        # 살아있는 장수 확인 함수
        def alive_my(): return [h for h in my_party if h['hp'] > 0]
        def alive_enemy(): return [h for h in enemy_party if h['hp'] > 0]

        while alive_my() and alive_enemy():
            # 화면 클리어 먼저
            TUI.clear()

            # ===== 군량 소모 시스템 (성 기반) =====
            rice_per_turn = len(alive_my()) * 50  # 장수당 50 군량
            enemy_rice_per_turn = len(alive_enemy()) * 50
            rice_msg = []  # 군량 관련 메시지 수집

            # 아군 군량 소모 (성 기반)
            if from_castle:
                from_castle['군량'] -= rice_per_turn
                if from_castle['군량'] <= 0:
                    from_castle['군량'] = 0
                    rice_msg.append(f"  {C.RED}⚠️ 군량 고갈! 아군 사기 저하!{C.RESET}")
                    for ally in alive_my():
                        ally['hp'] = int(ally['hp'] * 0.9)
                        ally['debuff'] = max(ally.get('debuff', 0), 2)
                    if turn > 5 and from_castle['군량'] <= 0:
                        rice_msg.append(f"  {C.RED}💀 굶주림으로 전투 지속 불가! 퇴각!{C.RESET}")
                        TUI.clear()
                        for msg in rice_msg:
                            print(msg)
                        time.sleep(1.5)
                        return False, my_injured, enemy_injured, my_captured + alive_my(), enemy_captured

            # 적군 군량 소모 (성 기반)
            if target_castle:
                target_castle['군량'] -= enemy_rice_per_turn
                if target_castle['군량'] <= 0:
                    target_castle['군량'] = 0
                    rice_msg.append(f"  {C.GREEN}⚠️ 적군 군량 고갈! 적 사기 저하!{C.RESET}")
                    for enemy in alive_enemy():
                        enemy['hp'] = int(enemy['hp'] * 0.9)
                        enemy['debuff'] = max(enemy.get('debuff', 0), 2)
                    if turn > 5 and target_castle['군량'] <= 0:
                        rice_msg.append(f"  {C.GREEN}🎉 적군 굶주림! 승리!{C.RESET}")
                        TUI.clear()
                        for msg in rice_msg:
                            print(msg)
                        time.sleep(1.5)
                        return True, my_injured, enemy_injured, my_captured, enemy_captured + alive_enemy()

            # MP 회복 (모든 살아있는 장수)
            for h in alive_my() + alive_enemy():
                if h['mp'] < h['max_mp']:
                    h['mp'] = min(h['max_mp'], h['mp'] + 10)

            # 방어전 보너스: 방어측 3% HP 회복
            defense_bonus_msg = []
            if is_defense and turn > 1:
                for defender in alive_my():
                    if defender['hp'] < defender['max_hp']:
                        heal_amount = int(defender['max_hp'] * 0.03)
                        defender['hp'] = min(defender['max_hp'], defender['hp'] + heal_amount)
                        defense_bonus_msg.append(f"  🏰 [방어 보너스] {defender['이름']} HP +{heal_amount}")

            # 3vs3 전투 상태 표시
            self.show_battle_status_3v3(my_party, enemy_party, turn)
            for msg in rice_msg:
                print(msg)
            for msg in defense_bonus_msg:
                print(msg)

            # 군량 상태 표시 (성 기반)
            if from_castle and target_castle:
                my_rice = from_castle['군량']
                e_rice = target_castle['군량']
                my_col = C.GREEN if my_rice > 500 else (C.YELLOW if my_rice > 0 else C.RED)
                e_col = C.GREEN if e_rice > 500 else (C.YELLOW if e_rice > 0 else C.RED)
                print(f"  {C.BLUE}아군 군량:{my_col}{my_rice:,}{C.RESET} | {C.RED}적군 군량:{e_col}{e_rice:,}{C.RESET}")

            # 상태이상 처리 (모든 살아있는 장수)
            skip_actors = set()
            for h in alive_my() + alive_enemy():
                # 버프/디버프 감소
                if h.get('buff', 0) > 0: h['buff'] -= 1
                if h.get('debuff', 0) > 0: h['debuff'] -= 1

                # 화상 데미지
                if h.get('burn', 0) > 0:
                    dmg = int(h['max_hp'] * 0.05) + 50
                    h['hp'] -= dmg
                    h['burn'] -= 1
                    print(f"  🔥 {h['이름']} 화상 데미지 -{dmg}")

                # 독 데미지
                if h.get('poison', 0) > 0:
                    dmg = int(h['max_hp'] * 0.04) + 30
                    h['hp'] -= dmg
                    h['poison'] -= 1
                    print(f"  ☠️ {h['이름']} 중독 데미지 -{dmg}")

                # 방어 버프 감소
                if h.get('defend_buff', 0) > 0:
                    h['defend_buff'] -= 1

                # 도원결의 불멸 효과 감소
                if h.get('oath_protect', 0) > 0:
                    h['oath_protect'] -= 1

                # 기절 체크 (15% 확률로 조기 해제)
                if h.get('stun', 0) > 0:
                    if random.random() < 0.15:
                        print(f"  ✨ {h['이름']} 정신 차림!")
                        h['stun'] = 0
                    else:
                        print(f"  💫 {h['이름']} 행동 불가")
                        h['stun'] -= 1
                        skip_actors.add(h['이름'])

            # 죽은 장수 처리
            for h in my_party[:]:
                if h['hp'] <= 0:
                    print(f"\n  💀 아군 {h['이름']} 전사!")
                    my_party.remove(h)
                    h['부상'] = random.randint(2, 4)
                    my_injured.append(h)
                    if random.random() < 0.25:
                        my_captured.append(h)
                        print(f"     → ⛓️ 적에게 사로잡힘!")

            for h in enemy_party[:]:
                if h['hp'] <= 0:
                    print(f"\n  💀 적장 {h['이름']} 전사!")
                    enemy_party.remove(h)
                    h['부상'] = random.randint(2, 4)
                    enemy_injured.append(h)
                    if random.random() < 0.25:
                        enemy_captured.append(h)
                        print(f"     → ⛓️ 아군이 사로잡음!")

            if not alive_my() or not alive_enemy():
                break

            # ===== 민첩 기반 행동 순서 결정 =====
            all_actors = []
            for h in alive_my():
                all_actors.append((h, "player", self.get_battle_stats(h)))
            for h in alive_enemy():
                all_actors.append((h, "enemy", self.get_battle_stats(h)))

            # 민첩 + 랜덤 요소로 정렬
            all_actors.sort(key=lambda x: x[0]['민첩'] + random.randint(-10, 10), reverse=True)

            print(f"\n  {C.CYAN}▶ 행동 순서: {', '.join([a[0]['이름'] for a in all_actors])}{C.RESET}")

            # ===== 3vs3 각 장수 행동 =====
            for actor, side, (war, intel) in all_actors:
                # 이미 죽은 장수 건너뛰기
                if actor['hp'] <= 0:
                    continue

                # 기절 상태면 건너뛰기
                if actor['이름'] in skip_actors:
                    continue

                # 적 전멸 체크
                if side == "player" and not alive_enemy():
                    break
                if side == "enemy" and not alive_my():
                    break

                if side == "player":
                    # ===== 아군 턴 - 타겟 선택 가능 =====
                    print(f"\n  {C.BLUE}▶▶ {actor['이름']}의 턴 ◀◀{C.RESET}")
                    self.show_battle_status_3v3(my_party, enemy_party, turn, actor)

                    while True:
                        skills = HeroSkills.show_skills(actor['이름'], actor['mp'])
                        cmd = get_valid_input("  명령: ", 1, len(skills))
                        skill_id = skills[cmd - 1]
                        skill_info = HeroSkills.get_skill_info(skill_id)

                        # MP 체크
                        if actor['mp'] < skill_info['mp']:
                            print(f"  ❌ MP 부족 (필요: {skill_info['mp']}, 현재: {actor['mp']}) - 다시 선택하세요")
                            continue
                        break

                    acted = False
                    actor['mp'] -= skill_info['mp']

                    # 타겟 결정 (스킬 타입에 따라)
                    target = None
                    targets = None
                    skill_type = skill_info.get('type', 'physical')

                    if skill_type in ['physical', 'magic'] and skill_id not in ['heal', 'rally', 'defend', 'rest', 'support', 'inspire', 'drill']:
                        target = self.select_target(enemy_party, "single")
                    elif skill_type in ['physical_multi', 'magic_multi', 'debuff_multi']:
                        count = 3 if 'triple' in skill_id or 'trio' in skill_id else 2
                        targets = self.select_target(enemy_party, "multi", count)
                    elif skill_type in ['physical_aoe', 'magic_aoe']:
                        targets = self.select_target(enemy_party, "all")
                    elif skill_type in ['heal_multi', 'buff_multi']:
                        count = 3 if 'trio' in skill_id or 'mass' in skill_id else 2
                        targets = self.select_ally_target(my_party, actor, "multi", count)
                    elif skill_type in ['heal_all', 'buff_all']:
                        targets = self.select_ally_target(my_party, actor, "all")

                    # 단일 타겟이 없으면 첫 번째 적 선택
                    if target is None and targets is None and skill_id not in ['heal', 'rally', 'defend', 'rest', 'support', 'inspire', 'drill',
                                                                                  'group_heal', 'mass_heal', 'duo_rally', 'trio_rally', 'war_drum', 'iron_wall']:
                        alive = [h for h in enemy_party if h['hp'] > 0]
                        if alive:
                            target = alive[0]

                    # ===== 스킬별 효과 처리 =====
                    if skill_id == "attack":
                        sound_mgr.play("sfx_attack.wav")
                        HeroDialogue.say(actor['이름'], "attack")
                        base_dmg = int(war * 9)
                        dmg, _, msg, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                        print(f"  ⚔️ {actor['이름']} → {target['이름']} 공격! {msg} {dmg} 피해 (방어{def_rate}%)")
                        if target['hp'] > 0 and dmg > 300:
                            HeroDialogue.say(target['이름'], "hurt")
                        acted = True

                    elif skill_id == "fire":
                        HeroDialogue.say(actor['이름'], "skill")
                        if random.randint(0, 100) < intel:
                            sound_mgr.play("sfx_fire.wav")
                            base_dmg = int(intel * 5)
                            dmg, _, msg, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                            target['burn'] = 3
                            print(f"  🔥 {actor['이름']} → {target['이름']} 화계! {msg} {dmg} 피해 + 화상 3턴")
                        else:
                            print(f"  ☁️ {actor['이름']} 화계 실패...")
                        acted = True

                    elif skill_id == "thunder":
                        sound_mgr.play("sfx_magic.wav")
                        HeroDialogue.say(actor['이름'], "skill")
                        if random.randint(0, 100) < intel + 30:
                            base_dmg = int(intel * 18)
                            dmg, _, msg, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                            print(f"  {C.YELLOW}⚡ {actor['이름']} → {target['이름']} 낙뢰!{C.RESET} {msg} {C.RED}{dmg}{C.RESET} 피해!")
                            if random.random() < 0.4:
                                target['stun'] = 2
                                print(f"     💫 {target['이름']} 감전! 기절!")
                        else:
                            print(f"  ☁️ {actor['이름']} 낙뢰 실패...")
                        acted = True

                    elif skill_id == "confuse":
                        sound_mgr.play("sfx_magic.wav")
                        t_int = self.get_battle_stats(target)[1] if target else 50
                        if random.randint(0, 100) < (60 + intel - t_int):
                            target['stun'] = 3
                            print(f"  💫 {actor['이름']} → {target['이름']} 혼란 성공! 기절!")
                        else:
                            print(f"  🛡️ {actor['이름']} 혼란 실패")
                        acted = True

                    elif skill_id == "heal":
                        sound_mgr.play("sfx_heal.wav")
                        # 아군 타겟 선택
                        heal_target = self.select_ally_target(my_party, actor, "single")
                        if heal_target:
                            h, c, m = self.calc_crit(int(intel * 3.5) + 200, actor['운'], is_heal=True)
                            heal_target['hp'] = min(heal_target['max_hp'], heal_target['hp'] + h)
                            print(f"  💊 {actor['이름']} → {heal_target['이름']} 치유 {m} (+{h})")
                        acted = True

                    elif skill_id == "rally":
                        sound_mgr.play("sfx_buff.wav")
                        actor['buff'] = min(10, actor.get('buff', 0) + 3)
                        print(f"  💪 {actor['이름']} 격려! 버프 +3턴! (현재 {actor['buff']}턴)")
                        acted = True

                    elif skill_id == "taunt":
                        sound_mgr.play("sfx_debuff.wav")
                        HeroDialogue.say(actor['이름'], "taunt")
                        t_int = self.get_battle_stats(target)[1] if target else 50
                        chance = 50 + (intel - t_int)
                        print(f"  🤬 {actor['이름']} → {target['이름']} 욕설! (확률 {min(100, max(0, chance))}%)", end="... ")
                        if random.randint(0, 100) < chance:
                            target['debuff'] = min(10, target.get('debuff', 0) + 3)
                            print(f"성공! 디버프 +3턴!")
                        else:
                            print("실패!")
                        acted = True

                    elif skill_id == "rest":
                        actor['mp'] = min(actor['max_mp'], actor['mp'] + 30)
                        print(f"  💤 {actor['이름']} 휴식 (MP +30)")

                    elif skill_id == "support":
                        if from_castle is None:
                            print("  ❌ 지원 불가 (성 정보 없음)")
                            actor['mp'] += skill_info['mp']
                        elif from_castle['병력'] < 500:
                            print("  ❌ 지원 병력 부족!")
                            actor['mp'] += skill_info['mp']
                        else:
                            support_troops = int(actor['통솔'] * 30)
                            support_troops = min(support_troops, from_castle['병력'] - 100)
                            heal_amount = support_troops
                            from_castle['병력'] -= support_troops
                            actor['hp'] = min(actor['max_hp'], actor['hp'] + heal_amount)
                            sound_mgr.play("sfx_heal.wav")
                            print(f"  🚩 {actor['이름']} 지원군! 병력 -{support_troops} → HP +{heal_amount}")
                            acted = True

                    elif skill_id == "charge":
                        sound_mgr.play("sfx_attack.wav")
                        HeroDialogue.say(actor['이름'], "attack")
                        base_dmg = int((war * 8) + (actor['민첩'] * 5))
                        dmg, _, msg, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                        print(f"  {C.GREEN}🐎 {actor['이름']} → {target['이름']} 돌격!{C.RESET} {msg} {C.RED}{dmg}{C.RESET} 피해!")
                        if random.random() < 0.3:
                            actor['buff'] = min(10, actor.get('buff', 0) + 2)
                            print(f"     ⚡ 기세 상승! 버프 +2턴!")
                        acted = True

                    elif skill_id == "combo":
                        sound_mgr.play("sfx_attack.wav")
                        HeroDialogue.say(actor['이름'], "skill")
                        base_dmg = int((war * 8) + (intel * 7))
                        dmg, _, msg, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                        print(f"  {C.MAGENTA}🌀 {actor['이름']} → {target['이름']} 연환계!{C.RESET} {msg} {C.RED}{dmg}{C.RESET} 피해!")
                        if intel > 70 and random.random() < 0.5:
                            target['debuff'] = 3
                            print(f"     🔽 {target['이름']} 혼란!")
                        acted = True

                    elif skill_id == "arrow":
                        sound_mgr.play("sfx_attack.wav")
                        hits = random.randint(3, 5)
                        total_dmg = 0
                        for i in range(hits):
                            base_dmg = int(war * 4)
                            dmg, _, _, _ = self.apply_damage(target, base_dmg, actor['운'])
                            total_dmg += dmg
                        print(f"  🏹 {actor['이름']} → {target['이름']} 난사! {hits}연속! 총 {C.RED}{total_dmg}{C.RESET} 피해!")
                        acted = True

                    elif skill_id == "defend":
                        sound_mgr.play("sfx_buff.wav")
                        actor['defend_buff'] = min(10, actor.get('defend_buff', 0) + 3)
                        print(f"  🛡️ {actor['이름']} 철벽 방어! 방어버프 +3턴!")
                        acted = True

                    elif skill_id == "poison":
                        sound_mgr.play("sfx_magic.wav")
                        t_int = self.get_battle_stats(target)[1] if target else 50
                        if random.randint(0, 100) < (50 + intel - t_int):
                            target['poison'] = 4
                            print(f"  ☠️ {actor['이름']} → {target['이름']} 독계! 중독 4턴!")
                        else:
                            print(f"  💨 {actor['이름']} 독계 실패...")
                        acted = True

                    elif skill_id == "inspire":
                        sound_mgr.play("sfx_buff.wav")
                        for ally in alive_my():
                            ally['buff'] = min(10, ally.get('buff', 0) + 4)
                            ally['hp'] = min(ally['max_hp'], ally['hp'] + 200)
                        print(f"  {C.CYAN}📯 {actor['이름']} 고무!{C.RESET} 전군 버프 +4턴! + HP회복!")
                        acted = True

                    elif skill_id == "drill":
                        sound_mgr.play("sfx_buff.wav")
                        agi_up = 20 + random.randint(10, 20)
                        luck_up = 20 + random.randint(10, 20)
                        actor['민첩'] += agi_up
                        actor['운'] += luck_up
                        print(f"  {C.GREEN}🎯 {actor['이름']} 조련!{C.RESET} 민첩 +{agi_up}, 운 +{luck_up}!")
                        acted = True

                    # ===== 새로운 다중 타겟 스킬 =====
                    elif skill_id == "twin_strike":
                        sound_mgr.play("sfx_attack.wav")
                        total_dmg = 0
                        for t in targets:
                            base_dmg = int(war * 7)
                            dmg, _, msg, _ = self.apply_damage(t, base_dmg, actor['운'])
                            total_dmg += dmg
                            print(f"  ⚔️ {actor['이름']} → {t['이름']} {dmg} 피해!")
                        print(f"  {C.RED}총 {total_dmg} 피해!{C.RESET}")
                        acted = True

                    elif skill_id == "triple_arrow":
                        sound_mgr.play("sfx_attack.wav")
                        total_dmg = 0
                        for t in targets:
                            base_dmg = int(war * 5)
                            dmg, _, _, _ = self.apply_damage(t, base_dmg, actor['운'])
                            total_dmg += dmg
                            print(f"  🏹 {actor['이름']} → {t['이름']} {dmg} 피해!")
                        print(f"  {C.RED}총 {total_dmg} 피해!{C.RESET}")
                        acted = True

                    elif skill_id == "chain_fire":
                        sound_mgr.play("sfx_fire.wav")
                        total_dmg = 0
                        for t in targets:
                            if random.randint(0, 100) < intel:
                                base_dmg = int(intel * 4)
                                dmg, _, _, _ = self.apply_damage(t, base_dmg, actor['운'])
                                t['burn'] = 3
                                total_dmg += dmg
                                print(f"  🔥 {actor['이름']} → {t['이름']} {dmg} 피해 + 화상!")
                        print(f"  {C.RED}총 {total_dmg} 피해!{C.RESET}")
                        acted = True

                    elif skill_id == "chain_thunder":
                        sound_mgr.play("sfx_magic.wav")
                        total_dmg = 0
                        for t in targets:
                            base_dmg = int(intel * 10)
                            dmg, _, _, _ = self.apply_damage(t, base_dmg, actor['운'])
                            total_dmg += dmg
                            print(f"  ⚡ {actor['이름']} → {t['이름']} {dmg} 피해!")
                            if random.random() < 0.3:
                                t['stun'] = 2
                                print(f"     💫 {t['이름']} 기절!")
                        print(f"  {C.RED}총 {total_dmg} 피해!{C.RESET}")
                        acted = True

                    elif skill_id == "mass_confuse":
                        sound_mgr.play("sfx_magic.wav")
                        for t in targets:
                            t_int = self.get_battle_stats(t)[1]
                            if random.randint(0, 100) < (50 + intel - t_int):
                                t['stun'] = 3
                                print(f"  💫 {actor['이름']} → {t['이름']} 혼란!")
                        acted = True

                    elif skill_id == "mass_poison":
                        sound_mgr.play("sfx_magic.wav")
                        for t in targets:
                            t_int = self.get_battle_stats(t)[1]
                            if random.randint(0, 100) < (50 + intel - t_int):
                                t['poison'] = 4
                                print(f"  ☠️ {actor['이름']} → {t['이름']} 중독!")
                        acted = True

                    elif skill_id == "group_heal":
                        sound_mgr.play("sfx_heal.wav")
                        for t in targets:
                            h, _, m = self.calc_crit(int(intel * 3) + 150, actor['운'], is_heal=True)
                            t['hp'] = min(t['max_hp'], t['hp'] + h)
                            print(f"  💚 {actor['이름']} → {t['이름']} +{h} 회복!")
                        acted = True

                    elif skill_id == "mass_heal":
                        sound_mgr.play("sfx_heal.wav")
                        for ally in alive_my():
                            h, _, _ = self.calc_crit(int(intel * 4) + 300, actor['운'], is_heal=True)
                            ally['hp'] = min(ally['max_hp'], ally['hp'] + h)
                            ally['burn'] = 0
                            ally['poison'] = 0
                            print(f"  💖 {actor['이름']} → {ally['이름']} +{h} 회복!")
                        print(f"  {C.GREEN}상태이상 해제!{C.RESET}")
                        acted = True

                    elif skill_id == "duo_rally":
                        sound_mgr.play("sfx_buff.wav")
                        for t in targets:
                            t['buff'] = min(10, t.get('buff', 0) + 4)
                            print(f"  💪 {actor['이름']} → {t['이름']} 버프 +4턴!")
                        acted = True

                    elif skill_id == "trio_rally":
                        sound_mgr.play("sfx_buff.wav")
                        for t in targets:
                            t['buff'] = min(10, t.get('buff', 0) + 4)
                            t['hp'] = min(t['max_hp'], t['hp'] + 100)
                            print(f"  📣 {actor['이름']} → {t['이름']} 버프 +4턴! +100 HP!")
                        acted = True

                    elif skill_id == "war_drum":
                        sound_mgr.play("sfx_buff.wav")
                        for ally in alive_my():
                            ally['buff'] = min(10, ally.get('buff', 0) + 5)
                        print(f"  {C.RED}🥁 {actor['이름']} 전고!{C.RESET} 전군 공격력 대폭 상승! (+5턴)")
                        acted = True

                    elif skill_id == "iron_wall":
                        sound_mgr.play("sfx_buff.wav")
                        for ally in alive_my():
                            ally['defend_buff'] = min(10, ally.get('defend_buff', 0) + 4)
                        print(f"  {C.CYAN}🛡️ {actor['이름']} 철벽진!{C.RESET} 전군 방어력 상승! (+4턴)")
                        acted = True

                    # ===== 군주 전용 사기 스킬 =====
                    # 조조 - 패도 (MP80): 적 전체에 막대한 피해
                    elif skill_id == "conquer":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.YELLOW}👑 ═══ 패 도 ═══ 👑{C.RESET}")
                        print(f"  {C.RED}\"천하는 나 조맹덕의 것이다!\"{C.RESET}")
                        time.sleep(0.5)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int((war * 15) + (intel * 10))
                                enemy['hp'] -= dmg
                                total_dmg += dmg
                        print(f"  {C.RED}💀 적 전체에 {total_dmg} 피해!{C.RESET}")
                        acted = True

                    # 조조 - 천하포무 (MP100): 적 하나 즉사 + 전체 큰 피해
                    elif skill_id == "ambition":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.MAGENTA}🌑 ═══ 천 하 포 무 ═══ 🌑{C.RESET}")
                        print(f"  {C.RED}\"천하에 나를 막을 자 없다!\"{C.RESET}")
                        time.sleep(0.8)
                        # 가장 HP 높은 적 즉사
                        alive_enemies = [e for e in enemy_party if e['hp'] > 0]
                        if alive_enemies:
                            main_target = max(alive_enemies, key=lambda x: x['hp'])
                            print(f"  ☠️ {main_target['이름']} 즉사!")
                            main_target['hp'] = 0
                        # 나머지 적 50% 피해
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(enemy['max_hp'] * 0.5)
                                enemy['hp'] -= dmg
                                print(f"     💥 {enemy['이름']}에게 {dmg} 피해!")
                        acted = True

                    # 유비 - 인덕 (MP80): 살아있는 아군만 완전 회복 + 버프
                    elif skill_id == "virtue":
                        sound_mgr.play("sfx_heal.wav")
                        print(f"\n  {C.YELLOW}☀️ ═══ 인 덕 ═══ ☀️{C.RESET}")
                        print(f"  {C.GREEN}\"백성과 함께라면 두려울 것이 없다!\"{C.RESET}")
                        time.sleep(0.5)
                        healed_count = 0
                        for ally in my_party:
                            if ally['hp'] > 0:  # 살아있는 아군만!
                                ally['hp'] = int(ally['max_hp'])  # 확실히 정수로 완전 회복
                                ally['mp'] = min(ally['max_mp'], ally['mp'] + 30)  # MP +30
                                ally['buff'] = min(10, ally.get('buff', 0) + 5)
                                ally['burn'] = 0
                                ally['poison'] = 0
                                ally['debuff'] = 0
                                ally['stun'] = 0
                                healed_count += 1
                                print(f"     ✨ {ally['이름']} HP {ally['hp']}/{ally['max_hp']} 완전 회복!")
                        print(f"  {C.GREEN}💫 {healed_count}명 HP 완전회복! MP +30! 상태이상 해제! 버프 +5턴!{C.RESET}")
                        acted = True

                    # 유비 - 도원결의 (MP100): 관우/장비 있으면 3인 연합공격, 아군 불멸
                    elif skill_id == "oath":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.MAGENTA}🍑 ═══ 도 원 결 의 ═══ 🍑{C.RESET}")
                        print(f"  {C.CYAN}\"죽는 날은 다를지라도 죽는 해, 달, 날은 같기를!\"{C.RESET}")
                        time.sleep(0.8)
                        # 관우/장비 찾기
                        brothers = [a for a in my_party if a['이름'] in ['관우', '장비'] and a['hp'] > 0]
                        if brothers:
                            print(f"  ⚔️ 의형제 연합 공격!")
                            total_dmg = 0
                            for bro in brothers + [actor]:
                                dmg = int(bro['무력'] * 12)
                                for enemy in enemy_party:
                                    if enemy['hp'] > 0:
                                        enemy['hp'] -= dmg
                                        total_dmg += dmg
                            print(f"  {C.RED}💀 적 전체에 {total_dmg} 피해!{C.RESET}")
                        # 아군 생존자 3턴간 불멸 (최소 HP 1)
                        for ally in my_party:
                            if ally['hp'] > 0:
                                ally['oath_protect'] = 3
                        print(f"  {C.YELLOW}🛡️ 아군 생존자 3턴간 사망 불가!{C.RESET}")
                        acted = True

                    # 손권 - 강동패업 (MP80): 5연속 강타
                    elif skill_id == "eastern":
                        sound_mgr.play("sfx_attack.wav")
                        print(f"\n  {C.CYAN}🌊 ═══ 강 동 패 업 ═══ 🌊{C.RESET}")
                        print(f"  {C.BLUE}\"강동의 호랑이가 간다!\"{C.RESET}")
                        time.sleep(0.5)
                        hits = 5
                        total_dmg = 0
                        for i in range(hits):
                            alive = [e for e in enemy_party if e['hp'] > 0]
                            if not alive:
                                break
                            t = random.choice(alive)
                            dmg = int((war * 8) + (intel * 5))
                            t['hp'] -= dmg
                            total_dmg += dmg
                            print(f"     ⚔️ {i+1}격! {t['이름']}에게 {dmg} 피해!")
                            time.sleep(0.2)
                        print(f"  {C.RED}총 {total_dmg} 피해!{C.RESET}")
                        acted = True

                    # 손권 - 적벽대화 (MP100): 전장 불태우기
                    elif skill_id == "redcliff":
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🔱 ═══ 적 벽 대 화 ═══ 🔱{C.RESET}")
                        print(f"  {C.YELLOW}\"적벽의 불길이여, 다시 한번!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                # 최대 HP의 60% 피해 + 화상 5턴
                                dmg = int(enemy['max_hp'] * 0.6)
                                enemy['hp'] -= dmg
                                enemy['burn'] = 5
                                total_dmg += dmg
                                print(f"     🔥 {enemy['이름']} {dmg} 피해 + 화상!")
                        print(f"  {C.RED}💀 적 전체에 {total_dmg} + 화상 5턴!{C.RESET}")
                        acted = True

                    # ===== 여포 사기 스킬 =====
                    # 여포 - 무쌍 (MP70): 단일 대상 초강력 공격
                    elif skill_id == "musou":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}💀 ═══ 무 쌍 ═══ 💀{C.RESET}")
                        print(f"  {C.YELLOW}\"천하에 나 여봉선을 당할 자 없다!\"{C.RESET}")
                        time.sleep(0.5)
                        base_dmg = int(war * 25)
                        dmg, is_crit, msg, _ = self.apply_damage(target, base_dmg, actor['운'])
                        if is_crit:
                            dmg = int(dmg * 1.5)
                            target['hp'] -= int(dmg * 0.5)
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {msg} {dmg} 피해!{C.RESET}")
                        if random.random() < 0.5:
                            target['stun'] = 2
                            print(f"     💫 {target['이름']} 기절!")
                        acted = True

                    # 여포 - 천하무적 (MP100): 적 전체 공격 + 자신 버프
                    elif skill_id == "sky_pierce":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.MAGENTA}🔱 ═══ 천 하 무 적 ═══ 🔱{C.RESET}")
                        print(f"  {C.RED}\"방천화극이 하늘을 가른다!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(war * 15)
                                enemy['hp'] -= dmg
                                total_dmg += dmg
                        print(f"  {C.RED}💀 적 전체에 {total_dmg} 피해!{C.RESET}")
                        actor['buff'] = min(10, actor.get('buff', 0) + 5)
                        actor['민첩'] += 30
                        print(f"  {C.CYAN}⚡ 여포 각성! 버프 +5턴, 민첩 +30!{C.RESET}")
                        acted = True

                    # ===== 관우 사기 스킬 =====
                    elif skill_id == "dragon_blade":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.GREEN}🐉 ═══ 청 룡 언 월 ═══ 🐉{C.RESET}")
                        print(f"  {C.CYAN}\"청룡언월도의 무게를 알겠느냐!\"{C.RESET}")
                        time.sleep(0.5)
                        base_dmg = int(war * 20)
                        dmg, _, msg, _ = self.apply_damage(target, base_dmg, actor['운'])
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {msg} {dmg} 피해!{C.RESET}")
                        if random.random() < 0.6:
                            extra = int(war * 8)
                            target['hp'] -= extra
                            print(f"     💥 방어 관통! 추가 {extra} 피해!")
                        acted = True

                    elif skill_id == "righteous":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.YELLOW}⚔️ ═══ 의 리 천 추 ═══ ⚔️{C.RESET}")
                        print(f"  {C.RED}\"의를 저버린 자여, 심판을 받아라!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(war * 12)
                                enemy['hp'] -= dmg
                                total_dmg += dmg
                        print(f"  {C.RED}💀 적 전체에 {total_dmg} 피해!{C.RESET}")
                        actor['oath_protect'] = 2
                        print(f"  {C.YELLOW}🛡️ 관우 2턴간 사망 불가!{C.RESET}")
                        acted = True

                    # ===== 장비 사기 스킬 =====
                    elif skill_id == "roar":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}🗣️ ═══ 장 판 파 후 ═══ 🗣️{C.RESET}")
                        print(f"  {C.YELLOW}\"으아아아아아!!!! 이 장익덕님이 상대다!!!!\"{C.RESET}")
                        time.sleep(0.8)
                        stunned = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                enemy['stun'] = 3
                                enemy['debuff'] = 3
                                stunned += 1
                                print(f"     💫 {enemy['이름']} 기절!")
                        print(f"  {C.CYAN}⚡ {stunned}명 기절 + 디버프 3턴!{C.RESET}")
                        acted = True

                    # ===== 제갈량 사기 스킬 =====
                    elif skill_id == "wind_fire":
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.CYAN}🌪️ ═══ 칠 성 단 ═══ 🌪️{C.RESET}")
                        print(f"  {C.GREEN}\"동남풍이여, 불어라!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(intel * 12)
                                enemy['hp'] -= dmg
                                enemy['burn'] = 4
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 적 전체에 {total_dmg} 피해 + 화상 4턴!{C.RESET}")
                        acted = True

                    elif skill_id == "bagua":
                        sound_mgr.play("sfx_magic.wav")
                        print(f"\n  {C.MAGENTA}☯️ ═══ 팔 진 도 ═══ ☯️{C.RESET}")
                        print(f"  {C.CYAN}\"팔문금쇄진, 그대들은 빠져나올 수 없다!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(intel * 15)
                                enemy['hp'] -= dmg
                                enemy['stun'] = 2
                                enemy['debuff'] = 3
                                total_dmg += dmg
                                print(f"     💫 {enemy['이름']} {dmg} 피해 + 혼란!")
                        print(f"  {C.RED}💀 적 전체 {total_dmg} 피해 + 기절 + 디버프!{C.RESET}")
                        acted = True

                    # ===== 조운 사기 스킬 =====
                    elif skill_id == "changban":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.WHITE}🏇 ═══ 장 판 돌 파 ═══ 🏇{C.RESET}")
                        print(f"  {C.CYAN}\"상산 조자룡, 만 명이 와도 뚫는다!\"{C.RESET}")
                        time.sleep(0.8)
                        # 7연속 랜덤 타겟 공격
                        hits = 7
                        total_dmg = 0
                        for i in range(hits):
                            alive = [e for e in enemy_party if e['hp'] > 0]
                            if not alive:
                                break
                            t = random.choice(alive)
                            dmg = int((war * 6) + (actor['민첩'] * 3))
                            t['hp'] -= dmg
                            total_dmg += dmg
                            print(f"     ⚔️ {i+1}격! {t['이름']}에게 {dmg} 피해!")
                            time.sleep(0.15)
                        print(f"  {C.RED}총 {total_dmg} 피해!{C.RESET}")
                        actor['민첩'] += 20
                        print(f"  {C.CYAN}⚡ 조운 민첩 +20!{C.RESET}")
                        acted = True

                    # ===== 사마의 사기 스킬 =====
                    elif skill_id == "patience":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.GRAY}🦊 ═══ 인 고 지 책 ═══ 🦊{C.RESET}")
                        print(f"  {C.CYAN}\"서두르지 마라... 때를 기다리는 것이다.\"{C.RESET}")
                        time.sleep(0.8)
                        actor['hp'] = min(actor['max_hp'], actor['hp'] + int(actor['max_hp'] * 0.5))
                        actor['mp'] = min(actor['max_mp'], actor['mp'] + 30)
                        actor['buff'] = min(10, actor['buff'] + 4)
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                enemy['debuff'] = 3
                        print(f"  {C.GREEN}💚 HP 50% 회복, MP +30, 버프 +4턴!{C.RESET}")
                        print(f"  {C.RED}💔 적 전체 디버프 3턴!{C.RESET}")
                        acted = True

                    elif skill_id == "dark_scheme":
                        sound_mgr.play("sfx_magic.wav")
                        print(f"\n  {C.MAGENTA}🕷️ ═══ 음 모 ═══ 🕷️{C.RESET}")
                        print(f"  {C.RED}\"제갈량, 오늘은 내가 이긴다.\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(intel * 10)
                                enemy['hp'] -= dmg
                                enemy['poison'] = 4
                                enemy['burn'] = 3
                                enemy['stun'] = 2
                                total_dmg += dmg
                                print(f"     ☠️ {enemy['이름']} {dmg} 피해 + 독/화상/기절!")
                        print(f"  {C.RED}💀 적 전체에 복합 상태이상!{C.RESET}")
                        acted = True

                    # ===== 주유 사기 스킬 =====
                    elif skill_id == "fire_attack":
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🔥 ═══ 화 공 ═══ 🔥{C.RESET}")
                        print(f"  {C.YELLOW}\"적벽의 불길을 기억하라!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(intel * 14)
                                enemy['hp'] -= dmg
                                enemy['burn'] = 5
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 적 전체에 {total_dmg} 피해 + 화상 5턴!{C.RESET}")
                        acted = True

                    elif skill_id == "genius":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.CYAN}🎭 ═══ 미 주 영 재 ═══ 🎭{C.RESET}")
                        print(f"  {C.GREEN}\"강동의 미주가 간다!\"{C.RESET}")
                        time.sleep(0.8)
                        # 가장 HP 높은 적 즉사 시도 (70% 확률)
                        alive = [e for e in enemy_party if e['hp'] > 0]
                        if alive:
                            main_target = max(alive, key=lambda x: x['hp'])
                            if random.random() < 0.7:
                                print(f"  ☠️ {main_target['이름']} 즉사!")
                                main_target['hp'] = 0
                            else:
                                dmg = int(main_target['max_hp'] * 0.7)
                                main_target['hp'] -= dmg
                                print(f"  💥 {main_target['이름']}에게 {dmg} 피해!")
                        # 나머지 적 디버프
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                enemy['debuff'] = 4
                        print(f"  {C.RED}💔 적 전체 디버프 4턴!{C.RESET}")
                        # 아군 버프
                        for ally in my_party:
                            if ally['hp'] > 0:
                                ally['buff'] = min(10, ally['buff'] + 3)
                        print(f"  {C.GREEN}💪 아군 전체 버프 +3턴!{C.RESET}")
                        acted = True

                    # ===== 광역 스킬 =====
                    elif skill_id == "fire_all":
                        sound_mgr.play("sfx_fire.wav")
                        print(f"  {C.RED}🔥 화염진!{C.RESET}")
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(intel * 8)
                                enemy['hp'] -= dmg
                                enemy['burn'] = 3
                                total_dmg += dmg
                        print(f"  🔥 적 전체에 {total_dmg} 피해 + 화상 3턴!")
                        acted = True

                    elif skill_id == "thunder_all":
                        sound_mgr.play("sfx_magic.wav")
                        print(f"  {C.YELLOW}⚡ 뇌격진!{C.RESET}")
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(intel * 10)
                                enemy['hp'] -= dmg
                                if random.random() < 0.3:
                                    enemy['stun'] = 2
                                total_dmg += dmg
                        print(f"  ⚡ 적 전체에 {total_dmg} 피해!")
                        acted = True

                    elif skill_id == "arrow_rain":
                        sound_mgr.play("sfx_attack.wav")
                        print(f"  {C.GREEN}🏹 {actor['이름']} 화시우!{C.RESET}")
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(war * 6)
                                enemy['hp'] -= dmg
                                total_dmg += dmg
                        print(f"  🏹 적 전체에 {total_dmg} 피해!")
                        acted = True

                    # ===== 새로운 유명 장수 사기 스킬 =====
                    # 황충 - 노장불사 (MP80): HP회복 + 치명타율 대폭 상승
                    elif skill_id == "old_glory":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.YELLOW}🏹 ═══ 노 장 불 사 ═══ 🏹{C.RESET}")
                        print(f"  {C.GREEN}\"늙었다고? 이 화살이 증명하리라!\"{C.RESET}")
                        time.sleep(0.5)
                        actor['hp'] = min(actor['max_hp'], actor['hp'] + int(actor['max_hp'] * 0.5))
                        actor['운'] += 50  # 크리티컬 확률 대폭 상승
                        actor['buff'] = min(10, actor.get('buff', 0) + 4)
                        print(f"  {C.GREEN}💚 HP 50% 회복! 운 +50! 버프 +4턴!{C.RESET}")
                        acted = True

                    # 하후돈 - 독안의 분노 (MP80): 눈을 뽑아 적 공포
                    elif skill_id == "eye_fury":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}👁️ ═══ 독 안 의 분 노 ═══ 👁️{C.RESET}")
                        print(f"  {C.YELLOW}\"부모에게 받은 정기, 버릴 수 없다!\"{C.RESET}")
                        time.sleep(0.8)
                        # 자신 HP 10% 소모, 적 전체 공포 + 피해
                        actor['hp'] = int(actor['hp'] * 0.9)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(war * 10)
                                enemy['hp'] -= dmg
                                enemy['stun'] = 2
                                enemy['debuff'] = 3
                                total_dmg += dmg
                        print(f"  {C.RED}💀 적 전체에 {total_dmg} 피해 + 기절 + 디버프!{C.RESET}")
                        acted = True

                    # 장료 - 합비의 용 (MP80): 800기로 10만을 막아낸 전설
                    elif skill_id == "hefei":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.CYAN}⚔️ ═══ 합 비 의 용 ═══ ⚔️{C.RESET}")
                        print(f"  {C.WHITE}\"장문원이 여기 있다!\"{C.RESET}")
                        time.sleep(0.8)
                        # 10연속 랜덤 타겟 공격
                        hits = 10
                        total_dmg = 0
                        for i in range(hits):
                            alive = [e for e in enemy_party if e['hp'] > 0]
                            if not alive:
                                break
                            t = random.choice(alive)
                            dmg = int(war * 5)
                            t['hp'] -= dmg
                            total_dmg += dmg
                        print(f"  {C.RED}⚔️ 10연속 공격! 총 {total_dmg} 피해!{C.RESET}")
                        actor['buff'] = min(10, actor.get('buff', 0) + 3)
                        print(f"  {C.CYAN}⚡ 기세 상승! 버프 +3턴!{C.RESET}")
                        acted = True

                    # 순욱 - 왕좌지책 (MP80): 아군 전체 대버프
                    elif skill_id == "kings_path":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.YELLOW}👑 ═══ 왕 좌 지 책 ═══ 👑{C.RESET}")
                        print(f"  {C.GREEN}\"주공이시여, 이것이 왕의 길입니다.\"{C.RESET}")
                        time.sleep(0.5)
                        for ally in alive_my():
                            ally['buff'] = min(10, ally.get('buff', 0) + 5)
                            ally['hp'] = min(ally['max_hp'], ally['hp'] + int(ally['max_hp'] * 0.3))
                            ally['mp'] = min(ally['max_mp'], ally['mp'] + 30)
                        print(f"  {C.GREEN}💫 아군 전체 버프 +5턴! HP 30% 회복! MP +30!{C.RESET}")
                        acted = True

                    # 육손 - 이릉 화공 (MP80): 적 전체 화염폭풍
                    elif skill_id == "yiling":
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🔥 ═══ 이 릉 화 공 ═══ 🔥{C.RESET}")
                        print(f"  {C.YELLOW}\"유비, 이 불길에서 벗어날 수 있겠느냐!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(intel * 15)
                                enemy['hp'] -= dmg
                                enemy['burn'] = 5
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 적 전체에 {total_dmg} 피해 + 화상 5턴!{C.RESET}")
                        acted = True

                    # 손책 - 소패왕 (MP80): 단일 대상 초강타
                    elif skill_id == "little_conqueror":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.CYAN}🐯 ═══ 소 패 왕 ═══ 🐯{C.RESET}")
                        print(f"  {C.WHITE}\"강동의 호랑이 손백부가 간다!\"{C.RESET}")
                        time.sleep(0.5)
                        base_dmg = int(war * 22)
                        dmg, _, msg, _ = self.apply_damage(target, base_dmg, actor['운'])
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {msg} {dmg} 피해!{C.RESET}")
                        if random.random() < 0.4:
                            extra = int(war * 10)
                            target['hp'] -= extra
                            target['stun'] = 2
                            print(f"     💥 추가 {extra} 피해! 기절!")
                        acted = True

                    # 감녕 - 백기야습 (MP80): 100기 야습 공격
                    elif skill_id == "night_raid":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.GRAY}🌙 ═══ 백 기 야 습 ═══ 🌙{C.RESET}")
                        print(f"  {C.WHITE}\"100기로 조조 대군을 습격하리라!\"{C.RESET}")
                        time.sleep(0.8)
                        # 가장 HP 높은 적에게 집중 공격 + 전체 공포
                        alive = [e for e in enemy_party if e['hp'] > 0]
                        if alive:
                            main_target = max(alive, key=lambda x: x['hp'])
                            dmg = int(war * 18)
                            main_target['hp'] -= dmg
                            print(f"  {C.RED}⚔️ {main_target['이름']}에게 {dmg} 피해!{C.RESET}")
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                enemy['debuff'] = 3
                        print(f"  {C.CYAN}💫 적 전체 공포! 디버프 3턴!{C.RESET}")
                        acted = True

                    # 마초 - 복수의 창 (MP80): 아버지의 원한
                    elif skill_id == "revenge":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}🔱 ═══ 복 수 의 창 ═══ 🔱{C.RESET}")
                        print(f"  {C.YELLOW}\"조조! 아버지의 원수!\"{C.RESET}")
                        time.sleep(0.8)
                        hp_ratio = actor['hp'] / actor['max_hp']
                        damage_mult = 2.0 - hp_ratio
                        base_dmg = int(war * 15 * damage_mult)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                enemy['hp'] -= base_dmg
                                total_dmg += base_dmg
                        print(f"  {C.RED}💀 적 전체에 {total_dmg} 피해! (분노 x{damage_mult:.1f}){C.RESET}")
                        acted = True

                    # ===== 추가 사기 스킬 구현 =====
                    # 방통 - 연환계책
                    elif skill_id == "linked_strategy":
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.MAGENTA}⛓️ ═══ 연 환 계 책 ═══ ⛓️{C.RESET}")
                        print(f"  {C.CYAN}\"배들을 쇠사슬로 묶어라!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(intel * 12)
                                enemy['hp'] -= dmg
                                enemy['burn'] = 4
                                enemy['stun'] = 2
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 적 전체에 {total_dmg} 피해 + 화상 + 행동불가!{C.RESET}")
                        acted = True

                    # 강유 - 북벌
                    elif skill_id == "northern_expedition":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.CYAN}🏔️ ═══ 북 벌 ═══ 🏔️{C.RESET}")
                        print(f"  {C.GREEN}\"승상의 뜻을 반드시 이루리라!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int((war * 8) + (intel * 8))
                                enemy['hp'] -= dmg
                                total_dmg += dmg
                        for ally in alive_my():
                            ally['buff'] = min(10, ally.get('buff', 0) + 3)
                        print(f"  {C.RED}⚔️ 적 전체에 {total_dmg} 피해! 아군 버프 +3턴!{C.RESET}")
                        acted = True

                    # 위연 - 반골의 일격
                    elif skill_id == "betrayal_strike":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}💀 ═══ 반 골 의 일 격 ═══ 💀{C.RESET}")
                        print(f"  {C.YELLOW}\"누가 나를 죽일 수 있단 말인가!\"{C.RESET}")
                        time.sleep(0.8)
                        base_dmg = int(war * 25)
                        dmg, _, msg, _ = self.apply_damage(target, base_dmg, actor['운'])
                        actor['buff'] = min(10, actor.get('buff', 0) + 5)
                        actor['hp'] = min(actor['max_hp'], actor['hp'] + int(actor['max_hp'] * 0.3))
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {msg} {dmg} 피해!{C.RESET}")
                        print(f"  {C.CYAN}💪 위연 HP 30% 회복 + 버프 5턴!{C.RESET}")
                        acted = True

                    # 조인 - 철옹성
                    elif skill_id == "iron_defense":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.CYAN}🏰 ═══ 철 옹 성 ═══ 🏰{C.RESET}")
                        print(f"  {C.WHITE}\"이 성은 절대 무너지지 않는다!\"{C.RESET}")
                        time.sleep(0.5)
                        for ally in alive_my():
                            ally['defend_buff'] = min(10, ally.get('defend_buff', 0) + 5)
                            ally['hp'] = min(ally['max_hp'], ally['hp'] + int(ally['max_hp'] * 0.2))
                        print(f"  {C.GREEN}🛡️ 아군 전체 방어 +5턴! HP 20% 회복!{C.RESET}")
                        acted = True

                    # 곽가 - 십승십패
                    elif skill_id == "ten_victories":
                        sound_mgr.play("sfx_magic.wav")
                        print(f"\n  {C.YELLOW}📜 ═══ 십 승 십 패 ═══ 📜{C.RESET}")
                        print(f"  {C.CYAN}\"원소의 열 가지 패착을 아시오?\"{C.RESET}")
                        time.sleep(0.8)
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                enemy['debuff'] = 5
                                enemy['stun'] = 2
                        for ally in alive_my():
                            ally['buff'] = min(10, ally.get('buff', 0) + 4)
                        print(f"  {C.RED}📉 적 전체 디버프 5턴 + 기절!{C.RESET}")
                        print(f"  {C.GREEN}📈 아군 전체 버프 4턴!{C.RESET}")
                        acted = True

                    # 허저 - 나체결투
                    elif skill_id == "naked_fury":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}💢 ═══ 나 체 결 투 ═══ 💢{C.RESET}")
                        print(f"  {C.YELLOW}\"허저가 미쳤다!\"{C.RESET}")
                        time.sleep(0.8)
                        hits = 6
                        total_dmg = 0
                        for i in range(hits):
                            alive = [e for e in enemy_party if e['hp'] > 0]
                            if not alive: break
                            t = random.choice(alive)
                            dmg = int(war * 8)
                            t['hp'] -= dmg
                            total_dmg += dmg
                        actor['buff'] = min(10, actor.get('buff', 0) + 4)
                        print(f"  {C.RED}⚔️ 6연속 공격! 총 {total_dmg} 피해! 버프 +4턴!{C.RESET}")
                        acted = True

                    # 전위 - 최후의 저항
                    elif skill_id == "last_stand":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.GRAY}⚰️ ═══ 최 후 의 저 항 ═══ ⚰️{C.RESET}")
                        print(f"  {C.RED}\"주공을 위해 죽어도 싸운다!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(war * 12)
                                enemy['hp'] -= dmg
                                total_dmg += dmg
                        actor['oath_protect'] = 3
                        print(f"  {C.RED}💀 적 전체에 {total_dmg} 피해!{C.RESET}")
                        print(f"  {C.YELLOW}🛡️ 전위 3턴간 사망 불가!{C.RESET}")
                        acted = True

                    # 서황 - 번성대첩
                    elif skill_id == "fancheng":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.CYAN}⚔️ ═══ 번 성 대 첩 ═══ ⚔️{C.RESET}")
                        print(f"  {C.WHITE}\"관우라도 나를 막을 수 없다!\"{C.RESET}")
                        time.sleep(0.8)
                        base_dmg = int(war * 22)
                        dmg, _, msg, _ = self.apply_damage(target, base_dmg, actor['운'])
                        target['debuff'] = 4
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {msg} {dmg} 피해 + 디버프 4턴!{C.RESET}")
                        acted = True

                    # 장합 - 기산방어
                    elif skill_id == "qishan":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.CYAN}🛡️ ═══ 기 산 방 어 ═══ 🛡️{C.RESET}")
                        print(f"  {C.WHITE}\"이 곳은 내가 지킨다!\"{C.RESET}")
                        time.sleep(0.5)
                        for ally in alive_my():
                            ally['defend_buff'] = min(10, ally.get('defend_buff', 0) + 4)
                            ally['buff'] = min(10, ally.get('buff', 0) + 3)
                        print(f"  {C.GREEN}🛡️ 아군 전체 방어버프 +4턴! 버프 +3턴!{C.RESET}")
                        acted = True

                    # 태사자 - 일기토
                    elif skill_id == "duel_master":
                        target = self.select_target(enemy_party, "single")
                        if target:
                            sound_mgr.play("sfx_crit.wav")
                            print(f"\n  {C.YELLOW}🤺 ═══ 일 기 토 ═══ 🤺{C.RESET}")
                            print(f"  {C.CYAN}\"나와 일대일로 승부하라!\"{C.RESET}")
                            time.sleep(0.8)
                            hits = 5
                            total_dmg = 0
                            for i in range(hits):
                                if target['hp'] <= 0: break
                                dmg = int(war * 7)
                                target['hp'] -= dmg
                                total_dmg += dmg
                            print(f"  {C.RED}⚔️ {target['이름']}에게 5연속! 총 {total_dmg} 피해!{C.RESET}")
                            acted = True

                    # 여몽 - 백의도강
                    elif skill_id == "white_robe":
                        sound_mgr.play("sfx_magic.wav")
                        print(f"\n  {C.WHITE}👻 ═══ 백 의 도 강 ═══ 👻{C.RESET}")
                        print(f"  {C.GRAY}\"형주는 우리 것이다!\"{C.RESET}")
                        time.sleep(0.8)
                        alive = [e for e in enemy_party if e['hp'] > 0]
                        if alive:
                            main_target = max(alive, key=lambda x: x['hp'])
                            dmg = int((war * 10) + (intel * 10))
                            main_target['hp'] -= dmg
                            main_target['stun'] = 3
                            print(f"  {C.RED}⚔️ {main_target['이름']}에게 {dmg} 피해 + 기절 3턴!{C.RESET}")
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                enemy['debuff'] = 3
                        print(f"  {C.CYAN}💫 적 전체 디버프!{C.RESET}")
                        acted = True

                    # 노숙 - 손유동맹
                    elif skill_id == "alliance":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.GREEN}🤝 ═══ 손 유 동 맹 ═══ 🤝{C.RESET}")
                        print(f"  {C.CYAN}\"오와 촉이 힘을 합친다!\"{C.RESET}")
                        time.sleep(0.5)
                        for ally in alive_my():
                            ally['hp'] = min(ally['max_hp'], ally['hp'] + int(ally['max_hp'] * 0.4))
                            ally['mp'] = min(ally['max_mp'], ally['mp'] + 30)
                            ally['buff'] = min(10, ally.get('buff', 0) + 4)
                        print(f"  {C.GREEN}💚 아군 전체 HP 40% + MP +30 + 버프 4턴!{C.RESET}")
                        acted = True

                    # 황개 - 고육지책
                    elif skill_id == "fire_ship":
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🚢 ═══ 고 육 지 책 ═══ 🚢{C.RESET}")
                        print(f"  {C.YELLOW}\"이 한 몸 불사르리라!\"{C.RESET}")
                        time.sleep(0.8)
                        actor['hp'] = int(actor['hp'] * 0.7)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(enemy['max_hp'] * 0.5)
                                enemy['hp'] -= dmg
                                enemy['burn'] = 5
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 적 전체에 최대HP 50% 피해 + 화상 5턴!{C.RESET}")
                        acted = True

                    # 주태 - 호위무쌍
                    elif skill_id == "bodyguard":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.CYAN}🛡️ ═══ 호 위 무 쌍 ═══ 🛡️{C.RESET}")
                        print(f"  {C.WHITE}\"주공을 지키는 것이 내 소명!\"{C.RESET}")
                        time.sleep(0.5)
                        actor['defend_buff'] = min(10, actor.get('defend_buff', 0) + 5)
                        actor['oath_protect'] = 3
                        for ally in alive_my():
                            if ally != actor:
                                ally['hp'] = min(ally['max_hp'], ally['hp'] + int(ally['max_hp'] * 0.25))
                        print(f"  {C.GREEN}🛡️ 주태 방어 +5턴, 3턴 불사! 아군 HP 25% 회복!{C.RESET}")
                        acted = True

                    # 능통 - 부친복수
                    elif skill_id == "revenge_blade":
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}😤 ═══ 부 친 복 수 ═══ 😤{C.RESET}")
                        print(f"  {C.YELLOW}\"아버지의 원수!\"{C.RESET}")
                        time.sleep(0.8)
                        base_dmg = int(war * 20)
                        dmg, _, msg, _ = self.apply_damage(target, base_dmg, actor['운'])
                        if target['hp'] > 0:
                            extra = int(war * 8)
                            target['hp'] -= extra
                            dmg += extra
                        actor['buff'] = min(10, actor.get('buff', 0) + 4)
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {msg} 총 {dmg} 피해!{C.RESET}")
                        print(f"  {C.CYAN}💪 분노! 버프 +4턴!{C.RESET}")
                        acted = True

                    # ===== 남만 스킬 =====
                    # 맹획 - 남만왕 (MP80): 맹수군단 소환
                    elif skill_id == "savage_king":
                        sound_mgr.play("sfx_attack.wav")
                        print(f"\n  {C.YELLOW}👑 ═══ 남 만 왕 ═══ 👑{C.RESET}")
                        print(f"  {C.RED}\"맹수들이여, 돌격하라!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(war * 8)
                                enemy['hp'] -= dmg
                                if random.random() < 0.4:
                                    enemy['stun'] = 2
                                total_dmg += dmg
                        print(f"  {C.RED}🐘 적 전체에 {total_dmg} 피해! 40% 확률로 기절!{C.RESET}")
                        acted = True

                    # 맹획 - 칠종칠금 (MP100): 불굴의 의지
                    elif skill_id == "seven_capture":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.YELLOW}🐘 ═══ 칠 종 칠 금 ═══ 🐘{C.RESET}")
                        print(f"  {C.WHITE}\"일곱 번 잡혀도 일곱 번 일어난다!\"{C.RESET}")
                        time.sleep(0.8)
                        actor['hp'] = actor['max_hp']
                        actor['mp'] = actor['max_mp']
                        actor['buff'] = min(10, actor.get('buff', 0) + 5)
                        actor['stun'] = 0
                        actor['burn'] = 0
                        actor['poison'] = 0
                        actor['debuff'] = 0
                        for ally in alive_my():
                            ally['buff'] = min(10, ally.get('buff', 0) + 3)
                        print(f"  {C.GREEN}💪 맹획 완전 회복! 아군 전체 버프 +3턴!{C.RESET}")
                        acted = True

                    # 축융 - 비도술 (MP50): 비도 연발
                    elif skill_id == "flying_blade":
                        target = self.select_target(enemy_party, "single")
                        if target:
                            sound_mgr.play("sfx_attack.wav")
                            print(f"  {C.MAGENTA}🗡️ 축융 비도술!{C.RESET}")
                            hits = random.randint(3, 5)
                            total_dmg = 0
                            for i in range(hits):
                                dmg = int(war * 4 + intel * 2)
                                target['hp'] -= dmg
                                total_dmg += dmg
                            print(f"  {C.RED}🗡️ {target['이름']}에게 {hits}연속 총 {total_dmg} 피해!{C.RESET}")
                            acted = True

                    # 축융 - 맹수여왕 (MP80): 맹수+화공
                    elif skill_id == "beast_queen":
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🔥 ═══ 맹 수 여 왕 ═══ 🔥{C.RESET}")
                        print(f"  {C.YELLOW}\"불과 맹수가 너희를 심판하리라!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(war * 6 + intel * 4)
                                enemy['hp'] -= dmg
                                enemy['burn'] = 3
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 적 전체에 {total_dmg} 피해 + 화상 3턴!{C.RESET}")
                        acted = True

                    # 올돌골 - 등갑병 (MP60): 아군 방어 버프
                    elif skill_id == "rattan_armor":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"  {C.CYAN}🛡️ 올돌골 등갑병!{C.RESET}")
                        for ally in alive_my():
                            ally['defend_buff'] = min(10, ally.get('defend_buff', 0) + 4)
                        print(f"  {C.GREEN}🛡️ 아군 전체 방어버프 +4턴!{C.RESET}")
                        acted = True

                    # 올돌골 - 불사지신 (MP100): 죽음을 거부
                    elif skill_id == "immortal_body":
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.GRAY}💀 ═══ 불 사 지 신 ═══ 💀{C.RESET}")
                        print(f"  {C.WHITE}\"나는 죽지 않는다!\"{C.RESET}")
                        time.sleep(0.8)
                        actor['hp'] = actor['max_hp']
                        actor['oath_protect'] = 5
                        actor['defend_buff'] = min(10, actor.get('defend_buff', 0) + 5)
                        print(f"  {C.GREEN}💀 올돌골 HP 완전회복! 5턴 불사 + 방어버프!{C.RESET}")
                        acted = True

                    # 아회남 - 독안개 (MP70): 독안개 살포
                    elif skill_id == "poison_fog":
                        sound_mgr.play("sfx_magic.wav")
                        print(f"  {C.MAGENTA}☠️ 아회남 독안개!{C.RESET}")
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(intel * 5)
                                enemy['hp'] -= dmg
                                enemy['poison'] = 4
                                enemy['debuff'] = min(10, enemy.get('debuff', 0) + 2)
                                total_dmg += dmg
                        print(f"  {C.RED}☠️ 적 전체에 {total_dmg} 피해 + 독 4턴 + 디버프!{C.RESET}")
                        acted = True

                    # 동도나 - 맹수돌격 (MP60): 코끼리 돌격
                    elif skill_id == "beast_charge":
                        sound_mgr.play("sfx_attack.wav")
                        print(f"  {C.YELLOW}🐘 동도나 맹수돌격!{C.RESET}")
                        total_dmg = 0
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                dmg = int(war * 7)
                                enemy['hp'] -= dmg
                                if random.random() < 0.3:
                                    enemy['stun'] = 1
                                total_dmg += dmg
                        print(f"  {C.RED}🐘 적 전체에 {total_dmg} 피해! 30% 확률 기절!{C.RESET}")
                        acted = True

                    # 연격 체크
                    if acted and target and target['hp'] > 0:
                        if random.random()*100 < self.get_double_chance(actor['민첩']):
                            time.sleep(0.3)
                            sound_mgr.play("sfx_double.wav")
                            base_dmg = int(war*6)
                            dmg, is_crit, msg, _ = self.apply_damage(target, base_dmg, actor['운'])
                            print(f"  💨 [연격] {actor['이름']} 추가타! {msg} {dmg} 피해")

                    # 아군 행동 완료 후 딜레이
                    if acted:
                        time.sleep(1.0)

                else:
                    # 적군 턴 - 장수별 스킬 기반 AI
                    print(f"\n  🔴 {actor['이름']}의 턴...")
                    time.sleep(0.5)
                    ai_acted = False
                    enemy_skills = HeroSkills.get_skills(actor['이름'])
                    e_int = intel  # AI 지력 (조기 정의)

                    # 타겟 조기 선택 (스킬 선택에 필요)
                    alive_targets = [h for h in my_party if h['hp'] > 0]
                    if alive_targets:
                        if random.random() < 0.4:
                            target = min(alive_targets, key=lambda x: x['hp'])
                        else:
                            target = random.choice(alive_targets)
                        p_int = target.get('지력', 50)
                    else:
                        target = None
                        p_int = 0

                    # AI 스킬 선택 로직
                    chosen_skill = None

                    # 0. 군주 사기 스킬 (위기 상황 or 확률)
                    is_lord = actor.get('is_lord', False)
                    if is_lord:
                        # 아군 위기시 (HP 30% 이하) 사기 스킬 사용
                        ally_critical = sum(1 for a in enemy_party if a['hp'] < a['max_hp'] * 0.3 and a['hp'] > 0)
                        enemy_strong = sum(1 for a in my_party if a['hp'] > a['max_hp'] * 0.5)

                        # 조조 사기 스킬
                        if actor['이름'] == '조조':
                            if actor['mp'] >= 100 and enemy_strong >= 2 and random.random() < 0.25:
                                chosen_skill = "ambition"
                            elif actor['mp'] >= 80 and random.random() < 0.3:
                                chosen_skill = "conquer"
                        # 유비 사기 스킬
                        elif actor['이름'] == '유비':
                            if actor['mp'] >= 100 and ally_critical >= 1 and random.random() < 0.35:
                                chosen_skill = "oath"
                            elif actor['mp'] >= 80 and ally_critical >= 1 and random.random() < 0.4:
                                chosen_skill = "virtue"
                        # 손권 사기 스킬
                        elif actor['이름'] == '손권':
                            if actor['mp'] >= 100 and enemy_strong >= 2 and random.random() < 0.25:
                                chosen_skill = "redcliff"
                            elif actor['mp'] >= 80 and random.random() < 0.3:
                                chosen_skill = "eastern"
                        # 맹획 사기 스킬
                        elif actor['이름'] == '맹획':
                            if actor['mp'] >= 100 and (actor['hp'] < actor['max_hp'] * 0.4 or ally_critical >= 2) and random.random() < 0.35:
                                chosen_skill = "seven_capture"
                            elif actor['mp'] >= 80 and enemy_strong >= 2 and random.random() < 0.35:
                                chosen_skill = "savage_king"

                    # 여포 사기 스킬 (재야 출신이지만 강력)
                    if not chosen_skill and actor['이름'] == '여포':
                        if actor['mp'] >= 100 and random.random() < 0.35:
                            chosen_skill = "sky_pierce"
                        elif actor['mp'] >= 70 and random.random() < 0.4:
                            chosen_skill = "musou"

                    # ===== 유명 장수 사기 스킬 =====
                    enemy_strong = sum(1 for a in my_party if a['hp'] > a['max_hp'] * 0.5)

                    # 관우
                    if not chosen_skill and actor['이름'] == '관우':
                        if actor['mp'] >= 100 and enemy_strong >= 2 and random.random() < 0.3:
                            chosen_skill = "righteous"
                        elif actor['mp'] >= 80 and random.random() < 0.35:
                            chosen_skill = "dragon_blade"

                    # 장비
                    if not chosen_skill and actor['이름'] == '장비':
                        if actor['mp'] >= 80 and enemy_strong >= 2 and random.random() < 0.35:
                            chosen_skill = "roar"

                    # 제갈량
                    if not chosen_skill and actor['이름'] == '제갈량':
                        if actor['mp'] >= 100 and enemy_strong >= 2 and random.random() < 0.3:
                            chosen_skill = "bagua"
                        elif actor['mp'] >= 80 and random.random() < 0.35:
                            chosen_skill = "wind_fire"

                    # 조운
                    if not chosen_skill and actor['이름'] == '조운':
                        if actor['mp'] >= 80 and random.random() < 0.35:
                            chosen_skill = "changban"

                    # 사마의
                    if not chosen_skill and actor['이름'] == '사마의':
                        if actor['mp'] >= 100 and enemy_strong >= 2 and random.random() < 0.3:
                            chosen_skill = "dark_scheme"
                        elif actor['mp'] >= 80 and actor['hp'] < actor['max_hp'] * 0.5 and random.random() < 0.4:
                            chosen_skill = "patience"

                    # 주유
                    if not chosen_skill and actor['이름'] == '주유':
                        if actor['mp'] >= 100 and random.random() < 0.3:
                            chosen_skill = "genius"
                        elif actor['mp'] >= 80 and random.random() < 0.35:
                            chosen_skill = "fire_attack"

                    # ===== 추가 장수 사기 스킬 AI =====
                    # 방통
                    if not chosen_skill and actor['이름'] == '방통':
                        if actor['mp'] >= 80 and enemy_strong >= 2 and random.random() < 0.35:
                            chosen_skill = "linked_strategy"

                    # 강유
                    if not chosen_skill and actor['이름'] == '강유':
                        if actor['mp'] >= 80 and random.random() < 0.35:
                            chosen_skill = "northern_expedition"

                    # 위연
                    if not chosen_skill and actor['이름'] == '위연':
                        if actor['mp'] >= 80 and random.random() < 0.4:
                            chosen_skill = "betrayal_strike"

                    # 조인
                    if not chosen_skill and actor['이름'] == '조인':
                        ally_hurt = sum(1 for a in enemy_party if a['hp'] < a['max_hp'] * 0.5 and a['hp'] > 0)
                        if actor['mp'] >= 80 and ally_hurt >= 1 and random.random() < 0.4:
                            chosen_skill = "iron_defense"

                    # 곽가
                    if not chosen_skill and actor['이름'] == '곽가':
                        if actor['mp'] >= 80 and enemy_strong >= 2 and random.random() < 0.35:
                            chosen_skill = "ten_victories"

                    # 허저
                    if not chosen_skill and actor['이름'] == '허저':
                        if actor['mp'] >= 80 and random.random() < 0.4:
                            chosen_skill = "naked_fury"

                    # 전위
                    if not chosen_skill and actor['이름'] == '전위':
                        if actor['mp'] >= 80 and random.random() < 0.35:
                            chosen_skill = "last_stand"

                    # 서황
                    if not chosen_skill and actor['이름'] == '서황':
                        if actor['mp'] >= 80 and random.random() < 0.4:
                            chosen_skill = "fancheng"

                    # 장합
                    if not chosen_skill and actor['이름'] == '장합':
                        ally_hurt = sum(1 for a in enemy_party if a['hp'] < a['max_hp'] * 0.5 and a['hp'] > 0)
                        if actor['mp'] >= 80 and ally_hurt >= 1 and random.random() < 0.4:
                            chosen_skill = "qishan"

                    # 태사자
                    if not chosen_skill and actor['이름'] == '태사자':
                        if actor['mp'] >= 80 and random.random() < 0.4:
                            chosen_skill = "duel_master"

                    # 여몽
                    if not chosen_skill and actor['이름'] == '여몽':
                        if actor['mp'] >= 80 and random.random() < 0.35:
                            chosen_skill = "white_robe"

                    # 노숙
                    if not chosen_skill and actor['이름'] == '노숙':
                        ally_hurt = sum(1 for a in enemy_party if a['hp'] < a['max_hp'] * 0.5 and a['hp'] > 0)
                        if actor['mp'] >= 80 and ally_hurt >= 1 and random.random() < 0.4:
                            chosen_skill = "alliance"

                    # 황개
                    if not chosen_skill and actor['이름'] == '황개':
                        if actor['mp'] >= 80 and enemy_strong >= 2 and random.random() < 0.35:
                            chosen_skill = "fire_ship"

                    # 주태
                    if not chosen_skill and actor['이름'] == '주태':
                        ally_hurt = sum(1 for a in enemy_party if a['hp'] < a['max_hp'] * 0.5 and a['hp'] > 0)
                        if actor['mp'] >= 80 and ally_hurt >= 1 and random.random() < 0.4:
                            chosen_skill = "bodyguard"

                    # 능통
                    if not chosen_skill and actor['이름'] == '능통':
                        if actor['mp'] >= 80 and random.random() < 0.4:
                            chosen_skill = "revenge_blade"

                    # 황충
                    if not chosen_skill and actor['이름'] == '황충':
                        if actor['mp'] >= 80 and (actor['hp'] < actor['max_hp'] * 0.5 or random.random() < 0.3):
                            chosen_skill = "old_glory"

                    # 마초
                    if not chosen_skill and actor['이름'] == '마초':
                        if actor['mp'] >= 80 and random.random() < 0.35:
                            chosen_skill = "revenge"

                    # 감녕
                    if not chosen_skill and actor['이름'] == '감녕':
                        if actor['mp'] >= 80 and random.random() < 0.35:
                            chosen_skill = "night_raid"

                    # 육손
                    if not chosen_skill and actor['이름'] == '육손':
                        if actor['mp'] >= 80 and enemy_strong >= 2 and random.random() < 0.35:
                            chosen_skill = "yiling"

                    # 손책
                    if not chosen_skill and actor['이름'] == '손책':
                        if actor['mp'] >= 80 and random.random() < 0.4:
                            chosen_skill = "little_conqueror"

                    # 광역 스킬 (여러 장수가 보유)
                    if not chosen_skill and enemy_strong >= 2:
                        if "fire_all" in enemy_skills and actor['mp'] >= 60 and random.random() < 0.3:
                            chosen_skill = "fire_all"
                        elif "thunder_all" in enemy_skills and actor['mp'] >= 70 and random.random() < 0.3:
                            chosen_skill = "thunder_all"
                        elif "arrow_rain" in enemy_skills and actor['mp'] >= 50 and random.random() < 0.35:
                            chosen_skill = "arrow_rain"

                    # 1. HP가 낮으면 회복 우선 (heal 스킬 보유시)
                    if not chosen_skill and actor['hp'] < actor['max_hp'] * 0.3:
                        if "heal" in enemy_skills and actor['mp'] >= 60:
                            chosen_skill = "heal"
                        elif "defend" in enemy_skills and actor['mp'] >= 30:
                            chosen_skill = "defend"

                    # 2. 고급 마법 스킬 (낙뢰, 독)
                    if not chosen_skill and e_int > 80:
                        if "thunder" in enemy_skills and actor['mp'] >= 50 and random.random() < 0.4:
                            chosen_skill = "thunder"
                        elif "poison" in enemy_skills and actor['mp'] >= 35 and target and target.get('poison', 0) == 0:
                            if random.random() < 0.5:
                                chosen_skill = "poison"

                    # 3. 화계/혼란 (마법형)
                    if not chosen_skill and e_int > 70 and target:
                        if "fire" in enemy_skills and actor['mp'] >= 20 and target.get('burn', 0) == 0:
                            if random.random() < 0.5:
                                chosen_skill = "fire"
                        elif "confuse" in enemy_skills and actor['mp'] >= 30 and target.get('stun', 0) == 0:
                            if random.random() < 0.4:
                                chosen_skill = "confuse"

                    # 4. 버프/디버프
                    if not chosen_skill:
                        if "drill" in enemy_skills and actor['mp'] >= 35 and random.random() < 0.3:
                            chosen_skill = "drill"
                        elif "inspire" in enemy_skills and actor['mp'] >= 50 and actor['buff'] == 0:
                            if random.random() < 0.3:
                                chosen_skill = "inspire"
                        elif "rally" in enemy_skills and actor['mp'] >= 40 and actor['buff'] == 0:
                            if random.random() < 0.35:
                                chosen_skill = "rally"
                        elif "taunt" in enemy_skills and actor['mp'] >= 40 and target and target.get('debuff', 0) == 0:
                            if e_int > p_int and random.random() < 0.4:
                                chosen_skill = "taunt"

                    # 5. 물리 공격 스킬
                    if not chosen_skill:
                        if "combo" in enemy_skills and actor['mp'] >= 45:
                            if random.random() < 0.4:
                                chosen_skill = "combo"
                        elif "charge" in enemy_skills and actor['mp'] >= 35:
                            if random.random() < 0.45:
                                chosen_skill = "charge"
                        elif "arrow" in enemy_skills and actor['mp'] >= 25:
                            if random.random() < 0.5:
                                chosen_skill = "arrow"

                    # 6. MP 부족시 휴식
                    if not chosen_skill and actor['mp'] < 15:
                        chosen_skill = "rest"

                    # 7. 기본 공격
                    if not chosen_skill:
                        chosen_skill = "attack"

                    # 스킬 실행
                    skill_info = HeroSkills.get_skill_info(chosen_skill)

                    if chosen_skill == "attack" and target:
                        sound_mgr.play("sfx_attack.wav")
                        HeroDialogue.say(actor['이름'], "attack")
                        base_dmg = int(war * 9)
                        d, _, m, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                        print(f"  ⚔️ {actor['이름']} → {target['이름']} 공격! {m} {d} 피해")
                        if target['hp'] > 0 and d > 300:
                            HeroDialogue.say(target['이름'], "hurt")
                        ai_acted = True

                    elif chosen_skill == "fire":
                        actor['mp'] -= 20
                        sound_mgr.play("sfx_fire.wav")
                        if random.randint(0, 100) < e_int:
                            base_dmg = int(e_int * 5)
                            d, _, m, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                            target['burn'] = 3
                            print(f"  🔥 적 화계! {m} {d} 피해 + 화상 (방어{def_rate}%)")
                        else:
                            print("  ☁️ 적 화계 실패")
                        ai_acted = True

                    elif chosen_skill == "thunder":
                        actor['mp'] -= 50
                        sound_mgr.play("sfx_magic.wav")
                        if random.randint(0, 100) < e_int + 20:
                            base_dmg = int(e_int * 10)
                            d, _, m, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                            print(f"  ⚡ 적 낙뢰! {m} {d} 피해! (방어{def_rate}%)")
                            if random.random() < 0.3:
                                target['stun'] = 2
                                print(f"     💫 감전!")
                        else:
                            print("  ☁️ 적 낙뢰 실패")
                        ai_acted = True

                    elif chosen_skill == "confuse":
                        actor['mp'] -= 30
                        sound_mgr.play("sfx_magic.wav")
                        if random.randint(0, 100) < (60 + e_int - p_int):
                            target['stun'] = 3
                            print("  💫 적 계략 성공!")
                        else:
                            print("  🛡️ 적 계략 실패")
                        ai_acted = True

                    elif chosen_skill == "heal":
                        actor['mp'] -= 60
                        sound_mgr.play("sfx_heal.wav")
                        h, c, m = self.calc_crit(int(e_int * 3.5) + 200, actor['운'], is_heal=True)
                        actor['hp'] = min(actor['max_hp'], actor['hp'] + h)
                        print(f"  💊 적 회복 {m} (+{h})")
                        ai_acted = True

                    elif chosen_skill == "rally":
                        actor['mp'] -= 40
                        sound_mgr.play("sfx_buff.wav")
                        actor['buff'] = min(10, actor['buff'] + 3)  # 누적
                        print(f"  💪 적 격려! 버프 +3턴!")
                        ai_acted = True

                    elif chosen_skill == "taunt":
                        actor['mp'] -= 40
                        sound_mgr.play("sfx_debuff.wav")
                        chance = 50 + (e_int - p_int)
                        if random.randint(0, 100) < chance:
                            target['debuff'] = 3
                            print(f"  🤬 적 욕설! 아군 능력치 하락!")
                        else:
                            print(f"  🤬 적 욕설! 아군이 무시함.")
                        ai_acted = True

                    elif chosen_skill == "rest":
                        actor['mp'] = min(actor['max_mp'], actor['mp'] + 30)
                        print("  💤 적 휴식 (MP +30)")

                    elif chosen_skill == "charge":
                        actor['mp'] -= 35
                        sound_mgr.play("sfx_attack.wav")
                        base_dmg = int((war * 6) + (actor['민첩'] * 3))
                        d, _, m, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                        print(f"  🐎 적 돌격! {m} {d} 피해! (방어{def_rate}%)")
                        ai_acted = True

                    elif chosen_skill == "combo":
                        actor['mp'] -= 45
                        sound_mgr.play("sfx_attack.wav")
                        base_dmg = int((war * 5) + (e_int * 4))
                        d, _, m, def_rate = self.apply_damage(target, base_dmg, actor['운'])
                        print(f"  🌀 적 연환계! {m} {d} 피해! (방어{def_rate}%)")
                        if e_int > 80 and random.random() < 0.4:
                            target['debuff'] = 2
                            print(f"     🔽 아군 혼란!")
                        ai_acted = True

                    elif chosen_skill == "arrow":
                        actor['mp'] -= 25
                        sound_mgr.play("sfx_attack.wav")
                        hits = random.randint(2, 4)
                        total_dmg = 0
                        for i in range(hits):
                            base_dmg = int(war * 3)
                            d, _, _, _ = self.apply_damage(target, base_dmg, actor['운'])
                            total_dmg += d
                        print(f"  🏹 적 난사! {hits}연속 총 {total_dmg} 피해!")
                        ai_acted = True

                    elif chosen_skill == "defend":
                        actor['mp'] -= 30
                        sound_mgr.play("sfx_buff.wav")
                        actor['defend_buff'] = min(10, actor.get('defend_buff', 0) + 3)  # 누적
                        print(f"  🛡️ 적 철벽 방어! 방어버프 +3턴!")
                        ai_acted = True

                    elif chosen_skill == "poison":
                        actor['mp'] -= 35
                        sound_mgr.play("sfx_magic.wav")
                        if random.randint(0, 100) < (50 + e_int - p_int):
                            target['poison'] = 4
                            print(f"  ☠️ 적 독계 성공! 아군 중독!")
                        else:
                            print("  💨 적 독계 실패...")
                        ai_acted = True

                    elif chosen_skill == "inspire":
                        actor['mp'] -= 50
                        sound_mgr.play("sfx_buff.wav")
                        for ally in enemy_party:
                            ally['buff'] = min(10, ally.get('buff', 0) + 2)  # 누적
                        print(f"  📯 적 고무! 적군 버프 +2턴!")
                        ai_acted = True

                    elif chosen_skill == "drill":
                        actor['mp'] -= 35
                        sound_mgr.play("sfx_buff.wav")
                        agi_up = 15 + random.randint(5, 15)
                        luck_up = 15 + random.randint(5, 15)
                        actor['민첩'] += agi_up
                        actor['운'] += luck_up
                        print(f"  🎯 적 조련! 민첩 +{agi_up}, 운 +{luck_up}!")
                        ai_acted = True

                    # ===== AI 군주 사기 스킬 =====
                    # 조조 - 패도
                    elif chosen_skill == "conquer":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.YELLOW}👑 ═══ 적 군주 패 도 ═══ 👑{C.RESET}")
                        print(f"  {C.RED}\"천하는 나 조맹덕의 것이다!\"{C.RESET}")
                        time.sleep(0.5)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int((war * 15) + (e_int * 10))
                                ally['hp'] -= dmg
                                total_dmg += dmg
                        print(f"  {C.RED}💀 아군 전체에 {total_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    # 조조 - 천하포무
                    elif chosen_skill == "ambition":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.MAGENTA}🌑 ═══ 적 군주 천 하 포 무 ═══ 🌑{C.RESET}")
                        print(f"  {C.RED}\"천하에 나를 막을 자 없다!\"{C.RESET}")
                        time.sleep(0.8)
                        alive_allies = [a for a in my_party if a['hp'] > 0]
                        if alive_allies:
                            main_target = max(alive_allies, key=lambda x: x['hp'])
                            if main_target.get('oath_protect', 0) <= 0:
                                print(f"  ☠️ {main_target['이름']} 즉사!")
                                main_target['hp'] = 0
                            else:
                                main_target['hp'] = 1
                                print(f"  ☠️ {main_target['이름']} 즉사... {C.YELLOW}[도원결의!]{C.RESET}")
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(ally['max_hp'] * 0.5)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                print(f"     💥 {ally['이름']}에게 {dmg} 피해!")
                        ai_acted = True

                    # 유비 - 인덕
                    elif chosen_skill == "virtue":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_heal.wav")
                        print(f"\n  {C.YELLOW}☀️ ═══ 적 군주 인 덕 ═══ ☀️{C.RESET}")
                        print(f"  {C.GREEN}\"백성과 함께라면 두려울 것이 없다!\"{C.RESET}")
                        time.sleep(0.5)
                        # 버그 수정: 살아있는 아군만 회복
                        for ally in enemy_party:
                            if ally['hp'] > 0:  # 살아있는 장수만!
                                ally['hp'] = ally['max_hp']
                                ally['mp'] = min(ally['max_mp'], ally['mp'] + 30)
                                ally['buff'] = min(10, ally.get('buff', 0) + 5)
                                ally['burn'] = 0
                                ally['poison'] = 0
                                ally['debuff'] = 0
                        print(f"  {C.GREEN}💫 적군 생존자 HP 완전회복! MP +30! 상태이상 해제!{C.RESET}")
                        ai_acted = True

                    # 유비 - 도원결의
                    elif chosen_skill == "oath":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.MAGENTA}🍑 ═══ 적 군주 도 원 결 의 ═══ 🍑{C.RESET}")
                        print(f"  {C.CYAN}\"죽는 날은 다를지라도...\"{C.RESET}")
                        time.sleep(0.8)
                        brothers = [a for a in enemy_party if a['이름'] in ['관우', '장비'] and a['hp'] > 0]
                        if brothers:
                            print(f"  ⚔️ 적 의형제 연합 공격!")
                            total_dmg = 0
                            for bro in brothers + [actor]:
                                dmg = int(bro['무력'] * 12)
                                for ally in my_party:
                                    if ally['hp'] > 0:
                                        ally['hp'] -= dmg
                                        if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                            ally['hp'] = 1
                                        total_dmg += dmg
                            print(f"  {C.RED}💀 아군 전체에 {total_dmg} 피해!{C.RESET}")
                        for ally in enemy_party:
                            ally['oath_protect'] = 3
                        print(f"  {C.YELLOW}🛡️ 적군 전원 3턴간 사망 불가!{C.RESET}")
                        ai_acted = True

                    # 손권 - 강동패업
                    elif chosen_skill == "eastern":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_attack.wav")
                        print(f"\n  {C.CYAN}🌊 ═══ 적 군주 강 동 패 업 ═══ 🌊{C.RESET}")
                        print(f"  {C.BLUE}\"강동의 호랑이가 간다!\"{C.RESET}")
                        time.sleep(0.5)
                        hits = 5
                        total_dmg = 0
                        for i in range(hits):
                            alive = [a for a in my_party if a['hp'] > 0]
                            if not alive:
                                break
                            t = random.choice(alive)
                            dmg = int((war * 8) + (e_int * 5))
                            t['hp'] -= dmg
                            if t.get('oath_protect', 0) > 0 and t['hp'] <= 0:
                                t['hp'] = 1
                            total_dmg += dmg
                            print(f"     ⚔️ {i+1}격! {t['이름']}에게 {dmg} 피해!")
                            time.sleep(0.2)
                        print(f"  {C.RED}총 {total_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    # 손권 - 적벽대화
                    elif chosen_skill == "redcliff":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🔱 ═══ 적 군주 적 벽 대 화 ═══ 🔱{C.RESET}")
                        print(f"  {C.YELLOW}\"적벽의 불길이여, 다시 한번!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(ally['max_hp'] * 0.6)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                ally['burn'] = 5
                                total_dmg += dmg
                                print(f"     🔥 {ally['이름']} {dmg} 피해 + 화상!")
                        print(f"  {C.RED}💀 아군 전체에 {total_dmg} + 화상 5턴!{C.RESET}")
                        ai_acted = True

                    # 여포 - 무쌍
                    elif chosen_skill == "musou":
                        actor['mp'] -= 70
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}💀 ═══ 적 여포 무 쌍 ═══ 💀{C.RESET}")
                        print(f"  {C.YELLOW}\"천하에 나 여봉선을 당할 자 없다!\"{C.RESET}")
                        time.sleep(0.5)
                        base_dmg = int(war * 25)
                        target['hp'] -= base_dmg
                        if target.get('oath_protect', 0) > 0 and target['hp'] <= 0:
                            target['hp'] = 1
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {base_dmg} 피해!{C.RESET}")
                        if random.random() < 0.5:
                            target['stun'] = 2
                            print(f"     💫 {target['이름']} 기절!")
                        ai_acted = True

                    # 여포 - 천하무적
                    elif chosen_skill == "sky_pierce":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.MAGENTA}🔱 ═══ 적 여포 천 하 무 적 ═══ 🔱{C.RESET}")
                        print(f"  {C.RED}\"방천화극이 하늘을 가른다!\"{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(war * 15)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                total_dmg += dmg
                        print(f"  {C.RED}💀 아군 전체에 {total_dmg} 피해!{C.RESET}")
                        actor['buff'] = min(10, actor['buff'] + 5)
                        actor['민첩'] += 30
                        print(f"  {C.CYAN}⚡ 여포 각성! 버프 +5턴, 민첩 +30!{C.RESET}")
                        ai_acted = True

                    # ===== 유명 장수 사기 스킬 (AI) =====
                    # 관우 - 청룡언월
                    elif chosen_skill == "dragon_blade":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.GREEN}🐉 ═══ 적 관우 청 룡 언 월 ═══ 🐉{C.RESET}")
                        time.sleep(0.5)
                        base_dmg = int(war * 20)
                        target['hp'] -= base_dmg
                        if target.get('oath_protect', 0) > 0 and target['hp'] <= 0:
                            target['hp'] = 1
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {base_dmg} 피해!{C.RESET}")
                        if random.random() < 0.6:
                            extra = int(war * 8)
                            target['hp'] -= extra
                            if target.get('oath_protect', 0) > 0 and target['hp'] <= 0:
                                target['hp'] = 1
                            print(f"     💥 방어 관통! 추가 {extra} 피해!")
                        ai_acted = True

                    # 관우 - 의리천추
                    elif chosen_skill == "righteous":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.YELLOW}⚔️ ═══ 적 관우 의 리 천 추 ═══ ⚔️{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(war * 12)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                total_dmg += dmg
                        print(f"  {C.RED}💀 아군 전체에 {total_dmg} 피해!{C.RESET}")
                        actor['oath_protect'] = 2
                        ai_acted = True

                    # 장비 - 장판파후
                    elif chosen_skill == "roar":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}🗣️ ═══ 적 장비 장 판 파 후 ═══ 🗣️{C.RESET}")
                        print(f"  {C.YELLOW}\"으아아아아아!!!!\"{C.RESET}")
                        time.sleep(0.8)
                        for ally in my_party:
                            if ally['hp'] > 0:
                                ally['stun'] = 3
                                ally['debuff'] = 3
                                print(f"     💫 {ally['이름']} 기절!")
                        ai_acted = True

                    # 제갈량 - 칠성단
                    elif chosen_skill == "wind_fire":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.CYAN}🌪️ ═══ 적 제갈량 칠 성 단 ═══ 🌪️{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(e_int * 12)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                ally['burn'] = 4
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 아군 전체에 {total_dmg} 피해 + 화상 4턴!{C.RESET}")
                        ai_acted = True

                    # 제갈량 - 팔진도
                    elif chosen_skill == "bagua":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_magic.wav")
                        print(f"\n  {C.MAGENTA}☯️ ═══ 적 제갈량 팔 진 도 ═══ ☯️{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(e_int * 15)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                ally['stun'] = 2
                                ally['debuff'] = 3
                                total_dmg += dmg
                        print(f"  {C.RED}💀 아군 전체 {total_dmg} 피해 + 기절 + 디버프!{C.RESET}")
                        ai_acted = True

                    # 조운 - 장판돌파
                    elif chosen_skill == "changban":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.WHITE}🏇 ═══ 적 조운 장 판 돌 파 ═══ 🏇{C.RESET}")
                        time.sleep(0.8)
                        hits = 7
                        total_dmg = 0
                        for i in range(hits):
                            alive = [a for a in my_party if a['hp'] > 0]
                            if not alive:
                                break
                            t = random.choice(alive)
                            dmg = int((war * 6) + (actor['민첩'] * 3))
                            t['hp'] -= dmg
                            if t.get('oath_protect', 0) > 0 and t['hp'] <= 0:
                                t['hp'] = 1
                            total_dmg += dmg
                            print(f"     ⚔️ {i+1}격! {t['이름']}에게 {dmg} 피해!")
                            time.sleep(0.15)
                        print(f"  {C.RED}총 {total_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    # 사마의 - 인고지책
                    elif chosen_skill == "patience":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.GRAY}🦊 ═══ 적 사마의 인 고 지 책 ═══ 🦊{C.RESET}")
                        time.sleep(0.8)
                        actor['hp'] = min(actor['max_hp'], actor['hp'] + int(actor['max_hp'] * 0.5))
                        actor['buff'] = min(10, actor['buff'] + 4)
                        for ally in my_party:
                            if ally['hp'] > 0:
                                ally['debuff'] = 3
                        print(f"  {C.GREEN}💚 사마의 HP 50% 회복!{C.RESET}")
                        print(f"  {C.RED}💔 아군 전체 디버프 3턴!{C.RESET}")
                        ai_acted = True

                    # 사마의 - 음모
                    elif chosen_skill == "dark_scheme":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_magic.wav")
                        print(f"\n  {C.MAGENTA}🕷️ ═══ 적 사마의 음 모 ═══ 🕷️{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(e_int * 10)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                ally['poison'] = 4
                                ally['burn'] = 3
                                ally['stun'] = 2
                                total_dmg += dmg
                        print(f"  {C.RED}💀 아군 전체에 복합 상태이상!{C.RESET}")
                        ai_acted = True

                    # 주유 - 화공
                    elif chosen_skill == "fire_attack":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🔥 ═══ 적 주유 화 공 ═══ 🔥{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(e_int * 14)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                ally['burn'] = 5
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 아군 전체에 {total_dmg} 피해 + 화상 5턴!{C.RESET}")
                        ai_acted = True

                    # 주유 - 미주영재
                    elif chosen_skill == "genius":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.CYAN}🎭 ═══ 적 주유 미 주 영 재 ═══ 🎭{C.RESET}")
                        time.sleep(0.8)
                        alive = [a for a in my_party if a['hp'] > 0]
                        if alive:
                            main_target = max(alive, key=lambda x: x['hp'])
                            if random.random() < 0.7 and main_target.get('oath_protect', 0) <= 0:
                                print(f"  ☠️ {main_target['이름']} 즉사!")
                                main_target['hp'] = 0
                            else:
                                dmg = int(main_target['max_hp'] * 0.7)
                                main_target['hp'] -= dmg
                                if main_target.get('oath_protect', 0) > 0 and main_target['hp'] <= 0:
                                    main_target['hp'] = 1
                                print(f"  💥 {main_target['이름']}에게 {dmg} 피해!")
                        for ally in my_party:
                            if ally['hp'] > 0:
                                ally['debuff'] = 4
                        for enemy in enemy_party:
                            if enemy['hp'] > 0:
                                enemy['buff'] = min(10, enemy['buff'] + 3)
                        print(f"  {C.RED}💔 아군 전체 디버프 4턴!{C.RESET}")
                        ai_acted = True

                    # 광역 스킬 (AI)
                    elif chosen_skill == "fire_all":
                        actor['mp'] -= 60
                        sound_mgr.play("sfx_fire.wav")
                        print(f"  {C.RED}🔥 적 화염진!{C.RESET}")
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(e_int * 8)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                ally['burn'] = 3
                                total_dmg += dmg
                        print(f"  🔥 아군 전체에 {total_dmg} 피해 + 화상 3턴!")
                        ai_acted = True

                    elif chosen_skill == "thunder_all":
                        actor['mp'] -= 70
                        sound_mgr.play("sfx_magic.wav")
                        print(f"  {C.YELLOW}⚡ 적 뇌격진!{C.RESET}")
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(e_int * 10)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                if random.random() < 0.3:
                                    ally['stun'] = 2
                                total_dmg += dmg
                        print(f"  ⚡ 아군 전체에 {total_dmg} 피해!")
                        ai_acted = True

                    elif chosen_skill == "arrow_rain":
                        actor['mp'] -= 50
                        sound_mgr.play("sfx_attack.wav")
                        print(f"  {C.GREEN}🏹 적 화시우!{C.RESET}")
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(war * 6)
                                ally['hp'] -= dmg
                                if ally.get('oath_protect', 0) > 0 and ally['hp'] <= 0:
                                    ally['hp'] = 1
                                total_dmg += dmg
                        print(f"  🏹 아군 전체에 {total_dmg} 피해!")
                        ai_acted = True

                    # ===== 추가 장수 사기 스킬 (AI) =====
                    elif chosen_skill == "linked_strategy":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.MAGENTA}⛓️ ═══ 적 방통 연 환 계 책 ═══ ⛓️{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(e_int * 12)
                                ally['hp'] -= dmg
                                ally['burn'] = 4
                                ally['stun'] = 2
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 아군 전체에 {total_dmg} 피해 + 화상 + 기절!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "northern_expedition":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.CYAN}🏔️ ═══ 적 강유 북 벌 ═══ 🏔️{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int((war * 8) + (e_int * 8))
                                ally['hp'] -= dmg
                                total_dmg += dmg
                        for e in enemy_party:
                            if e['hp'] > 0:
                                e['buff'] = min(10, e.get('buff', 0) + 3)
                        print(f"  {C.RED}⚔️ 아군 전체에 {total_dmg} 피해! 적군 버프!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "betrayal_strike":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}💀 ═══ 적 위연 반 골 의 일 격 ═══ 💀{C.RESET}")
                        time.sleep(0.8)
                        base_dmg = int(war * 25)
                        target['hp'] -= base_dmg
                        actor['buff'] = min(10, actor.get('buff', 0) + 5)
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {base_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "iron_defense":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.CYAN}🏰 ═══ 적 조인 철 옹 성 ═══ 🏰{C.RESET}")
                        time.sleep(0.5)
                        for e in enemy_party:
                            if e['hp'] > 0:
                                e['defend_buff'] = min(10, e.get('defend_buff', 0) + 5)
                                e['hp'] = min(e['max_hp'], e['hp'] + int(e['max_hp'] * 0.2))
                        print(f"  {C.GREEN}🛡️ 적군 전체 방어 +5턴! HP 회복!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "ten_victories":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_magic.wav")
                        print(f"\n  {C.YELLOW}📜 ═══ 적 곽가 십 승 십 패 ═══ 📜{C.RESET}")
                        time.sleep(0.8)
                        for ally in my_party:
                            if ally['hp'] > 0:
                                ally['debuff'] = 5
                                ally['stun'] = 2
                        for e in enemy_party:
                            if e['hp'] > 0:
                                e['buff'] = min(10, e.get('buff', 0) + 4)
                        print(f"  {C.RED}📉 아군 전체 디버프 + 기절!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "naked_fury":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}💢 ═══ 적 허저 나 체 결 투 ═══ 💢{C.RESET}")
                        time.sleep(0.8)
                        hits = 6
                        total_dmg = 0
                        for i in range(hits):
                            alive = [a for a in my_party if a['hp'] > 0]
                            if not alive: break
                            t = random.choice(alive)
                            dmg = int(war * 8)
                            t['hp'] -= dmg
                            total_dmg += dmg
                        print(f"  {C.RED}⚔️ 6연속! 아군에 총 {total_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "last_stand":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.GRAY}⚰️ ═══ 적 전위 최 후 의 저 항 ═══ ⚰️{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(war * 12)
                                ally['hp'] -= dmg
                                total_dmg += dmg
                        actor['oath_protect'] = 3
                        print(f"  {C.RED}💀 아군 전체에 {total_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "fancheng":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.CYAN}⚔️ ═══ 적 서황 번 성 대 첩 ═══ ⚔️{C.RESET}")
                        time.sleep(0.8)
                        base_dmg = int(war * 22)
                        target['hp'] -= base_dmg
                        target['debuff'] = 4
                        print(f"  {C.RED}⚔️ {target['이름']}에게 {base_dmg} 피해 + 디버프!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "qishan":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.CYAN}🛡️ ═══ 적 장합 기 산 방 어 ═══ 🛡️{C.RESET}")
                        time.sleep(0.5)
                        for e in enemy_party:
                            if e['hp'] > 0:
                                e['defend_buff'] = min(10, e.get('defend_buff', 0) + 4)
                                e['buff'] = min(10, e.get('buff', 0) + 3)
                        print(f"  {C.GREEN}🛡️ 적군 전체 방어버프!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "duel_master":
                        actor['mp'] -= 80
                        alive_targets = [a for a in my_party if a['hp'] > 0]
                        if alive_targets:
                            target = random.choice(alive_targets)
                            sound_mgr.play("sfx_crit.wav")
                            print(f"\n  {C.YELLOW}🤺 ═══ 적 태사자 일 기 토 ═══ 🤺{C.RESET}")
                            time.sleep(0.8)
                            total_dmg = 0
                            for i in range(5):
                                if target['hp'] <= 0: break
                                dmg = int(war * 7)
                                target['hp'] -= dmg
                                total_dmg += dmg
                            print(f"  {C.RED}⚔️ {target['이름']}에게 5연속! 총 {total_dmg} 피해!{C.RESET}")
                            ai_acted = True

                    elif chosen_skill == "white_robe":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_magic.wav")
                        print(f"\n  {C.WHITE}👻 ═══ 적 여몽 백 의 도 강 ═══ 👻{C.RESET}")
                        time.sleep(0.8)
                        alive = [a for a in my_party if a['hp'] > 0]
                        if alive:
                            main_target = max(alive, key=lambda x: x['hp'])
                            dmg = int((war * 10) + (e_int * 10))
                            main_target['hp'] -= dmg
                            main_target['stun'] = 3
                            print(f"  {C.RED}⚔️ {main_target['이름']}에게 {dmg} 피해 + 기절!{C.RESET}")
                        for ally in my_party:
                            if ally['hp'] > 0:
                                ally['debuff'] = 3
                        ai_acted = True

                    elif chosen_skill == "alliance":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.GREEN}🤝 ═══ 적 노숙 손 유 동 맹 ═══ 🤝{C.RESET}")
                        time.sleep(0.5)
                        for e in enemy_party:
                            if e['hp'] > 0:
                                e['hp'] = min(e['max_hp'], e['hp'] + int(e['max_hp'] * 0.4))
                                e['mp'] = min(e['max_mp'], e['mp'] + 30)
                                e['buff'] = min(10, e.get('buff', 0) + 4)
                        print(f"  {C.GREEN}💚 적군 전체 HP 40% + MP +30 + 버프!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "fire_ship":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🚢 ═══ 적 황개 고 육 지 책 ═══ 🚢{C.RESET}")
                        time.sleep(0.8)
                        actor['hp'] = int(actor['hp'] * 0.7)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(ally['max_hp'] * 0.5)
                                ally['hp'] -= dmg
                                ally['burn'] = 5
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 아군 전체에 최대HP 50% 피해 + 화상!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "bodyguard":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.CYAN}🛡️ ═══ 적 주태 호 위 무 쌍 ═══ 🛡️{C.RESET}")
                        time.sleep(0.5)
                        actor['defend_buff'] = min(10, actor.get('defend_buff', 0) + 5)
                        actor['oath_protect'] = 3
                        for e in enemy_party:
                            if e != actor and e['hp'] > 0:
                                e['hp'] = min(e['max_hp'], e['hp'] + int(e['max_hp'] * 0.25))
                        print(f"  {C.GREEN}🛡️ 주태 방어 + 적군 HP 회복!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "revenge_blade":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}😤 ═══ 적 능통 부 친 복 수 ═══ 😤{C.RESET}")
                        time.sleep(0.8)
                        base_dmg = int(war * 20)
                        target['hp'] -= base_dmg
                        if target['hp'] > 0:
                            extra = int(war * 8)
                            target['hp'] -= extra
                            base_dmg += extra
                        print(f"  {C.RED}⚔️ {target['이름']}에게 총 {base_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "old_glory":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.YELLOW}🏹 ═══ 적 황충 노 장 불 사 ═══ 🏹{C.RESET}")
                        time.sleep(0.5)
                        actor['hp'] = min(actor['max_hp'], actor['hp'] + int(actor['max_hp'] * 0.5))
                        actor['운'] += 50
                        actor['buff'] = min(10, actor.get('buff', 0) + 4)
                        print(f"  {C.GREEN}💚 황충 HP 회복 + 강화!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "revenge":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.RED}🔱 ═══ 적 마초 복 수 의 창 ═══ 🔱{C.RESET}")
                        time.sleep(0.8)
                        hp_ratio = actor['hp'] / actor['max_hp']
                        damage_mult = 2.0 - hp_ratio
                        base_dmg = int(war * 15 * damage_mult)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                ally['hp'] -= base_dmg
                                total_dmg += base_dmg
                        print(f"  {C.RED}💀 아군 전체에 {total_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "night_raid":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.GRAY}🌙 ═══ 적 감녕 백 기 야 습 ═══ 🌙{C.RESET}")
                        time.sleep(0.8)
                        alive = [a for a in my_party if a['hp'] > 0]
                        if alive:
                            main_target = max(alive, key=lambda x: x['hp'])
                            dmg = int(war * 18)
                            main_target['hp'] -= dmg
                            print(f"  {C.RED}⚔️ {main_target['이름']}에게 {dmg} 피해!{C.RESET}")
                        for ally in my_party:
                            if ally['hp'] > 0:
                                ally['debuff'] = 3
                        print(f"  {C.CYAN}💫 아군 전체 디버프!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "yiling":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🔥 ═══ 적 육손 이 릉 화 공 ═══ 🔥{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(e_int * 15)
                                ally['hp'] -= dmg
                                ally['burn'] = 5
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 아군 전체에 {total_dmg} 피해 + 화상!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "little_conqueror":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_crit.wav")
                        print(f"\n  {C.CYAN}🐯 ═══ 적 손책 소 패 왕 ═══ 🐯{C.RESET}")
                        time.sleep(0.8)
                        base_dmg = int(war * 22)
                        target['hp'] -= base_dmg
                        if random.random() < 0.4:
                            extra = int(war * 10)
                            target['hp'] -= extra
                            target['stun'] = 2
                            print(f"  {C.RED}⚔️ {target['이름']}에게 {base_dmg + extra} 피해 + 기절!{C.RESET}")
                        else:
                            print(f"  {C.RED}⚔️ {target['이름']}에게 {base_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    # ===== 남만 AI 스킬 =====
                    elif chosen_skill == "savage_king":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_attack.wav")
                        print(f"\n  {C.YELLOW}👑 ═══ 적 맹획 남 만 왕 ═══ 👑{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(war * 8)
                                ally['hp'] -= dmg
                                if random.random() < 0.4:
                                    ally['stun'] = 2
                                total_dmg += dmg
                        print(f"  {C.RED}🐘 아군 전체에 {total_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "seven_capture":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.YELLOW}🐘 ═══ 적 맹획 칠 종 칠 금 ═══ 🐘{C.RESET}")
                        time.sleep(0.8)
                        actor['hp'] = actor['max_hp']
                        actor['mp'] = actor['max_mp']
                        actor['buff'] = min(10, actor.get('buff', 0) + 5)
                        actor['stun'] = 0
                        actor['burn'] = 0
                        actor['poison'] = 0
                        actor['debuff'] = 0
                        for e in enemy_party:
                            if e['hp'] > 0:
                                e['buff'] = min(10, e.get('buff', 0) + 3)
                        print(f"  {C.GREEN}💪 적 맹획 완전 회복! 적군 전체 버프!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "flying_blade":
                        actor['mp'] -= 50
                        alive_targets = [a for a in my_party if a['hp'] > 0]
                        if alive_targets:
                            target = random.choice(alive_targets)
                            sound_mgr.play("sfx_attack.wav")
                            print(f"  {C.MAGENTA}🗡️ 적 축융 비도술!{C.RESET}")
                            hits = random.randint(3, 5)
                            total_dmg = 0
                            for i in range(hits):
                                dmg = int(war * 4 + e_int * 2)
                                target['hp'] -= dmg
                                total_dmg += dmg
                            print(f"  {C.RED}🗡️ {target['이름']}에게 {hits}연속 총 {total_dmg} 피해!{C.RESET}")
                            ai_acted = True

                    elif chosen_skill == "beast_queen":
                        actor['mp'] -= 80
                        sound_mgr.play("sfx_fire.wav")
                        print(f"\n  {C.RED}🔥 ═══ 적 축융 맹 수 여 왕 ═══ 🔥{C.RESET}")
                        time.sleep(0.8)
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(war * 6 + e_int * 4)
                                ally['hp'] -= dmg
                                ally['burn'] = 3
                                total_dmg += dmg
                        print(f"  {C.RED}🔥 아군 전체에 {total_dmg} 피해 + 화상!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "rattan_armor":
                        actor['mp'] -= 60
                        sound_mgr.play("sfx_buff.wav")
                        print(f"  {C.CYAN}🛡️ 적 올돌골 등갑병!{C.RESET}")
                        for e in enemy_party:
                            if e['hp'] > 0:
                                e['defend_buff'] = min(10, e.get('defend_buff', 0) + 4)
                        print(f"  {C.GREEN}🛡️ 적군 전체 방어버프!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "immortal_body":
                        actor['mp'] -= 100
                        sound_mgr.play("sfx_buff.wav")
                        print(f"\n  {C.GRAY}💀 ═══ 적 올돌골 불 사 지 신 ═══ 💀{C.RESET}")
                        time.sleep(0.8)
                        actor['hp'] = actor['max_hp']
                        actor['oath_protect'] = 5
                        actor['defend_buff'] = min(10, actor.get('defend_buff', 0) + 5)
                        print(f"  {C.GREEN}💀 적 올돌골 완전회복 + 불사!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "poison_fog":
                        actor['mp'] -= 70
                        sound_mgr.play("sfx_magic.wav")
                        print(f"  {C.MAGENTA}☠️ 적 아회남 독안개!{C.RESET}")
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(e_int * 5)
                                ally['hp'] -= dmg
                                ally['poison'] = 4
                                ally['debuff'] = min(10, ally.get('debuff', 0) + 2)
                                total_dmg += dmg
                        print(f"  {C.RED}☠️ 아군 전체에 {total_dmg} 피해 + 독 + 디버프!{C.RESET}")
                        ai_acted = True

                    elif chosen_skill == "beast_charge":
                        actor['mp'] -= 60
                        sound_mgr.play("sfx_attack.wav")
                        print(f"  {C.YELLOW}🐘 적 동도나 맹수돌격!{C.RESET}")
                        total_dmg = 0
                        for ally in my_party:
                            if ally['hp'] > 0:
                                dmg = int(war * 7)
                                ally['hp'] -= dmg
                                if random.random() < 0.3:
                                    ally['stun'] = 1
                                total_dmg += dmg
                        print(f"  {C.RED}🐘 아군 전체에 {total_dmg} 피해!{C.RESET}")
                        ai_acted = True

                    # 적 연격 체크
                    if ai_acted and target and target['hp'] > 0:
                        if random.random() * 100 < self.get_double_chance(actor['민첩']):
                            time.sleep(0.3)
                            sound_mgr.play("sfx_double.wav")
                            base_dmg = int(war * 6)
                            d, is_crit, msg, _ = self.apply_damage(target, base_dmg, actor['운'])
                            print(f"  💨 [연격] {actor['이름']} 추가타! {msg} {d} 피해")

                    # 적군 행동 완료 후 딜레이
                    if ai_acted:
                        time.sleep(1.0)

            # 턴 종료 - Enter 대기
            turn += 1
            print(f"\n  {C.GRAY}[Enter를 눌러 다음 턴...]{C.RESET}")
            try:
                input()
            except:
                time.sleep(1.5)

        # 전투 결과 반환
        alive_my = [h for h in my_party if h['hp'] > 0]
        alive_enemy = [h for h in enemy_party if h['hp'] > 0]
        won = len(alive_my) > 0 and len(alive_enemy) == 0

        # 승리/패배 대사
        if won and alive_my:
            print(f"\n  🎊 전투 승리!")
            HeroDialogue.say(alive_my[0]['이름'], "win")
            time.sleep(1.5)
        elif not won and alive_enemy:
            print(f"\n  😢 전투 패배...")
            time.sleep(1.5)

        return won, my_injured, enemy_injured, my_captured, enemy_captured

    def defensive_battle(self, attacker_id, attacker_castle_name, target_castle_name):
        """방어전 - 성 기반"""
        enemy = self.factions[attacker_id]
        attacker_castle = self.castles[attacker_castle_name]
        target_castle = self.castles[target_castle_name]
        pl = self.get_player()

        if not attacker_castle['장수']:
            return

        print(f"\n{'!' * 60}")
        print(f"  🚨 [긴급] {enemy['이름']}군이 {target_castle_name}을(를) 침공!")
        print(f"{'!' * 60}")

        # 방어 성의 장수로 방어
        available_heroes = [h for h in target_castle['장수'] if h.get('부상', 0) == 0]
        max_d = min(5, len(available_heroes))

        if max_d == 0:
            print(f"  ❌ {target_castle_name}에 수비 가능한 장수가 없습니다!")
            target_castle['소속'] = attacker_id
            print(f"  🔥 {target_castle_name} 함락!")
            return

        print(f"\n  📊 {target_castle_name} 병력: {target_castle['병력']:,}")
        print(f"  👥 수비 가능 장수: {max_d}명")
        num_defenders = get_valid_input(f"  몇 명 수비? (1~{max_d}): ", 1, max_d)

        # 병력 분배
        troops_per_hero = target_castle['병력'] // num_defenders if target_castle['병력'] > 0 else 0
        enemy_count = min(5, len(attacker_castle['장수']))
        enemy_troops_per_hero = attacker_castle['병력'] // enemy_count if enemy_count > 0 else 0

        print(f"\n  📊 장수당 병력: {troops_per_hero:,}")
        print("  👇 수비할 장수를 선택하세요:")

        my_party = []
        selected = []
        for i in range(num_defenders):
            print(f"\n  수비장수 [{i+1}/{num_defenders}] 선택:")
            for j, h in enumerate(available_heroes, 1):
                if h not in selected:
                    print(f"  {j}. {h['이름']} (무력:{h['무력']} 지력:{h['지력']})")
            choice = get_valid_input("  선택: ", 1, len(available_heroes))
            hero = available_heroes[choice - 1]
            if hero in selected:
                continue
            selected.append(hero)

            f = hero.copy()
            max_lead_hp = hero['통솔'] * 100
            f['max_hp'] = min(troops_per_hero, max_lead_hp)
            f['hp'] = f['max_hp']
            f['mp'] = 100
            f['max_mp'] = 100
            f['burn'] = 0
            f['stun'] = 0
            f['buff'] = 0
            f['debuff'] = 0
            my_party.append(f)

        # 적군 파티 구성
        enemy_party = []
        attacker_heroes = sorted(attacker_castle['장수'], key=lambda x: x['무력'], reverse=True)[:5]
        for h in random.sample(attacker_heroes, enemy_count):
            ef = h.copy()
            max_lead_hp = h['통솔'] * 100
            ef['max_hp'] = min(enemy_troops_per_hero, max_lead_hp)
            ef['hp'] = ef['max_hp']
            ef['mp'] = 100
            ef['max_mp'] = 100
            ef['burn'] = 0
            ef['stun'] = 0
            ef['buff'] = 0
            ef['debuff'] = 0
            enemy_party.append(ef)

        won, my_injured, enemy_injured, my_captured, enemy_captured = self.execute_battle(
            my_party, enemy_party, is_defense=True, my_faction=pl, enemy_faction=enemy,
            from_castle=target_castle, target_castle=attacker_castle
        )

        # 부상 처리
        for injured in my_injured:
            for h in target_castle['장수']:
                if h['이름'] == injured['이름']:
                    h['부상'] = injured['부상']

        for injured in enemy_injured:
            for h in attacker_castle['장수']:
                if h['이름'] == injured['이름']:
                    h['부상'] = injured['부상']

        # 포로 처리
        for captured in my_captured:
            for h in target_castle['장수'][:]:
                if h['이름'] == captured['이름']:
                    target_castle['장수'].remove(h)
                    self.prisoners[attacker_id].append(h)

        for captured in enemy_captured:
            for h in attacker_castle['장수'][:]:
                if h['이름'] == captured['이름']:
                    attacker_castle['장수'].remove(h)
                    self.prisoners[self.player_id].append(h)
                    if h.get('is_lord', False):
                        print(f"\n  {C.YELLOW}👑👑👑 군주 {h['이름']} 포로! 👑👑👑{C.RESET}")
                        for cname, cdata in self.castles.items():
                            if cdata['소속'] == attacker_id:
                                cdata['소속'] = self.player_id
                                for remaining in cdata['장수'][:]:
                                    cdata['장수'].remove(remaining)
                                    self.prisoners[self.player_id].append(remaining)
                        print(f"  {C.RED}🏴 {enemy['이름']}군 전체 영토 흡수!{C.RESET}")
                        time.sleep(1)

        if won:
            print(f"\n  🏆 {target_castle_name} 방어 성공! 금 +1000")
            pl['금'] += 1000
            attacker_castle['병력'] = int(attacker_castle['병력'] * 0.7)
            target_castle['병력'] = int(target_castle['병력'] * 0.9)
        else:
            print(f"\n  🔥 {target_castle_name} 함락!")
            target_castle['소속'] = attacker_id
            target_castle['병력'] = int(target_castle['병력'] * 0.5)

    def run_war(self):
        """전쟁 - 성 기반"""
        pl = self.get_player()

        # 1. 출발 성 선택
        print(f"\n{'═' * 50}")
        print("  ⚔️ 전쟁 - 출발 성 선택")
        print(f"{'═' * 50}")

        my_castles = self.get_faction_castles(self.player_id)
        # 인접 적성이 있는 성만 표시
        attack_castles = []
        for name, castle in my_castles.items():
            enemy_adj = self.get_adjacent_enemy_castles(name)
            if enemy_adj and castle['장수']:  # 인접 적성이 있고 장수가 있어야 함
                attack_castles.append(name)

        if not attack_castles:
            print("  ❌ 출격 가능한 성이 없습니다. (인접 적성이 없거나 장수가 없음)")
            return

        print("\n  출격할 성을 선택하세요:")
        for i, name in enumerate(attack_castles, 1):
            castle = my_castles[name]
            enemy_adj = self.get_adjacent_enemy_castles(name)
            print(f"  {i}. {name} - 병력:{castle['병력']:,} 군량:{castle['군량']:,} 장수:{len(castle['장수'])}명 → 적성: {', '.join(enemy_adj)}")
        print("  0. 취소")

        choice = get_valid_input("  선택: ", 0, len(attack_castles))
        if choice == 0:
            return
        from_castle_name = attack_castles[choice - 1]
        from_castle = self.castles[from_castle_name]

        # 군량 확인
        if from_castle['군량'] < 2000:
            print(f"  ❌ {from_castle_name}의 군량 부족 (필요: 2000, 보유: {from_castle['군량']})")
            return

        # 2. 목표 적성 선택
        enemy_targets = self.get_adjacent_enemy_castles(from_castle_name)
        my_alliance = self.alliances.get(self.player_id)

        print(f"\n  공격할 적성을 선택하세요:")
        valid_targets = []
        for i, target_name in enumerate(enemy_targets, 1):
            target = self.castles[target_name]
            enemy_faction = self.factions[target['소속']]
            # 동맹 체크
            if my_alliance and my_alliance['대상'] == target['소속']:
                ally_mark = " 🤝동맹"
            else:
                ally_mark = ""
                valid_targets.append(target_name)
            print(f"  {i}. {target_name} ({enemy_faction['이름']}군) - 병력:{target['병력']:,} 장수:{len(target['장수'])}명{ally_mark}")
        print("  0. 취소")

        if not valid_targets:
            print("  ❌ 공격 가능한 적성이 없습니다. (모두 동맹)")
            return

        choice = get_valid_input("  선택: ", 0, len(enemy_targets))
        if choice == 0:
            return
        target_castle_name = enemy_targets[choice - 1]
        target_castle = self.castles[target_castle_name]
        e_id = target_castle['소속']
        enemy = self.factions[e_id]

        # 동맹 체크
        if my_alliance and my_alliance['대상'] == e_id:
            print(f"  ❌ {enemy['이름']}군은 동맹 세력입니다!")
            return

        # 군량 소모
        from_castle['군량'] -= 2000

        # 3. 출전 장수 선택
        available_heroes = [h for h in from_castle['장수']
                          if h.get('부상', 0) == 0 and h['이름'] not in self.acted_heroes]
        max_heroes = min(5, len(available_heroes))

        if max_heroes == 0:
            print("  ❌ 출전 가능한 장수가 없습니다!")
            from_castle['군량'] += 2000  # 환불
            return

        print(f"\n  📊 {from_castle_name} 병력: {from_castle['병력']:,}")
        print(f"  👥 출전 가능 장수: {max_heroes}명")
        num_heroes = get_valid_input(f"  몇 명 출전? (1~{max_heroes}): ", 1, max_heroes)

        # 병력 분배
        troops_per_hero = from_castle['병력'] // num_heroes
        enemy_count = min(5, len(target_castle['장수'])) if target_castle['장수'] else 0
        enemy_troops_per_hero = target_castle['병력'] // enemy_count if enemy_count > 0 else 0

        print(f"\n  📊 장수당 병력: {troops_per_hero:,}")
        print(f"  👇 출진할 장수 {num_heroes}명을 선택하세요:")

        my_party = []
        selected_heroes = []
        for i in range(num_heroes):
            print(f"\n  장수 [{i+1}/{num_heroes}] 선택:")
            for j, h in enumerate(available_heroes, 1):
                if h not in selected_heroes:
                    print(f"  {j}. {h['이름']} (무력:{h['무력']} 지력:{h['지력']} 통솔:{h['통솔']})")
            choice = get_valid_input("  선택: ", 1, len(available_heroes))
            hero = available_heroes[choice - 1]
            if hero in selected_heroes:
                print("  ❌ 이미 선택한 장수입니다.")
                continue
            selected_heroes.append(hero)
            self.acted_heroes.append(hero['이름'])

            f = hero.copy()
            max_lead_hp = hero['통솔'] * 100
            f['max_hp'] = min(troops_per_hero, max_lead_hp)
            f['hp'] = f['max_hp']
            f['mp'] = 100
            f['max_mp'] = 100
            f['burn'] = 0
            f['stun'] = 0
            f['buff'] = 0
            f['debuff'] = 0
            my_party.append(f)

        # 4. 전투 실행
        enemy_party = []
        if not target_castle['장수']:
            print(f"\n  {C.YELLOW}🏳️ {target_castle_name}에 장수가 없습니다! 무혈 점령!{C.RESET}")
            time.sleep(1)
            won = True
            my_injured = []
            enemy_injured = []
            my_captured = []
            enemy_captured = []
        else:
            for h in random.sample(target_castle['장수'], enemy_count):
                ef = h.copy()
                max_lead_hp = h['통솔'] * 100
                ef['max_hp'] = min(enemy_troops_per_hero, max_lead_hp)
                ef['hp'] = ef['max_hp']
                ef['mp'] = 100
                ef['max_mp'] = 100
                ef['burn'] = 0
                ef['stun'] = 0
                ef['buff'] = 0
                ef['debuff'] = 0
                enemy_party.append(ef)

            won, my_injured, enemy_injured, my_captured, enemy_captured = self.execute_battle(
                my_party, enemy_party, my_faction=pl, enemy_faction=enemy,
                from_castle=from_castle, target_castle=target_castle
            )

        # 5. 부상 처리
        for injured in my_injured:
            for h in from_castle['장수']:
                if h['이름'] == injured['이름']:
                    h['부상'] = injured['부상']

        for injured in enemy_injured:
            for h in target_castle['장수']:
                if h['이름'] == injured['이름']:
                    h['부상'] = injured['부상']

        # 6. 포로 처리
        for captured in my_captured:
            for h in from_castle['장수'][:]:
                if h['이름'] == captured['이름']:
                    from_castle['장수'].remove(h)
                    self.prisoners[e_id].append(h)

        for captured in enemy_captured:
            for h in target_castle['장수'][:]:
                if h['이름'] == captured['이름']:
                    target_castle['장수'].remove(h)
                    self.prisoners[self.player_id].append(h)
                    if h.get('is_lord', False):
                        print(f"\n  {C.YELLOW}👑👑👑 군주 {h['이름']} 포로! 👑👑👑{C.RESET}")
                        # 모든 적성 점령
                        for cname, cdata in self.castles.items():
                            if cdata['소속'] == e_id:
                                cdata['소속'] = self.player_id
                                for remaining in cdata['장수'][:]:
                                    cdata['장수'].remove(remaining)
                                    self.prisoners[self.player_id].append(remaining)
                        print(f"  {C.RED}🏴 {enemy['이름']}군 전체 영토 흡수!{C.RESET}")
                        time.sleep(1)

        # 7. 승패 처리
        if won:
            print(f"\n  🏆 승리! {target_castle_name} 점령!")
            target_castle['소속'] = self.player_id
            pl['금'] += 2000
            from_castle['병력'] = int(from_castle['병력'] * 0.8)

            # 세력 멸망 체크
            if self.get_faction_castle_count(e_id) == 0:
                print(f"\n  {C.YELLOW}🏴🏴🏴 {enemy['이름']}군 멸망! 🏴🏴🏴{C.RESET}")
                time.sleep(1)
        else:
            print("\n  ☠️ 패배... 퇴각합니다.")
            from_castle['병력'] = int(from_castle['병력'] * 0.5)

    def process_event(self):
        """이벤트 처리"""
        pl = self.get_player()
        event = EventSystem.roll_event()

        if event:
            print(f"\n╔{'═' * 56}╗")
            print(f"║  {event['icon']} [ 이벤트 ] {event['name']:<40}║")
            print(f"╠{'═' * 56}╣")
            print(f"║  {event['desc']:<52}║")

            # 이벤트 대상 결정 (금 관련은 세력, 그 외는 수도 성)
            effect = event.get("effect", "")
            if effect == "gold":
                target = pl  # 금은 세력 단위
            else:
                # 수도 성 찾기
                my_castles = self.get_faction_castles(self.player_id)
                target = None
                for cname, cdata in my_castles.items():
                    if cdata.get('수도'):
                        target = cdata
                        break
                if not target and my_castles:
                    target = list(my_castles.values())[0]

            if target:
                result = EventSystem.apply_event(event, target)

                if result["applied"]:
                    print(f"║  ➤ 결과: {result['detail']:<44}║")
                    # 이탈한 장수는 재야로
                    if "leaving_hero" in result:
                        self.free_heroes.append(result["leaving_hero"])
                else:
                    print(f"║  ➤ {result['detail']:<48}║")
            else:
                print(f"║  ➤ 이벤트 적용 실패 (성 없음)                      ║")

            print(f"╚{'═' * 56}╝")
            time.sleep(1.5)

    def process_ai_turn(self):
        print("\n┌─────────────── 적군 동향 ───────────────┐")

        for fid in self.factions:
            if fid == self.player_id or self.get_faction_castle_count(fid) <= 0:
                continue

            fac = self.factions[fid]
            ai_castles = self.get_faction_castles(fid)
            ai_heroes = self.get_faction_heroes(fid)
            acted = False
            actions_done = []  # 이번 턴에 한 행동들

            # AI 분기 수입 (성 기반)
            for cname, cdata in ai_castles.items():
                fac['금'] += cdata['상업'] * 5
                cdata['군량'] += cdata['농업'] * 5

            # AI 이벤트 (간소화)
            if random.random() < 0.15:
                event = EventSystem.roll_event()
                if event and event["effect"] not in ["hero_leave", "hero_join"]:
                    # 성 기반 이벤트 적용
                    if ai_castles:
                        target_castle = random.choice(list(ai_castles.values()))
                        EventSystem.apply_event(event, target_castle)

            # === 등용 시도 (재야 장수) - 수도에 배치 ===
            capital_castle = None
            for cname, cdata in ai_castles.items():
                if cdata.get('수도'):
                    capital_castle = (cname, cdata)
                    break
            if not capital_castle and ai_castles:
                capital_castle = list(ai_castles.items())[0]

            if self.free_heroes and fac['금'] >= 150 and len(ai_heroes) < 12 and capital_castle:
                # 매력 높은 장수가 등용 시도
                if ai_heroes:
                    recruiter = max(ai_heroes, key=lambda x: x.get('매력', 50))
                    target_hero = random.choice(self.free_heroes)
                    success_chance = 50 + recruiter.get('매력', 50) // 2

                    if random.randint(0, 100) < success_chance:
                        fac['금'] -= 150
                        target_hero['충성'] = 70
                        target_hero['원소속'] = fid
                        capital_castle[1]['장수'].append(target_hero)  # 수도에 배치
                        self.free_heroes.remove(target_hero)
                        actions_done.append(f"🎓 {target_hero['이름']} 등용!")
                        acted = True

            # === 포로 등용 시도 ===
            my_prisoners = self.prisoners.get(fid, [])
            if my_prisoners and fac['금'] >= 100 and len(ai_heroes) < 12 and ai_heroes and capital_castle:
                recruiter = max(ai_heroes, key=lambda x: x.get('매력', 50))
                target_prisoner = random.choice(my_prisoners)
                success_chance = 60 + recruiter.get('매력', 50) // 2

                if random.randint(0, 100) < success_chance:
                    fac['금'] -= 100
                    target_prisoner['충성'] = 60
                    target_prisoner['원소속'] = fid
                    capital_castle[1]['장수'].append(target_prisoner)  # 수도에 배치
                    my_prisoners.remove(target_prisoner)
                    actions_done.append(f"⛓️→🎓 {target_prisoner['이름']} 포로 등용!")
                    acted = True

            # === 충성도 낮은 장수 포상 ===
            if fac['금'] >= 300:
                low_loyalty = [h for h in ai_heroes if h['충성'] < 60]
                if low_loyalty and random.random() < 0.4:
                    target = random.choice(low_loyalty)
                    fac['금'] -= 300
                    target['충성'] = min(100, target['충성'] + 20)
                    actions_done.append(f"💎 {target['이름']} 포상")
                    acted = True

            # === 계략 (다른 세력 공작) ===
            if fac['금'] >= 400 and random.random() < 0.2:
                targets = [i for i in self.factions if i != fid and i != self.player_id and self.get_faction_castle_count(i) > 0]
                if targets:
                    t_id = random.choice(targets)
                    t_fac = self.factions[t_id]
                    t_heroes = self.get_faction_heroes(t_id)
                    t_castles = self.get_faction_castles(t_id)
                    scheme_type = random.choice(['이간책', '파괴공작'])

                    if scheme_type == '이간책' and t_heroes:
                        fac['금'] -= 300
                        for h in t_heroes:
                            h['충성'] = max(0, h['충성'] - 8)
                        actions_done.append(f"🕵️ {t_fac['이름']}군 이간책")
                    elif t_castles:
                        fac['금'] -= 400
                        target_castle = random.choice(list(t_castles.values()))
                        target_castle['농업'] = max(0, target_castle['농업'] - 10)
                        target_castle['상업'] = max(0, target_castle['상업'] - 10)
                        actions_done.append(f"💣 {t_fac['이름']}군 파괴공작")
                    acted = True

            # === 전쟁 체크 (성 기반) - 6% 확률로 전쟁 ===
            total_troops = self.get_faction_total_troops(fid)
            if total_troops > 12000 and random.random() < 0.06:
                # AI 성 중 인접 적성이 있는 성 찾기
                ai_castles = self.get_faction_castles(fid)
                attack_options = []
                for cname, cdata in ai_castles.items():
                    if cdata['장수'] and cdata['병력'] > 2000:
                        for adj in cdata['인접']:
                            adj_castle = self.castles[adj]
                            if adj_castle['소속'] != fid:
                                # 동맹 체크
                                ai_alliance = self.alliances.get(fid)
                                ally_id = ai_alliance['대상'] if ai_alliance else None
                                if adj_castle['소속'] != ally_id:
                                    attack_options.append((cname, adj))

                if attack_options:
                    attacker_castle, target_castle = random.choice(attack_options)
                    t_id = self.castles[target_castle]['소속']

                    if t_id == self.player_id:
                        # 플레이어 공격 → 방어전
                        if actions_done:
                            for act in actions_done:
                                print(f"│  {self.pad_kr(fac['이름'],4)}군: {act}")
                        print("└─────────────────────────────────────────┘")
                        self.defensive_battle(fid, attacker_castle, target_castle)
                        return
                    else:
                        # AI vs AI: 단순 처리
                        atk_castle = self.castles[attacker_castle]
                        tgt_castle = self.castles[target_castle]
                        if atk_castle['병력'] > tgt_castle['병력']:
                            tgt_castle['소속'] = fid
                            actions_done.append(f"⚔️ {target_castle} 점령!")
                            acted = True

            # === 접경 성 파악 ===
            border_castles = {}  # {성이름: (성데이터, 인접적성수)}
            rear_castles = {}    # 후방 성
            for cname, cdata in ai_castles.items():
                enemy_adj_count = 0
                for adj in cdata['인접']:
                    adj_castle = self.castles[adj]
                    if adj_castle['소속'] != fid:
                        # 동맹 체크
                        ai_alliance = self.alliances.get(fid)
                        ally_id = ai_alliance['대상'] if ai_alliance else None
                        if adj_castle['소속'] != ally_id:
                            enemy_adj_count += 1
                if enemy_adj_count > 0:
                    border_castles[cname] = (cdata, enemy_adj_count)
                else:
                    rear_castles[cname] = cdata

            # === 장수 이동 (후방 → 접경) ===
            if border_castles and rear_castles:
                for rear_name, rear_data in rear_castles.items():
                    if len(rear_data['장수']) > 1:  # 장수가 2명 이상인 후방 성
                        # 장수가 부족한 접경 성 찾기
                        for border_name, (border_data, _) in border_castles.items():
                            if border_name in rear_data['인접'] and len(border_data['장수']) < 3:
                                # 장수 1명 이동
                                hero_to_move = rear_data['장수'][-1]
                                rear_data['장수'].remove(hero_to_move)
                                border_data['장수'].append(hero_to_move)
                                actions_done.append(f"🚶 {hero_to_move['이름']} → {border_name}")
                                break

            # === 병력 이동 (후방 → 접경) ===
            if border_castles and rear_castles:
                for rear_name, rear_data in rear_castles.items():
                    if rear_data['병력'] > 3000:  # 후방에 병력이 많으면
                        for border_name, (border_data, _) in border_castles.items():
                            if border_name in rear_data['인접'] and border_data['병력'] < 5000:
                                # 병력 이동 (최대 2000)
                                move_troops = min(2000, rear_data['병력'] - 1000)
                                if move_troops > 0:
                                    rear_data['병력'] -= move_troops
                                    border_data['병력'] += move_troops
                                    actions_done.append(f"🚚 병력 {move_troops:,} → {border_name}")
                                    break

            # === 병력 모집 (적극적, 여러 성에서) ===
            total_troops = self.get_faction_total_troops(fid)
            recruit_count = 0
            for cname, cdata in ai_castles.items():
                if recruit_count >= 2:  # 턴당 최대 2회 징병
                    break
                if total_troops < 30000 and fac['금'] >= 400 and cdata['군량'] >= 800:
                    rec = 1200 + random.randint(0, 800)
                    cdata['병력'] += rec
                    cdata['군량'] -= 400
                    fac['금'] -= 400
                    total_troops += rec
                    recruit_count += 1
                    if recruit_count == 1:
                        actions_done.append(f"🛡️ 징병 +{rec:,}")
                    acted = True

            # === 내정 (농업/상업 개발, 성 기반) ===
            if fac['금'] >= 100 and len(actions_done) < 3 and ai_castles:
                # 개발도가 낮은 성 우선
                target_castle = min(ai_castles.values(), key=lambda c: c['농업'] + c['상업'])
                if target_castle['농업'] < target_castle['상업'] or random.random() < 0.5:
                    target_castle['농업'] += random.randint(8, 15)
                    actions_done.append("🌾 농업 개발")
                else:
                    target_castle['상업'] += random.randint(8, 15)
                    fac['금'] -= 100
                    actions_done.append("💰 상업 개발")
                acted = True

            # === 결과 출력 ===
            if actions_done:
                for act in actions_done:
                    print(f"│  {self.pad_kr(fac['이름'],4)}군: {act}")
            else:
                print(f"│  💤 {self.pad_kr(fac['이름'],4)}군: 휴식 중...")

        print("└─────────────────────────────────────────┘")

    def run_policy(self, cmd):
        pl = self.get_player()

        if cmd == 1:
            # 농업 - 성 선택
            castle_name = self.select_my_castle("농업 개발할 성을 선택하세요")
            if not castle_name:
                return
            castle = self.castles[castle_name]
            if castle['군량'] < 100:
                print(f"  ❌ {castle_name}의 군량이 부족합니다 (필요: 100)")
                return
            # 해당 성의 장수 선택
            available = [h for h in castle['장수'] if h.get('부상', 0) == 0 and h['이름'] not in self.acted_heroes]
            if not available:
                print(f"  ❌ {castle_name}에 행동 가능한 장수가 없습니다")
                return
            print(f"\n  농업 담당 장수 선택:")
            for i, h in enumerate(available, 1):
                print(f"  {i}. {h['이름']} (지력:{h['지력']})")
            choice = get_valid_input("  선택: ", 1, len(available))
            hero = available[choice - 1]
            self.acted_heroes.append(hero['이름'])

            inc = hero['지력']//2 + 10
            castle['농업'] += inc
            castle['군량'] -= 100
            print(f"  ✅ {hero['이름']}의 노력으로 {castle_name} 농업 +{inc}")
            time.sleep(1)
        elif cmd == 2:
            # 상업 - 성 선택
            castle_name = self.select_my_castle("상업 개발할 성을 선택하세요")
            if not castle_name:
                return
            castle = self.castles[castle_name]
            if pl['금'] < 100:
                print("  ❌ 금이 부족합니다 (필요: 100)")
                return
            available = [h for h in castle['장수'] if h.get('부상', 0) == 0 and h['이름'] not in self.acted_heroes]
            if not available:
                print(f"  ❌ {castle_name}에 행동 가능한 장수가 없습니다")
                return
            print(f"\n  상업 담당 장수 선택:")
            for i, h in enumerate(available, 1):
                print(f"  {i}. {h['이름']} (지력:{h['지력']})")
            choice = get_valid_input("  선택: ", 1, len(available))
            hero = available[choice - 1]
            self.acted_heroes.append(hero['이름'])

            inc = hero['지력']//2 + 10
            castle['상업'] += inc
            pl['금'] -= 100
            print(f"  ✅ {hero['이름']}의 노력으로 {castle_name} 상업 +{inc}")
            time.sleep(1)
        elif cmd == 3:
            # 포상 - 성 선택 후 장수 선택
            castle_name = self.select_my_castle("포상할 장수가 있는 성을 선택하세요")
            if not castle_name:
                return
            castle = self.castles[castle_name]
            if pl['금'] < 500:
                print("  ❌ 금이 부족합니다 (필요: 500)")
                return
            if not castle['장수']:
                print(f"  ❌ {castle_name}에 장수가 없습니다")
                return
            print(f"\n  포상 대상 장수 선택:")
            for i, h in enumerate(castle['장수'], 1):
                print(f"  {i}. {h['이름']} (충성:{h['충성']})")
            choice = get_valid_input("  선택: ", 1, len(castle['장수']))
            hero = castle['장수'][choice - 1]

            pl['금'] -= 500
            hero['충성'] = min(100, hero['충성'] + 15)
            print(f"  💰 {hero['이름']}의 충성도 +15 (현재: {hero['충성']})")
            time.sleep(1)
        elif cmd == 4:
            # 징병 - 성 선택
            castle_name = self.select_my_castle("징병할 성을 선택하세요")
            if not castle_name:
                return
            castle = self.castles[castle_name]
            if pl['금'] < 800:
                print("  ❌ 금이 부족합니다 (필요: 800)")
                return
            rec = 1500 + (castle['농업'] * 5)
            pl['금'] -= 800
            castle['병력'] += rec
            print(f"  🛡️ {castle_name}에서 {rec:,}명 징병! (현재: {castle['병력']:,}명)")
            time.sleep(1)
        elif cmd == 6:
            targets = [f for f in self.factions if f!=self.player_id and self.get_faction_castle_count(f)>0]
            if not targets:
                print("  ❌ 대상 없음")
                return

            # 계략 서브메뉴
            print("\n┌─────────── 계략 선택 ───────────┐")
            print("│  1. 이간책 (충성도 하락) - 금 300  │")
            print("│  2. 파괴공작 (농업/상업 하락) - 금 500  │")
            print("└─────────────────────────────────┘")
            sub_cmd = get_valid_input("  계략 선택: ", 1, 2)

            # 진영 선택
            print("\n┌─────────── 대상 진영 ───────────┐")
            for fid in targets:
                f = self.factions[fid]
                castle_cnt = self.get_faction_castle_count(fid)
                troop_cnt = self.get_faction_total_troops(fid)
                print(f"│  {fid}. {f['이름']}군 (성:{castle_cnt}, 병력:{troop_cnt:,})  │")
            print("└─────────────────────────────────┘")
            t_id = get_valid_input("  진영 선택: ", 1, max(self.factions.keys()))

            if t_id not in targets:
                print("  ❌ 잘못된 선택")
                return

            target = self.factions[t_id]
            h = self.select_hero("계략 담당")

            if sub_cmd == 1:
                # 이간책 - 충성도 하락
                if pl['금'] < 300:
                    print("  ❌ 금이 부족합니다 (필요: 300)")
                    return
                pl['금'] -= 300
                success_chance = 50 + (h['지력'] - 70)
                print(f"  🕵️ {h['이름']}이(가) {target['이름']}군에 이간책 시도... (성공률: {min(100, max(0, success_chance))}%)")
                time.sleep(1)
                if random.randint(0, 100) < success_chance:
                    loyalty_drop = 10 + (h['지력'] // 10)
                    target_heroes = self.get_faction_heroes(t_id)
                    for th in target_heroes:
                        th['충성'] = max(0, th['충성'] - loyalty_drop)
                    print(f"  ✅ 성공! {target['이름']}군 장수들의 충성도가 {loyalty_drop} 하락했습니다!")
                else:
                    print(f"  ❌ 실패... 계략이 발각되었습니다.")

            elif sub_cmd == 2:
                # 파괴공작 - 농업/상업 하락 (성 기반)
                if pl['금'] < 500:
                    print("  ❌ 금이 부족합니다 (필요: 500)")
                    return
                pl['금'] -= 500
                success_chance = 40 + (h['지력'] - 70)
                print(f"  🔥 {h['이름']}이(가) {target['이름']}군에 파괴공작 시도... (성공률: {min(100, max(0, success_chance))}%)")
                time.sleep(1)
                if random.randint(0, 100) < success_chance:
                    agri_drop = 15 + random.randint(5, 15)
                    comm_drop = 15 + random.randint(5, 15)
                    # 무작위 성에 피해
                    target_castles = self.get_faction_castles(t_id)
                    if target_castles:
                        damaged_castle = random.choice(list(target_castles.values()))
                        damaged_castle['농업'] = max(10, damaged_castle['농업'] - agri_drop)
                        damaged_castle['상업'] = max(10, damaged_castle['상업'] - comm_drop)
                    print(f"  ✅ 성공! {target['이름']}군의 농업 -{agri_drop}, 상업 -{comm_drop}!")
                else:
                    print(f"  ❌ 실패... 첩자가 잡혔습니다.")
        elif cmd == 8:
            targets = [f for f in self.factions if f!=self.player_id and self.get_faction_castle_count(f)>0]
            my_prisoners = self.prisoners.get(self.player_id, [])

            # 등용 대상 선택 (포로 / 재야 / 적 세력)
            print("\n┌─────────── 등용 대상 ───────────┐")
            print(f"│  9. 포로 ({len(my_prisoners)}명)                 │")
            print(f"│  0. 재야 장수 ({len(self.free_heroes)}명)            │")
            for fid in targets:
                f = self.factions[fid]
                hero_cnt = len(self.get_faction_heroes(fid))
                print(f"│  {fid}. {f['이름']}군 (장수: {hero_cnt}명)      │")
            print("└─────────────────────────────────┘")
            t_id = get_valid_input("  대상 선택 (9=포로, 0=재야): ", 0, 9)

            if t_id == 9:
                # 포로 등용
                if not my_prisoners:
                    print("  ❌ 보유 중인 포로가 없습니다")
                    return

                print(f"\n{'─' * 60}")
                print(f"  ⛓️ 포로 목록")
                print(f"{'─' * 60}")

                headers = ["#", "이름", "무력", "지력", "통솔", "매력", "원소속"]
                rows = []
                for i, th in enumerate(my_prisoners):
                    orig = self.factions.get(th.get('원소속', 0), {}).get('이름', '재야')
                    rows.append([
                        str(i+1), th['이름'],
                        str(th['무력']), str(th['지력']), str(th['통솔']),
                        str(th['매력']), orig
                    ])
                print(TUI.table(headers, rows, [3, 8, 5, 5, 5, 5, 8]))

                t_idx = get_valid_input("  등용할 포로 선택: ", 1, len(my_prisoners))
                t_h = my_prisoners[t_idx - 1]

                # 사절 선택
                h = self.select_hero("설득 담당", check_acted=True)
                if h is None:
                    return

                # 포로 등용은 성공률 높음 (매력 + 40)
                success_chance = h['매력'] - 30 + 40
                print(f"\n  🗣️ {h['이름']}이(가) 포로 {t_h['이름']}을(를) 설득 중...")
                print(f"     (성공률: {min(100, max(0, success_chance))}%)")
                time.sleep(1)

                if random.randint(0, 100) < success_chance:
                    print(f"  🎉 {t_h['이름']} 등용 성공! 아군이 되었습니다!")
                    t_h['충성'] = 60  # 포로 출신은 충성도 60으로 시작
                    t_h['부상'] = 0   # 부상 해제
                    # 수도에 배치
                    my_castles = self.get_faction_castles(self.player_id)
                    capital = None
                    for cname, cdata in my_castles.items():
                        if cdata.get('수도'):
                            capital = cdata
                            break
                    if not capital:
                        capital = list(my_castles.values())[0]
                    capital['장수'].append(t_h)
                    my_prisoners.remove(t_h)
                    time.sleep(1.5)
                else:
                    print(f"  💬 등용 실패... {t_h['이름']}이(가) 완강히 거부합니다.")
                    # 실패 시 30% 확률로 포로가 탈출 시도
                    if random.random() < 0.3:
                        my_prisoners.remove(t_h)
                        t_h['충성'] = 50
                        self.free_heroes.append(t_h)
                        print(f"  🏃 {t_h['이름']}이(가) 틈을 타 탈출했습니다!")
                    time.sleep(1.5)

            elif t_id == 0:
                # 재야 장수 등용
                if not self.free_heroes:
                    print("  ❌ 재야에 장수가 없습니다")
                    return

                print(f"\n{'─' * 60}")
                print(f"  📋 재야 장수 목록")
                print(f"{'─' * 60}")

                headers = ["#", "이름", "무력", "지력", "통솔", "매력", "충성"]
                rows = []
                for i, th in enumerate(self.free_heroes):
                    rows.append([
                        str(i+1), th['이름'],
                        str(th['무력']), str(th['지력']), str(th['통솔']),
                        str(th['매력']), str(th['충성'])
                    ])
                print(TUI.table(headers, rows, [3, 8, 5, 5, 5, 5, 5]))

                t_idx = get_valid_input("  등용할 장수 선택: ", 1, len(self.free_heroes))
                t_h = self.free_heroes[t_idx - 1]

                # 사절 선택
                h = self.select_hero("외교 사절")

                # 재야 장수는 등용 성공률 높음
                success_chance = h['매력'] - t_h['충성'] + 50
                print(f"\n  🕵️ {h['이름']}이(가) 재야의 {t_h['이름']}에게 접촉 시도...")
                print(f"     (성공률: {min(100, max(0, success_chance))}% = 매력{h['매력']} - 충성{t_h['충성']} + 50)")
                time.sleep(1)

                if random.randint(0, 100) < success_chance:
                    print(f"  🎉 {t_h['이름']} 등용 성공! 아군이 되었습니다!")
                    t_h['충성'] = 75  # 재야 출신은 충성도 75로 시작
                    # 수도에 배치
                    my_castles = self.get_faction_castles(self.player_id)
                    capital = None
                    for cname, cdata in my_castles.items():
                        if cdata.get('수도'):
                            capital = cdata
                            break
                    if not capital:
                        capital = list(my_castles.values())[0]
                    capital['장수'].append(t_h)
                    self.free_heroes.remove(t_h)
                    time.sleep(1.5)
                else:
                    print(f"  💬 등용 실패... {t_h['이름']}이(가) 아직 뜻을 정하지 못했습니다.")
                    time.sleep(1.5)

            elif t_id in targets:
                t_fac = self.factions[t_id]
                t_heroes = self.get_faction_heroes(t_id)
                if not t_heroes:
                    print("  ❌ 상대 장수 없음")
                    return

                # 상대 장수 목록 표시
                print(f"\n{'─' * 60}")
                print(f"  📋 {t_fac['이름']}군 장수 목록")
                print(f"{'─' * 60}")

                headers = ["#", "이름", "무력", "지력", "통솔", "매력", "충성"]
                rows = []
                for i, th in enumerate(t_heroes):
                    rows.append([
                        str(i+1), th['이름'],
                        str(th['무력']), str(th['지력']), str(th['통솔']),
                        str(th['매력']), str(th['충성'])
                    ])
                print(TUI.table(headers, rows, [3, 8, 5, 5, 5, 5, 5]))

                t_idx = get_valid_input("  등용할 장수 선택: ", 1, len(t_heroes))
                t_h = t_heroes[t_idx - 1]

                # 사절 선택
                h = self.select_hero("외교 사절")

                # 등용 시도
                success_chance = h['매력'] - t_h['충성'] + 30
                print(f"\n  🕵️ {h['이름']}이(가) {t_h['이름']}에게 접촉 시도...")
                print(f"     (성공률: {min(100, max(0, success_chance))}% = 매력{h['매력']} - 충성{t_h['충성']} + 30)")
                time.sleep(1)

                if random.randint(0, 100) < success_chance:
                    print(f"  🎉 {t_h['이름']} 등용 성공! 아군이 되었습니다!")
                    t_h['충성'] = 70  # 새로 등용된 장수는 충성도 70으로 시작
                    # 플레이어 수도에 배치
                    my_castles = self.get_faction_castles(self.player_id)
                    capital = None
                    for cname, cdata in my_castles.items():
                        if cdata.get('수도'):
                            capital = cdata
                            break
                    if not capital:
                        capital = list(my_castles.values())[0]
                    capital['장수'].append(t_h)
                    # 적 성에서 제거
                    for cname, cdata in self.castles.items():
                        if cdata['소속'] == t_id and t_h in cdata['장수']:
                            cdata['장수'].remove(t_h)
                            break
                    time.sleep(1.5)
                else:
                    print(f"  💬 등용 실패... {t_h['이름']}이(가) 거절했습니다.")
                    time.sleep(1.5)
            else:
                print("  ❌ 잘못된 선택")

    def show_info(self):
        """정보 화면 (성 기반)"""
        # 세력별 통계 생성
        rows = []
        for fid, fac in self.factions.items():
            castle_count = self.get_faction_castle_count(fid)
            total_troops = self.get_faction_total_troops(fid)
            hero_count = len(self.get_faction_heroes(fid))
            # 농업/상업 합계 계산
            total_agri = 0
            total_comm = 0
            for cname, cdata in self.castles.items():
                if cdata['소속'] == fid:
                    total_agri += cdata['농업']
                    total_comm += cdata['상업']
            rows.append([fac['이름'], str(castle_count), f"{total_troops:,}", str(hero_count), str(total_agri), str(total_comm)])

        print("\n" + TUI.table(
            ["세력", "성", "병력", "장수", "농업", "상업"],
            rows,
            [8, 6, 10, 6, 6, 6]
        ))

        # 재야 장수 정보
        if self.free_heroes:
            print(f"\n  📜 재야 장수: {len(self.free_heroes)}명")
            for h in self.free_heroes:
                print(f"     - {h['이름']} (무력:{h['무력']} 지력:{h['지력']} 통솔:{h['통솔']})")

        # 포로 정보
        my_prisoners = self.prisoners.get(self.player_id, [])
        if my_prisoners:
            print(f"\n  ⛓️ 보유 포로: {len(my_prisoners)}명")
            for h in my_prisoners:
                print(f"     - {h['이름']} (무력:{h['무력']} 지력:{h['지력']} 원소속:{self.factions.get(h.get('원소속', 0), {}).get('이름', '재야')})")

        input("\n  엔터를 누르면 계속...")

    # === 이동 시스템 ===
    def run_move(self):
        """이동 명령 (장수/병력/군량)"""
        print(f"\n{'═' * 50}")
        print("  🚚 이동")
        print(f"{'═' * 50}")
        print("  1. 장수 이동")
        print("  2. 병력 이동")
        print("  3. 군량 이동")
        print("  0. 취소")

        choice = get_valid_input("  선택: ", 0, 3)
        if choice == 0:
            return
        elif choice == 1:
            self.move_hero()
        elif choice == 2:
            self.move_troops()
        elif choice == 3:
            self.move_supply()

    def select_my_castle(self, msg="성을 선택하세요"):
        """내 성 선택"""
        my_castles = self.get_faction_castles(self.player_id)
        castle_list = list(my_castles.keys())

        print(f"\n  {msg}")
        for i, name in enumerate(castle_list, 1):
            castle = my_castles[name]
            hero_names = ", ".join([h['이름'] for h in castle['장수']]) if castle['장수'] else "(없음)"
            print(f"  {i}. {name} - 병력:{castle['병력']:,} 군량:{castle['군량']:,} 장수:{hero_names}")
        print("  0. 취소")

        choice = get_valid_input("  선택: ", 0, len(castle_list))
        if choice == 0:
            return None
        return castle_list[choice - 1]

    def move_hero(self):
        """장수 이동 (여러 명 동시 이동 가능)"""
        # 1. 출발 성 선택
        from_castle = self.select_my_castle("출발 성을 선택하세요")
        if not from_castle:
            return

        castle = self.castles[from_castle]
        # 이동 가능한 장수 (부상X, 행동완료X)
        available = [h for h in castle['장수']
                     if h.get('부상', 0) == 0 and h['이름'] not in self.acted_heroes]

        if not available:
            print("  ❌ 이동 가능한 장수가 없습니다.")
            return

        # 2. 목적지 먼저 선택 (인접 아군 성)
        friendly = self.get_adjacent_friendly_castles(from_castle)
        if not friendly:
            print("  ❌ 인접한 아군 성이 없습니다.")
            return

        print(f"\n  목적지를 선택하세요:")
        for i, name in enumerate(friendly, 1):
            c = self.castles[name]
            hero_names = ', '.join([h['이름'] for h in c['장수']]) if c['장수'] else '없음'
            print(f"  {i}. {name} - 병력:{c['병력']:,} 장수:{hero_names}")
        print("  0. 취소")

        choice = get_valid_input("  선택: ", 0, len(friendly))
        if choice == 0:
            return
        to_castle = friendly[choice - 1]

        # 3. 장수 선택 (여러 명 가능)
        print(f"\n  이동할 장수를 선택하세요 (예: 1,2,3 또는 all):")
        for i, h in enumerate(available, 1):
            print(f"  {i}. {h['이름']} (무력:{h['무력']} 지력:{h['지력']})")
        print("  0. 취소")

        selection = input("  선택: ").strip().lower()
        if selection == '0' or selection == '':
            return

        # 선택 파싱
        selected_heroes = []
        if selection == 'all':
            selected_heroes = available[:]
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(available):
                        if available[idx - 1] not in selected_heroes:
                            selected_heroes.append(available[idx - 1])
            except ValueError:
                print("  ❌ 잘못된 입력입니다.")
                return

        if not selected_heroes:
            print("  ❌ 선택된 장수가 없습니다.")
            return

        # 4. 이동 실행
        moved_names = []
        for hero in selected_heroes:
            castle['장수'].remove(hero)
            self.castles[to_castle]['장수'].append(hero)
            self.acted_heroes.append(hero['이름'])
            moved_names.append(hero['이름'])

        print(f"\n  ✅ {', '.join(moved_names)}이(가) {from_castle}에서 {to_castle}(으)로 이동했습니다.")
        self.advance_day()

    def move_troops(self):
        """병력 이동"""
        # 1. 출발 성 선택
        from_castle = self.select_my_castle("출발 성을 선택하세요")
        if not from_castle:
            return

        castle = self.castles[from_castle]
        if castle['병력'] <= 0:
            print("  ❌ 이동할 병력이 없습니다.")
            return

        # 이동 가능한 장수 확인 (호송 필요)
        available = [h for h in castle['장수']
                     if h.get('부상', 0) == 0 and h['이름'] not in self.acted_heroes]
        if not available:
            print("  ❌ 병력을 호송할 장수가 없습니다.")
            return

        # 2. 호송 장수 선택
        print(f"\n  호송할 장수를 선택하세요:")
        for i, h in enumerate(available, 1):
            print(f"  {i}. {h['이름']}")
        print("  0. 취소")

        choice = get_valid_input("  선택: ", 0, len(available))
        if choice == 0:
            return
        escort = available[choice - 1]

        # 3. 목적지 선택
        friendly = self.get_adjacent_friendly_castles(from_castle)
        if not friendly:
            print("  ❌ 인접한 아군 성이 없습니다.")
            return

        print(f"\n  목적지를 선택하세요:")
        for i, name in enumerate(friendly, 1):
            c = self.castles[name]
            print(f"  {i}. {name} - 현재 병력:{c['병력']:,}")
        print("  0. 취소")

        choice = get_valid_input("  선택: ", 0, len(friendly))
        if choice == 0:
            return
        to_castle = friendly[choice - 1]

        # 4. 이동량 선택
        max_troops = castle['병력']
        print(f"\n  이동할 병력 수 (최대 {max_troops:,}):")
        amount = get_valid_input("  병력: ", 1, max_troops)

        # 5. 이동 실행
        castle['병력'] -= amount
        self.castles[to_castle]['병력'] += amount
        self.acted_heroes.append(escort['이름'])

        print(f"\n  ✅ {escort['이름']}이(가) 병력 {amount:,}을(를) {to_castle}(으)로 호송했습니다.")
        self.advance_day()

    def move_supply(self):
        """군량 이동"""
        # 1. 출발 성 선택
        from_castle = self.select_my_castle("출발 성을 선택하세요")
        if not from_castle:
            return

        castle = self.castles[from_castle]
        if castle['군량'] <= 0:
            print("  ❌ 이동할 군량이 없습니다.")
            return

        # 호송 장수 확인
        available = [h for h in castle['장수']
                     if h.get('부상', 0) == 0 and h['이름'] not in self.acted_heroes]
        if not available:
            print("  ❌ 군량을 호송할 장수가 없습니다.")
            return

        # 2. 호송 장수 선택
        print(f"\n  호송할 장수를 선택하세요:")
        for i, h in enumerate(available, 1):
            print(f"  {i}. {h['이름']}")
        print("  0. 취소")

        choice = get_valid_input("  선택: ", 0, len(available))
        if choice == 0:
            return
        escort = available[choice - 1]

        # 3. 목적지 선택
        friendly = self.get_adjacent_friendly_castles(from_castle)
        if not friendly:
            print("  ❌ 인접한 아군 성이 없습니다.")
            return

        print(f"\n  목적지를 선택하세요:")
        for i, name in enumerate(friendly, 1):
            c = self.castles[name]
            print(f"  {i}. {name} - 현재 군량:{c['군량']:,}")
        print("  0. 취소")

        choice = get_valid_input("  선택: ", 0, len(friendly))
        if choice == 0:
            return
        to_castle = friendly[choice - 1]

        # 4. 이동량 선택
        max_supply = castle['군량']
        print(f"\n  이동할 군량 (최대 {max_supply:,}):")
        amount = get_valid_input("  군량: ", 1, max_supply)

        # 5. 이동 실행
        castle['군량'] -= amount
        self.castles[to_castle]['군량'] += amount
        self.acted_heroes.append(escort['이름'])

        print(f"\n  ✅ {escort['이름']}이(가) 군량 {amount:,}을(를) {to_castle}(으)로 호송했습니다.")
        self.advance_day()

    def run_diplomacy(self):
        """외교 명령 (동맹 체결/파기)"""
        pl = self.get_player()
        my_alliance = self.alliances.get(self.player_id)

        print("\n┌─────────────────── 외 교 ───────────────────┐")

        # 현재 동맹 상태 표시
        if my_alliance:
            ally_name = self.factions[my_alliance['대상']]['이름']
            print(f"│  현재 동맹: {ally_name}군 (남은 기간: {my_alliance['남은개월']}개월)  │")
        else:
            print("│  현재 동맹: 없음                              │")

        print("├─────────────────────────────────────────────┤")
        print("│  1. 동맹 체결                               │")
        print("│  2. 동맹 파기                               │")
        print("│  0. 돌아가기                                │")
        print("└─────────────────────────────────────────────┘")

        cmd = get_valid_input("  선택: ", 0, 2)

        if cmd == 0:
            return

        elif cmd == 1:
            # 동맹 체결
            if my_alliance:
                print(f"  ❌ 이미 {self.factions[my_alliance['대상']]['이름']}군과 동맹 중입니다.")
                print("     기존 동맹을 파기해야 새로운 동맹을 맺을 수 있습니다.")
                return

            # 동맹 가능한 세력 목록
            available = [f for f in self.factions if f != self.player_id and self.get_faction_castle_count(f) > 0]
            if not available:
                print("  ❌ 동맹 가능한 세력이 없습니다.")
                return

            print("\n┌─────────── 동맹 대상 선택 ───────────┐")
            for fid in available:
                f = self.factions[fid]
                castle_cnt = self.get_faction_castle_count(fid)
                troop_cnt = self.get_faction_total_troops(fid)
                # 상대가 이미 다른 세력과 동맹 중인지 확인
                their_alliance = self.alliances.get(fid)
                if their_alliance:
                    status = f"(동맹중: {self.factions[their_alliance['대상']]['이름']}군)"
                else:
                    status = ""
                print(f"│  {fid}. {f['이름']}군 (성:{castle_cnt}, 병력:{troop_cnt:,}) {status}  │")
            print("└─────────────────────────────────────┘")

            t_id = get_valid_input("  대상 선택 (0=취소): ", 0, max(self.factions.keys()))
            if t_id == 0 or t_id not in available:
                return

            # 상대가 이미 동맹 중이면 거절
            if self.alliances.get(t_id):
                print(f"  ❌ {self.factions[t_id]['이름']}군은 이미 다른 세력과 동맹 중입니다.")
                return

            # 동맹 체결 시도 (매력 기반 성공률)
            h = self.select_hero("외교 담당", check_acted=False, mark_acted=False)
            if h is None:
                return

            # 성공률: 기본 40% + 매력/2
            success_rate = 40 + h['매력'] // 2
            print(f"\n  🤝 {h['이름']}이(가) {self.factions[t_id]['이름']}군에 동맹을 제안합니다... (성공률: {min(100, success_rate)}%)")
            time.sleep(1)

            if random.randint(0, 100) < success_rate:
                # 동맹 체결 성공 (1년 = 12개월)
                self.alliances[self.player_id] = {"대상": t_id, "남은개월": 12}
                self.alliances[t_id] = {"대상": self.player_id, "남은개월": 12}
                print(f"  ✅ {self.factions[t_id]['이름']}군과 동맹을 체결했습니다! (기간: 1년)")
                self.advance_day()
            else:
                print(f"  ❌ {self.factions[t_id]['이름']}군이 동맹을 거절했습니다.")
                self.advance_day()

        elif cmd == 2:
            # 동맹 파기
            if not my_alliance:
                print("  ❌ 현재 동맹 중인 세력이 없습니다.")
                return

            ally_id = my_alliance['대상']
            ally_name = self.factions[ally_id]['이름']

            print(f"\n  ⚠️ 정말로 {ally_name}군과의 동맹을 파기하시겠습니까?")
            print("     동맹 파기 시 휘하 장수들의 충성도가 하락합니다!")
            confirm = get_valid_input("  1=파기, 0=취소: ", 0, 1)

            if confirm == 0:
                return

            # 동맹 파기
            del self.alliances[self.player_id]
            if ally_id in self.alliances:
                del self.alliances[ally_id]

            # 장수 충성도 하락 (신의 없는 군주라는 평판)
            loyalty_drop = 15
            print(f"\n  💔 {ally_name}군과의 동맹을 파기했습니다!")
            print(f"  📉 휘하 장수들의 충성도가 {loyalty_drop} 하락합니다...")

            my_heroes = self.get_faction_heroes(self.player_id)
            for h in my_heroes:
                if not h.get('is_lord', False):  # 군주 제외
                    h['충성'] = max(0, h['충성'] - loyalty_drop)

            self.advance_day()

    def advance_day(self):
        """날짜 진행 (1일 → 11일 → 21일 → 다음달 1일)"""
        self.actions_left -= 1

        if self.actions_left <= 0:
            # 다음 달로
            self.month += 1
            self.actions_left = 3
            self.acted_heroes = []  # 행동한 장수 목록 초기화
            self.day = 1

            # 월별 처리
            self.process_monthly()

            if self.month > 12:
                self.month = 1
                self.year += 1
        else:
            # 같은 달 내 날짜 진행
            if self.day == 1:
                self.day = 11
            elif self.day == 11:
                self.day = 21

    def process_monthly(self):
        """월별 처리: 부상 회복, 포로 탈출 체크"""

        # 부상 회복 (플레이어 장수)
        my_heroes = self.get_faction_heroes(self.player_id)
        for h in my_heroes:
            if h.get('부상', 0) > 0:
                h['부상'] -= 1
                if h['부상'] == 0:
                    print(f"  💊 {h['이름']}의 부상이 완치되었습니다!")

        # 포로 탈출 체크 (각 세력별)
        for fid, prisoners in self.prisoners.items():
            escaped = []
            for prisoner in prisoners[:]:  # 복사본으로 순회
                # 15% 확률로 탈출
                if random.random() < 0.15:
                    escaped.append(prisoner)
                    prisoners.remove(prisoner)
                    prisoner['충성'] = 70  # 본 세력 복귀 시 충성도 회복

                    # 원래 세력이 존재하면 그 세력으로 복귀
                    original_faction = prisoner.get('원소속', 0)
                    if original_faction > 0 and original_faction in self.factions and self.get_faction_castle_count(original_faction) > 0:
                        # 원래 세력의 수도에 배치
                        orig_castles = self.get_faction_castles(original_faction)
                        orig_capital = None
                        for cname, cdata in orig_castles.items():
                            if cdata.get('수도'):
                                orig_capital = cdata
                                break
                        if not orig_capital:
                            orig_capital = list(orig_castles.values())[0]
                        orig_capital['장수'].append(prisoner)
                        if fid == self.player_id:
                            print(f"  🏃 포로 {prisoner['이름']}이(가) 탈출하여 {self.factions[original_faction]['이름']}군으로 돌아갔습니다!")
                    else:
                        # 원래 세력이 멸망했으면 재야로
                        prisoner['충성'] = 50
                        self.free_heroes.append(prisoner)
                        if fid == self.player_id:
                            print(f"  🏃 포로 {prisoner['이름']}이(가) 탈출했습니다! (재야로)")

        # 동맹 기간 감소
        expired_alliances = []
        for fid, alliance in list(self.alliances.items()):
            alliance['남은개월'] -= 1
            if alliance['남은개월'] <= 0:
                expired_alliances.append(fid)

        # 만료된 동맹 제거
        for fid in expired_alliances:
            if fid in self.alliances:
                ally_id = self.alliances[fid]['대상']
                ally_name = self.factions.get(ally_id, {}).get('이름', '???')
                if fid == self.player_id:
                    print(f"  📜 {ally_name}군과의 동맹이 만료되었습니다.")
                del self.alliances[fid]

        # 분기 수입 (3, 6, 9, 12월) - 성별로 계산
        if self.month in [3, 6, 9, 12]:
            pl = self.get_player()
            total_gold = 0
            total_rice = 0
            my_castles = self.get_faction_castles(self.player_id)
            for castle_name, castle in my_castles.items():
                g = castle['상업'] * 20
                r = castle['농업'] * 30
                total_gold += g
                castle['군량'] += r
                total_rice += r
            pl['금'] += total_gold
            print(f"\n  📦 [{self.month}월 분기 수입] 금 +{total_gold:,} / 군량 +{total_rice:,}")

    def show_victory_ending(self):
        """천하통일 엔딩"""
        pl = self.get_player()
        TUI.clear()
        sound_mgr.play("sfx_buff.wav")

        # 총 플레이 기간 계산
        total_months = (self.year - 200) * 12 + self.month

        victory_art = f"""
{C.YELLOW}╔═══════════════════════════════════════════════════════════════╗
║                                                                 ║
║       🏆  천 하 통 일  🏆                                       ║
║                                                                 ║
║         {C.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.YELLOW}         ║
║                                                                 ║
║         {C.GREEN}축하합니다! {pl['이름']}께서 천하를 통일하셨습니다!{C.YELLOW}      ║
║                                                                 ║
║         {C.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.YELLOW}         ║
║                                                                 ║
╚═══════════════════════════════════════════════════════════════╝{C.RESET}
"""
        print(victory_art)
        time.sleep(1)

        print(f"\n{C.BOLD}═══════════ 통일 기록 ═══════════{C.RESET}")
        print(f"  📅 통일 달성: {self.year}년 {self.month}월 (총 {total_months}개월)")
        print(f"  🏰 최종 영토: {self.get_faction_castle_count(self.player_id)}개 성")
        print(f"  ⚔️ 병력: {self.get_faction_total_troops(self.player_id):,}명")
        print(f"  💰 금: {pl['금']:,} / 군량: {self.get_faction_total_supply(self.player_id):,}")

        print(f"\n{C.BOLD}═══════════ 휘하 장수 ═══════════{C.RESET}")
        my_heroes = self.get_faction_heroes(self.player_id)
        for i, h in enumerate(my_heroes):
            rank = "👑" if i == 0 else "⭐" if i < 3 else "🎖️"
            print(f"  {rank} {h['이름']} (무력:{h['무력']} 지력:{h['지력']} 통솔:{h['통솔']})")

        # 등급 계산
        if total_months <= 24:
            grade = "S"
            title = "신화적 정복왕"
        elif total_months <= 48:
            grade = "A"
            title = "대륙의 패왕"
        elif total_months <= 72:
            grade = "B"
            title = "중원의 영웅"
        elif total_months <= 120:
            grade = "C"
            title = "난세의 군웅"
        else:
            grade = "D"
            title = "끈기의 지도자"

        print(f"\n{C.YELLOW}══════════════════════════════════{C.RESET}")
        print(f"  🏅 최종 등급: {C.BOLD}{grade}{C.RESET}")
        print(f"  📜 칭호: {C.CYAN}{title}{C.RESET}")
        print(f"{C.YELLOW}══════════════════════════════════{C.RESET}")

        print(f"\n  {C.GREEN}난세는 끝났고, 새로운 시대가 열렸습니다.{C.RESET}")
        print(f"  {C.GREEN}{pl['이름']}의 이름은 역사에 길이 남을 것입니다.{C.RESET}")
        print(f"\n  {C.GRAY}아무 키나 누르면 종료합니다...{C.RESET}")
        input()

    def main_loop(self):
        TUI.clear()
        sound_mgr.play("bgm_main.mp3")

        title_art = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     ⚔️  삼 국 지 : 패 왕 의  길  ⚔️                  ║
    ║                                                       ║
    ║         Three Kingdoms: Path of the Conqueror         ║
    ║                    [ v2.0 TUI Edition ]               ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
        """
        print(title_art)

        print("\n  1. 새 게임")
        print("  2. 불러오기")

        choice = get_valid_input("\n  선택: ", 1, 2)

        if choice == 1:
            self.setup()
        else:
            self.show_save_slots(show_auto=True)
            slot = get_valid_input("  로드할 슬롯 (0~3, -1=취소): ", -1, 3)
            if slot >= 0:
                try:
                    self.load_game(slot)
                except FileNotFoundError:
                    print("\n  저장 파일이 없습니다. 새 게임을 시작합니다.")
                    input("  아무 키나 누르세요...")
                    self.setup()
            else:
                self.setup()

        while True:
            pl = self.get_player()

            # ===== 패배 조건: 성 0개 =====
            my_castle_count = self.get_faction_castle_count(self.player_id)
            if my_castle_count <= 0:
                print("\n" + "=" * 50)
                print("  🏳️ 멸망... 천하통일의 꿈은 여기서 끝났습니다.")
                print("=" * 50)
                break

            # ===== 승리 조건: 천하통일 (모든 성 점령) =====
            enemies_alive = [f for f in self.factions if f != self.player_id and self.get_faction_castle_count(f) > 0]
            if not enemies_alive:
                self.show_victory_ending()
                break

            # 새로운 달 시작 시 이벤트 및 AI 처리
            if self.day == 1 and self.actions_left == 3:
                if not (self.year == 200 and self.month == 1):  # 첫 달 제외
                    self.process_event()
                    # AI도 월 3회 행동
                    for ai_turn in range(3):
                        self.process_ai_turn()

            my_castle_count = self.get_faction_castle_count(self.player_id)
            if my_castle_count <= 0:
                print("\n  🏳️ 적의 침공으로 멸망했습니다...")
                break

            # 상태 표시 (화면 클리어 후)
            TUI.clear()
            self.auto_save()  # 매 턴 자동 저장 (슬롯 0)
            self.show_status()
            self.show_commands()

            c = get_valid_input("  명령 선택: ", 0, 12)

            if c == 0:
                print("\n  게임을 종료합니다.")
                break
            elif c == 5:
                self.run_war()
                self.advance_day()
            elif c == 7:
                self.show_info()
                # 정보 보기는 행동 소모 안함
            elif c == 9:
                self.run_diplomacy()
                # 외교는 행동 소모 안함 (체결/파기만 소모)
            elif c == 10:
                # 이동 (장수/병력/군량)
                self.run_move()
            elif c == 11:
                # 저장
                self.show_save_slots()
                slot = get_valid_input("  저장할 슬롯 (1~3, 0=취소): ", 0, 3)
                if slot > 0:
                    self.save_game(slot)
            elif c == 12:
                # 로드
                self.show_save_slots(show_auto=True)
                slot = get_valid_input("  로드할 슬롯 (0~3, -1=취소): ", -1, 3)
                if slot >= 0:
                    self.load_game(slot)
            else:
                self.run_policy(c)
                self.advance_day()


if __name__ == "__main__":
    Game().main_loop()
