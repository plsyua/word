# 251027_구현 - Phase2 구현계획서 v1.0

**작성일**: 2025-10-27  
**문서명**: 251027_구현 - Phase2 구현계획서 v1.0.md  
**프로젝트**: 스마트 단어장 (Smart Vocabulary Builder)  
**작성자**: AI Software Student Team

---

## 1. Phase 2 개요

### 1.1 목표

**Phase 2의 핵심 목표**: Controller 계층 완성 및 비즈니스 로직 구현

- Model과 View(미래) 사이의 중간 계층 구현
- 비즈니스 로직 및 데이터 가공 처리
- 입력 검증 및 에러 처리 강화
- Controller 단위테스트 작성
- Phase 1에서 구현한 Model 계층과 통합

### 1.2 Phase 1 완료 현황

**✅ 완료된 파일 (17개)**:
- config.py, db_connection.py, logger.py
- schema.sql, init_data.sql
- base_model.py, word_model.py, learning_model.py, exam_model.py
- statistics_model.py, settings_model.py
- validators.py, csv_handler.py, datetime_helper.py
- conftest.py, test_models.py
- main.py (통합 테스트)

**✅ 검증 완료**:
- Model 계층 통합 테스트 성공
- 데이터베이스 연결 및 CRUD 동작 확인
- 학습/시험 흐름 정상 동작

### 1.3 Phase 2 범위

**포함 사항**:
- ✅ Controller 계층 5개 클래스
- ✅ 비즈니스 로직 구현
- ✅ 데이터 가공 및 변환
- ✅ 에러 처리 및 검증 강화
- ✅ Controller 단위테스트

**제외 사항**:
- ❌ View 계층 (Phase 3 이후)
- ❌ GUI 구현 (Phase 4 이후)
- ❌ PyQt5 통합 (Phase 4 이후)

### 1.4 예상 소요 시간

**총 예상 기간**: 2-3일

| 작업 | 예상 시간 | 비고 |
|------|-----------|------|
| WordController | 2-3시간 | 단어 관리 로직 |
| FlashcardController | 2-3시간 | 학습 세션 로직 |
| ExamController | 2-3시간 | 시험 진행 로직 |
| StatisticsController | 1-2시간 | 통계 계산 로직 |
| SettingsController | 1시간 | 설정 관리 로직 |
| Controller 단위테스트 | 3-4시간 | 전체 Controller 테스트 |
| 통합 및 디버깅 | 1-2시간 | 전체 동작 확인 |

---

## 2. 구현할 파일 목록

### 2.1 Phase 2 파일 목록 (총 7개)

```
word/
├── controllers/
│   ├── __init__.py                  # 1. 패키지 초기화
│   ├── word_controller.py           # 2. 단어 관리 컨트롤러
│   ├── flashcard_controller.py      # 3. 플래시카드 학습 컨트롤러
│   ├── exam_controller.py           # 4. 시험 컨트롤러
│   ├── statistics_controller.py     # 5. 통계 컨트롤러
│   └── settings_controller.py       # 6. 설정 컨트롤러
└── tests/
    └── test_controllers.py          # 7. Controller 단위테스트
```

---

## 3. 파일별 구현 내용

### 3.1 controllers/word_controller.py

**파일 위치**: `word/controllers/word_controller.py`

**목적**: 단어 관리 비즈니스 로직

