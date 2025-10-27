# 2025-10-27 - 스마트 단어장 - 플래시카드 학습 컨트롤러
# 파일 위치: word/controllers/flashcard_controller.py - v1.0

"""
플래시카드 학습 컨트롤러

주요 기능:
- 학습 세션 시작/종료
- 단어 출제 및 답변 처리
- 학습 순서 관리 (순차/랜덤/개인화)
- 진행 상황 추적
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
from models.learning_model import LearningModel
from models.statistics_model import StatisticsModel
from utils.logger import get_logger
from utils.datetime_helper import get_current_datetime

logger = get_logger(__name__)


class FlashcardController:
    """플래시카드 학습 컨트롤러"""
    
    def __init__(self):
        """컨트롤러 초기화"""
        self.word_model = WordModel()
        self.learning_model = LearningModel()
        self.statistics_model = StatisticsModel()
        self.logger = logger
        
        # 세션 상태 관리
        self.current_session_id = None
        self.study_mode = None  # 'flashcard_en_ko' or 'flashcard_ko_en'
        self.current_words = []  # 학습할 단어 목록
        self.current_index = 0
        self.session_results = []  # [(word_id, is_correct, response_time), ...]
        self.session_start_time = None
    
    # === 세션 관리 ===
    
    def start_session(self, study_mode, word_order='sequential', 
                     filter_favorite=False, word_count=None):
        """
        학습 세션 시작
        
        Args:
            study_mode (str): 'flashcard_en_ko' | 'flashcard_ko_en'
            word_order (str): 'sequential' | 'random' | 'personalized'
            filter_favorite (bool): 즐겨찾기만 학습
            word_count (int, optional): 학습할 단어 수 (None이면 전체)
        
        Returns:
            Tuple[bool, str, int]: (성공여부, 메시지, 총 단어 수)
        """
        try:
            # 1. 기존 세션이 있으면 종료
            if self.current_session_id:
                self.logger.warning("기존 세션 존재, 강제 종료")
                self.end_session()
            
            # 2. study_mode 검증
            if study_mode not in ['flashcard_en_ko', 'flashcard_ko_en']:
                return (False, "잘못된 학습 모드입니다.", 0)
            
            # 3. 세션 생성
            session_type = 'flashcard'
            db_study_mode = 'sequential'  # DB용 간단한 모드
            
            session_id = self.learning_model.create_session(session_type, db_study_mode)
            
            if not session_id:
                return (False, "세션 생성에 실패했습니다.", 0)
            
            # 4. 단어 목록 가져오기
            if filter_favorite:
                words = self.word_model.get_favorite_words()
            else:
                words = self.word_model.get_all_words()
            
            if not words:
                self.learning_model.end_session(session_id, 0, 0, 0)
                return (False, "학습할 단어가 없습니다.", 0)
            
            # 5. 단어 순서 결정
            if word_order == 'random':
                random.shuffle(words)
            elif word_order == 'personalized':
                # 개인화 점수 기반 정렬
                words_with_score = []
                for word in words:
                    score = self.statistics_model.calculate_personalization_score(
                        word['word_id']
                    )
                    words_with_score.append((word, score))
                
                # 점수 높은 순 정렬 (우선순위 높은 단어부터)
                words_with_score.sort(key=lambda x: x[1], reverse=True)
                words = [w[0] for w in words_with_score]
            # sequential은 DB 순서 그대로
            
            # 6. 단어 수 제한
            if word_count and word_count > 0:
                words = words[:word_count]
            
            # 7. 상태 초기화
            self.current_session_id = session_id
            self.study_mode = study_mode
            self.current_words = words
            self.current_index = 0
            self.session_results = []
            self.session_start_time = datetime.now()
            
            total_words = len(words)
            self.logger.info(
                f"세션 시작: ID={session_id}, 모드={study_mode}, "
                f"순서={word_order}, 단어수={total_words}"
            )
            
            return (True, f"학습 세션 시작 ({total_words}개 단어)", total_words)
            
        except Exception as e:
            self.logger.error(f"세션 시작 실패: {e}", exc_info=True)
            return (False, "세션 시작 중 오류가 발생했습니다.", 0)
    
    def get_current_word(self):
        """
        현재 단어 조회
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 단어 정보)
            {
                'word_id': 1,
                'question': '사과',  # study_mode에 따라 다름
                'current': 1,
                'total': 20
            }
        """
        try:
            # 세션 확인
            if not self.current_session_id:
                return (False, "진행 중인 세션이 없습니다.", None)
            
            # 범위 확인
            if self.current_index >= len(self.current_words):
                return (False, "모든 단어를 완료했습니다.", None)
            
            # 현재 단어
            word = self.current_words[self.current_index]
            
            # 문제 텍스트 결정
            if self.study_mode == 'flashcard_en_ko':
                question = word['english']
            else:  # flashcard_ko_en
                question = word['korean']
            
            result = {
                'word_id': word['word_id'],
                'question': question,
                'current': self.current_index + 1,
                'total': len(self.current_words)
            }
            
            return (True, "현재 단어", result)
            
        except Exception as e:
            self.logger.error(f"현재 단어 조회 실패: {e}", exc_info=True)
            return (False, "단어 조회 중 오류가 발생했습니다.", None)
    
    def submit_answer(self, user_answer, response_time):
        """
        답변 제출 및 정답 확인
        
        Args:
            user_answer (str): 사용자 답변
            response_time (float): 응답 시간 (초)
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 결과)
            {
                'is_correct': True,
                'correct_answer': 'apple',
                'user_answer': 'apple'
            }
        """
        try:
            # 1. 세션 확인
            if not self.current_session_id:
                return (False, "진행 중인 세션이 없습니다.", None)
            
            # 2. 현재 단어 확인
            if self.current_index >= len(self.current_words):
                return (False, "모든 단어를 완료했습니다.", None)
            
            current_word = self.current_words[self.current_index]
            word_id = current_word['word_id']
            
            # 3. 정답 확인
            if self.study_mode == 'flashcard_en_ko':
                correct_answer = current_word['korean']
            else:  # flashcard_ko_en
                correct_answer = current_word['english']
            
            # 대소문자 무시, 앞뒤 공백 제거하여 비교
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
            
            # 4. 학습 이력 저장
            success = self.learning_model.add_learning_history(
                session_id=self.current_session_id,
                word_id=word_id,
                study_mode=self.study_mode,
                is_correct=is_correct,
                response_time=response_time,
                user_answer=user_answer
            )
            
            if not success:
                self.logger.warning(f"학습 이력 저장 실패: word_id={word_id}")
            
            # 5. 통계 업데이트
            self.statistics_model.update_word_statistics(word_id, is_correct)
            
            # 6. 결과 기록
            self.session_results.append((word_id, is_correct, response_time))
            
            # 7. 다음 단어로 이동
            self.current_index += 1
            
            result = {
                'is_correct': is_correct,
                'correct_answer': correct_answer,
                'user_answer': user_answer
            }
            
            result_text = "정답" if is_correct else "오답"
            self.logger.debug(
                f"답변 제출: {result_text} - {user_answer} "
                f"({response_time:.1f}초)"
            )
            
            return (True, result_text, result)
            
        except Exception as e:
            self.logger.error(f"답변 제출 실패: {e}", exc_info=True)
            return (False, "답변 처리 중 오류가 발생했습니다.", None)
    
    def skip_word(self):
        """
        현재 단어 건너뛰기
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            # 세션 확인
            if not self.current_session_id:
                return (False, "진행 중인 세션이 없습니다.")
            
            # 범위 확인
            if self.current_index >= len(self.current_words):
                return (False, "모든 단어를 완료했습니다.")
            
            # 다음 단어로 이동
            self.current_index += 1
            
            self.logger.debug(f"단어 건너뛰기: 인덱스={self.current_index}")
            return (True, "단어를 건너뛰었습니다.")
            
        except Exception as e:
            self.logger.error(f"단어 건너뛰기 실패: {e}", exc_info=True)
            return (False, "처리 중 오류가 발생했습니다.")
    
    def end_session(self):
        """
        세션 종료 및 결과 반환
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 통계)
            {
                'total_words': 20,
                'correct_count': 16,
                'wrong_count': 4,
                'accuracy': 80.0,
                'total_time': 180
            }
        """
        try:
            # 세션 확인
            if not self.current_session_id:
                return (False, "진행 중인 세션이 없습니다.", None)
            
            # 1. 통계 계산
            total_words = len(self.session_results)
            correct_count = sum(1 for _, is_correct, _ in self.session_results if is_correct)
            wrong_count = total_words - correct_count
            
            # 소요 시간 계산
            if self.session_start_time:
                total_time = int((datetime.now() - self.session_start_time).total_seconds())
            else:
                total_time = 0
            
            # 2. 세션 종료 처리
            success = self.learning_model.end_session(
                self.current_session_id,
                total_words,
                correct_count,
                wrong_count
            )
            
            if not success:
                self.logger.warning("세션 종료 처리 실패")
            
            # 3. 통계 데이터
            stats = {
                'total_words': total_words,
                'correct_count': correct_count,
                'wrong_count': wrong_count,
                'accuracy': round((correct_count / total_words * 100) if total_words > 0 else 0.0, 1),
                'total_time': total_time
            }
            
            self.logger.info(
                f"세션 종료: ID={self.current_session_id}, "
                f"단어={total_words}, 정답률={stats['accuracy']}%"
            )
            
            # 4. 상태 초기화
            self.current_session_id = None
            self.study_mode = None
            self.current_words = []
            self.current_index = 0
            self.session_results = []
            self.session_start_time = None
            
            return (True, "학습 세션 종료", stats)
            
        except Exception as e:
            self.logger.error(f"세션 종료 실패: {e}", exc_info=True)
            return (False, "세션 종료 중 오류가 발생했습니다.", None)
    
    # === 진행 상황 ===
    
    def get_progress(self):
        """
        현재 진행 상황
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 진행 상황)
            {'current': 5, 'total': 20, 'percentage': 25.0}
        """
        try:
            if not self.current_session_id:
                return (False, "진행 중인 세션이 없습니다.", None)
            
            total = len(self.current_words)
            current = self.current_index
            percentage = round((current / total * 100) if total > 0 else 0.0, 1)
            
            progress = {
                'current': current,
                'total': total,
                'percentage': percentage
            }
            
            return (True, "진행 상황", progress)
            
        except Exception as e:
            self.logger.error(f"진행 상황 조회 실패: {e}", exc_info=True)
            return (False, "조회 중 오류가 발생했습니다.", None)
    
    def has_next(self):
        """
        다음 단어 존재 여부
        
        Returns:
            Tuple[bool, str, bool]: (성공여부, 메시지, 다음 단어 존재 여부)
        """
        try:
            if not self.current_session_id:
                return (False, "진행 중인 세션이 없습니다.", False)
            
            has_next = self.current_index < len(self.current_words)
            
            return (True, "확인 완료", has_next)
            
        except Exception as e:
            self.logger.error(f"다음 단어 확인 실패: {e}", exc_info=True)
            return (False, "확인 중 오류가 발생했습니다.", False)
    
    # === 유틸리티 ===
    
    def get_session_info(self):
        """
        현재 세션 정보 조회
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 세션 정보)
        """
        try:
            if not self.current_session_id:
                return (False, "진행 중인 세션이 없습니다.", None)
            
            info = {
                'session_id': self.current_session_id,
                'study_mode': self.study_mode,
                'total_words': len(self.current_words),
                'current_index': self.current_index,
                'answered_count': len(self.session_results)
            }
            
            return (True, "세션 정보", info)
            
        except Exception as e:
            self.logger.error(f"세션 정보 조회 실패: {e}", exc_info=True)
            return (False, "조회 중 오류가 발생했습니다.", None)