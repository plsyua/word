# 251020_구현 - Phase1 구현계획서 v1.0.md

**작성일**: 2025-10-20  
**문서명**: 251020_구현 - Phase1 구현계획서 v1.0.md  
**프로젝트**: 스마트 단어장 (Smart Vocabulary Builder)  
**작성자**: AI Software Student Team

---

## 1. Phase 1 개요

### 1.1 목표

**Phase 1의 핵심 목표**: 프로젝트의 기반 구조 구축 및 Model 계층 완성

- 데이터베이스 연결 및 초기화 시스템 구현
- 로깅 시스템 구현
- Model 계층 전체 구현 (5개 모델)
- 각 Model의 단위테스트 작성
- 기본 설정 관리 시스템 구현

### 1.2 범위

**포함 사항**:
- ✅ 프로젝트 설정 파일 (config.py)
- ✅ 데이터베이스 연결 관리 (Singleton)
- ✅ 데이터베이스 스키마 생성 (SQL)
- ✅ 로깅 시스템
- ✅ Model 계층 5개 클래스
- ✅ 유틸리티 함수들
- ✅ 단위테스트

**제외 사항**:
- ❌ Controller 계층 (Phase 2)
- ❌ View 계층 (Phase 4 이후)
- ❌ GUI 구현 (Phase 4 이후)

### 1.3 예상 소요 시간

**총 예상 기간**: 2-3일

| 작업 | 예상 시간 | 비고 |
|------|-----------|------|
| 기반 구조 파일 | 2-3시간 | config, db_connection, logger |
| 데이터베이스 스키마 | 1시간 | schema.sql, init_data.sql |
| Model 계층 | 4-6시간 | 5개 모델 + base_model |
| 유틸리티 | 1-2시간 | validators, csv_handler 등 |
| 단위테스트 | 3-4시간 | Model 계층 테스트 |
| 통합 및 디버깅 | 1-2시간 | 전체 동작 확인 |

---

## 2. 구현할 파일 목록

### 2.1 Phase 1 파일 목록 (총 17개)

```
word/
├── config.py                           # 1. 전역 설정
├── main.py                             # 2. 임시 테스트용 진입점
├── database/
│   ├── __init__.py
│   ├── db_connection.py                # 3. DB 연결 관리
│   ├── schema.sql                      # 4. 테이블 생성 DDL
│   └── init_data.sql                   # 5. 초기 설정 데이터
├── models/
│   ├── __init__.py
│   ├── base_model.py                   # 6. 베이스 모델
│   ├── word_model.py                   # 7. 단어 모델
│   ├── learning_model.py               # 8. 학습 모델
│   ├── exam_model.py                   # 9. 시험 모델
│   ├── statistics_model.py             # 10. 통계 모델
│   └── settings_model.py               # 11. 설정 모델
├── utils/
│   ├── __init__.py
│   ├── logger.py                       # 12. 로깅 시스템
│   ├── validators.py                   # 13. 입력 검증
│   ├── csv_handler.py                  # 14. CSV 처리
│   └── datetime_helper.py              # 15. 날짜/시간 유틸
└── tests/
    ├── __init__.py
    ├── test_models.py                  # 16. Model 단위테스트
    └── conftest.py                     # 17. pytest 설정
```

---

## 3. 파일별 구현 내용

### 3.1 config.py (전역 설정)

**파일 위치**: `word/config.py`

**목적**: 프로젝트 전역에서 사용할 설정 상수 정의

**포함 내용**:
```python
# 애플리케이션 메타데이터
APP_NAME = "Smart Vocab Builder"
APP_VERSION = "1.0.0"
APP_AUTHOR = "AI Software Student Team"

# 파일 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'resources', 'vocabulary.db')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# 로그 설정
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 데이터베이스 설정
DB_TIMEOUT = 30.0
DB_CHECK_SAME_THREAD = False

# 학습 설정 (기본값)
DEFAULT_DAILY_WORD_GOAL = 50
DEFAULT_DAILY_TIME_GOAL = 30  # 분
DEFAULT_FLASHCARD_TIME_LIMIT = 0  # 0 = 무제한
DEFAULT_EXAM_TIME_LIMIT = 0  # 0 = 무제한

# UI 설정 (기본값)
DEFAULT_THEME = 'light'
DEFAULT_FONT_SIZE = 14

# 개인화 알고리즘 가중치
PERSONALIZATION_WEIGHTS = {
    'wrong_rate': 0.4,
    'days_since_last_study': 0.3,
    'mastery_level': 0.2,
    'wrong_count': 0.1
}

# 오답 노트 설정
CONSECUTIVE_CORRECT_TO_RESOLVE = 3  # 연속 정답 시 오답 노트 해결

# CSV 설정
CSV_ENCODING = 'utf-8-sig'
CSV_DELIMITER = ','

# 객관식 설정
MULTIPLE_CHOICE_OPTIONS = 4  # 4지선다
```

