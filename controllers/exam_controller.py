# 2025-10-27 - 스마트 단어장 - 시험 컨트롤러
# 파일 위치: word/controllers/exam_controller.py - v1.0

"""
시험 진행 컨트롤러

주요 기능:
- 시험 생성 (주관식/객관식)
- 문제 출제 및 답안 처리
- 시험 채점 및 결과 관리
- 오답 노트 관리
"""

import sys
import os
import random
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.word_model import WordModel
from models.exam_model import ExamModel
from models.statistics_model import StatisticsModel
from utils.logger import get_logger
from utils.datetime_helper import get_current_datetime
import config

logger = get_logger(__name__)


class ExamController:
    """시험 컨트롤러"""
    
    def __init__(self):
        """컨트롤러 초기화"""
        self.word_model = WordModel()
        self.exam_model = ExamModel()
        self.statistics_model = StatisticsModel()
        self.logger = logger
        
        # 시험 상태 관리
        self.current_exam_id = None
        self.exam_type = None  # 'short_answer' or 'multiple_choice'
        self.question_mode = None  # 'en_to_ko' or 'ko_to_en' or 'mixed'
        self.exam_questions = []  # 시험 문제 목록
        self.current_question_index = 0
        self.exam_start_time = None
    
    # === 시험 생성 ===
    
    def create_exam(self, exam_type, question_mode, total_questions, 
                   word_order='random', time_limit=None):
        """
        시험 생성
        
        Args:
            exam_type (str): 'short_answer' | 'multiple_choice'
            question_mode (str): 'en_to_ko' | 'ko_to_en' | 'mixed'
            total_questions (int): 총 문항 수
            word_order (str): 'random' | 'personalized'
            time_limit (int, optional): 제한 시간 (초, None이면 무제한)
        
        Returns:
            Tuple[bool, str, int]: (성공여부, 메시지, exam_id)
        """
        try:
            # 1. 기존 시험이 있으면 종료
            if self.current_exam_id:
                self.logger.warning("기존 시험 존재, 강제 종료")
                # 강제 종료는 하지 않고 오류 반환
                return (False, "진행 중인 시험이 있습니다. 먼저 종료하세요.", None)
            
            # 2. 검증
            if exam_type not in ['short_answer', 'multiple_choice']:
                return (False, "잘못된 시험 유형입니다.", None)
            
            if question_mode not in ['en_to_ko', 'ko_to_en', 'mixed']:
                return (False, "잘못된 문제 모드입니다.", None)
            
            if total_questions <= 0:
                return (False, "문항 수는 1개 이상이어야 합니다.", None)
            
            # 3. 단어 선택
            all_words = self.word_model.get_all_words()
            
            if not all_words:
                return (False, "시험 출제할 단어가 없습니다.", None)
            
            if len(all_words) < total_questions:
                return (
                    False, 
                    f"단어가 부족합니다. (필요: {total_questions}개, 보유: {len(all_words)}개)",
                    None
                )
            
            # 4. 단어 정렬/선택
            if word_order == 'personalized':
                # 개인화 점수 기반 정렬
                words_with_score = []
                for word in all_words:
                    score = self.statistics_model.calculate_personalization_score(
                        word['word_id']
                    )
                    words_with_score.append((word, score))
                
                words_with_score.sort(key=lambda x: x[1], reverse=True)
                selected_words = [w[0] for w in words_with_score[:total_questions]]
            else:  # random
                selected_words = random.sample(all_words, total_questions)
            
            # 5. 시험 생성 (DB)
            exam_id = self.exam_model.create_exam(
                exam_type=exam_type,
                question_mode=question_mode,
                total_questions=total_questions,
                time_limit=time_limit
            )
            
            if not exam_id:
                return (False, "시험 생성에 실패했습니다.", None)
            
            # 6. 문제 목록 생성
            self.exam_questions = []
            
            for idx, word in enumerate(selected_words, 1):
                # mixed 모드면 문제별로 랜덤 결정
                if question_mode == 'mixed':
                    current_mode = random.choice(['en_to_ko', 'ko_to_en'])
                else:
                    current_mode = question_mode
                
                # 문제/정답 결정
                if current_mode == 'en_to_ko':
                    question_text = word['english']
                    correct_answer = word['korean']
                else:  # ko_to_en
                    question_text = word['korean']
                    correct_answer = word['english']
                
                # 객관식이면 선택지 생성
                choices = None
                if exam_type == 'multiple_choice':
                    choices = self._generate_choices(
                        word['word_id'],
                        correct_answer,
                        current_mode
                    )
                
                # 문제 저장
                question_id = self.exam_model.save_exam_question(
                    exam_id=exam_id,
                    word_id=word['word_id'],
                    question_number=idx,
                    correct_answer=correct_answer,
                    choices=choices
                )
                
                # 문제 정보 저장
                self.exam_questions.append({
                    'question_id': question_id,
                    'question_number': idx,
                    'word_id': word['word_id'],
                    'question_text': question_text,
                    'correct_answer': correct_answer,
                    'choices': choices,
                    'user_answer': None
                })
            
            # 7. 상태 초기화
            self.current_exam_id = exam_id
            self.exam_type = exam_type
            self.question_mode = question_mode
            self.current_question_index = 0
            self.exam_start_time = datetime.now()
            
            self.logger.info(
                f"시험 생성: ID={exam_id}, 유형={exam_type}, "
                f"문항수={total_questions}"
            )
            
            return (True, f"시험이 생성되었습니다 ({total_questions}문항)", exam_id)
            
        except Exception as e:
            self.logger.error(f"시험 생성 실패: {e}", exc_info=True)
            return (False, "시험 생성 중 오류가 발생했습니다.", None)
    
    def _generate_choices(self, word_id, correct_answer, mode):
        """
        객관식 선택지 생성 (4지선다)
        
        Args:
            word_id (int): 정답 단어 ID
            correct_answer (str): 정답
            mode (str): 'en_to_ko' or 'ko_to_en'
        
        Returns:
            List[str]: [선택지1, 선택지2, 선택지3, 선택지4] (정답 포함, 셔플됨)
        """
        try:
            # 오답 선택지로 사용할 단어들 가져오기
            all_words = self.word_model.get_all_words()
            
            # 현재 단어 제외
            other_words = [w for w in all_words if w['word_id'] != word_id]
            
            if len(other_words) < 3:
                # 단어가 부족하면 정답만 반환
                return [correct_answer]
            
            # 오답 3개 랜덤 선택
            wrong_words = random.sample(other_words, 3)
            
            # 오답 선택지 생성
            wrong_choices = []
            for word in wrong_words:
                if mode == 'en_to_ko':
                    wrong_choices.append(word['korean'])
                else:  # ko_to_en
                    wrong_choices.append(word['english'])
            
            # 정답 + 오답 합치고 셔플
            choices = [correct_answer] + wrong_choices
            random.shuffle(choices)
            
            return choices
            
        except Exception as e:
            self.logger.error(f"선택지 생성 실패: {e}", exc_info=True)
            return [correct_answer]
    
    # === 시험 진행 ===
    
    def get_current_question(self):
        """
        현재 문제 조회
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 문제 정보)
            {
                'question_number': 1,
                'question_text': '사과',
                'choices': ['apple', 'banana', 'grape', 'orange'],  # 객관식만
                'current': 1,
                'total': 10
            }
        """
        try:
            # 시험 확인
            if not self.current_exam_id:
                return (False, "진행 중인 시험이 없습니다.", None)
            
            # 범위 확인
            if self.current_question_index >= len(self.exam_questions):
                return (False, "모든 문제를 완료했습니다.", None)
            
            # 현재 문제
            question = self.exam_questions[self.current_question_index]
            
            result = {
                'question_number': question['question_number'],
                'question_text': question['question_text'],
                'choices': question['choices'],  # 주관식이면 None
                'current': self.current_question_index + 1,
                'total': len(self.exam_questions)
            }
            
            return (True, "현재 문제", result)
            
        except Exception as e:
            self.logger.error(f"현재 문제 조회 실패: {e}", exc_info=True)
            return (False, "문제 조회 중 오류가 발생했습니다.", None)
    
    def submit_answer(self, user_answer):
        """
        답안 제출
        
        Args:
            user_answer: 사용자 답변 (주관식: str, 객관식: int 0-3 또는 str)
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            # 시험 확인
            if not self.current_exam_id:
                return (False, "진행 중인 시험이 없습니다.")
            
            # 범위 확인
            if self.current_question_index >= len(self.exam_questions):
                return (False, "모든 문제를 완료했습니다.")
            
            # 현재 문제
            question = self.exam_questions[self.current_question_index]
            
            # 객관식이면 선택지 인덱스를 실제 답으로 변환
            if self.exam_type == 'multiple_choice' and isinstance(user_answer, int):
                choices = question['choices']
                if 0 <= user_answer < len(choices):
                    user_answer = choices[user_answer]
                else:
                    return (False, "잘못된 선택지 번호입니다.")
            
            # 답안 저장 (메모리)
            question['user_answer'] = user_answer
            
            # 다음 문제로 이동
            self.current_question_index += 1
            
            self.logger.debug(
                f"답안 제출: 문제 {question['question_number']} - {user_answer}"
            )
            
            return (True, "답안이 제출되었습니다.")
            
        except Exception as e:
            self.logger.error(f"답안 제출 실패: {e}", exc_info=True)
            return (False, "답안 제출 중 오류가 발생했습니다.")
    
    def go_to_question(self, question_number):
        """
        특정 문제로 이동
        
        Args:
            question_number (int): 문제 번호 (1부터 시작)
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            if not self.current_exam_id:
                return (False, "진행 중인 시험이 없습니다.")
            
            # 인덱스로 변환 (1-based → 0-based)
            index = question_number - 1
            
            if 0 <= index < len(self.exam_questions):
                self.current_question_index = index
                return (True, f"{question_number}번 문제로 이동했습니다.")
            else:
                return (False, "잘못된 문제 번호입니다.")
                
        except Exception as e:
            self.logger.error(f"문제 이동 실패: {e}", exc_info=True)
            return (False, "이동 중 오류가 발생했습니다.")
    
    def finish_exam(self):
        """
        시험 종료 및 채점
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 결과)
            {
                'exam_id': 1,
                'total_questions': 10,
                'correct_count': 8,
                'wrong_count': 2,
                'score': 80.0,
                'time_taken': 300
            }
        """
        try:
            # 시험 확인
            if not self.current_exam_id:
                return (False, "진행 중인 시험이 없습니다.", None)
            
            # 1. 채점
            correct_count = 0
            wrong_count = 0
            
            for question in self.exam_questions:
                user_answer = question.get('user_answer', '')
                correct_answer = question['correct_answer']
                
                # 정답 확인 (대소문자 무시, 공백 제거)
                if user_answer and str(user_answer).strip().lower() == str(correct_answer).strip().lower():
                    is_correct = True
                    correct_count += 1
                else:
                    is_correct = False
                    wrong_count += 1
                
                # DB 업데이트
                self.exam_model.update_exam_question(
                    question_id=question['question_id'],
                    user_answer=user_answer,
                    is_correct=is_correct
                )
                
                # 통계 업데이트
                self.statistics_model.update_word_statistics(
                    question['word_id'],
                    is_correct
                )
                
                # 오답이면 오답 노트에 추가
                if not is_correct:
                    self.exam_model.add_to_wrong_note(
                        self.current_exam_id,
                        question['word_id']
                    )
            
            # 2. 점수 계산
            total_questions = len(self.exam_questions)
            score = round((correct_count / total_questions * 100) if total_questions > 0 else 0.0, 1)
            
            # 3. 소요 시간 계산
            if self.exam_start_time:
                time_taken = int((datetime.now() - self.exam_start_time).total_seconds())
            else:
                time_taken = 0
            
            # 4. 시험 종료 처리 (DB)
            success = self.exam_model.finish_exam(
                self.current_exam_id,
                score,
                time_taken
            )
            
            if not success:
                self.logger.warning("시험 종료 처리 실패")
            
            # 5. 결과 데이터
            result = {
                'exam_id': self.current_exam_id,
                'total_questions': total_questions,
                'correct_count': correct_count,
                'wrong_count': wrong_count,
                'score': score,
                'time_taken': time_taken
            }
            
            self.logger.info(
                f"시험 종료: ID={self.current_exam_id}, "
                f"점수={score}점 ({correct_count}/{total_questions})"
            )
            
            # 6. 상태 초기화
            self.current_exam_id = None
            self.exam_type = None
            self.question_mode = None
            self.exam_questions = []
            self.current_question_index = 0
            self.exam_start_time = None
            
            return (True, "시험이 종료되었습니다.", result)
            
        except Exception as e:
            self.logger.error(f"시험 종료 실패: {e}", exc_info=True)
            return (False, "시험 종료 중 오류가 발생했습니다.", None)
    
    # === 시험 결과 ===
    
    def get_exam_result(self, exam_id):
        """
        시험 결과 상세 조회
        
        Args:
            exam_id (int): 시험 ID
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 시험 결과)
        """
        try:
            # 시험 정보
            exam_info = self.exam_model.get_exam_by_id(exam_id)
            if not exam_info:
                return (False, "시험을 찾을 수 없습니다.", None)
            
            # 문제 상세
            questions = self.exam_model.get_exam_questions(exam_id)
            
            result = {
                'exam_info': exam_info,
                'questions': questions
            }
            
            return (True, "시험 결과 조회 완료", result)
            
        except Exception as e:
            self.logger.error(f"시험 결과 조회 실패 (ID={exam_id}): {e}", exc_info=True)
            return (False, "시험 결과 조회 중 오류가 발생했습니다.", None)
    
    def get_exam_history(self, limit=10):
        """
        시험 이력 조회
        
        Args:
            limit (int): 조회할 개수
        
        Returns:
            Tuple[bool, str, List[Dict]]: (성공여부, 메시지, 시험 목록)
        """
        try:
            exams = self.exam_model.get_recent_exams(limit)
            
            self.logger.debug(f"시험 이력 조회: {len(exams)}개")
            return (True, f"{len(exams)}개 시험 조회 완료", exams)
            
        except Exception as e:
            self.logger.error(f"시험 이력 조회 실패: {e}", exc_info=True)
            return (False, "시험 이력 조회 중 오류가 발생했습니다.", [])
    
    # === 오답 노트 ===
    
    def get_wrong_notes(self):
        """
        오답 노트 조회
        
        Returns:
            Tuple[bool, str, List[Dict]]: (성공여부, 메시지, 오답 목록)
        """
        try:
            wrong_notes = self.exam_model.get_unresolved_wrong_notes()
            
            self.logger.debug(f"오답 노트 조회: {len(wrong_notes)}개")
            return (True, f"{len(wrong_notes)}개 오답 조회 완료", wrong_notes)
            
        except Exception as e:
            self.logger.error(f"오답 노트 조회 실패: {e}", exc_info=True)
            return (False, "오답 노트 조회 중 오류가 발생했습니다.", [])
    
    def mark_wrong_note_resolved(self, word_id):
        """
        오답 노트 해결 처리
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            success = self.exam_model.mark_wrong_note_resolved(word_id)
            
            if success:
                self.logger.info(f"오답 노트 해결: word_id={word_id}")
                return (True, "오답 노트가 해결 처리되었습니다.")
            else:
                return (False, "오답 노트 해결 처리에 실패했습니다.")
                
        except Exception as e:
            self.logger.error(f"오답 노트 해결 실패 (word_id={word_id}): {e}", exc_info=True)
            return (False, "처리 중 오류가 발생했습니다.")