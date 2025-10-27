# 2025-10-20 - 스마트 단어장 - pytest 설정 및 fixture
# 파일 위치: C:\dev\word\tests\conftest.py - v1.0

"""
pytest 공통 설정 및 fixture
- 테스트용 DB 생성/삭제
- 모델 인스턴스 제공
- 샘플 데이터 제공
"""

import pytest
import sys
import os
import tempfile

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import config
from database.db_connection import DBConnection
from models.word_model import WordModel
from models.settings_model import SettingsModel
from models.statistics_model import StatisticsModel
from models.learning_model import LearningModel
from models.exam_model import ExamModel


@pytest.fixture(scope='function')
def test_db():
    """
    테스트용 임시 DB 생성
    각 테스트 함수마다 새로운 DB 사용
    """
    # 임시 DB 파일 생성
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = temp_db.name
    temp_db.close()
    
    # 원본 DB 경로 백업
    original_db_path = config.DATABASE_PATH
    
    # 테스트용 DB 경로로 변경
    config.DATABASE_PATH = temp_db_path
    
    # DBConnection 인스턴스 초기화 (새 DB 사용)
    DBConnection._instance = None
    DBConnection._connection = None
    db = DBConnection()
    
    yield db
    
    # 정리: DB 연결 종료 및 파일 삭제
    db.close()
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)
    
    # 원본 DB 경로 복원
    config.DATABASE_PATH = original_db_path
    DBConnection._instance = None
    DBConnection._connection = None


@pytest.fixture(scope='function')
def word_model(test_db):
    """WordModel 인스턴스"""
    return WordModel()


@pytest.fixture(scope='function')
def settings_model(test_db):
    """SettingsModel 인스턴스"""
    return SettingsModel()


@pytest.fixture(scope='function')
def statistics_model(test_db):
    """StatisticsModel 인스턴스"""
    return StatisticsModel()


@pytest.fixture(scope='function')
def learning_model(test_db):
    """LearningModel 인스턴스"""
    return LearningModel()


@pytest.fixture(scope='function')
def exam_model(test_db):
    """ExamModel 인스턴스"""
    return ExamModel()


@pytest.fixture(scope='function')
def sample_words():
    """테스트용 샘플 단어 데이터"""
    return [
        {'english': 'apple', 'korean': '사과', 'memo': '과일'},
        {'english': 'book', 'korean': '책', 'memo': None},
        {'english': 'computer', 'korean': '컴퓨터', 'memo': 'IT 관련'},
        {'english': 'dog', 'korean': '개', 'memo': '동물'},
        {'english': 'elephant', 'korean': '코끼리', 'memo': '큰 동물'},
    ]


@pytest.fixture(scope='function')
def inserted_words(word_model, statistics_model, sample_words):
    """DB에 삽입된 샘플 단어들 (word_id 리스트 반환)"""
    word_ids = []
    for word_data in sample_words:
        word_id = word_model.add_word(
            word_data['english'],
            word_data['korean'],
            word_data['memo']
        )
        if word_id:
            word_ids.append(word_id)
            statistics_model.initialize_word_statistics(word_id)
    
    return word_ids


@pytest.fixture(scope='function')
def sample_session(learning_model, inserted_words):
    """테스트용 학습 세션 생성"""
    session_id = learning_model.create_session('flashcard', 'random')
    
    # 몇 개 단어 학습 이력 추가
    for i, word_id in enumerate(inserted_words[:3]):
        learning_model.add_learning_history(
            session_id,
            word_id,
            'flashcard_en_ko',
            is_correct=(i % 2 == 0),
            response_time=2.5 + i
        )
    
    # 세션 종료
    learning_model.end_session(session_id, 3, 2, 1)
    
    return session_id


@pytest.fixture(scope='function')
def sample_exam(exam_model, word_model, inserted_words):
    """테스트용 시험 생성"""
    exam_id = exam_model.create_exam('short_answer', 'en_to_ko', 5, time_limit=300)
    
    # 문제 저장
    for i, word_id in enumerate(inserted_words):
        word = word_model.get_word_by_id(word_id)
        
        exam_model.save_exam_question(
            exam_id,
            word_id,
            i + 1,
            word['korean'],
            word['korean'] if i % 2 == 0 else '오답',
            1 if i % 2 == 0 else 0,
            response_time=3.0 + i
        )
    
    # 시험 종료
    exam_model.finish_exam(exam_id, 60.0, 180)
    
    return exam_id