**특이사항**:
- 절대 경로 사용으로 실행 위치 무관하게 동작
- 설정값은 추후 settings 테이블로 오버라이드 가능

---

### 3.2 database/db_connection.py (DB 연결 관리)

**파일 위치**: `word/database/db_connection.py`

**목적**: SQLite 데이터베이스 연결 관리 (Singleton 패턴)

**주요 기능**:
1. Singleton 패턴으로 단일 연결 보장
2. 데이터베이스 파일 존재 여부 확인
3. 최초 실행 시 스키마 자동 생성
4. 연결 풀 관리 (필요시)
5. 트랜잭션 관리 헬퍼 메서드

**클래스 구조**:
```python
class DBConnection:
    _instance = None
    _connection = None
    
    @classmethod
    def get_instance(cls)
        # Singleton 인스턴스 반환
    
    def __init__(self)
        # 최초 한번만 초기화
    
    def _initialize_database(self)
        # DB 파일 없으면 생성 및 스키마 실행
    
    def get_connection(self)
        # sqlite3.Connection 객체 반환
    
    def execute_script(self, sql_file_path)
        # SQL 스크립트 파일 실행
    
    def close(self)
        # 연결 종료 (프로그램 종료 시)
```

**특이사항**:
- 최초 실행 시 `schema.sql` 자동 실행
- `init_data.sql`로 기본 설정 자동 삽입
- 에러 발생 시 logger 사용하여 로그 기록

---

### 3.3 database/schema.sql (테이블 생성 DDL)

**파일 위치**: `word/database/schema.sql`

**목적**: 데이터베이스 스키마 정의

**포함 테이블**:
1. words (단어 정보)
2. learning_sessions (학습 세션)
3. learning_history (학습 이력)
4. word_statistics (단어별 통계)
5. exam_history (시험 이력)
6. exam_questions (시험 문제 상세)
7. wrong_note (오답 노트)
8. user_settings (사용자 설정)

**내용**: 
- 데이터 설계서(251013)의 모든 테이블 CREATE 문
- 인덱스 생성 문
- UNIQUE 제약조건, CHECK 제약조건 포함

**특이사항**:
- `IF NOT EXISTS` 사용하여 멱등성 보장
- 외래키 제약조건 활성화 필요

---

### 3.4 database/init_data.sql (초기 설정 데이터)

**파일 위치**: `word/database/init_data.sql`

**목적**: 최초 실행 시 기본 설정값 삽입

**포함 내용**:
```sql
-- user_settings 테이블 기본값 삽입
INSERT OR IGNORE INTO user_settings 
    (setting_key, setting_value, setting_type, description, modified_date) 
VALUES
    ('daily_word_goal', '50', 'integer', '일일 학습 목표 단어 수', datetime('now')),
    ('daily_time_goal', '30', 'integer', '일일 학습 목표 시간 (분)', datetime('now')),
    ('flashcard_time_limit', '0', 'integer', '플래시카드 제한 시간 (초, 0=무제한)', datetime('now')),
    ('exam_time_limit', '0', 'integer', '시험 전체 제한 시간 (초, 0=무제한)', datetime('now')),
    ('theme_mode', 'light', 'string', 'UI 테마 (light/dark)', datetime('now')),
    ('font_size', '14', 'integer', '폰트 크기', datetime('now')),
    ('show_pronunciation', 'false', 'boolean', '발음 기호 표시 여부', datetime('now'));
```

**특이사항**:
- `INSERT OR IGNORE` 사용하여 중복 방지
- config.py의 기본값과 동기화

---

### 3.5 utils/logger.py (로깅 시스템)

**파일 위치**: `word/utils/logger.py`

**목적**: 애플리케이션 전역 로깅 시스템

**주요 기능**:
1. 콘솔 + 파일 로그 동시 출력
2. 로그 레벨별 포매팅
3. 로그 파일 로테이션 (10MB, 5개 백업)
4. 예외 스택 트레이스 자동 기록

**로그 레벨 정책**:
- **DEBUG**: 개발용 상세 정보
- **INFO**: 세션 시작/종료, 데이터 로드 등
- **WARNING**: 중복 단어 임포트, 빈 결과 등
- **ERROR**: DB 연결 실패, 파일 없음 등
- **CRITICAL**: 프로그램 종료 수준 오류

