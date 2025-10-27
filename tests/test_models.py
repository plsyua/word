# 2025-10-20 - 스마트 단어장 - Model 단위테스트
# 파일 위치: C:\dev\word\tests\test_models.py - v1.0

"""
Model 계층 단위테스트
- WordModel
- SettingsModel
- StatisticsModel
- LearningModel
- ExamModel
"""

import pytest


class TestWordModel:
    """WordModel 테스트"""
    
    def test_add_word(self, word_model):
        """단어 추가 테스트"""
        word_id = word_model.add_word('test', '테스트', '테스트용')
        assert word_id is not None
        assert word_id > 0
    
    def test_add_duplicate_word(self, word_model):
        """중복 단어 추가 방지 테스트"""
        word_model.add_word('test', '테스트', None)
        duplicate_id = word_model.add_word('test', '테스트', None)
        assert duplicate_id is None
    
    def test_get_all_words(self, word_model, inserted_words):
        """전체 단어 조회 테스트"""
        words = word_model.get_all_words()
        assert len(words) == len(inserted_words)
    
    def test_get_word_by_id(self, word_model, inserted_words):
        """ID로 단어 조회 테스트"""
        word = word_model.get_word_by_id(inserted_words[0])
        assert word is not None
        assert word['word_id'] == inserted_words[0]
        assert 'english' in word
        assert 'korean' in word
    
    def test_search_words(self, word_model, inserted_words):
        """단어 검색 테스트"""
        results = word_model.search_words('apple', 'english')
        assert len(results) >= 1
        assert results[0]['english'] == 'apple'
    
    def test_update_word(self, word_model, inserted_words):
        """단어 수정 테스트"""
        word_id = inserted_words[0]
        success = word_model.update_word(word_id, memo='수정된 메모')
        assert success is True
        
        updated = word_model.get_word_by_id(word_id)
        assert updated['memo'] == '수정된 메모'
    
    def test_delete_word(self, word_model):
        """단어 삭제 테스트"""
        word_id = word_model.add_word('delete_test', '삭제테스트', None)
        success = word_model.delete_word(word_id)
        assert success is True
        
        deleted = word_model.get_word_by_id(word_id)
        assert deleted is None
    
    def test_toggle_favorite(self, word_model, inserted_words):
        """즐겨찾기 토글 테스트"""
        word_id = inserted_words[0]
        
        # 첫 번째 토글 (0 -> 1)
        new_state = word_model.toggle_favorite(word_id)
        assert new_state == 1
        
        # 두 번째 토글 (1 -> 0)
        new_state = word_model.toggle_favorite(word_id)
        assert new_state == 0
    
    def test_get_word_count(self, word_model, inserted_words):
        """단어 수 조회 테스트"""
        count = word_model.get_word_count()
        assert count == len(inserted_words)


class TestSettingsModel:
    """SettingsModel 테스트"""
    
    def test_get_setting(self, settings_model):
        """설정 조회 테스트"""
        value = settings_model.get_setting('daily_word_goal')
        assert value is not None
        assert isinstance(value, int)
        assert value == 50
    
    def test_set_setting(self, settings_model):
        """설정 변경 테스트"""
        success = settings_model.set_setting('daily_word_goal', 100)
        assert success is True
        
        new_value = settings_model.get_setting('daily_word_goal')
        assert new_value == 100
    
    def test_get_all_settings(self, settings_model):
        """전체 설정 조회 테스트"""
        settings = settings_model.get_all_settings()
        assert isinstance(settings, dict)
        assert len(settings) >= 10
        assert 'daily_word_goal' in settings
    
    def test_type_conversion(self, settings_model):
        """타입 변환 테스트"""
        # integer
        int_value = settings_model.get_setting('daily_word_goal')
        assert isinstance(int_value, int)
        
        # string
        str_value = settings_model.get_setting('theme_mode')
        assert isinstance(str_value, str)
        
        # boolean
        bool_value = settings_model.get_setting('show_pronunciation')
        assert isinstance(bool_value, bool)


class TestStatisticsModel:
    """StatisticsModel 테스트"""
    
    def test_initialize_word_statistics(self, statistics_model, word_model):
        """통계 초기화 테스트"""
        word_id = word_model.add_word('stats_test', '통계테스트', None)
        success = statistics_model.initialize_word_statistics(word_id)
        assert success is True
        
        stats = statistics_model.get_word_statistics(word_id)
        assert stats is not None
        assert stats['total_attempts'] == 0
        assert stats['mastery_level'] == 0
    
    def test_update_word_statistics(self, statistics_model, inserted_words):
        """통계 업데이트 테스트"""
        word_id = inserted_words[0]
        
        # 정답 처리
        success = statistics_model.update_word_statistics(word_id, True)
        assert success is True
        
        stats = statistics_model.get_word_statistics(word_id)
        assert stats['total_attempts'] == 1
        assert stats['correct_count'] == 1
        assert stats['consecutive_correct'] == 1
    
    def test_get_today_statistics(self, statistics_model, sample_session):
        """오늘의 통계 테스트"""
        stats = statistics_model.get_today_statistics()
        assert stats is not None
        assert 'total_words' in stats
        assert 'accuracy' in stats
    
    def test_calculate_personalization_score(self, statistics_model, inserted_words):
        """개인화 점수 계산 테스트"""
        word_id = inserted_words[0]
        score = statistics_model.calculate_personalization_score(word_id)
        assert score >= 0
        assert isinstance(score, float)


