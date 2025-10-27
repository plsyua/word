# 2025-10-20 - 스마트 단어장 - 단어 모델
# 파일 위치: C:\dev\word\models\word_model.py - v1.0

"""
단어(words 테이블) CRUD 연산
- 단어 조회/추가/수정/삭제
- 검색 및 필터링
- CSV 임포트/엑스포트
- 즐겨찾기 관리
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
from utils.validators import validate_word


class WordModel(BaseModel):
    """
    단어 모델 클래스
    words 테이블 관리
    """
    
    def get_all_words(self, filter_favorite=False, filter_unlearned=False):
        """
        전체 단어 조회
        
        Args:
            filter_favorite (bool): 즐겨찾기만 조회
            filter_unlearned (bool): 미학습 단어만 조회
        
        Returns:
            list: 단어 리스트 (통계 정보 포함)
        """
        query = """
            SELECT 
                w.*,
                COALESCE(ws.wrong_rate, 0) as wrong_rate,
                COALESCE(ws.mastery_level, 0) as mastery_level,
                ws.last_study_date
            FROM words w
            LEFT JOIN word_statistics ws ON w.word_id = ws.word_id
        """
        
        conditions = []
        params = []
        
        if filter_favorite:
            conditions.append("w.is_favorite = 1")
        
        if filter_unlearned:
            conditions.append("ws.total_attempts IS NULL OR ws.total_attempts = 0")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY w.word_id"
        
        result = self.execute_query(query, tuple(params) if params else None)
        self.logger.info(f"전체 단어 조회: {len(result)}개")
        return result
    
    def get_word_by_id(self, word_id):
        """
        단어 ID로 조회
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            dict: 단어 정보 (없으면 None)
        """
        query = """
            SELECT 
                w.*,
                COALESCE(ws.wrong_rate, 0) as wrong_rate,
                COALESCE(ws.mastery_level, 0) as mastery_level,
                ws.last_study_date
            FROM words w
            LEFT JOIN word_statistics ws ON w.word_id = ws.word_id
            WHERE w.word_id = ?
        """
        result = self.execute_query(query, (word_id,))
        return result[0] if result else None
    
    def search_words(self, keyword, search_type='all'):
        """
        단어 검색
        
        Args:
            keyword (str): 검색 키워드
            search_type (str): 'english', 'korean', 'memo', 'all'
        
        Returns:
            list: 검색 결과
        """
        if not keyword:
            return self.get_all_words()
        
        keyword_pattern = f"%{keyword}%"
        
        if search_type == 'english':
            condition = "w.english LIKE ?"
            params = (keyword_pattern,)
        elif search_type == 'korean':
            condition = "w.korean LIKE ?"
            params = (keyword_pattern,)
        elif search_type == 'memo':
            condition = "w.memo LIKE ?"
            params = (keyword_pattern,)
        else:  # 'all'
            condition = "(w.english LIKE ? OR w.korean LIKE ? OR w.memo LIKE ?)"
            params = (keyword_pattern, keyword_pattern, keyword_pattern)
        
        query = f"""
            SELECT 
                w.*,
                COALESCE(ws.wrong_rate, 0) as wrong_rate,
                COALESCE(ws.mastery_level, 0) as mastery_level,
                ws.last_study_date
            FROM words w
            LEFT JOIN word_statistics ws ON w.word_id = ws.word_id
            WHERE {condition}
            ORDER BY w.word_id
        """
        
        result = self.execute_query(query, params)
        self.logger.info(f"검색 결과: '{keyword}' - {len(result)}개")
        return result
    
    def add_word(self, english, korean, memo=None, is_favorite=0):
        """
        단어 추가
        
        Args:
            english (str): 영어 단어
            korean (str): 한국어 뜻
            memo (str, optional): 메모
            is_favorite (int): 즐겨찾기 여부 (0 or 1)
        
        Returns:
            int: 생성된 word_id (실패 시 None)
        """
        # 입력 검증
        is_valid, error_msg = validate_word(english, korean, memo)
        if not is_valid:
            self.logger.warning(f"단어 추가 검증 실패: {error_msg}")
            return None
        
        # 중복 체크
        check_query = "SELECT word_id FROM words WHERE english = ? AND korean = ?"
        existing = self.execute_query(check_query, (english.strip(), korean.strip()))
        if existing:
            self.logger.warning(f"중복 단어: {english} - {korean}")
            return None
        
        # 단어 추가
        query = """
            INSERT INTO words (english, korean, memo, is_favorite, created_date)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            english.strip(),
            korean.strip(),
            memo.strip() if memo else None,
            is_favorite,
            get_current_datetime()
        )
        
        word_id = self.execute_update(query, params)
        
        if word_id:
            self.logger.info(f"단어 추가 완료: {english} - {korean} (ID: {word_id})")
            
            # word_statistics 초기화
            self._initialize_statistics(word_id)
        
        return word_id
    
    def update_word(self, word_id, **kwargs):
        """
        단어 수정
        
        Args:
            word_id (int): 단어 ID
            **kwargs: 수정할 필드 (english, korean, memo, is_favorite)
        
        Returns:
            bool: 성공 여부
        """
        if not kwargs:
            return False
        
        # 존재 확인
        if not self.exists('words', 'word_id', word_id):
            self.logger.warning(f"단어 수정 실패: word_id={word_id} 존재하지 않음")
            return False
        
        # 입력 검증 (english, korean이 있는 경우)
        if 'english' in kwargs or 'korean' in kwargs:
            current = self.get_word_by_id(word_id)
            english = kwargs.get('english', current['english'])
            korean = kwargs.get('korean', current['korean'])
            memo = kwargs.get('memo', current.get('memo'))
            
            is_valid, error_msg = validate_word(english, korean, memo)
            if not is_valid:
                self.logger.warning(f"단어 수정 검증 실패: {error_msg}")
                return False
        
        # modified_date 자동 추가
        kwargs['modified_date'] = get_current_datetime()
        
        # UPDATE 쿼리 실행
        query, params = self._build_update_query('words', 'word_id', word_id, **kwargs)
        result = self.execute_update(query, params)
        
        if result and result > 0:
            self.logger.info(f"단어 수정 완료: word_id={word_id}")
            return True
        else:
            return False
    
    def delete_word(self, word_id):
        """
        단어 삭제 (CASCADE로 연관 데이터도 삭제)
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            bool: 성공 여부
        """
        # 단어 정보 조회 (로그용)
        word = self.get_word_by_id(word_id)
        
        result = self.delete_by_id('words', 'word_id', word_id)
        
        if result and word:
            self.logger.info(f"단어 삭제 완료: {word['english']} - {word['korean']} (ID: {word_id})")
        
        return result
    
    def toggle_favorite(self, word_id):
        """
        즐겨찾기 토글
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            int: 새로운 상태 (0 or 1), 실패 시 None
        """
        word = self.get_word_by_id(word_id)
        if not word:
            self.logger.warning(f"즐겨찾기 토글 실패: word_id={word_id} 존재하지 않음")
            return None
        
        new_state = 0 if word['is_favorite'] == 1 else 1
        
        if self.update_word(word_id, is_favorite=new_state):
            self.logger.info(f"즐겨찾기 {'추가' if new_state == 1 else '제거'}: {word['english']}")
            return new_state
        else:
            return None
    
    def import_from_csv(self, csv_data, skip_duplicates=True):
        """
        CSV 데이터 일괄 추가
        
        Args:
            csv_data (list): [{'english': '...', 'korean': '...', 'memo': '...'}, ...]
            skip_duplicates (bool): True면 중복 건너뛰기, False면 오류
        
        Returns:
            dict: {'success': 10, 'failed': 2, 'errors': [...]}
        """
        success_count = 0
        failed_count = 0
        errors = []
        
        for i, data in enumerate(csv_data, 1):
            english = data.get('english', '').strip()
            korean = data.get('korean', '').strip()
            memo = data.get('memo', '').strip() if data.get('memo') else None
            
            word_id = self.add_word(english, korean, memo)
            
            if word_id:
                success_count += 1
            else:
                failed_count += 1
                errors.append(f"행 {i}: {english} - {korean}")
                if not skip_duplicates:
                    break
        
        result = {
            'success': success_count,
            'failed': failed_count,
            'errors': errors
        }
        
        self.logger.info(f"CSV 임포트 완료: 성공 {success_count}개, 실패 {failed_count}개")
        return result
    
    def export_to_csv(self):
        """
        전체 단어 내보내기
        
        Returns:
            list: CSV 형식 데이터 [{'english': '...', 'korean': '...', 'memo': '...'}, ...]
        """
        query = "SELECT english, korean, memo FROM words ORDER BY word_id"
        result = self.execute_query(query)
        self.logger.info(f"CSV 엑스포트: {len(result)}개 단어")
        return result
    
    def get_word_count(self, filter_favorite=False):
        """
        단어 수 조회
        
        Args:
            filter_favorite (bool): 즐겨찾기만 카운트
        
        Returns:
            int: 단어 수
        """
        if filter_favorite:
            return self.get_count('words', 'is_favorite = 1')
        else:
            return self.get_count('words')
    
    def _initialize_statistics(self, word_id):
        """
        새 단어의 통계 초기화 (내부 메서드)
        
        Args:
            word_id (int): 단어 ID
        """
        query = """
            INSERT INTO word_statistics (word_id)
            VALUES (?)
        """
        self.execute_update(query, (word_id,))


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("WordModel 테스트")
    print("=" * 50)
    
    model = WordModel()
    
    # 단어 추가 테스트
    print("\n[단어 추가]")
    word_id1 = model.add_word("test", "테스트", "테스트용 단어")
    if word_id1:
        print(f"✓ 단어 추가 성공: test (ID: {word_id1})")
    
    word_id2 = model.add_word("example", "예시", None, is_favorite=1)
    if word_id2:
        print(f"✓ 단어 추가 성공: example (ID: {word_id2})")
    
    # 중복 추가 테스트
    duplicate_id = model.add_word("test", "테스트", "중복")
    if not duplicate_id:
        print("✓ 중복 단어 추가 방지")
    
    # 전체 조회
    print("\n[전체 단어 조회]")
    all_words = model.get_all_words()
    print(f"✓ 총 {len(all_words)}개 단어")
    for word in all_words[:5]:
        print(f"  - {word['english']}: {word['korean']}")
    
    # ID로 조회
    print("\n[ID로 조회]")
    if word_id1:
        word = model.get_word_by_id(word_id1)
        if word:
            print(f"✓ word_id={word_id1}: {word['english']} - {word['korean']}")
    
    # 검색
    print("\n[단어 검색]")
    results = model.search_words("test", "english")
    print(f"✓ 'test' 검색 결과: {len(results)}개")
    
    # 즐겨찾기 토글
    print("\n[즐겨찾기 토글]")
    if word_id1:
        new_state = model.toggle_favorite(word_id1)
        print(f"✓ 즐겨찾기 상태: {new_state}")
    
    # 단어 수정
    print("\n[단어 수정]")
    if word_id1:
        success = model.update_word(word_id1, memo="수정된 메모")
        print(f"✓ 단어 수정: {'성공' if success else '실패'}")
    
    # 단어 삭제
    print("\n[단어 삭제]")
    if word_id1:
        success = model.delete_word(word_id1)
        print(f"✓ 단어 삭제: {'성공' if success else '실패'}")
    if word_id2:
        model.delete_word(word_id2)
    
    print("\n" + "=" * 50)
    print("WordModel 테스트 완료")
    print("=" * 50)