**함수 구조**:
```python
def setup_logger(name, log_file=None, level=logging.INFO)
    # 로거 설정 및 반환

def get_logger(name)
    # 설정된 로거 반환
```

**사용 예시**:
```python
from utils.logger import get_logger
logger = get_logger(__name__)

logger.info("데이터베이스 연결 성공")
logger.error("파일을 찾을 수 없습니다: %s", file_path)
```

---

### 3.6 models/base_model.py (베이스 모델)

**파일 위치**: `word/models/base_model.py`

**목적**: 모든 Model 클래스의 기반 클래스

**주요 기능**:
1. DBConnection 인스턴스 참조
2. 공통 DB 연산 메서드 제공
3. 에러 처리 및 로깅
4. 트랜잭션 헬퍼

**클래스 구조**:
```python
class BaseModel:
    def __init__(self)
        # DBConnection 인스턴스 저장
        # Logger 초기화
    
    def execute_query(self, query, params=None)
        # SELECT 쿼리 실행 및 결과 반환
        # 에러 발생 시 로그 기록 및 빈 리스트 반환
    
    def execute_update(self, query, params=None)
        # INSERT/UPDATE/DELETE 실행
        # lastrowid 또는 rowcount 반환
        # 에러 발생 시 로그 기록 및 None 반환
    
    def execute_many(self, query, params_list)
        # 여러 행 일괄 처리
    
    def begin_transaction(self)
        # 트랜잭션 시작
    
    def commit(self)
        # 커밋
    
    def rollback(self)
        # 롤백
```

**특이사항**:
- 모든 쿼리는 Parameterized Query 사용 (SQL Injection 방지)
- 에러 발생 시 로그 기록 후 안전하게 처리

---

### 3.7 models/word_model.py (단어 모델)

**파일 위치**: `word/models/word_model.py`

**목적**: 단어(words 테이블) CRUD 연산

**주요 메서드**:
```python
class WordModel(BaseModel):
    def get_all_words(self, filter_favorite=False, filter_unlearned=False)
        # 전체 단어 조회
        # 필터: 즐겨찾기만, 미학습만
        # 반환: List[Dict] - 단어 정보 + 통계
    
    def get_word_by_id(self, word_id)
        # 단어 ID로 조회
        # 반환: Dict 또는 None
    
    def search_words(self, keyword, search_type='all')
        # 단어 검색
        # search_type: 'english', 'korean', 'memo', 'all'
        # LIKE 검색 사용
    
    def add_word(self, english, korean, memo=None, is_favorite=0)
        # 단어 추가
        # 중복 체크 (UNIQUE 제약)
        # 반환: word_id 또는 None
    
    def update_word(self, word_id, **kwargs)
        # 단어 수정 (english, korean, memo, is_favorite)
        # 반환: 성공 여부 (bool)
    
    def delete_word(self, word_id)
        # 단어 삭제 (CASCADE로 연관 데이터도 삭제)
        # 반환: 성공 여부 (bool)
    
    def toggle_favorite(self, word_id)
        # 즐겨찾기 토글
        # 반환: 새로운 상태 (0 또는 1)
    
    def import_from_csv(self, csv_data, skip_duplicates=True)
        # CSV 데이터 일괄 삽입
        # csv_data: List[Dict] - [{'english': '...', 'korean': '...', 'memo': '...'}]
        # skip_duplicates: True면 중복 건너뛰기, False면 오류
        # 반환: Dict - {'success': 10, 'failed': 2, 'errors': [...]}
    
    def export_to_csv(self)
        # 전체 단어 내보내기
        # 반환: List[Dict] - CSV 형식 데이터
    
    def get_word_count(self)
        # 전체 단어 수 조회
```

**쿼리 예시**:
```sql
-- get_all_words
SELECT w.*, ws.wrong_rate, ws.mastery_level, ws.last_study_date
FROM words w
LEFT JOIN word_statistics ws ON w.word_id = ws.word_id
WHERE w.is_favorite = ? OR ? = 0
ORDER BY w.word_id;

-- search_words
SELECT * FROM words
WHERE english LIKE ? OR korean LIKE ? OR memo LIKE ?;
```

---

### 3.8 models/learning_model.py (학습 모델)

**파일 위치**: `word/models/learning_model.py`

**목적**: 학습 세션 및 이력 관리

