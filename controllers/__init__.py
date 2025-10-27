# 2025-10-27 - 스마트 단어장 - Controller 패키지
# 파일 위치: word/controllers/__init__.py

"""
Controller 계층 패키지

Controller는 Model과 View 사이의 중간 계층으로,
비즈니스 로직 처리, 데이터 가공, 입력 검증 등을 담당합니다.

사용 예시:
    from controllers.word_controller import WordController
    from controllers.flashcard_controller import FlashcardController
    
    word_ctrl = WordController()
    success, message, word_id = word_ctrl.add_word("apple", "사과")
"""

from controllers.settings_controller import SettingsController
from controllers.word_controller import WordController
from controllers.flashcard_controller import FlashcardController
from controllers.exam_controller import ExamController
from controllers.statistics_controller import StatisticsController

__all__ = [
    'SettingsController',
    'WordController',
    'FlashcardController',
    'ExamController',
    'StatisticsController',
]