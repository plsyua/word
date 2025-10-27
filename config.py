# 2025-10-20 - 스마트 단어장 - 전역 설정 파일
# 파일 위치: C:\dev\word\config.py - v1.0

"""
프로젝트 전역 설정 상수 정의
모든 모듈에서 import하여 사용
"""

import os

# ============================================================
# 애플리케이션 메타데이터
# ============================================================
APP_NAME = "Smart Vocab Builder"
APP_VERSION = "1.0.0"
APP_AUTHOR = "AI Software Student Team"
APP_DESCRIPTION = "고등학생 및 대학생을 위한 영어 단어 학습 프로그램"

# ============================================================
# 파일 경로 설정
# ============================================================
# 프로젝트 루트 디렉토리 (C:\dev\word)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 데이터베이스 경로
DATABASE_PATH = os.path.join(BASE_DIR, 'resources', 'vocabulary.db')

# 로그 디렉토리 및 파일
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# 리소스 디렉토리
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
ICONS_DIR = os.path.join(RESOURCES_DIR, 'icons')
STYLES_DIR = os.path.join(RESOURCES_DIR, 'styles')

# ============================================================
# 로그 설정
# ============================================================
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5  # 백업 파일 개수

# ============================================================
# 데이터베이스 설정
# ============================================================
DB_TIMEOUT = 30.0  # 초
DB_CHECK_SAME_THREAD = False  # 멀티스레드 지원
DB_ISOLATION_LEVEL = None  # 자동 커밋 비활성화 (수동 관리)

# ============================================================
# 학습 설정 (기본값)
# ============================================================
# 일일 목표
DEFAULT_DAILY_WORD_GOAL = 50  # 개
DEFAULT_DAILY_TIME_GOAL = 30  # 분

# 시간 제한
DEFAULT_FLASHCARD_TIME_LIMIT = 0  # 초 (0 = 무제한)
DEFAULT_EXAM_TIME_LIMIT = 0  # 초 (0 = 무제한)
DEFAULT_QUESTION_TIME_LIMIT = 30  # 초 (문제당)

# ============================================================
# UI 설정 (기본값)
# ============================================================
DEFAULT_THEME = 'light'  # 'light' or 'dark'
DEFAULT_FONT_SIZE = 14  # pt
DEFAULT_FONT_FAMILY = '맑은 고딕'

# 윈도우 크기
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 700

# ============================================================
# 개인화 알고리즘 설정
# ============================================================
# 우선순위 계산 가중치 (합계 = 1.0)
PERSONALIZATION_WEIGHTS = {
    'wrong_rate': 0.4,           # 오답률 (40%)
    'days_since_last_study': 0.3, # 복습 주기 (30%)
    'mastery_level': 0.2,        # 숙지도 (20%)
    'wrong_count': 0.1           # 누적 오답 횟수 (10%)
}

# 숙지도 레벨 기준
MASTERY_LEVELS = {
    0: "미학습",
    1: "매우 낮음",
    2: "낮음",
    3: "보통",
    4: "높음",
    5: "완전 숙지"
}

# 숙지도 자동 조정 기준
MASTERY_LEVEL_UP_CONSECUTIVE = 3  # 연속 정답 N회 시 레벨 상승
MASTERY_LEVEL_DOWN_CONSECUTIVE = 2  # 연속 오답 N회 시 레벨 하락

# ============================================================
# 오답 노트 설정
# ============================================================
CONSECUTIVE_CORRECT_TO_RESOLVE = 3  # 연속 정답 시 오답 노트 해결
WRONG_NOTE_AUTO_ADD = True  # 시험 오답 자동 추가

# ============================================================
# CSV 설정
# ============================================================
CSV_ENCODING = 'utf-8-sig'  # UTF-8 with BOM (엑셀 호환)
CSV_DELIMITER = ','
CSV_REQUIRED_COLUMNS = ['english', 'korean']  # 필수 컬럼
CSV_OPTIONAL_COLUMNS = ['memo']  # 선택 컬럼

# ============================================================
# 시험 설정
# ============================================================
# 객관식
MULTIPLE_CHOICE_OPTIONS = 4  # 4지선다
MIN_WORDS_FOR_MULTIPLE_CHOICE = 4  # 객관식 최소 단어 수

# 문항 수 범위
MIN_EXAM_QUESTIONS = 5
MAX_EXAM_QUESTIONS = 100

# ============================================================
# 검증 규칙
# ============================================================
# 단어 입력 제한
MAX_ENGLISH_LENGTH = 100
MAX_KOREAN_LENGTH = 200
MAX_MEMO_LENGTH = 500

# 학습 시간 제한
MAX_SESSION_TIME = 180  # 분 (3시간)

# ============================================================
# 날짜/시간 형식
# ============================================================
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
ISO8601_FORMAT = '%Y-%m-%dT%H:%M:%S'  # SQLite 저장용

# ============================================================
# 통계 설정
# ============================================================
# 차트 기본 기간
DEFAULT_CHART_DAYS = 7  # 일일 학습량 추이
DEFAULT_WEEKLY_DAYS = 7  # 주간 통계

# Top N 설정
TOP_WRONG_WORDS_LIMIT = 20  # 오답률 높은 단어

# ============================================================
# 디버그 설정
# ============================================================
DEBUG_MODE = False  # 개발 시 True로 변경
SHOW_SQL_QUERIES = False  # SQL 쿼리 로그 출력

# ============================================================
# 기타 설정
# ============================================================
# 자동 저장
AUTO_SAVE_INTERVAL = 300  # 초 (5분)

# 백업
AUTO_BACKUP_ENABLED = True
BACKUP_INTERVAL_DAYS = 7  # 일