**주요 메서드**:
```python
class LearningModel(BaseModel):
    def create_session(self, session_type, study_mode)
        # 새 학습 세션 생성
        # session_type: 'flashcard', 'exam'
        # study_mode: 'sequential', 'random', 'personalized'
        # 반환: session_id
    
    def end_session(self, session_id, total_words, correct_count, wrong_count)
        # 세션 종료 및 통계 업데이트
        # accuracy_rate 자동 계산
        # end_time 현재 시간으로 설정
    
    def add_learning_history(self, session_id, word_id, study_mode, 
                             is_correct, response_time=None, user_answer=None)
        # 학습 이력 추가
        # study_mode: 'flashcard_en_ko', 'flashcard_ko_en', 등
        # 반환: history_id
    
    def get_session_history(self, session_id)
        # 특정 세션의 학습 이력 조회
        # 반환: List[Dict] - 단어 정보 포함
    
    def get_recent_sessions(self, limit=10, session_type=None)
        # 최근 세션 목록 조회
        # 반환: List[Dict] - 세션 정보
    
    def get_today_sessions(self)
        # 오늘의 세션 목록
        # 반환: List[Dict]
```

**특이사항**:
- 세션 생성 시 start_time은 자동으로 현재 시간
- 학습 이력 추가 시 word_statistics 업데이트 필요 (statistics_model 연동)

---

### 3.9 models/exam_model.py (시험 모델)

**파일 위치**: `word/models/exam_model.py`

**목적**: 시험 생성 및 관리

**주요 메서드**:
```python
class ExamModel(BaseModel):
    def create_exam(self, exam_type, question_mode, total_questions, 
                    time_limit=None)
        # 시험 생성
        # exam_type: 'short_answer', 'multiple_choice'
        # question_mode: 'en_to_ko', 'ko_to_en', 'mixed'
        # 반환: exam_id
    
    def save_exam_question(self, exam_id, word_id, question_number,
                          correct_answer, user_answer=None, 
                          is_correct=0, response_time=None, choices=None)
        # 시험 문제 저장
        # choices: JSON 문자열 (객관식만)
        # 반환: question_id
    
    def update_exam_question(self, question_id, user_answer, is_correct, 
                            response_time=None)
        # 시험 답안 업데이트 (채점)
    
    def finish_exam(self, exam_id, score, time_taken)
        # 시험 종료 및 채점
        # correct_count, wrong_count 자동 계산
    
    def get_exam_detail(self, exam_id)
        # 시험 상세 조회 (문제별)
        # 반환: Dict - exam 정보 + questions 리스트
    
    def get_exam_history(self, limit=10)
        # 시험 이력 조회
        # 반환: List[Dict]
    
    def get_wrong_questions(self, exam_id)
        # 특정 시험의 오답 문제 조회
        # 반환: List[Dict] - 단어 정보 포함
```

**쿼리 예시**:
```sql
-- get_exam_detail
SELECT eq.*, w.english, w.korean
FROM exam_questions eq
JOIN words w ON eq.word_id = w.word_id
WHERE eq.exam_id = ?
ORDER BY eq.question_number;
```

---

### 3.10 models/statistics_model.py (통계 모델)

**파일 위치**: `word/models/statistics_model.py`

**목적**: 학습 통계 조회 및 업데이트

**주요 메서드**:
```python
class StatisticsModel(BaseModel):
    def get_word_statistics(self, word_id)
        # 단어별 통계 조회
        # 반환: Dict 또는 None
    
    def update_word_statistics(self, word_id, is_correct)
        # 단어 통계 업데이트 (학습 후 호출)
        # total_attempts += 1
        # correct_count 또는 wrong_count += 1
        # wrong_rate 재계산
        # consecutive_correct 업데이트
        # mastery_level 자동 조정
        # last_study_date 현재 시간
    
    def initialize_word_statistics(self, word_id)
        # 새 단어 추가 시 통계 초기화
    
    def get_daily_statistics(self, date)
        # 특정 날짜의 학습 통계
        # 반환: Dict - {'total_words': 50, 'study_time': 25, 'accuracy': 80.0}
    
    def get_today_statistics(self)
        # 오늘의 학습 통계
    
    def get_weekly_statistics(self, start_date, end_date)
        # 주간 학습 통계
        # 반환: List[Dict] - 날짜별
    
    def get_top_wrong_words(self, limit=20)
        # 오답률 높은 단어 Top N
        # 반환: List[Dict] - 단어 정보 + 통계
    
    def get_mastery_distribution(self)
        # 숙지도 레벨별 단어 수 분포
        # 반환: Dict - {0: 10, 1: 20, ...}
    
    def calculate_personalization_score(self, word_id)
        # 개인화 우선순위 점수 계산
        # 알고리즘: config.PERSONALIZATION_WEIGHTS 사용
        # 반환: float
```