**주요 메서드**:
```python
class WordController:
    """단어 관리 컨트롤러"""
    
    def __init__(self):
        self.word_model = WordModel()
        self.statistics_model = StatisticsModel()
    
    # === 조회 기능 ===
    def get_word_list(self, filter_favorite=False, category=None):
        """
        단어 목록 조회 (필터 적용)
        
        Args:
            filter_favorite: 즐겨찾기만 조회
            category: 카테고리 필터 (미구현, 향후 확장용)
        
        Returns:
            List[Dict]: 단어 목록
        """
        pass
    
    def search_words(self, keyword, search_in='all'):
        """
        단어 검색
        
        Args:
            keyword: 검색 키워드
            search_in: 검색 대상 ('english', 'korean', 'memo', 'all')
        
        Returns:
            List[Dict]: 검색 결과
        """
        pass
    
    def get_word_by_id(self, word_id):
        """
        단어 상세 조회
        
        Returns:
            Dict or None: 단어 정보
        """
        pass
    
    # === 추가/수정/삭제 ===
    def add_word(self, english, korean, memo=None):
        """
        단어 추가 (검증 포함)
        
        Returns:
            Tuple[bool, str, int]: (성공여부, 메시지, word_id)
        """
        # 1. 입력 검증 (validators 사용)
        # 2. 중복 체크
        # 3. Model 호출
        # 4. 통계 초기화
        pass
    
    def update_word(self, word_id, english=None, korean=None, memo=None):
        """
        단어 수정
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        pass
    
    def delete_word(self, word_id):
        """
        단어 삭제
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        pass
    
    def toggle_favorite(self, word_id):
        """
        즐겨찾기 토글
        
        Returns:
            Tuple[bool, str, bool]: (성공여부, 메시지, 새로운 즐겨찾기 상태)
        """
        pass
    
    # === CSV 임포트/엑스포트 ===
    def import_from_csv(self, file_path, skip_duplicates=True):
        """
        CSV 임포트
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 통계)
            통계 = {'success': 18, 'duplicate': 2, 'error': 0}
        """
        pass
    
    def export_to_csv(self, file_path, word_ids=None):
        """
        CSV 엑스포트
        
        Args:
            word_ids: 특정 단어만 내보내기 (None이면 전체)
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        pass
    
    # === 통계 조회 ===
    def get_word_count(self, filter_favorite=False):
        """
        단어 수 조회
        """
        pass
```

**특이사항**:
- 모든 메서드는 (성공여부, 메시지, [추가데이터]) 형태로 반환
- View에서 사용하기 쉽도록 일관된 반환 형식
- 에러는 로그에 기록하되, 사용자 친화적 메시지 반환

---

### 3.2 controllers/flashcard_controller.py

**파일 위치**: `word/controllers/flashcard_controller.py`

**목적**: 플래시카드 학습 로직

**주요 메서드**:
```python
class FlashcardController:
    """플래시카드 학습 컨트롤러"""
    
    def __init__(self):
        self.word_model = WordModel()
        self.learning_model = LearningModel()
        self.statistics_model = StatisticsModel()
        
        # 세션 상태 관리
        self.current_session_id = None
        self.current_words = []
        self.current_index = 0
        self.session_results = []  # [(word_id, is_correct, response_time), ...]
    
    # === 세션 관리 ===
    def start_session(self, study_mode, word_order='sequential', 
                     filter_favorite=False, word_count=None):
        """
        학습 세션 시작
        
        Args:
            study_mode: 'flashcard_en_ko' | 'flashcard_ko_en'
            word_order: 'sequential' | 'random' | 'personalized'
            filter_favorite: 즐겨찾기만 학습
            word_count: 학습할 단어 수 (None이면 전체)
        
        Returns:
            Tuple[bool, str, int]: (성공여부, 메시지, 총 단어 수)
        """
        # 1. 세션 생성
        # 2. 단어 목록 가져오기
        # 3. 단어 순서 결정
        #    - sequential: DB 순서
        #    - random: 랜덤 셔플
        #    - personalized: 개인화 점수 기반 정렬
        # 4. 상태 초기화
        pass
    
    def get_current_word(self):
        """
        현재 단어 조회
        
        Returns:
            Dict or None: 단어 정보 + 진행 상황
            {
                'word_id': 1,
                'question': '사과',  # study_mode에 따라 다름
                'current': 1,
                'total': 20
            }
        """
        pass
    
    def submit_answer(self, user_answer, response_time):
        """
        답변 제출 및 정답 확인
        
        Args:
            user_answer: 사용자 답변
            response_time: 응답 시간 (초)
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 결과)
            결과 = {
                'is_correct': True,
                'correct_answer': 'apple',
                'user_answer': 'apple'
            }
        """
        # 1. 정답 여부 확인 (대소문자 무시, 공백 제거)
        # 2. 학습 이력 저장
        # 3. 통계 업데이트
        # 4. 다음 단어로 이동
        pass
    
    def skip_word(self):
        """
        현재 단어 건너뛰기
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        pass
    
    def end_session(self):
        """
        세션 종료 및 결과 반환
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 통계)
            통계 = {
                'total_words': 20,
                'correct_count': 16,
                'wrong_count': 4,
                'accuracy': 80.0,
                'total_time': 180  # 초
            }
        """
        pass
    
    # === 진행 상황 ===
    def get_progress(self):
        """
        현재 진행 상황
        
        Returns:
            Dict: {'current': 5, 'total': 20, 'percentage': 25.0}
        """
        pass
    
    def has_next(self):
        """다음 단어 존재 여부"""
        pass
```

