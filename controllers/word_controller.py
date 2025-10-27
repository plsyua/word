# 2025-10-27 - 스마트 단어장 - 단어 관리 컨트롤러
# 파일 위치: word/controllers/word_controller.py - v1.0

"""
단어 관리 컨트롤러

주요 기능:
- 단어 CRUD (추가, 조회, 수정, 삭제)
- 단어 검색 및 필터링
- 즐겨찾기 관리
- CSV 임포트/엑스포트
"""

import sys
import os

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.word_model import WordModel
from models.statistics_model import StatisticsModel
from utils.logger import get_logger
from utils.validators import validate_word
from utils.csv_handler import read_csv, write_csv

logger = get_logger(__name__)


class WordController:
    """단어 관리 컨트롤러"""
    
    def __init__(self):
        """컨트롤러 초기화"""
        self.word_model = WordModel()
        self.statistics_model = StatisticsModel()
        self.logger = logger
    
    # === 조회 기능 ===
    
    def get_word_list(self, filter_favorite=False, category=None):
        """
        단어 목록 조회 (필터 적용)
        
        Args:
            filter_favorite (bool): 즐겨찾기만 조회
            category (str, optional): 카테고리 필터 (향후 확장용)
        
        Returns:
            Tuple[bool, str, List[Dict]]: (성공여부, 메시지, 단어 목록)
        """
        try:
            if filter_favorite:
                words = self.word_model.get_favorite_words()
                self.logger.debug(f"즐겨찾기 단어 조회: {len(words)}개")
            else:
                words = self.word_model.get_all_words()
                self.logger.debug(f"전체 단어 조회: {len(words)}개")
            
            if words:
                return (True, f"{len(words)}개 단어 조회 완료", words)
            else:
                return (True, "단어가 없습니다.", [])
                
        except Exception as e:
            self.logger.error(f"단어 목록 조회 실패: {e}", exc_info=True)
            return (False, "단어 목록 조회 중 오류가 발생했습니다.", [])
    
    def search_words(self, keyword, search_in='all'):
        """
        단어 검색
        
        Args:
            keyword (str): 검색 키워드
            search_in (str): 검색 대상 ('english', 'korean', 'memo', 'all')
        
        Returns:
            Tuple[bool, str, List[Dict]]: (성공여부, 메시지, 검색 결과)
        """
        try:
            if not keyword or not keyword.strip():
                return (False, "검색어를 입력하세요.", [])
            
            keyword = keyword.strip()
            
            # search_in에 따라 검색
            if search_in == 'all':
                results = self.word_model.search_words(keyword)
            elif search_in == 'english':
                results = self.word_model.search_words_by_english(keyword)
            elif search_in == 'korean':
                results = self.word_model.search_words_by_korean(keyword)
            elif search_in == 'memo':
                results = self.word_model.search_words_by_memo(keyword)
            else:
                return (False, f"잘못된 검색 대상: {search_in}", [])
            
            self.logger.debug(f"단어 검색 ({search_in}): '{keyword}' - {len(results)}개")
            
            if results:
                return (True, f"{len(results)}개 단어 검색 완료", results)
            else:
                return (True, "검색 결과가 없습니다.", [])
                
        except Exception as e:
            self.logger.error(f"단어 검색 실패 ({keyword}): {e}", exc_info=True)
            return (False, "단어 검색 중 오류가 발생했습니다.", [])
    
    def get_word_by_id(self, word_id):
        """
        단어 상세 조회
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 단어 정보)
        """
        try:
            if not isinstance(word_id, int) or word_id <= 0:
                return (False, "유효하지 않은 단어 ID입니다.", None)
            
            word = self.word_model.get_word_by_id(word_id)
            
            if word:
                self.logger.debug(f"단어 조회: ID={word_id}")
                return (True, "단어 조회 완료", word)
            else:
                return (False, "단어를 찾을 수 없습니다.", None)
                
        except Exception as e:
            self.logger.error(f"단어 조회 실패 (ID={word_id}): {e}", exc_info=True)
            return (False, "단어 조회 중 오류가 발생했습니다.", None)
    
    # === 추가/수정/삭제 ===
    
    def add_word(self, english, korean, memo=None):
        """
        단어 추가 (검증 포함)
        
        Args:
            english (str): 영어 단어
            korean (str): 한글 뜻
            memo (str, optional): 메모
        
        Returns:
            Tuple[bool, str, int]: (성공여부, 메시지, word_id)
        """
        try:
            # 1. 입력 검증
            is_valid, error_msg = validate_word(english, korean, memo)
            if not is_valid:
                self.logger.warning(f"단어 검증 실패: {error_msg}")
                return (False, error_msg, None)
            
            # 2. 중복 체크
            existing = self.word_model.get_word_by_english(english.strip())
            if existing:
                self.logger.warning(f"중복 단어: {english}")
                return (False, f"'{english}' 단어가 이미 존재합니다.", None)
            
            # 3. 단어 추가
            word_id = self.word_model.add_word(
                english.strip(),
                korean.strip(),
                memo.strip() if memo else None
            )
            
            if word_id:
                # 4. 통계 초기화
                self.statistics_model.initialize_word_statistics(word_id)
                
                self.logger.info(f"단어 추가 완료: {english} (ID={word_id})")
                return (True, f"'{english}' 단어가 추가되었습니다.", word_id)
            else:
                self.logger.error(f"단어 추가 실패: {english}")
                return (False, "단어 추가에 실패했습니다.", None)
                
        except Exception as e:
            self.logger.error(f"단어 추가 실패 ({english}): {e}", exc_info=True)
            return (False, "단어 추가 중 오류가 발생했습니다.", None)
    
    def update_word(self, word_id, english=None, korean=None, memo=None):
        """
        단어 수정
        
        Args:
            word_id (int): 단어 ID
            english (str, optional): 새 영어 단어
            korean (str, optional): 새 한글 뜻
            memo (str, optional): 새 메모
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            # 1. 단어 존재 확인
            existing = self.word_model.get_word_by_id(word_id)
            if not existing:
                return (False, "수정할 단어를 찾을 수 없습니다.")
            
            # 2. 변경할 내용이 있는지 확인
            if english is None and korean is None and memo is None:
                return (False, "변경할 내용이 없습니다.")
            
            # 3. 변경할 값 준비 (None이면 기존 값 유지)
            new_english = english.strip() if english else existing['english']
            new_korean = korean.strip() if korean else existing['korean']
            new_memo = memo.strip() if memo else existing['memo']
            
            # 4. 검증
            is_valid, error_msg = validate_word(new_english, new_korean, new_memo)
            if not is_valid:
                self.logger.warning(f"단어 수정 검증 실패: {error_msg}")
                return (False, error_msg)
            
            # 5. 영어 단어 변경 시 중복 체크
            if english and english.strip() != existing['english']:
                duplicate = self.word_model.get_word_by_english(new_english)
                if duplicate:
                    return (False, f"'{new_english}' 단어가 이미 존재합니다.")
            
            # 6. 단어 수정
            success = self.word_model.update_word(
                word_id,
                new_english,
                new_korean,
                new_memo
            )
            
            if success:
                self.logger.info(f"단어 수정 완료: ID={word_id}")
                return (True, "단어가 수정되었습니다.")
            else:
                self.logger.error(f"단어 수정 실패: ID={word_id}")
                return (False, "단어 수정에 실패했습니다.")
                
        except Exception as e:
            self.logger.error(f"단어 수정 실패 (ID={word_id}): {e}", exc_info=True)
            return (False, "단어 수정 중 오류가 발생했습니다.")
    
    def delete_word(self, word_id):
        """
        단어 삭제
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            # 1. 단어 존재 확인
            word = self.word_model.get_word_by_id(word_id)
            if not word:
                return (False, "삭제할 단어를 찾을 수 없습니다.")
            
            # 2. 단어 삭제 (CASCADE로 관련 데이터도 삭제됨)
            success = self.word_model.delete_word(word_id)
            
            if success:
                self.logger.info(f"단어 삭제 완료: {word['english']} (ID={word_id})")
                return (True, f"'{word['english']}' 단어가 삭제되었습니다.")
            else:
                self.logger.error(f"단어 삭제 실패: ID={word_id}")
                return (False, "단어 삭제에 실패했습니다.")
                
        except Exception as e:
            self.logger.error(f"단어 삭제 실패 (ID={word_id}): {e}", exc_info=True)
            return (False, "단어 삭제 중 오류가 발생했습니다.")
    
    def toggle_favorite(self, word_id):
        """
        즐겨찾기 토글
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            Tuple[bool, str, bool]: (성공여부, 메시지, 새로운 즐겨찾기 상태)
        """
        try:
            # 1. 단어 존재 확인
            word = self.word_model.get_word_by_id(word_id)
            if not word:
                return (False, "단어를 찾을 수 없습니다.", None)
            
            # 2. 즐겨찾기 토글
            success = self.word_model.toggle_favorite(word_id)
            
            if success:
                # 새로운 상태 확인
                updated_word = self.word_model.get_word_by_id(word_id)
                new_status = updated_word['is_favorite']
                
                status_text = "추가" if new_status else "해제"
                self.logger.info(
                    f"즐겨찾기 {status_text}: {word['english']} (ID={word_id})"
                )
                return (True, f"즐겨찾기가 {status_text}되었습니다.", new_status)
            else:
                self.logger.error(f"즐겨찾기 토글 실패: ID={word_id}")
                return (False, "즐겨찾기 변경에 실패했습니다.", None)
                
        except Exception as e:
            self.logger.error(f"즐겨찾기 토글 실패 (ID={word_id}): {e}", exc_info=True)
            return (False, "즐겨찾기 변경 중 오류가 발생했습니다.", None)
    
    # === CSV 임포트/엑스포트 ===
    
    def import_from_csv(self, file_path, skip_duplicates=True):
        """
        CSV 임포트
        
        Args:
            file_path (str): CSV 파일 경로
            skip_duplicates (bool): 중복 단어 건너뛰기
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 통계)
            통계 = {'success': 18, 'duplicate': 2, 'error': 0}
        """
        try:
            # 1. CSV 파일 읽기
            words_data = read_csv(file_path)
            
            if words_data is None:
                return (False, "CSV 파일을 읽을 수 없습니다.", None)
            
            if not words_data:
                return (False, "CSV 파일이 비어있습니다.", None)
            
            # 2. 통계 초기화
            stats = {
                'success': 0,
                'duplicate': 0,
                'error': 0
            }
            
            # 3. 단어별로 임포트
            for word_data in words_data:
                english = word_data.get('english', '').strip()
                korean = word_data.get('korean', '').strip()
                memo = word_data.get('memo', '').strip() or None
                
                # 검증
                is_valid, error_msg = validate_word(english, korean, memo)
                if not is_valid:
                    self.logger.warning(f"CSV 단어 검증 실패: {english} - {error_msg}")
                    stats['error'] += 1
                    continue
                
                # 중복 체크
                existing = self.word_model.get_word_by_english(english)
                if existing:
                    if skip_duplicates:
                        self.logger.debug(f"중복 단어 건너뜀: {english}")
                        stats['duplicate'] += 1
                        continue
                    else:
                        # 중복이어도 추가 시도 (실패할 것임)
                        pass
                
                # 단어 추가
                word_id = self.word_model.add_word(english, korean, memo)
                if word_id:
                    # 통계 초기화
                    self.statistics_model.initialize_word_statistics(word_id)
                    stats['success'] += 1
                else:
                    stats['error'] += 1
            
            # 4. 결과 메시지 생성
            total = stats['success'] + stats['duplicate'] + stats['error']
            message = f"CSV 임포트 완료: 성공 {stats['success']}개"
            
            if stats['duplicate'] > 0:
                message += f", 중복 {stats['duplicate']}개"
            if stats['error'] > 0:
                message += f", 오류 {stats['error']}개"
            
            self.logger.info(
                f"CSV 임포트: {file_path} - "
                f"성공 {stats['success']}/{total}"
            )
            
            if stats['success'] > 0:
                return (True, message, stats)
            else:
                return (False, "임포트된 단어가 없습니다.", stats)
                
        except Exception as e:
            self.logger.error(f"CSV 임포트 실패 ({file_path}): {e}", exc_info=True)
            return (False, "CSV 임포트 중 오류가 발생했습니다.", None)
    
    def export_to_csv(self, file_path, word_ids=None):
        """
        CSV 엑스포트
        
        Args:
            file_path (str): CSV 파일 경로
            word_ids (List[int], optional): 특정 단어만 내보내기 (None이면 전체)
        
        Returns:
            Tuple[bool, str]: (성공여부, 메시지)
        """
        try:
            # 1. 단어 목록 가져오기
            if word_ids:
                words = []
                for word_id in word_ids:
                    word = self.word_model.get_word_by_id(word_id)
                    if word:
                        words.append(word)
            else:
                words = self.word_model.get_all_words()
            
            if not words:
                return (False, "내보낼 단어가 없습니다.")
            
            # 2. CSV 데이터 준비
            csv_data = []
            for word in words:
                csv_data.append({
                    'english': word['english'],
                    'korean': word['korean'],
                    'memo': word['memo'] or ''
                })
            
            # 3. CSV 파일 쓰기
            success = write_csv(file_path, csv_data)
            
            if success:
                self.logger.info(f"CSV 엑스포트 완료: {file_path} - {len(words)}개")
                return (True, f"{len(words)}개 단어가 내보내기 되었습니다.")
            else:
                self.logger.error(f"CSV 엑스포트 실패: {file_path}")
                return (False, "CSV 파일 쓰기에 실패했습니다.")
                
        except Exception as e:
            self.logger.error(f"CSV 엑스포트 실패 ({file_path}): {e}", exc_info=True)
            return (False, "CSV 엑스포트 중 오류가 발생했습니다.")
    
    # === 통계 조회 ===
    
    def get_word_count(self, filter_favorite=False):
        """
        단어 수 조회
        
        Args:
            filter_favorite (bool): 즐겨찾기만 카운트
        
        Returns:
            Tuple[bool, str, int]: (성공여부, 메시지, 단어 수)
        """
        try:
            if filter_favorite:
                words = self.word_model.get_favorite_words()
            else:
                words = self.word_model.get_all_words()
            
            count = len(words)
            return (True, f"단어 수: {count}개", count)
            
        except Exception as e:
            self.logger.error(f"단어 수 조회 실패: {e}", exc_info=True)
            return (False, "단어 수 조회 중 오류가 발생했습니다.", 0)