**알고리즘 구현**:
```python
# calculate_personalization_score 내부
stats = self.get_word_statistics(word_id)
days_since = (datetime.now() - stats['last_study_date']).days

score = (
    stats['wrong_rate'] * WEIGHTS['wrong_rate'] +
    days_since * WEIGHTS['days_since_last_study'] +
    (5 - stats['mastery_level']) * WEIGHTS['mastery_level'] +
    stats['wrong_count'] * WEIGHTS['wrong_count']
)
return score
```

---

### 3.11 models/settings_model.py (설정 모델)

**파일 위치**: `word/models/settings_model.py`

**목적**: 사용자 설정 관리

**주요 메서드**:
```python
class SettingsModel(BaseModel):
    def get_setting(self, key)
        # 설정 값 조회
        # 타입 변환 (setting_type 기반)
        # 반환: 타입 변환된 값 또는 None
    
    def set_setting(self, key, value)
        # 설정 값 변경
        # modified_date 자동 업데이트
        # 반환: 성공 여부 (bool)
    
    def get_all_settings(self)
        # 전체 설정 조회
        # 반환: Dict - {key: value} 형태 (타입 변환됨)
    
    def reset_to_default(self, key=None)
        # 기본값으로 초기화
        # key=None이면 전체 초기화
    
    def _convert_type(self, value, setting_type)
        # 문자열을 실제 타입으로 변환
        # 'integer' -> int
        # 'boolean' -> bool
        # 'float' -> float
        # 'string' -> str
```

**특이사항**:
- 설정 값은 DB에 문자열로 저장되므로 타입 변환 필요
- config.py의 기본값과 일치하도록 관리

---

### 3.12 utils/validators.py (입력 검증)

**파일 위치**: `word/utils/validators.py`

**목적**: 사용자 입력 데이터 검증

**주요 함수**:
```python
def validate_word(english, korean, memo=None)
    # 단어 입력 검증
    # english: 1-100자, 공백 불가
    # korean: 1-200자
    # memo: 최대 500자
    # 반환: (bool, error_message)

def validate_positive_integer(value, min_val=1, max_val=None)
    # 양의 정수 검증
    # 문항 수, 시간 제한 등에 사용

def validate_percentage(value)
    # 0-100 범위 검증
    # 정답률, 오답률 등에 사용

def validate_setting_value(key, value, setting_type)
    # 설정 값 검증
    # 타입별 검증 규칙 적용

def sanitize_string(text, max_length=None)
    # 문자열 정제 (앞뒤 공백 제거, 길이 제한)
```

**반환 형식**:
```python
# 성공
(True, None)

# 실패
(False, "영어 단어는 1-100자여야 합니다")
```

---

### 3.13 utils/csv_handler.py (CSV 처리)

**파일 위치**: `word/utils/csv_handler.py`

**목적**: CSV 파일 임포트/엑스포트

**주요 함수**:
```python
def read_csv(file_path)
    # CSV 파일 읽기
    # 헤더 검증 (english, korean, memo)
    # 반환: List[Dict] 또는 None (에러 시)

def write_csv(file_path, data)
    # CSV 파일 쓰기
    # data: List[Dict]
    # 반환: 성공 여부 (bool)

def validate_csv_structure(file_path)
    # CSV 구조 검증 (미리보기용)
    # 반환: (bool, error_message, preview_data)

def parse_csv_row(row)
    # CSV 행 파싱 및 검증
    # 필수 컬럼 체크, 데이터 정제
```

**CSV 형식**:
```csv
english,korean,memo
apple,사과,과일 종류
book,책,
computer,컴퓨터,IT 관련
```

**특이사항**:
- UTF-8 BOM 처리 (엑셀 호환)
- 빈 메모 허용
- 중복 단어 처리는 word_model에서

---

### 3.14 utils/datetime_helper.py (날짜/시간 유틸)

**파일 위치**: `word/utils/datetime_helper.py`

**목적**: 날짜/시간 관련 유틸리티 함수

**주요 함수**:
```python
def get_current_datetime()
    # 현재 시간 ISO 8601 형식 반환
    # 예: '2025-10-20T14:30:00'

def parse_datetime(datetime_str)
    # ISO 8601 문자열 -> datetime 객체
    # 반환: datetime 또는 None

def format_datetime(dt, format_type='full')
    # datetime 객체 -> 포맷팅된 문자열
    # format_type: 'full', 'date', 'time', 'short'
    # 예: '2025-10-20 14:30:00', '2025-10-20', '14:30'

def get_date_range(days=7)
    # 최근 N일 날짜 범위
    # 반환: (start_date, end_date) - ISO 8601 문자열

def calculate_days_between(date1, date2)
    # 두 날짜 간 일수 차이
    # 반환: int

def get_today_start_end()
    # 오늘의 시작/종료 시간
    # 반환: (start, end) - ISO 8601 문자열
```

