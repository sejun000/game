#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시연이 키우기 - 육성 시뮬레이션 게임
11살부터 18살까지 8년간 키우는 게임
자동 진행 모드: 0.5초마다 하루씩 진행
"""

import random
import os
import time

class SiyeonGame:
    def __init__(self):
        self.name = "시연"
        self.age = 11
        self.day = 0  # 총 일수 (8년 = 2920일)
        self.money = 50000  # 시작 자금 5만원

        # 스탯 초기화
        self.stats = {
            "도덕심": 50,
            "지력": 30,
            "매력": 30,
            "자존감": 50,
            "화술": 20,
            "작문": 20,
            "수학력": 20,
            "영어력": 20,
            "체력": 60,
            "스트레스": 10
        }

        # 현재 활동 (2주 = 14일 단위로 변경)
        self.current_activity = None
        self.activity_days_left = 0
        self.current_activity_data = None

        # 강제 휴식
        self.forced_rest = False

        # 연속 활동 카운터 (같은 활동 연속으로 할수록 숙련도 상승)
        self.activity_streak = {}  # {"활동명": 연속일수}
        self.last_activity = None

        # 이벤트 메시지
        self.event_message = None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_age(self):
        return 11 + (self.day // 365)

    def get_date_string(self):
        age = self.get_age()
        day_in_year = self.day % 365
        month = day_in_year // 30 + 1
        day_in_month = day_in_year % 30 + 1
        return f"{age}살 {month}월 {day_in_month}일"

    def display_status(self):
        # 상태바 형태로 표시
        bar_width = 15

        def make_bar(value, max_val=100):
            filled = int((value / max_val) * bar_width)
            return "█" * filled + "░" * (bar_width - filled)

        print("\033[2J\033[H", end="")  # 화면 클리어
        print("=" * 65)
        print(f"  {'🌸 시연이 키우기 🌸':^55}")
        print("=" * 65)
        print(f"  📅 {self.get_date_string()}  |  💰 {self.money:,}원")

        # 숙련도 표시
        streak = self.activity_streak.get(self.current_activity, 0) if self.current_activity else 0
        streak_text = f"숙련도: {min(streak, 100)}%" if streak > 0 else ""
        print(f"  📌 현재: {self.current_activity if self.current_activity else '없음'} ({self.activity_days_left}일) {streak_text}")
        print("-" * 65)

        # 스탯을 2열로 표시
        stats_order = ["도덕심", "지력", "매력", "자존감", "화술", "작문", "수학력", "영어력", "체력", "스트레스"]

        for i in range(0, len(stats_order), 2):
            stat1 = stats_order[i]
            val1 = self.stats[stat1]
            bar1 = make_bar(val1)

            if i + 1 < len(stats_order):
                stat2 = stats_order[i + 1]
                val2 = self.stats[stat2]
                bar2 = make_bar(val2)
                print(f"  {stat1:4}{val1:5.1f} {bar1} | {stat2:4}{val2:5.1f} {bar2}")
            else:
                print(f"  {stat1:4}{val1:5.1f} {bar1}")

        print("-" * 65)

        # 경고 표시
        if self.stats['스트레스'] >= self.stats['체력']:
            print("  ⚠️  스트레스 과다! 강제 휴식 중...")
        print("=" * 65)

    def modify_stat(self, stat_name, value):
        self.stats[stat_name] = max(0, min(100, self.stats[stat_name] + value))

    def get_available_jobs(self):
        """나이에 따라 이용 가능한 알바 목록 반환"""
        jobs = {
            "영화관 알바": {
                "money": 1100, "stress": 0.6, "min_age": 11,
                "effects": {"화술": (0.15, 70), "매력": (0.08, 60), "체력": (0.05, 50), "수학력": (-0.05, 30), "작문": (-0.05, 25)}
            },
            "편의점 알바": {
                "money": 900, "stress": 0.7, "min_age": 11,
                "effects": {"화술": (0.08, 60), "도덕심": (0.08, 50), "지력": (-0.05, 25), "매력": (0.05, 35), "체력": (-0.05, 40)}
            },
            "카페 알바": {
                "money": 1000, "stress": 0.5, "min_age": 11,
                "effects": {"매력": (0.15, 70), "화술": (0.12, 65), "체력": (-0.05, 50), "자존감": (0.05, 40), "수학력": (-0.04, 20)}
            },
            "광산 알바": {
                "money": 2200, "stress": 1.8, "min_age": 11,
                "effects": {"체력": (0.2, 80), "매력": (-0.15, 75), "자존감": (-0.12, 55), "도덕심": (-0.06, 35)}
            },
            "유튜브": {
                "money": 600, "stress": 0.4, "min_age": 11, "youtube": True,
                "effects": {"화술": (0.08, 55), "매력": (0.18, 50), "지력": (-0.05, 25), "자존감": (0.12, 45), "작문": (0.06, 35)}
            },
            "건설 알바": {
                "money": 2500, "stress": 1.5, "min_age": 12,
                "effects": {"체력": (0.25, 85), "매력": (-0.12, 65), "자존감": (-0.06, 40), "도덕심": (0.05, 25)}
            },
            "쿠팡배달": {
                "money": 1800, "stress": 1.1, "min_age": 12,
                "effects": {"체력": (0.12, 70), "매력": (-0.06, 45), "화술": (0.05, 35), "지력": (-0.04, 25)}
            },
            "과외 알바": {
                "money": 2900, "stress": 0.9, "min_age": 14, "req_stat": ("지력", 50),
                "effects": {"지력": (0.12, 70), "화술": (0.12, 65), "수학력": (0.08, 55), "자존감": (0.1, 50), "체력": (-0.05, 35), "매력": (0.04, 25)}
            },
            "시장 알바": {
                "money": 1300, "stress": 0.85, "min_age": 15,
                "effects": {"화술": (0.18, 75), "도덕심": (0.12, 60), "매력": (-0.05, 35), "체력": (0.06, 45), "자존감": (0.05, 25)}
            },
            "청와대 알바": {
                "money": 4300, "stress": 1.1, "min_age": 16, "req_stat": ("지력", 60),
                "effects": {"도덕심": (0.22, 80), "화술": (0.18, 75), "자존감": (0.18, 70), "지력": (0.12, 60), "매력": (0.1, 55), "영어력": (0.06, 40), "작문": (0.05, 35)}
            },
        }

        available = {}
        age = self.get_age()

        for job_name, job_data in jobs.items():
            if age >= job_data["min_age"]:
                if "req_stat" in job_data:
                    stat_name, req_value = job_data["req_stat"]
                    if self.stats[stat_name] < req_value:
                        continue
                available[job_name] = job_data

        return available

    def get_available_studies(self):
        """이용 가능한 공부 목록 반환"""
        studies = {
            "대치동 과외": {
                "cost": 3600, "stress": 1.3,
                "effects": {"지력": (0.25, 85), "수학력": (0.22, 80), "영어력": (0.18, 75), "체력": (-0.1, 60), "매력": (-0.05, 40), "자존감": (-0.1, 35), "작문": (0.05, 25)}
            },
            "평촌 과외": {
                "cost": 2200, "stress": 0.85,
                "effects": {"지력": (0.18, 75), "수학력": (0.18, 70), "영어력": (0.12, 65), "체력": (-0.05, 40), "자존감": (-0.05, 25), "작문": (0.05, 35)}
            },
            "평촌 영수학원": {
                "cost": 1400, "stress": 0.6,
                "effects": {"수학력": (0.12, 70), "영어력": (0.12, 70), "지력": (0.06, 50), "체력": (-0.04, 25), "화술": (0.04, 20)}
            },
            "영어 과외": {
                "cost": 1800, "stress": 0.6,
                "effects": {"영어력": (0.22, 80), "화술": (0.06, 45), "수학력": (-0.05, 30), "매력": (0.05, 35), "지력": (0.05, 25)}
            },
            "국어 과외": {
                "cost": 1800, "stress": 0.6,
                "effects": {"작문": (0.22, 80), "지력": (0.12, 60), "수학력": (-0.05, 30), "화술": (0.08, 45), "도덕심": (0.05, 25)}
            },
        }
        return studies

    def get_available_activities(self):
        """이용 가능한 활동(운동/예술) 목록 반환"""
        activities = {
            "운동": {
                "cost": 700, "stress": -0.4,
                "effects": {"체력": (0.25, 85), "자존감": (0.12, 65), "매력": (0.12, 55), "지력": (-0.04, 20), "도덕심": (0.05, 25)}
            },
            "미술 학원": {
                "cost": 1800, "stress": 0.35,
                "effects": {"매력": (0.18, 75), "자존감": (0.12, 60), "지력": (0.06, 35), "수학력": (-0.05, 25), "작문": (0.06, 30), "도덕심": (0.05, 20)}
            },
            "피아노 학원": {
                "cost": 2100, "stress": 0.4,
                "effects": {"매력": (0.18, 75), "자존감": (0.12, 60), "지력": (0.08, 45), "체력": (-0.04, 35), "화술": (0.05, 25), "영어력": (0.04, 15)}
            },
        }
        return activities

    def get_rest_options(self):
        """휴식 옵션 반환"""
        options = {
            "집에서 휴식": {
                "cost": 0, "stress": -1.1,
                "effects": {"체력": (0.18, 75), "지력": (-0.04, 15), "매력": (-0.04, 12)}
            },
            "PC방": {
                "cost": 350, "stress": -1.4,
                "effects": {"체력": (-0.1, 55), "지력": (0.05, 35), "매력": (-0.05, 25), "화술": (0.05, 30)}
            },
            "친구 만나기": {
                "cost": 700, "stress": -1.3,
                "effects": {"화술": (0.12, 70), "자존감": (0.08, 55), "매력": (0.1, 55), "도덕심": (0.05, 35), "체력": (-0.04, 20)}
            },
            "독서": {
                "cost": 200, "stress": -0.7,
                "effects": {"지력": (0.12, 70), "작문": (0.12, 70), "도덕심": (0.06, 45), "매력": (-0.04, 15), "영어력": (0.05, 25)}
            },
        }
        return options

    def get_travel_options(self):
        """여행 옵션 반환"""
        travels = {
            "국내 여행": {
                "cost": 7100, "stress": -2.2,
                "effects": {"자존감": (0.18, 80), "체력": (0.06, 50), "매력": (0.1, 60), "도덕심": (0.1, 45), "화술": (0.05, 35)}
            },
            "제주도 여행": {
                "cost": 14300, "stress": -2.8,
                "effects": {"자존감": (0.22, 85), "체력": (0.12, 65), "매력": (0.15, 70), "도덕심": (0.1, 55), "화술": (0.1, 45), "지력": (0.05, 25)}
            },
            "동남아 여행": {
                "cost": 35700, "stress": -3.5,
                "effects": {"자존감": (0.28, 90), "영어력": (0.18, 75), "매력": (0.18, 75), "화술": (0.15, 65), "도덕심": (0.1, 45), "지력": (0.1, 35), "체력": (0.05, 25)}
            },
            "유럽 여행": {
                "cost": 71400, "stress": -4.2,
                "effects": {"자존감": (0.35, 95), "영어력": (0.28, 85), "매력": (0.28, 85), "지력": (0.18, 70), "도덕심": (0.18, 65), "화술": (0.18, 55), "작문": (0.1, 45), "체력": (0.1, 35)}
            },
        }
        return travels

    def get_events(self):
        """활동별 이벤트 정의"""
        return {
            "영화관 알바": [
                ("유명 배우를 만났다!", {"매력": 3, "자존감": 2}, 5),
                ("손님이 팝콘을 쏟았다...", {"스트레스": 5}, 10),
                ("팁을 받았다!", {"money": 5000}, 8),
                ("영화를 몰래 봤다!", {"스트레스": -3, "도덕심": -1}, 7),
            ],
            "편의점 알바": [
                ("진상 손님 등장!", {"스트레스": 8, "화술": 1}, 12),
                ("야간 수당 보너스!", {"money": 3000}, 10),
                ("도둑을 잡았다!", {"도덕심": 3, "자존감": 2}, 3),
                ("유통기한 임박 도시락 득템!", {"money": 2000}, 15),
            ],
            "카페 알바": [
                ("라떼아트 성공!", {"매력": 2, "자존감": 2}, 10),
                ("커피를 쏟았다...", {"스트레스": 5, "자존감": -1}, 8),
                ("단골손님에게 칭찬받았다!", {"화술": 2, "자존감": 3}, 12),
                ("바리스타 자격증 권유받음!", {"지력": 1, "자존감": 2}, 5),
            ],
            "광산 알바": [
                ("금맥을 발견했다!", {"money": 20000}, 2),
                ("낙석 사고! 다행히 무사함", {"스트레스": 10, "체력": -2}, 5),
                ("동료에게 도움받음", {"도덕심": 2}, 8),
                ("체력이 강해지는 느낌!", {"체력": 3}, 10),
            ],
            "유튜브": [
                ("영상이 대박났다!", {"money": 50000, "매력": 5}, 3),
                ("악플 테러...", {"스트레스": 10, "자존감": -3}, 8),
                ("구독자 1000명 달성!", {"자존감": 5, "화술": 2}, 5),
                ("협찬 제의가 왔다!", {"money": 30000, "매력": 2}, 4),
                ("편집 실력이 늘었다!", {"지력": 2, "작문": 1}, 10),
            ],
            "건설 알바": [
                ("안전사고 위기! 무사함", {"스트레스": 8}, 5),
                ("현장 소장에게 칭찬받음!", {"자존감": 3, "money": 5000}, 8),
                ("근육이 붙는 느낌!", {"체력": 4, "매력": 1}, 12),
                ("동료들과 삼겹살 회식!", {"스트레스": -5, "화술": 1}, 10),
            ],
            "쿠팡배달": [
                ("팁을 많이 받았다!", {"money": 8000}, 10),
                ("비 오는 날 배달...", {"스트레스": 8, "체력": -1}, 8),
                ("최단시간 배달 달성!", {"자존감": 2, "체력": 1}, 7),
                ("길을 잘못 들었다...", {"스트레스": 5}, 10),
            ],
            "과외 알바": [
                ("학생 성적이 올랐다!", {"자존감": 5, "지력": 2, "money": 10000}, 8),
                ("학부모에게 칭찬받음!", {"화술": 2, "자존감": 3}, 10),
                ("학생이 안 듣는다...", {"스트레스": 8}, 12),
                ("가르치면서 나도 복습됨!", {"수학력": 2, "영어력": 2}, 15),
            ],
            "시장 알바": [
                ("단골 어르신이 덕담해주심!", {"도덕심": 3, "자존감": 2}, 12),
                ("흥정 실력이 늘었다!", {"화술": 3}, 10),
                ("떨이로 싸게 샀다!", {"money": 3000}, 15),
                ("무거운 짐 나르기...", {"체력": 2, "스트레스": 3}, 8),
            ],
            "청와대 알바": [
                ("고위 공무원을 만났다!", {"도덕심": 3, "화술": 3, "자존감": 5}, 5),
                ("중요한 회의에 참석!", {"지력": 3, "도덕심": 2}, 8),
                ("보안 교육 이수!", {"도덕심": 2, "지력": 1}, 15),
                ("대통령 연설문 열람!", {"작문": 3, "지력": 2}, 3),
            ],
            "대치동 과외": [
                ("선생님이 특별 과외 해줌!", {"지력": 4, "수학력": 3}, 5),
                ("너무 어려워서 멘붕...", {"스트레스": 10, "자존감": -2}, 10),
                ("모의고사 성적 급상승!", {"자존감": 5, "지력": 3}, 8),
                ("공부 비법을 깨달았다!", {"지력": 3, "수학력": 2, "영어력": 2}, 5),
            ],
            "평촌 과외": [
                ("선생님과 좋은 관계!", {"자존감": 2, "화술": 1}, 12),
                ("이해가 안 돼...", {"스트레스": 5}, 10),
                ("성적이 조금 올랐다!", {"자존감": 2, "지력": 2}, 15),
            ],
            "평촌 영수학원": [
                ("친구를 사귀었다!", {"화술": 2, "자존감": 1}, 12),
                ("졸다가 혼남...", {"스트레스": 3, "도덕심": -1}, 8),
                ("단체 시험에서 1등!", {"자존감": 4, "지력": 2}, 5),
            ],
            "영어 과외": [
                ("원어민과 대화 성공!", {"영어력": 4, "자존감": 3, "화술": 2}, 5),
                ("발음 교정받음!", {"영어력": 2, "매력": 1}, 10),
                ("영어 영화 자막없이 봄!", {"영어력": 3, "지력": 1}, 8),
            ],
            "국어 과외": [
                ("선생님이 글 칭찬해줌!", {"작문": 4, "자존감": 3}, 8),
                ("책을 선물받음!", {"작문": 2, "지력": 2}, 10),
                ("글짓기 대회 입상!", {"작문": 5, "자존감": 5, "money": 50000}, 2),
            ],
            "운동": [
                ("새로운 기록 달성!", {"체력": 4, "자존감": 4}, 8),
                ("근육통...", {"스트레스": 3, "체력": 2}, 15),
                ("운동 친구 생김!", {"화술": 2, "자존감": 1}, 10),
                ("몸이 가벼워지는 느낌!", {"체력": 3, "매력": 2}, 12),
            ],
            "미술 학원": [
                ("작품이 전시됐다!", {"매력": 5, "자존감": 5}, 3),
                ("색 감각이 좋아짐!", {"매력": 3}, 12),
                ("그림이 잘 안 그려짐...", {"스트레스": 5}, 10),
                ("선생님에게 재능있다고 칭찬!", {"자존감": 4, "매력": 2}, 8),
            ],
            "피아노 학원": [
                ("발표회에서 연주 성공!", {"매력": 5, "자존감": 5, "화술": 2}, 5),
                ("손가락이 아프다...", {"스트레스": 3, "체력": -1}, 10),
                ("새로운 곡을 마스터!", {"지력": 2, "자존감": 3}, 12),
                ("절대음감이 생기는 느낌!", {"지력": 3, "매력": 2}, 5),
            ],
            "집에서 휴식": [
                ("푹 잤다!", {"체력": 5, "스트레스": -5}, 15),
                ("심심해...", {"스트레스": 2}, 10),
                ("좋은 영화를 봤다!", {"지력": 1, "스트레스": -3}, 12),
            ],
            "PC방": [
                ("게임에서 1등!", {"자존감": 3, "스트레스": -5}, 8),
                ("밤새다가 지침...", {"체력": -3, "스트레스": -2}, 10),
                ("게임 친구 생김!", {"화술": 2}, 12),
            ],
            "친구 만나기": [
                ("속 시원하게 수다 떨음!", {"스트레스": -8, "화술": 3}, 15),
                ("친구가 고민 상담 해줌!", {"자존감": 3, "도덕심": 1}, 10),
                ("맛집 탐방!", {"스트레스": -5, "money": -5000}, 12),
            ],
            "독서": [
                ("인생책을 발견!", {"지력": 4, "작문": 3, "도덕심": 2}, 5),
                ("집중이 안 돼...", {"스트레스": 2}, 10),
                ("새로운 지식을 얻음!", {"지력": 3, "작문": 2}, 15),
            ],
            "국내 여행": [
                ("멋진 풍경 발견!", {"자존감": 4, "스트레스": -8}, 15),
                ("맛있는 음식!", {"스트레스": -5}, 20),
                ("새로운 친구를 만남!", {"화술": 3, "매력": 2}, 8),
            ],
            "제주도 여행": [
                ("오름 등반 성공!", {"체력": 4, "자존감": 4}, 12),
                ("바다가 너무 예뻤다!", {"스트레스": -10, "자존감": 3}, 18),
                ("흑돼지 먹방!", {"스트레스": -5}, 20),
            ],
            "동남아 여행": [
                ("영어로 대화 성공!", {"영어력": 5, "자존감": 4, "화술": 3}, 15),
                ("이국적인 문화 체험!", {"지력": 3, "도덕심": 2}, 12),
                ("물가가 싸서 횡재 기분!", {"스트레스": -8, "자존감": 2}, 15),
            ],
            "유럽 여행": [
                ("미술관에서 감동!", {"매력": 5, "지력": 4, "자존감": 4}, 12),
                ("역사 유적지 탐방!", {"지력": 5, "도덕심": 3}, 15),
                ("현지인과 친구됨!", {"영어력": 5, "화술": 4, "매력": 3}, 8),
            ],
        }

    def apply_daily_effects(self, activity_data):
        """하루치 효과 적용"""
        changes = []
        self.event_message = None

        # 숙련도 계산 (같은 활동 연속할수록 증가)
        if self.current_activity:
            if self.current_activity not in self.activity_streak:
                self.activity_streak[self.current_activity] = 0
            self.activity_streak[self.current_activity] += 1

        streak = self.activity_streak.get(self.current_activity, 0)
        work_success_rate = min(50 + streak, 95)  # 기본 50%, 최대 95%

        # 제대로 일한 날만 돈 받음 (알바의 경우)
        if "money" in activity_data:
            if random.randint(1, 100) <= work_success_rate:
                self.money += activity_data["money"]
                changes.append(f"💰+{activity_data['money']:,}")
            else:
                changes.append("💤")

        # 비용은 항상 지출
        if "cost" in activity_data:
            self.money -= activity_data["cost"]

        # 스트레스
        self.modify_stat("스트레스", activity_data.get("stress", 0))

        # 스탯 변화 (3~4일에 한번)
        if "effects" in activity_data:
            for stat, (change, probability) in activity_data["effects"].items():
                daily_prob = probability * 0.28
                if random.randint(1, 100) <= daily_prob:
                    actual_change = change * random.uniform(0.7, 1.3)
                    self.modify_stat(stat, actual_change)
                    if abs(actual_change) >= 0.05:
                        sign = "↑" if actual_change > 0 else "↓"
                        changes.append(f"{stat}{sign}")

        # 이벤트 발생 체크
        events = self.get_events()
        if self.current_activity in events:
            for event_text, effects, probability in events[self.current_activity]:
                if random.randint(1, 100) <= probability:
                    self.event_message = f"🎯 {event_text}"
                    for key, value in effects.items():
                        if key == "money":
                            self.money += value
                        else:
                            self.modify_stat(key, value)
                    break  # 하루에 하나의 이벤트만

        return changes

    def show_selection_menu(self):
        """사용자가 활동 선택하는 메뉴"""
        self.clear_screen()
        self.display_status()

        # 강제 휴식 체크
        if self.stats['스트레스'] >= self.stats['체력']:
            print("\n  ⚠️ 스트레스 과다! 강제 휴식입니다.")
            input("  Enter를 누르면 2주간 휴식합니다...")
            return ("집에서 휴식", self.get_rest_options()["집에서 휴식"])

        print("\n  [ 다음 2주 동안 할 활동을 선택하세요 ]")
        print()
        print("  1. 아르바이트")
        print("  2. 공부")
        print("  3. 활동 (운동/예술)")
        print("  4. 휴식")
        print("  5. 여행")
        print()

        while True:
            choice = input("  선택 (1-5): ").strip()

            if choice == "1":
                return self.select_job()
            elif choice == "2":
                return self.select_study()
            elif choice == "3":
                return self.select_activity_menu()
            elif choice == "4":
                return self.select_rest()
            elif choice == "5":
                return self.select_travel()
            else:
                print("  잘못된 입력입니다. 1-5 중에서 선택하세요.")

    def select_job(self):
        """알바 선택"""
        jobs = self.get_available_jobs()
        job_list = list(jobs.items())

        print("\n  [ 아르바이트 선택 ]")
        print("-" * 50)
        for i, (name, data) in enumerate(job_list, 1):
            req = ""
            if "req_stat" in data:
                req = f" [요구: {data['req_stat'][0]} {data['req_stat'][1]}]"
            print(f"  {i}. {name}{req} - 일당 {data['money']:,}원")
        print("  0. 뒤로가기")
        print("-" * 50)

        while True:
            choice = input("  선택: ").strip()
            if choice == "0":
                return self.show_selection_menu()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(job_list):
                    return job_list[idx]
            except ValueError:
                pass
            print("  잘못된 입력입니다.")

    def select_study(self):
        """공부 선택"""
        studies = self.get_available_studies()
        study_list = list(studies.items())

        print("\n  [ 공부 선택 ]")
        print("-" * 50)
        for i, (name, data) in enumerate(study_list, 1):
            affordable = "O" if self.money >= data['cost'] * 14 else "X"
            print(f"  {i}. {name} - 일 {data['cost']:,}원 (2주: {data['cost']*14:,}원) [{affordable}]")
        print("  0. 뒤로가기")
        print("-" * 50)

        while True:
            choice = input("  선택: ").strip()
            if choice == "0":
                return self.show_selection_menu()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(study_list):
                    return study_list[idx]
            except ValueError:
                pass
            print("  잘못된 입력입니다.")

    def select_activity_menu(self):
        """활동 선택"""
        activities = self.get_available_activities()
        activity_list = list(activities.items())

        print("\n  [ 활동 선택 ]")
        print("-" * 50)
        for i, (name, data) in enumerate(activity_list, 1):
            affordable = "O" if self.money >= data['cost'] * 14 else "X"
            stress_text = f"스트레스 {data['stress']:+.1f}/일"
            print(f"  {i}. {name} - 일 {data['cost']:,}원 | {stress_text} [{affordable}]")
        print("  0. 뒤로가기")
        print("-" * 50)

        while True:
            choice = input("  선택: ").strip()
            if choice == "0":
                return self.show_selection_menu()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(activity_list):
                    return activity_list[idx]
            except ValueError:
                pass
            print("  잘못된 입력입니다.")

    def select_rest(self):
        """휴식 선택"""
        rests = self.get_rest_options()
        rest_list = list(rests.items())

        print("\n  [ 휴식 선택 ]")
        print("-" * 50)
        for i, (name, data) in enumerate(rest_list, 1):
            cost_text = f"일 {data['cost']:,}원" if data['cost'] > 0 else "무료"
            print(f"  {i}. {name} - {cost_text} | 스트레스 {data['stress']:+.1f}/일")
        print("  0. 뒤로가기")
        print("-" * 50)

        while True:
            choice = input("  선택: ").strip()
            if choice == "0":
                return self.show_selection_menu()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(rest_list):
                    return rest_list[idx]
            except ValueError:
                pass
            print("  잘못된 입력입니다.")

    def select_travel(self):
        """여행 선택"""
        travels = self.get_travel_options()
        travel_list = list(travels.items())

        print("\n  [ 여행 선택 ]")
        print("-" * 50)
        for i, (name, data) in enumerate(travel_list, 1):
            affordable = "O" if self.money >= data['cost'] * 14 else "X"
            print(f"  {i}. {name} - 일 {data['cost']:,}원 (2주: {data['cost']*14:,}원) [{affordable}]")
        print("  0. 뒤로가기")
        print("-" * 50)

        while True:
            choice = input("  선택: ").strip()
            if choice == "0":
                return self.show_selection_menu()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(travel_list):
                    return travel_list[idx]
            except ValueError:
                pass
            print("  잘못된 입력입니다.")

    def check_game_end(self):
        """게임 종료 조건 체크"""
        return self.day >= 2920  # 8년 = 2920일

    def show_ending(self):
        """엔딩 표시"""
        self.clear_screen()
        print("=" * 65)
        print(f"  {'🎓 시연이가 18살이 되었습니다! 🎓':^55}")
        print("=" * 65)
        print()
        print("  [ 최종 스탯 ]")
        print("-" * 65)
        total = 0
        for stat, value in self.stats.items():
            if stat != "스트레스":
                bar = "█" * int(value / 5) + "░" * (20 - int(value / 5))
                print(f"  {stat:6} {value:5.1f} {bar}")
                total += value
        print("-" * 65)
        print(f"  총 스탯 합계: {total:.1f}")
        print(f"  최종 소지금: {self.money:,}원")
        print()

        # 엔딩 결정
        avg_stat = total / 9
        if avg_stat >= 80 and self.money >= 1000000:
            print("  🌟 PERFECT ENDING 🌟")
            print("  시연이는 모든 분야에서 뛰어난 인재가 되었습니다!")
        elif avg_stat >= 60:
            print("  ⭐ GOOD ENDING ⭐")
            print("  시연이는 훌륭하게 성장했습니다!")
        elif avg_stat >= 40:
            print("  📖 NORMAL ENDING 📖")
            print("  시연이는 평범하지만 행복하게 자랐습니다.")
        else:
            print("  💔 BAD ENDING 💔")
            print("  시연이는 힘든 시간을 보냈습니다...")

        print()
        print("=" * 65)

    def run(self):
        """게임 메인 루프"""
        self.clear_screen()
        print("=" * 60)
        print(f"  {'🌸 시연이 키우기 🌸':^50}")
        print("=" * 60)
        print()
        print("  11살 시연이를 18살까지 키워주세요!")
        print("  2주마다 활동을 선택하면 0.5초씩 하루가 진행됩니다.")
        print()
        print("  Ctrl+C로 중간에 종료할 수 있습니다.")
        print()
        input("  Enter를 눌러 시작...")

        try:
            while not self.check_game_end():
                # 2주마다 사용자가 활동 선택
                if self.activity_days_left <= 0:
                    activity_name, activity_data = self.show_selection_menu()
                    self.current_activity = activity_name
                    self.activity_days_left = 14
                    self.current_activity_data = activity_data

                # 하루 진행
                changes = self.apply_daily_effects(self.current_activity_data)

                # 화면 표시
                self.display_status()

                # 이벤트 표시
                if self.event_message:
                    print(f"  {self.event_message}")

                # 변화 표시
                if changes:
                    print(f"  📊 {', '.join(changes)}")

                # 다음 날로
                self.day += 1
                self.activity_days_left -= 1

                # 0.5초 대기
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n\n  게임이 중단되었습니다.")

        # 게임 종료
        self.show_ending()
        input("\n  Enter를 눌러 종료...")


if __name__ == "__main__":
    game = SiyeonGame()
    game.run()