**특이사항**:
- 세션 상태를 인스턴스 변수로 관리
- 단일 세션만 지원 (새 세션 시작 시 기존 세션 종료)
- personalized 모드는 StatisticsModel의 개인화 점수 활용

---

### 3.3 controllers/exam_controller.py

**파일 위치**: `word/controllers/exam_controller.py`

**목적**: 시험 진행 로직

**주요 메서드**:
```python
class ExamController:
    """시험 컨트롤러"""
    
    def __init__(self):
        self.word_model = WordModel()
        self.exam_model = ExamModel()
        self.statistics_model = StatisticsModel()
        
        # 시험 상태 관리
        self.current_exam_id = None
        self.exam_questions = []  # 시험 문제 목록
        self.current_question_index = 0
        self.start_time = None
    
    # === 시험 생성 ===
    def create_exam(self, exam_type, question_mode, total_questions, 
                   word_order='random', time_limit=None):
        """
        시험 생성
        
        Args:
            exam_type: 'short_answer' | 'multiple_choice'
            question_mode: 'en_to_ko' | 'ko_to_en' | 'mixed'
            total_questions: 총 문항 수
            word_order: 'random' | 'personalized'
            time_limit: 제한 시간 (초, None이면 무제한)
        
        Returns:
            Tuple[bool, str, int]: (성공여부, 메시지, exam_id)
        """
        # 1. 단어 선택
        #    - random: 랜덤 선택
        #    - personalized: 오답률 높은 단어 우선
        # 2. question_mode가 'mixed'면 문제별로 랜덤 설정
        # 3. 객관식이면 오답 선택지 생성 (3개)
        # 4. 시험 DB 저장
        # 5. 문제 목록 생성
        pass
    
    def _generate_choices(self, word_id, correct_answer):
        """
        객관식 선택지 생성 (4지선다)
        
        Returns:
            List[str]: [정답, 오답1, 오답2, 오답3] (셔플됨)
        """
        pass
    
    # === 시험 진행 ===
    def get_current_question(self):
        """
        현재 문제 조회
        
        Returns:
            Dict or None: 문제 정보
            {
                'question_number': 1,
                'question_text': '사과',
                'choices': ['apple', 'banana', 'grape', 'orange'],  # 객관식만
                'current': 1,
                'total': 10
            }
        """
        pass
    
    def submit_answer(self, user_answer):
        """
        답안 제출
        
        Args:
            user_answer: 사용자 답변 (주관식) 또는 선택 번호 (객관식: 0-3)
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        # 1. 답안 저장 (정답 여부는 채점 시 결정)
        # 2. 다음 문제로 이동
        pass
    
    def go_to_question(self, question_number):
        """특정 문제로 이동"""
        pass
    
    def finish_exam(self):
        """
        시험 종료 및 채점
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 결과)
            결과 = {
                'exam_id': 1,
                'total_questions': 10,
                'correct_count': 8,
                'wrong_count': 2,
                'score': 80.0,
                'time_taken': 300  # 초
            }
        """
        # 1. 채점 (정답 확인)
        # 2. 점수 계산
        # 3. 시험 종료 처리 (exam_model)
        # 4. 오답 노트 자동 추가
        # 5. 통계 업데이트
        pass
    
    # === 시험 결과 ===
    def get_exam_result(self, exam_id):
        """
        시험 결과 상세 조회
        
        Returns:
            Dict: 시험 정보 + 문제별 상세
        """
        pass
    
    def get_exam_history(self, limit=10):
        """
        시험 이력 조회
        
        Returns:
            List[Dict]: 최근 시험 목록
        """
        pass
    
    # === 오답 노트 ===
    def get_wrong_notes(self):
        """
        오답 노트 조회
        
        Returns:
            List[Dict]: 미해결 오답 목록
        """
        pass
    
    def mark_wrong_note_resolved(self, word_id):
        """
        오답 노트 해결 처리
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        pass
```

**특이사항**:
- 객관식 오답 선택지는 다른 단어에서 랜덤 선택
- 시험 중 답안 수정 가능 (go_to_question 사용)
- 시험 종료 시 자동 채점 및 오답 노트 생성

---

### 3.4 controllers/statistics_controller.py

**파일 위치**: `word/controllers/statistics_controller.py`

**목적**: 통계 계산 및 분석 로직