**특이사항**:
- SQLite TEXT 타입으로 저장되므로 ISO 8601 형식 사용
- 한국 표준시(KST) 기준

---

### 3.15 tests/conftest.py (pytest 설정)

**파일 위치**: `word/tests/conftest.py`

**목적**: pytest 공통 설정 및 fixture

**주요 fixture**:
```python
@pytest.fixture(scope='function')
def test_db():
    # 테스트용 임시 DB 생성
    # 테스트 후 자동 삭제
    # 반환: DBConnection 인스턴스

@pytest.fixture(scope='function')
def sample_words():
    # 테스트용 샘플 단어 데이터
    # 반환: List[Dict]

@pytest.fixture(scope='function')
def word_model(test_db):
    # WordModel 인스턴스
    # 반환: WordModel

@pytest.fixture(scope='function')
def learning_model(test_db):
    # LearningModel 인스턴스
    # 반환: LearningModel

# 기타 모델 fixture들...
```

**특이사항**:
- scope='function'으로 각 테스트마다 독립적인 환경
- 임시 DB는 메모리 DB `:memory:` 사용 가능

---

### 3.16 tests/test_models.py (Model 단위테스트)

**파일 위치**: `word/tests/test_models.py`

**목적**: Model 계층 단위테스트

**테스트 구조**:
```python
class TestWordModel:
    def test_add_word(self, word_model):
        # 단어 추가 테스트
    
    def test_add_duplicate_word(self, word_model):
        # 중복 단어 처리 테스트
    
    def test_get_all_words(self, word_model, sample_words):
        # 전체 조회 테스트
    
    def test_search_words(self, word_model):
        # 검색 테스트
    
    def test_update_word(self, word_model):
        # 수정 테스트
    
    def test_delete_word(self, word_model):
        # 삭제 테스트
    
    def test_toggle_favorite(self, word_model):
        # 즐겨찾기 토글 테스트
    
    def test_import_csv(self, word_model):
        # CSV 임포트 테스트

class TestLearningModel:
    def test_create_session(self, learning_model):
        # 세션 생성 테스트
    
    def test_add_learning_history(self, learning_model):
        # 학습 이력 추가 테스트
    
    def test_end_session(self, learning_model):
        # 세션 종료 테스트

class TestExamModel:
    def test_create_exam(self, exam_model):
        # 시험 생성 테스트
    
    def test_save_exam_question(self, exam_model):
        # 문제 저장 테스트
    
    def test_finish_exam(self, exam_model):
        # 시험 종료 테스트

class TestStatisticsModel:
    def test_update_word_statistics(self, statistics_model):
        # 통계 업데이트 테스트
    
    def test_calculate_personalization_score(self, statistics_model):
        # 개인화 점수 계산 테스트
    
    def test_get_daily_statistics(self, statistics_model):
        # 일일 통계 테스트

class TestSettingsModel:
    def test_get_setting(self, settings_model):
        # 설정 조회 테스트
    
    def test_set_setting(self, settings_model):
        # 설정 변경 테스트
    
    def test_type_conversion(self, settings_model):
        # 타입 변환 테스트
```

**테스트 실행**:
```bash
# 모든 테스트 실행
pytest tests/test_models.py -v

# 커버리지 확인
pytest tests/test_models.py --cov=models --cov-report=html
```

**목표 커버리지**: Model 계층 100%

---

### 3.17 main.py (임시 테스트용 진입점)

**파일 위치**: `word/main.py`

**목적**: Phase 1 구현 후 통합 테스트용

**내용**:
```python
def test_basic_operations():
    # 기본 CRUD 테스트
    # 1. 단어 추가
    # 2. 단어 조회
    # 3. 학습 세션 생성
    # 4. 학습 이력 추가
    # 5. 통계 조회
    # 각 단계 결과 출력

if __name__ == '__main__':
    print("Phase 1 통합 테스트 시작")
    test_basic_operations()
    print("Phase 1 통합 테스트 완료")
```

**특이사항**:
- Phase 4에서 GUI 구현 시 교체 예정
- 현재는 Model 계층 동작 확인용

---

## 4. 구현 순서

### 4.1 구현 단계