class TestLearningModel:
    """LearningModel 테스트"""
    
    def test_create_session(self, learning_model):
        """세션 생성 테스트"""
        session_id = learning_model.create_session('flashcard', 'random')
        assert session_id is not None
        assert session_id > 0
    
    def test_add_learning_history(self, learning_model, inserted_words):
        """학습 이력 추가 테스트"""
        session_id = learning_model.create_session('flashcard', 'random')
        word_id = inserted_words[0]
        
        history_id = learning_model.add_learning_history(
            session_id, word_id, 'flashcard_en_ko', True, 2.5
        )
        assert history_id is not None
        assert history_id > 0
    
    def test_end_session(self, learning_model):
        """세션 종료 테스트"""
        session_id = learning_model.create_session('flashcard', 'random')
        success = learning_model.end_session(session_id, 10, 8, 2)
        assert success is True
        
        session = learning_model.get_session_info(session_id)
        assert session['total_words'] == 10
        assert session['correct_count'] == 8
        assert session['accuracy_rate'] == 80.0
    
    def test_get_session_history(self, learning_model, sample_session):
        """세션 이력 조회 테스트"""
        history = learning_model.get_session_history(sample_session)
        assert len(history) == 3


class TestExamModel:
    """ExamModel 테스트"""
    
    def test_create_exam(self, exam_model):
        """시험 생성 테스트"""
        exam_id = exam_model.create_exam('short_answer', 'en_to_ko', 10, 600)
        assert exam_id is not None
        assert exam_id > 0
    
    def test_save_exam_question(self, exam_model, word_model):
        """시험 문제 저장 테스트"""
        # 테스트용 단어 추가
        word_id = word_model.add_word('exam_test', '시험테스트', None)
        
        # 시험 생성
        exam_id = exam_model.create_exam('short_answer', 'en_to_ko', 1)
        
        # 문제 저장
        question_id = exam_model.save_exam_question(
            exam_id, word_id, 1, '시험테스트', '시험테스트', 1, 3.0
        )
        assert question_id is not None
        assert question_id > 0
    
    def test_finish_exam(self, exam_model, word_model, statistics_model):
        """시험 종료 테스트"""
        # 테스트용 단어들 추가
        word_ids = []
        for i in range(3):
            word_id = word_model.add_word(f'finish{i}', f'종료{i}', None)
            word_ids.append(word_id)
            statistics_model.initialize_word_statistics(word_id)
        
        # 시험 생성
        exam_id = exam_model.create_exam('short_answer', 'en_to_ko', 3)
        
        # 문제들 저장
        for i, word_id in enumerate(word_ids):
            word = word_model.get_word_by_id(word_id)
            exam_model.save_exam_question(
                exam_id, word_id, i + 1, word['korean'],
                word['korean'] if i % 2 == 0 else '오답',
                1 if i % 2 == 0 else 0, 2.0
            )
        
        # 시험 종료
        success = exam_model.finish_exam(exam_id, 66.67, 120)
        assert success is True
        
        exam = exam_model.get_exam_detail(exam_id)
        assert exam is not None
        assert exam['exam']['correct_count'] == 2
        assert exam['exam']['wrong_count'] == 1
    
    def test_get_wrong_questions(self, exam_model, word_model, statistics_model):
        """오답 문제 조회 테스트"""
        # 테스트용 단어들 추가
        word_ids = []
        for i in range(3):
            word_id = word_model.add_word(f'wrong{i}', f'오답{i}', None)
            word_ids.append(word_id)
            statistics_model.initialize_word_statistics(word_id)
        
        # 시험 생성
        exam_id = exam_model.create_exam('short_answer', 'en_to_ko', 3)
        
        # 문제들 저장 (모두 오답으로)
        for i, word_id in enumerate(word_ids):
            word = word_model.get_word_by_id(word_id)
            exam_model.save_exam_question(
                exam_id, word_id, i + 1, word['korean'],
                '틀린답', 0, 2.0
            )
        
        # 시험 종료
        exam_model.finish_exam(exam_id, 0.0, 120)
        
        # 오답 조회
        wrong = exam_model.get_wrong_questions(exam_id)
        assert len(wrong) == 3


if __name__ == "__main__":
    pytest.main([__file__, '-v'])