**주요 메서드**:
```python
class StatisticsController:
    """통계 컨트롤러"""
    
    def __init__(self):
        self.statistics_model = StatisticsModel()
        self.learning_model = LearningModel()
        self.exam_model = ExamModel()
        self.settings_model = SettingsModel()
    
    # === 요약 통계 ===
    def get_today_summary(self):
        """
        오늘의 학습 요약
        
        Returns:
            Dict: {
                'words_learned': 50,
                'sessions': 3,
                'accuracy': 85.0,
                'goal_achievement': 100.0,  # %
                'streak_days': 7  # 연속 학습 일수
            }
        """
        pass
    
    def get_weekly_summary(self):
        """
        주간 학습 요약
        
        Returns:
            Dict: 주간 통계
        """
        pass
    
    # === 학습 진척도 ===
    def get_learning_trend(self, days=7):
        """
        학습 추세 (차트용 데이터)
        
        Args:
            days: 조회 일수
        
        Returns:
            List[Dict]: [
                {'date': '2025-10-20', 'words': 50, 'accuracy': 80.0},
                {'date': '2025-10-21', 'words': 45, 'accuracy': 85.0},
                ...
            ]
        """
        pass
    
    def get_mastery_distribution(self):
        """
        숙지도 분포
        
        Returns:
            Dict: {0: 10, 1: 20, 2: 30, 3: 25, 4: 10, 5: 5}
        """
        pass
    
    # === 목표 달성 ===
    def calculate_goal_achievement(self):
        """
        학습 목표 달성률 계산
        
        Returns:
            Dict: {
                'daily_word_goal': 50,
                'daily_word_actual': 45,
                'daily_word_achievement': 90.0,  # %
                'daily_time_goal': 30,  # 분
                'daily_time_actual': 25,
                'daily_time_achievement': 83.3
            }
        """
        pass
    
    # === 오답 분석 ===
    def get_top_wrong_words(self, limit=20):
        """
        오답률 높은 단어 Top N
        
        Returns:
            List[Dict]: 단어 정보 + 통계
        """
        pass
    
    def get_improvement_suggestions(self):
        """
        학습 개선 제안
        
        Returns:
            List[str]: 제안 메시지 목록
            예: ["3일 연속 학습 중! 계속 유지하세요.",
                 "오답률이 높은 단어 10개를 집중 학습하세요."]
        """
        pass
    
    # === 연속 학습 일수 ===
    def calculate_streak_days(self):
        """
        연속 학습 일수 계산
        
        Returns:
            int: 연속 학습 일수
        """
        pass
```

**특이사항**:
- 통계 데이터는 캐싱 고려 가능 (향후 확장)
- 개선 제안은 간단한 규칙 기반 (향후 AI 활용 가능)

---

### 3.5 controllers/settings_controller.py

**파일 위치**: `word/controllers/settings_controller.py`

**목적**: 설정 관리 로직

**주요 메서드**:
```python
class SettingsController:
    """설정 컨트롤러"""
    
    def __init__(self):
        self.settings_model = SettingsModel()
    
    # === 설정 조회 ===
    def get_all_settings(self):
        """
        전체 설정 조회
        
        Returns:
            Dict: 설정 key-value 쌍
        """
        pass
    
    def get_setting(self, key):
        """
        특정 설정 조회
        
        Returns:
            Any: 설정 값 (타입 변환됨)
        """
        pass
    
    def get_settings_by_category(self):
        """
        카테고리별 설정 조회
        
        Returns:
            Dict: {
                'learning': {...},
                'ui': {...},
                'exam': {...}
            }
        """
        pass
    
    # === 설정 변경 ===
    def update_setting(self, key, value):
        """
        설정 변경
        
        Args:
            key: 설정 키
            value: 새 값
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        # 1. 검증 (validators 사용)
        # 2. Model 호출
        pass
    
    def update_multiple_settings(self, settings_dict):
        """
        여러 설정 한번에 변경
        
        Args:
            settings_dict: {key: value, ...}
        
        Returns:
            Tuple[bool, str, List]: (성공여부, 메시지, 실패한 키 목록)
        """
        pass
    
    def reset_to_default(self, key=None):
        """
        기본값으로 초기화
        
        Args:
            key: 특정 설정 (None이면 전체)
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        pass
    
    # === 설정 검증 ===
    def validate_setting(self, key, value):
        """
        설정 값 검증
        
        Returns:
            Tuple[bool, str]: (유효여부, 에러 메시지)
        """
        pass
```