**1단계: 기반 구조** (예상 2-3시간)
```
1. config.py 작성
2. utils/logger.py 작성
3. utils/datetime_helper.py 작성
4. database/db_connection.py 작성
5. database/schema.sql 작성
6. database/init_data.sql 작성
```

**동작 확인**:
- DB 파일 생성 확인
- 테이블 생성 확인
- 로그 파일 생성 확인

---

**2단계: 유틸리티** (예상 1-2시간)
```
7. utils/validators.py 작성
8. utils/csv_handler.py 작성
```

**동작 확인**:
- 입력 검증 함수 테스트
- CSV 읽기/쓰기 테스트

---

**3단계: Model 기반** (예상 1시간)
```
9. models/base_model.py 작성
```

**동작 확인**:
- DB 쿼리 실행 테스트
- 에러 처리 테스트

---

**4단계: Model 구현 1** (예상 2-3시간)
```
10. models/word_model.py 작성
11. models/settings_model.py 작성
```

**동작 확인**:
- 단어 CRUD 테스트
- 설정 관리 테스트

---

**5단계: Model 구현 2** (예상 2-3시간)
```
12. models/statistics_model.py 작성
13. models/learning_model.py 작성
14. models/exam_model.py 작성
```

**동작 확인**:
- 각 모델별 기본 기능 테스트
- 모델 간 연동 테스트

---

**6단계: 단위테스트** (예상 3-4시간)
```
15. tests/conftest.py 작성
16. tests/test_models.py 작성
    - TestWordModel
    - TestLearningModel
    - TestExamModel
    - TestStatisticsModel
    - TestSettingsModel
```

**동작 확인**:
- pytest 실행
- 커버리지 확인 (목표: 100%)

---

**7단계: 통합 테스트** (예상 1-2시간)
```
17. main.py 작성 (통합 테스트 스크립트)
```

**동작 확인**:
- 전체 흐름 테스트
- 실제 사용 시나리오 시뮬레이션

---

### 4.2 일별 계획 (예시)

**Day 1**:
- 오전: 1단계 (기반 구조)
- 오후: 2단계 (유틸리티) + 3단계 (Model 기반)

**Day 2**:
- 오전: 4단계 (Model 구현 1)
- 오후: 5단계 (Model 구현 2)

**Day 3**:
- 오전: 6단계 (단위테스트)
- 오후: 7단계 (통합 테스트) + 디버깅

---

## 5. 테스트 계획

### 5.1 단위테스트 범위

**WordModel**:
- ✅ 단어 추가 (정상/중복/검증 실패)
- ✅ 단어 조회 (전체/ID/검색)
- ✅ 단어 수정 (정상/존재하지 않는 ID)
- ✅ 단어 삭제 (정상/CASCADE 확인)
- ✅ 즐겨찾기 토글
- ✅ CSV 임포트 (정상/중복 처리)
- ✅ CSV 엑스포트

**LearningModel**:
- ✅ 세션 생성
- ✅ 학습 이력 추가
- ✅ 세션 종료 (통계 계산)
- ✅ 세션 조회

**ExamModel**:
- ✅ 시험 생성
- ✅ 문제 저장
- ✅ 답안 업데이트
- ✅ 시험 종료 (채점)
- ✅ 시험 이력 조회

**StatisticsModel**:
- ✅ 통계 업데이트 (정답/오답)
- ✅ 숙지도 자동 조정
- ✅ 개인화 점수 계산
- ✅ 일일/주간 통계 조회

**SettingsModel**:
- ✅ 설정 조회 (타입 변환)
- ✅ 설정 변경
- ✅ 전체 설정 조회
- ✅ 기본값 초기화

### 5.2 통합테스트 시나리오

**시나리오 1: 기본 학습 흐름**
```
1. 단어 5개 추가
2. 플래시카드 세션 생성
3. 5개 단어 학습 (정답 3개, 오답 2개)
4. 세션 종료
5. 통계 확인 (정답률 60%)
6. 오답 단어 확인
```

**시나리오 2: 시험 흐름**
```
1. 단어 10개 추가
2. 시험 생성 (10문항)
3. 문제별 답안 입력
4. 시험 종료 및 채점
5. 오답 노트 자동 생성 확인
6. 통계 업데이트 확인
```

**시나리오 3: CSV 임포트**
```
1. CSV 파일 준비 (20개 단어, 2개 중복)
2. CSV 임포트 (skip_duplicates=True)
3. 결과 확인 (18개 성공, 2개 중복 건너뜀)
4. 단어 목록 조회
```

---

## 6. 에러 처리 정책

### 6.1 공통 에러 처리

