# 2025-10-20 - 스마트 단어장 - 시험 모델
# 파일 위치: C:\dev\word\models\exam_model.py - v1.0

"""
시험 생성 및 관리
- 시험 생성/종료
- 문제 저장/업데이트
- 시험 이력 조회
- 오답 문제 관리
"""

import sys
import os
import json

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.base_model import BaseModel
from utils.datetime_helper import get_current_datetime
from utils.validators import validate_exam_settings


class ExamModel(BaseModel):
    """
    시험 모델 클래스
    exam_history, exam_questions 테이블 관리
    """
    
    def create_exam(self, exam_type, question_mode, total_questions, time_limit=None):
        """
        시험 생성
        
        Args:
            exam_type (str): 'short_answer' or 'multiple_choice'
            question_mode (str): 'en_to_ko', 'ko_to_en', 'mixed'
            total_questions (int): 총 문항 수
            time_limit (int, optional): 제한 시간 (초)
        
        Returns:
            int: exam_id (실패 시 None)
        """
        # 유효성 검증
        is_valid, error_msg = validate_exam_settings(
            exam_type, question_mode, total_questions, time_limit
        )
        if not is_valid:
            self.logger.warning(f"시험 생성 검증 실패: {error_msg}")
            return None
        
        query = """
            INSERT INTO exam_history
                (exam_date, exam_type, question_mode, total_questions, 
                 time_limit, score)
            VALUES (?, ?, ?, ?, ?, 0.0)
        """
        params = (
            get_current_datetime(),
            exam_type,
            question_mode,
            total_questions,
            time_limit
        )
        
        exam_id = self.execute_update(query, params)
        
        if exam_id:
            self.logger.info(
                f"시험 생성: ID={exam_id}, 타입={exam_type}, "
                f"문항={total_questions}"
            )
        
        return exam_id
    
    def save_exam_question(self, exam_id, word_id, question_number,
                          correct_answer, user_answer=None, 
                          is_correct=0, response_time=None, choices=None):
        """
        시험 문제 저장
        
        Args:
            exam_id (int): 시험 ID
            word_id (int): 단어 ID
            question_number (int): 문제 번호
            correct_answer (str): 정답
            user_answer (str, optional): 사용자 답변
            is_correct (int): 정답 여부 (0 or 1)
            response_time (float, optional): 응답 시간 (초)
            choices (list, optional): 객관식 선택지 리스트
        
        Returns:
            int: question_id (실패 시 None)
        """
        # 선택지를 JSON 문자열로 변환
        choices_json = None
        if choices:
            choices_json = json.dumps(choices, ensure_ascii=False)
        
        query = """
            INSERT INTO exam_questions
                (exam_id, word_id, question_number, correct_answer,
                 user_answer, is_correct, response_time, choices)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            exam_id,
            word_id,
            question_number,
            correct_answer,
            user_answer,
            is_correct,
            response_time,
            choices_json
        )
        
        question_id = self.execute_update(query, params)
        
        if question_id:
            self.logger.debug(
                f"문제 저장: exam_id={exam_id}, Q{question_number}, "
                f"정답={'O' if is_correct else 'X'}"
            )
        
        return question_id
    
    def update_exam_question(self, question_id, user_answer, is_correct, 
                            response_time=None):
        """
        시험 답안 업데이트 (채점)
        
        Args:
            question_id (int): 문제 ID
            user_answer (str): 사용자 답변
            is_correct (bool): 정답 여부
            response_time (float, optional): 응답 시간 (초)
        
        Returns:
            bool: 성공 여부
        """
        query = """
            UPDATE exam_questions
            SET user_answer = ?,
                is_correct = ?,
                response_time = ?
            WHERE question_id = ?
        """
        params = (
            user_answer,
            1 if is_correct else 0,
            response_time,
            question_id
        )
        
        result = self.execute_update(query, params)
        
        return result is not None and result > 0
    
    def finish_exam(self, exam_id, score, time_taken):
        """
        시험 종료 및 채점
        
        Args:
            exam_id (int): 시험 ID
            score (float): 점수 (0-100)
            time_taken (int): 소요 시간 (초)
        
        Returns:
            bool: 성공 여부
        """
        # 정답/오답 수 계산
        stats_query = """
            SELECT 
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_count,
                SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as wrong_count
            FROM exam_questions
            WHERE exam_id = ?
        """
        stats_result = self.execute_query(stats_query, (exam_id,))
        
        if not stats_result:
            self.logger.error(f"시험 통계 조회 실패: exam_id={exam_id}")
            return False
        
        correct_count = stats_result[0]['correct_count'] or 0
        wrong_count = stats_result[0]['wrong_count'] or 0
        
        # 시험 정보 업데이트
        update_query = """
            UPDATE exam_history
            SET correct_count = ?,
                wrong_count = ?,
                score = ?,
                time_taken = ?
            WHERE exam_id = ?
        """
        params = (
            correct_count,
            wrong_count,
            round(score, 2),
            time_taken,
            exam_id
        )
        
        result = self.execute_update(update_query, params)
        
        if result and result > 0:
            self.logger.info(
                f"시험 종료: ID={exam_id}, 점수={score:.1f}, "
                f"정답={correct_count}/{correct_count+wrong_count}"
            )
            return True
        else:
            return False
    
    def get_exam_detail(self, exam_id):
        """
        시험 상세 조회 (문제 포함)
        
        Args:
            exam_id (int): 시험 ID
        
        Returns:
            dict: {'exam': {...}, 'questions': [...]}
        """
        # 시험 정보
        exam = self.get_by_id('exam_history', 'exam_id', exam_id)
        
        if not exam:
            return None
        
        # 문제 목록
        questions_query = """
            SELECT 
                eq.*,
                w.english,
                w.korean
            FROM exam_questions eq
            JOIN words w ON eq.word_id = w.word_id
            WHERE eq.exam_id = ?
            ORDER BY eq.question_number
        """
        questions = self.execute_query(questions_query, (exam_id,))
        
        # choices를 JSON에서 리스트로 변환
        for question in questions:
            if question['choices']:
                try:
                    question['choices'] = json.loads(question['choices'])
                except json.JSONDecodeError:
                    question['choices'] = None
        
        return {
            'exam': exam,
            'questions': questions
        }
    
    def get_exam_history(self, limit=10):
        """
        시험 이력 조회
        
        Args:
            limit (int): 조회 개수
        
        Returns:
            list: 시험 이력 리스트
        """
        query = """
            SELECT *
            FROM exam_history
            ORDER BY exam_date DESC
            LIMIT ?
        """
        
        result = self.execute_query(query, (limit,))
        return result
    
    def get_wrong_questions(self, exam_id):
        """
        특정 시험의 오답 문제 조회
        
        Args:
            exam_id (int): 시험 ID
        
        Returns:
            list: 오답 문제 리스트 (단어 정보 포함)
        """
        query = """
            SELECT 
                eq.*,
                w.english,
                w.korean,
                w.memo
            FROM exam_questions eq
            JOIN words w ON eq.word_id = w.word_id
            WHERE eq.exam_id = ? AND eq.is_correct = 0
            ORDER BY eq.question_number
        """
        
        result = self.execute_query(query, (exam_id,))
        
        # choices 변환
        for question in result:
            if question['choices']:
                try:
                    question['choices'] = json.loads(question['choices'])
                except json.JSONDecodeError:
                    question['choices'] = None
        
        return result
    
    def get_exam_statistics(self, exam_id):
        """
        시험 통계 상세
        
        Args:
            exam_id (int): 시험 ID
        
        Returns:
            dict: 통계 정보
        """
        exam = self.get_by_id('exam_history', 'exam_id', exam_id)
        
        if not exam:
            return None
        
        query = """
            SELECT 
                AVG(response_time) as avg_response_time,
                MAX(response_time) as max_response_time,
                MIN(response_time) as min_response_time
            FROM exam_questions
            WHERE exam_id = ? AND response_time IS NOT NULL
        """
        
        result = self.execute_query(query, (exam_id,))
        
        stats = {
            'exam_id': exam_id,
            'total_questions': exam['total_questions'],
            'correct_count': exam['correct_count'],
            'wrong_count': exam['wrong_count'],
            'score': exam['score'],
            'time_taken': exam['time_taken'],
            'avg_response_time': 0.0,
            'max_response_time': 0.0,
            'min_response_time': 0.0
        }
        
        if result:
            stats['avg_response_time'] = round(result[0]['avg_response_time'] or 0, 2)
            stats['max_response_time'] = round(result[0]['max_response_time'] or 0, 2)
            stats['min_response_time'] = round(result[0]['min_response_time'] or 0, 2)
        
        return stats
    
    def delete_exam(self, exam_id):
        """
        시험 삭제 (CASCADE로 문제도 삭제)
        
        Args:
            exam_id (int): 시험 ID
        
        Returns:
            bool: 성공 여부
        """
        return self.delete_by_id('exam_history', 'exam_id', exam_id)
    
    def get_question_by_id(self, question_id):
        """
        문제 ID로 조회
        
        Args:
            question_id (int): 문제 ID
        
        Returns:
            dict: 문제 정보 (없으면 None)
        """
        return self.get_by_id('exam_questions', 'question_id', question_id)


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("ExamModel 테스트")
    print("=" * 50)
    
    from models.word_model import WordModel
    
    model = ExamModel()
    word_model = WordModel()
    
    # 테스트용 단어 추가
    print("\n[테스트 단어 추가]")
    test_words = []
    for i in range(5):
        word_id = word_model.add_word(f"exam{i}", f"시험{i}", f"시험용 {i}")
        if word_id:
            test_words.append(word_id)
    print(f"✓ {len(test_words)}개 단어 추가")
    
    # 시험 생성
    print("\n[시험 생성]")
    exam_id = model.create_exam('short_answer', 'en_to_ko', 5, time_limit=300)
    if exam_id:
        print(f"✓ 시험 생성: ID={exam_id}")
    
    # 문제 저장
    print("\n[문제 저장]")
    correct_count = 0
    for i, word_id in enumerate(test_words):
        word = word_model.get_word_by_id(word_id)
        is_correct = i % 2 == 0  # 짝수 번호는 정답
        
        question_id = model.save_exam_question(
            exam_id,
            word_id,
            i + 1,
            word['korean'],
            word['korean'] if is_correct else '오답',
            1 if is_correct else 0,
            response_time=3.0 + i
        )
        
        if is_correct:
            correct_count += 1
    
    print(f"✓ {len(test_words)}개 문제 저장")
    
    # 시험 종료
    print("\n[시험 종료]")
    score = (correct_count / len(test_words)) * 100
    success = model.finish_exam(exam_id, score, 180)
    print(f"✓ 시험 종료: 점수={score:.1f}점")
    
    # 시험 상세 조회
    print("\n[시험 상세 조회]")
    detail = model.get_exam_detail(exam_id)
    if detail:
        print(f"✓ 시험 ID: {detail['exam']['exam_id']}")
        print(f"  타입: {detail['exam']['exam_type']}")
        print(f"  점수: {detail['exam']['score']}점")
        print(f"  문제 수: {len(detail['questions'])}개")
    
    # 오답 문제 조회
    print("\n[오답 문제 조회]")
    wrong = model.get_wrong_questions(exam_id)
    print(f"✓ 오답 {len(wrong)}개:")
    for q in wrong:
        print(f"  Q{q['question_number']}. {q['english']} (답: {q['user_answer']})")
    
    # 시험 통계
    print("\n[시험 통계]")
    stats = model.get_exam_statistics(exam_id)
    if stats:
        print(f"✓ 정답/오답: {stats['correct_count']}/{stats['wrong_count']}")
        print(f"  평균 응답시간: {stats['avg_response_time']}초")
    
    # 시험 이력
    print("\n[시험 이력]")
    history = model.get_exam_history(limit=5)
    print(f"✓ 최근 시험 {len(history)}개")
    
    # 정리
    print("\n[정리]")
    model.delete_exam(exam_id)
    for word_id in test_words:
        word_model.delete_word(word_id)
    print(f"✓ 테스트 데이터 삭제")
    
    print("\n" + "=" * 50)
    print("ExamModel 테스트 완료")
    print("=" * 50)