**특이사항**:
- 설정 변경 시 즉시 DB 반영
- 검증 실패 시 롤백 (트랜잭션 고려)

---

## 4. 구현 순서

### 4.1 구현 단계

**1단계: SettingsController** (예상 1시간)
```
가장 단순한 Controller부터 시작
1. controllers/__init__.py 생성
2. controllers/settings_controller.py 구현
3. 간단한 테스트로 구조 검증
```

**2단계: WordController** (예상 2-3시간)
```
1. controllers/word_controller.py 구현
2. CSV 임포트/엑스포트 로직 포함
3. 검증 로직 강화
```

**3단계: StatisticsController** (예상 1-2시간)
```
1. controllers/statistics_controller.py 구현
2. 통계 계산 로직 구현
3. 목표 달성률 계산
```

**4단계: FlashcardController** (예상 2-3시간)
```
1. controllers/flashcard_controller.py 구현
2. 세션 상태 관리
3. 개인화 로직 구현
```

**5단계: ExamController** (예상 2-3시간)
```
1. controllers/exam_controller.py 구현
2. 객관식 선택지 생성 로직
3. 오답 노트 자동 생성
```

**6단계: Controller 단위테스트** (예상 3-4시간)
```
1. tests/test_controllers.py 작성
2. 각 Controller별 테스트 케이스
3. 통합 시나리오 테스트
```

**7단계: 통합 및 디버깅** (예상 1-2시간)
```
1. main.py 업데이트 (Controller 계층 사용)
2. 전체 흐름 테스트
3. 에러 처리 검증
```

### 4.2 일별 계획

**Day 1**:
- 오전: 1단계 (SettingsController) + 2단계 시작 (WordController)
- 오후: 2단계 완료 + 3단계 (StatisticsController)

**Day 2**:
- 오전: 4단계 (FlashcardController)
- 오후: 5단계 (ExamController)

**Day 3**:
- 오전: 6단계 (Controller 단위테스트)
- 오후: 7단계 (통합 및 디버깅)

---

## 5. 테스트 계획

### 5.1 단위테스트 범위

**WordController**:
- ✅ 단어 추가 (검증 성공/실패)
- ✅ 단어 조회 (전체/검색/필터)
- ✅ 단어 수정/삭제
- ✅ CSV 임포트 (정상/중복/에러)
- ✅ CSV 엑스포트

**FlashcardController**:
- ✅ 세션 시작 (순차/랜덤/개인화)
- ✅ 답변 제출 (정답/오답)
- ✅ 세션 종료 (통계 계산)
- ✅ 진행 상황 조회

**ExamController**:
- ✅ 시험 생성 (주관식/객관식)
- ✅ 문제 조회
- ✅ 답안 제출
- ✅ 시험 종료 및 채점
- ✅ 오답 노트 생성

**StatisticsController**:
- ✅ 오늘/주간 요약
- ✅ 학습 추세 계산
- ✅ 목표 달성률 계산
- ✅ 연속 학습 일수 계산

**SettingsController**:
- ✅ 설정 조회/변경
- ✅ 설정 검증
- ✅ 기본값 초기화

### 5.2 통합테스트 시나리오

**시나리오 1: 플래시카드 학습 (Controller 사용)**
```
1. WordController로 단어 10개 추가
2. FlashcardController로 학습 세션 시작 (personalized)
3. 10개 단어 학습 진행
4. 세션 종료
5. StatisticsController로 통계 확인
```

**시나리오 2: 시험 진행 (객관식)**
```
1. WordController로 단어 20개 추가
2. ExamController로 객관식 시험 생성 (10문항)
3. 문제별 답안 제출
4. 시험 종료
5. 오답 노트 확인
6. 통계 업데이트 확인
```

**시나리오 3: CSV 임포트 및 학습**
```
1. WordController로 CSV 임포트 (중복 처리)
2. StatisticsController로 현재 통계 확인
3. FlashcardController로 학습 시작
4. 학습 후 통계 변화 확인
```

---

## 6. 에러 처리 및 검증 정책

### 6.1 반환 형식 표준화

모든 Controller 메서드는 일관된 형식으로 반환:

```python
# 성공/실패만 필요한 경우
return (True, "성공 메시지")
return (False, "에러 메시지")

# 추가 데이터가 필요한 경우
return (True, "성공 메시지", data)
return (False, "에러 메시지", None)

# 예시
success, message, word_id = word_controller.add_word("apple", "사과")
if success:
    print(f"{message} - ID: {word_id}")
else:
    print(f"실패: {message}")
```