**DB 연결 오류**:
```python
try:
    # DB 연산
except sqlite3.Error as e:
    logger.error(f"DB 오류: {e}")
    return None  # 또는 기본값
```

**파일 오류**:
```python
try:
    # 파일 읽기/쓰기
except (FileNotFoundError, IOError) as e:
    logger.error(f"파일 오류: {e}")
    return False
```

**검증 오류**:
```python
is_valid, error_msg = validate_word(english, korean)
if not is_valid:
    logger.warning(f"검증 실패: {error_msg}")
    return None
```

### 6.2 에러 로깅 레벨

| 상황 | 로그 레벨 | 예시 |
|------|-----------|------|
| 정상 동작 | INFO | "단어 추가 완료: apple" |
| 중복/빈 결과 | WARNING | "중복 단어: apple (건너뜀)" |
| 파일 없음 | ERROR | "CSV 파일 없음: words.csv" |
| DB 연결 실패 | ERROR | "DB 연결 실패: vocabulary.db" |
| 프로그램 종료 오류 | CRITICAL | "치명적 오류: 데이터 손실" |

---

## 7. 성공 기준

### 7.1 완료 조건

✅ **모든 파일 구현 완료** (17개)

✅ **단위테스트 통과**:
- pytest 실행 시 모든 테스트 통과
- 커버리지 90% 이상 (목표: 100%)

✅ **통합테스트 통과**:
- 3개 시나리오 모두 정상 동작
- main.py 실행 시 에러 없음

✅ **로그 기록 확인**:
- logs/app.log 파일 생성
- 주요 동작 로그 기록

✅ **DB 파일 생성 확인**:
- resources/vocabulary.db 파일 생성
- 8개 테이블 모두 생성
- 기본 설정 데이터 삽입

### 7.2 검증 방법

**자동 검증**:
```bash
# 1. 단위테스트
pytest tests/test_models.py -v --cov=models

# 2. 통합테스트
python main.py

# 3. 로그 확인
type logs\app.log
```

**수동 검증**:
```bash
# DB 확인
sqlite3 resources/vocabulary.db
.tables
SELECT * FROM user_settings;
.quit
```

---

## 8. 위험 요소 및 대응

### 8.1 잠재적 문제

**문제 1: DB 동시 접근 오류**
- **증상**: 여러 모델에서 동시 쓰기 시 LOCKED 에러
- **대응**: 
  - Singleton 패턴으로 연결 공유
  - 트랜잭션 적절히 관리
  - timeout 설정 (30초)

**문제 2: CSV 인코딩 오류**
- **증상**: 한글 깨짐
- **대응**: UTF-8 BOM 사용 (`utf-8-sig`)

**문제 3: 테스트 간 데이터 오염**
- **증상**: 이전 테스트 데이터가 남아있음
- **대응**: 
  - scope='function'으로 독립 실행
  - 테스트용 임시 DB 사용
  - teardown에서 정리

**문제 4: 외래키 제약 위반**
- **증상**: CASCADE 동작하지 않음
- **대응**: 
  - SQLite에서 외래키 활성화 필요
  - `PRAGMA foreign_keys = ON;`

### 8.2 롤백 계획

**각 단계 완료 후 커밋**:
- Git 사용 시 단계별로 커밋
- 문제 발생 시 이전 단계로 복원 가능

**백업 방안**:
- 주요 파일 완성 시 백업 복사본 생성
- DB 스키마 변경 시 이전 버전 보관

---

## 9. 다음 단계 (Phase 2 예고)

Phase 1 완료 후 진행할 Phase 2:

**Phase 2: Controller 계층** (예상 2-3일)
- controllers/word_controller.py
- controllers/flashcard_controller.py
- controllers/exam_controller.py
- controllers/statistics_controller.py
- controllers/settings_controller.py

**Phase 2 목표**:
- Model과 View 사이의 비즈니스 로직 구현
- 입력 검증 및 데이터 가공
- 에러 처리 및 사용자 피드백
- Controller 단위테스트

---

## 10. 의사결정 확인

Phase 1 구현 시작 전 최종 확인:

✅ **구현 파일 목록** 승인 (17개)
✅ **구현 순서** 승인 (7단계)
✅ **테스트 범위** 승인 (단위테스트 + 통합테스트)
✅ **성공 기준** 승인 (커버리지 90% 이상)

**구현 시작 준비 완료!**

다음 작업:
1. 1단계 구현 시작 (config.py부터)
2. 각 파일 완성 후 개별 테스트
3. 단계별 완료 보고

---

**작성 완료일**: 2025-10-20