# 2025-10-20 - 스마트 단어장 - 학습 모델
# 파일 위치: C:\dev\word\models\learning_model.py - v1.0

"""
학습 세션 및 이력 관리
- 세션 생성/종료
- 학습 이력 추가
- 세션 조회
"""

import sys
import os

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.base_model import BaseModel
from utils.datetime_helper import get_current_datetime


class LearningModel(BaseModel):
    """
    학습 모델 클래스
    learning_sessions, learning_history 테이블 관리
    """
    
    def create_session(self, session_type, study_mode):
        """
        새 학습 세션 생성
        
        Args:
            session_type (str): 'flashcard' or 'exam'
            study_mode (str): 'sequential', 'random', 'personalized'
        
        Returns:
            int: session_id (실패 시 None)
        """
        # 유효성 검증
        if session_type not in ('flashcard', 'exam'):
            self.logger.warning(f"잘못된 세션 타입: {session_type}")
            return None
        
        if study_mode not in ('sequential', 'random', 'personalized'):
            self.logger.warning(f"잘못된 학습 모드: {study_mode}")
            return None
        
        query = """
            INSERT INTO learning_sessions 
                (session_type, start_time, study_mode)
            VALUES (?, ?, ?)
        """
        params = (session_type, get_current_datetime(), study_mode)
        
        session_id = self.execute_update(query, params)
        
        if session_id:
            self.logger.info(f"세션 생성: ID={session_id}, 타입={session_type}, 모드={study_mode}")
        
        return session_id
    
    def end_session(self, session_id, total_words, correct_count, wrong_count):
        """
        세션 종료 및 통계 업데이트
        
        Args:
            session_id (int): 세션 ID
            total_words (int): 총 학습 단어 수
            correct_count (int): 정답 수
            wrong_count (int): 오답 수
        
        Returns:
            bool: 성공 여부
        """
        # 정답률 계산
        accuracy_rate = 0.0
        if total_words > 0:
            accuracy_rate = (correct_count / total_words) * 100
        
        query = """
            UPDATE learning_sessions
            SET end_time = ?,
                total_words = ?,
                correct_count = ?,
                wrong_count = ?,
                accuracy_rate = ?
            WHERE session_id = ?
        """
        params = (
            get_current_datetime(),
            total_words,
            correct_count,
            wrong_count,
            round(accuracy_rate, 2),
            session_id
        )
        
        result = self.execute_update(query, params)
        
        if result and result > 0:
            self.logger.info(
                f"세션 종료: ID={session_id}, "
                f"단어={total_words}, 정답률={accuracy_rate:.1f}%"
            )
            return True
        else:
            return False
    
    def add_learning_history(self, session_id, word_id, study_mode, 
                            is_correct, response_time=None, user_answer=None):
        """
        학습 이력 추가
        
        Args:
            session_id (int): 세션 ID
            word_id (int): 단어 ID
            study_mode (str): 'flashcard_en_ko', 'flashcard_ko_en', 
                             'exam_en_ko', 'exam_ko_en'
            is_correct (bool): 정답 여부
            response_time (float, optional): 응답 시간 (초)
            user_answer (str, optional): 사용자 답변
        
        Returns:
            int: history_id (실패 시 None)
        """
        # 유효성 검증
        valid_modes = ('flashcard_en_ko', 'flashcard_ko_en', 
                      'exam_en_ko', 'exam_ko_en')
        if study_mode not in valid_modes:
            self.logger.warning(f"잘못된 학습 모드: {study_mode}")
            return None
        
        query = """
            INSERT INTO learning_history
                (session_id, word_id, study_date, study_mode, 
                 is_correct, response_time, user_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            session_id,
            word_id,
            get_current_datetime(),
            study_mode,
            1 if is_correct else 0,
            response_time,
            user_answer
        )
        
        history_id = self.execute_update(query, params)
        
        if history_id:
            self.logger.debug(
                f"학습 이력 추가: word_id={word_id}, "
                f"정답={is_correct}, 모드={study_mode}"
            )
        
        return history_id
    
    def get_session_history(self, session_id):
        """
        특정 세션의 학습 이력 조회
        
        Args:
            session_id (int): 세션 ID
        
        Returns:
            list: 학습 이력 리스트 (단어 정보 포함)
        """
        query = """
            SELECT 
                lh.*,
                w.english,
                w.korean
            FROM learning_history lh
            JOIN words w ON lh.word_id = w.word_id
            WHERE lh.session_id = ?
            ORDER BY lh.history_id
        """
        
        result = self.execute_query(query, (session_id,))
        return result
    
    def get_session_info(self, session_id):
        """
        세션 정보 조회
        
        Args:
            session_id (int): 세션 ID
        
        Returns:
            dict: 세션 정보 (없으면 None)
        """
        return self.get_by_id('learning_sessions', 'session_id', session_id)
    
    def get_recent_sessions(self, limit=10, session_type=None):
        """
        최근 세션 목록 조회
        
        Args:
            limit (int): 조회 개수
            session_type (str, optional): 'flashcard' or 'exam'
        
        Returns:
            list: 세션 리스트
        """
        query = """
            SELECT *
            FROM learning_sessions
        """
        
        params = []
        if session_type:
            query += " WHERE session_type = ?"
            params.append(session_type)
        
        query += " ORDER BY start_time DESC LIMIT ?"
        params.append(limit)
        
        result = self.execute_query(query, tuple(params))
        return result
    
    def get_today_sessions(self):
        """
        오늘의 세션 목록
        
        Returns:
            list: 세션 리스트
        """
        from utils.datetime_helper import get_today_start_end
        
        start, end = get_today_start_end()
        
        query = """
            SELECT *
            FROM learning_sessions
            WHERE start_time >= ? AND start_time <= ?
            ORDER BY start_time DESC
        """
        
        result = self.execute_query(query, (start, end))
        return result
    
    def get_session_statistics(self, session_id):
        """
        세션 통계 상세 (이력 기반)
        
        Args:
            session_id (int): 세션 ID
        
        Returns:
            dict: 통계 정보
        """
        query = """
            SELECT 
                COUNT(*) as total_count,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_count,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as wrong_count,
                AVG(response_time) as avg_response_time
            FROM learning_history
            WHERE session_id = ?
        """
        
        result = self.execute_query(query, (session_id,))
        
        if result:
            data = result[0]
            total = data['total_count']
            correct = data['correct_count']
            
            return {
                'total_words': total,
                'correct_count': correct,
                'wrong_count': data['wrong_count'],
                'accuracy': round((correct / total * 100) if total > 0 else 0, 2),
                'avg_response_time': round(data['avg_response_time'] or 0, 2)
            }
        else:
            return {
                'total_words': 0,
                'correct_count': 0,
                'wrong_count': 0,
                'accuracy': 0.0,
                'avg_response_time': 0.0
            }
    
    def get_word_learning_history(self, word_id, limit=10):
        """
        특정 단어의 학습 이력
        
        Args:
            word_id (int): 단어 ID
            limit (int): 조회 개수
        
        Returns:
            list: 학습 이력 리스트
        """
        query = """
            SELECT 
                lh.*,
                ls.session_type,
                ls.start_time as session_start
            FROM learning_history lh
            JOIN learning_sessions ls ON lh.session_id = ls.session_id
            WHERE lh.word_id = ?
            ORDER BY lh.study_date DESC
            LIMIT ?
        """
        
        result = self.execute_query(query, (word_id, limit))
        return result
    
    def delete_session(self, session_id):
        """
        세션 삭제 (CASCADE로 이력도 삭제)
        
        Args:
            session_id (int): 세션 ID
        
        Returns:
            bool: 성공 여부
        """
        return self.delete_by_id('learning_sessions', 'session_id', session_id)


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("LearningModel 테스트")
    print("=" * 50)
    
    from models.word_model import WordModel
    from models.statistics_model import StatisticsModel
    
    model = LearningModel()
    word_model = WordModel()
    stats_model = StatisticsModel()
    
    # 테스트용 단어 추가
    print("\n[테스트 단어 추가]")
    test_words = []
    for i in range(3):
        word_id = word_model.add_word(f"test{i}", f"테스트{i}", f"테스트용 {i}")
        if word_id:
            test_words.append(word_id)
            stats_model.initialize_word_statistics(word_id)
    print(f"✓ {len(test_words)}개 단어 추가")
    
    # 세션 생성
    print("\n[세션 생성]")
    session_id = model.create_session('flashcard', 'random')
    if session_id:
        print(f"✓ 세션 생성: ID={session_id}")
    
    # 학습 이력 추가
    print("\n[학습 이력 추가]")
    correct_count = 0
    wrong_count = 0
    
    for i, word_id in enumerate(test_words):
        is_correct = i % 2 == 0  # 0번, 2번은 정답
        history_id = model.add_learning_history(
            session_id,
            word_id,
            'flashcard_en_ko',
            is_correct,
            response_time=2.5 + i
        )
        
        if history_id:
            if is_correct:
                correct_count += 1
            else:
                wrong_count += 1
            
            # 통계 업데이트
            stats_model.update_word_statistics(word_id, is_correct)
    
    print(f"✓ {len(test_words)}개 이력 추가 (정답: {correct_count}, 오답: {wrong_count})")
    
    # 세션 종료
    print("\n[세션 종료]")
    success = model.end_session(session_id, len(test_words), correct_count, wrong_count)
    print(f"✓ 세션 종료: {'성공' if success else '실패'}")
    
    # 세션 정보 조회
    print("\n[세션 정보 조회]")
    session_info = model.get_session_info(session_id)
    if session_info:
        print(f"✓ 세션 ID: {session_info['session_id']}")
        print(f"  타입: {session_info['session_type']}")
        print(f"  단어 수: {session_info['total_words']}")
        print(f"  정답률: {session_info['accuracy_rate']}%")
    
    # 세션 이력 조회
    print("\n[세션 이력 조회]")
    history = model.get_session_history(session_id)
    print(f"✓ 이력 {len(history)}개:")
    for h in history:
        result = "정답" if h['is_correct'] == 1 else "오답"
        print(f"  - {h['english']}: {result} ({h['response_time']:.1f}초)")
    
    # 세션 통계
    print("\n[세션 통계]")
    stats = model.get_session_statistics(session_id)
    print(f"✓ 총 단어: {stats['total_words']}")
    print(f"  정답률: {stats['accuracy']}%")
    print(f"  평균 응답시간: {stats['avg_response_time']}초")
    
    # 최근 세션 조회
    print("\n[최근 세션 조회]")
    recent = model.get_recent_sessions(limit=5)
    print(f"✓ 최근 세션 {len(recent)}개")
    
    # 정리
    print("\n[정리]")
    model.delete_session(session_id)
    for word_id in test_words:
        word_model.delete_word(word_id)
    print(f"✓ 테스트 데이터 삭제")
    
    print("\n" + "=" * 50)
    print("LearningModel 테스트 완료")
    print("=" * 50)