### 6.2 검증 레벨

**Level 1: Controller 검증**
- 비즈니스 로직 검증
- 상태 확인 (예: 세션이 시작되었는지)
- 데이터 정합성

**Level 2: Validator 검증**
- 입력 형식 검증
- 타입 검증
- 범위 검증

**Level 3: Model 검증**
- DB 제약조건 확인
- 외래키 존재 확인
- 중복 확인

### 6.3 에러 로깅

```python
try:
    # Controller 로직
    result = self.model.some_method()
    return (True, "성공", result)
except Exception as e:
    self.logger.error(f"에러 발생: {e}", exc_info=True)
    return (False, "작업 실패. 관리자에게 문의하세요.", None)
```

---

## 7. 성공 기준

### 7.1 완료 조건

✅ **모든 파일 구현 완료** (7개)

✅ **Controller 단위테스트 통과**:
- pytest 실행 시 모든 테스트 통과
- 커버리지 90% 이상

✅ **통합테스트 통과**:
- 3개 시나리오 모두 정상 동작
- Controller를 통한 전체 흐름 확인

✅ **에러 처리 검증**:
- 잘못된 입력에 대한 적절한 에러 메시지
- 예외 상황 처리 확인

✅ **문서화 완료**:
- 각 Controller 메서드 docstring
- 반환 형식 명시

### 7.2 검증 방법

**자동 검증**:
```bash
# Controller 단위테스트
pytest tests/test_controllers.py -v --cov=controllers

# 전체 테스트 (Model + Controller)
pytest tests/ -v --cov=models --cov=controllers
```

**수동 검증**:
```bash
# 통합 테스트 실행
python main.py  # Controller 사용하도록 업데이트된 버전

# 로그 확인
type logs\app.log
```

---

## 8. 위험 요소 및 대응

### 8.1 잠재적 문제

**문제 1: Controller 간 의존성**
- **증상**: 순환 참조 또는 과도한 결합
- **대응**: 
  - Controller는 Model만 참조
  - Controller 간 직접 호출 금지
  - 필요 시 공통 로직은 Model이나 Utils로 분리

**문제 2: 상태 관리 복잡도**
- **증상**: 세션 상태가 꼬임
- **대응**:
  - 명확한 상태 초기화
  - 세션 시작 전 기존 세션 종료
  - 상태 검증 로직 추가

**문제 3: 에러 메시지 일관성**
- **증상**: 에러 메시지가 제각각
- **대응**:
  - 에러 메시지 상수 정의
  - 공통 에러 처리 함수 사용

**문제 4: 테스트 데이터 오염**
- **증상**: 테스트 간 데이터 공유로 실패
- **대응**:
  - 테스트용 별도 DB 사용
  - setUp/tearDown 철저히
  - Mock 객체 활용

### 8.2 성능 고려사항

**개인화 정렬 최적화**:
- 단어 수가 많을 때 정렬 성능 저하 가능
- 필요 시 캐싱 또는 페이지네이션 고려

**통계 계산 최적화**:
- 복잡한 통계는 계산 비용이 클 수 있음
- 필요 시 사전 계산 또는 캐싱

---

## 9. Phase 3 준비 사항

Phase 2 완료 후 진행할 Phase 3:

**Phase 3: View 계층 준비**
- PyQt5 설치 및 환경 설정
- 기본 윈도우 및 레이아웃 설계
- QSS 스타일시트 작성 (테마)
- 간단한 화면 프로토타입

**Phase 3 선행 작업**:
- PyQt5 학습 및 예제 작성
- UI 목업 작성 (화면 설계서 참고)
- 아이콘 및 리소스 준비

---

## 10. 의사결정 확인

Phase 2 구현 시작 전 최종 확인:

✅ **구현 파일 목록** 승인 (7개)
✅ **구현 순서** 승인 (7단계)
✅ **반환 형식 표준화** 승인
✅ **테스트 범위** 승인
✅ **성공 기준** 승인

**구현 시작 준비 완료!**

---

## 11. 다음 작업

Phase 2 구현계획서가 완성되었습니다.

**즉시 시작 가능한 작업**:
1. controllers/__init__.py 생성
2. controllers/settings_controller.py 구현 시작
3. 각 파일 완성 후 개별 테스트
4. 단계별 완료 보고

**시작하시겠습니까?**

---

**작성 완료일**: 2025-10-27
**작성 시각**: KST 22:47