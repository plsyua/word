# 2025-10-20 - 스마트 단어장 - 베이스 모델
# 파일 위치: C:\dev\word\models\base_model.py - v1.0

"""
모든 Model 클래스의 기반 클래스
- DBConnection 인스턴스 참조
- 공통 DB 연산 메서드
- 에러 처리 및 로깅
- 트랜잭션 관리
"""

import sqlite3
import sys
import os

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.db_connection import get_db_connection
from utils.logger import get_logger


class BaseModel:
    """
    모든 Model 클래스의 기반 클래스
    공통 데이터베이스 연산 제공
    """
    
    def __init__(self):
        """
        초기화
        - DBConnection 싱글톤 인스턴스 참조
        - 로거 초기화
        """
        self.db = get_db_connection()
        self.logger = get_logger(self.__class__.__name__)
    
    def execute_query(self, query, params=None):
        """
        SELECT 쿼리 실행
        
        Args:
            query (str): SQL 쿼리
            params (tuple, optional): 쿼리 파라미터
        
        Returns:
            list: 결과 행 리스트 (dict 형태)
                  오류 시 빈 리스트 반환
        """
        try:
            result = self.db.execute_query(query, params)
            return result
        except Exception as e:
            self.logger.error(f"쿼리 실행 오류: {e}\nQuery: {query}\nParams: {params}")
            return []
    
    def execute_update(self, query, params=None):
        """
        INSERT/UPDATE/DELETE 쿼리 실행
        
        Args:
            query (str): SQL 쿼리
            params (tuple, optional): 쿼리 파라미터
        
        Returns:
            int: lastrowid (INSERT) 또는 rowcount (UPDATE/DELETE)
                 오류 시 None 반환
        """
        try:
            result = self.db.execute_update(query, params)
            return result
        except Exception as e:
            self.logger.error(f"업데이트 실행 오류: {e}\nQuery: {query}\nParams: {params}")
            return None
    
    def execute_many(self, query, params_list):
        """
        여러 행 일괄 처리
        
        Args:
            query (str): SQL 쿼리
            params_list (list): 파라미터 리스트
        
        Returns:
            int: 처리된 행 수
                 오류 시 0 반환
        """
        try:
            result = self.db.execute_many(query, params_list)
            return result
        except Exception as e:
            self.logger.error(f"일괄 처리 오류: {e}\nQuery: {query}")
            return 0
    
    def begin_transaction(self):
        """
        트랜잭션 시작
        """
        try:
            self.db.begin_transaction()
        except Exception as e:
            self.logger.error(f"트랜잭션 시작 오류: {e}")
            raise
    
    def commit(self):
        """
        트랜잭션 커밋
        """
        try:
            self.db.commit()
        except Exception as e:
            self.logger.error(f"커밋 오류: {e}")
            raise
    
    def rollback(self):
        """
        트랜잭션 롤백
        """
        try:
            self.db.rollback()
        except Exception as e:
            self.logger.error(f"롤백 오류: {e}")
    
    def get_by_id(self, table_name, id_column, id_value):
        """
        ID로 단일 행 조회 (공통 메서드)
        
        Args:
            table_name (str): 테이블 이름
            id_column (str): ID 컬럼 이름
            id_value: ID 값
        
        Returns:
            dict: 조회 결과 (없으면 None)
        """
        query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
        result = self.execute_query(query, (id_value,))
        return result[0] if result else None
    
    def exists(self, table_name, id_column, id_value):
        """
        레코드 존재 여부 확인
        
        Args:
            table_name (str): 테이블 이름
            id_column (str): ID 컬럼 이름
            id_value: ID 값
        
        Returns:
            bool: 존재 여부
        """
        query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {id_column} = ?"
        result = self.execute_query(query, (id_value,))
        return result[0]['count'] > 0 if result else False
    
    def delete_by_id(self, table_name, id_column, id_value):
        """
        ID로 행 삭제 (공통 메서드)
        
        Args:
            table_name (str): 테이블 이름
            id_column (str): ID 컬럼 이름
            id_value: ID 값
        
        Returns:
            bool: 삭제 성공 여부
        """
        query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
        result = self.execute_update(query, (id_value,))
        
        if result is not None and result > 0:
            self.logger.info(f"{table_name} 삭제 완료: {id_column}={id_value}")
            return True
        else:
            self.logger.warning(f"{table_name} 삭제 실패: {id_column}={id_value} (존재하지 않음)")
            return False
    
    def get_count(self, table_name, condition=None, params=None):
        """
        테이블 행 수 조회
        
        Args:
            table_name (str): 테이블 이름
            condition (str, optional): WHERE 조건
            params (tuple, optional): 조건 파라미터
        
        Returns:
            int: 행 수
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        
        result = self.execute_query(query, params)
        return result[0]['count'] if result else 0
    
    def table_exists(self, table_name):
        """
        테이블 존재 여부 확인
        
        Args:
            table_name (str): 테이블 이름
        
        Returns:
            bool: 존재 여부
        """
        return self.db.table_exists(table_name)
    
    def _build_update_query(self, table_name, id_column, id_value, **kwargs):
        """
        UPDATE 쿼리 빌더 (내부 헬퍼 메서드)
        
        Args:
            table_name (str): 테이블 이름
            id_column (str): ID 컬럼 이름
            id_value: ID 값
            **kwargs: 업데이트할 컬럼=값 쌍
        
        Returns:
            tuple: (query, params)
        """
        if not kwargs:
            return None, None
        
        # SET 절 구성
        set_clauses = []
        params = []
        
        for column, value in kwargs.items():
            set_clauses.append(f"{column} = ?")
            params.append(value)
        
        # WHERE 절 파라미터 추가
        params.append(id_value)
        
        query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {id_column} = ?"
        
        return query, tuple(params)
    
    def _dict_to_row(self, data_dict, columns):
        """
        딕셔너리를 지정된 컬럼 순서의 튜플로 변환 (내부 헬퍼 메서드)
        
        Args:
            data_dict (dict): 데이터 딕셔너리
            columns (list): 컬럼 순서 리스트
        
        Returns:
            tuple: 값 튜플
        """
        return tuple(data_dict.get(col) for col in columns)


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("BaseModel 테스트")
    print("=" * 50)
    
    # BaseModel 인스턴스 생성
    base = BaseModel()
    
    # 테이블 존재 확인
    print("\n[테이블 존재 확인]")
    tables = ['words', 'user_settings', 'learning_sessions']
    for table in tables:
        exists = base.table_exists(table)
        status = "✓" if exists else "✗"
        print(f"{status} {table}: {'존재' if exists else '없음'}")
    
    # 행 수 조회
    print("\n[행 수 조회]")
    if base.table_exists('user_settings'):
        count = base.get_count('user_settings')
        print(f"✓ user_settings: {count}개 행")
    
    # ID로 조회
    print("\n[ID로 조회]")
    if base.table_exists('user_settings'):
        result = base.get_by_id('user_settings', 'setting_id', 1)
        if result:
            print(f"✓ setting_id=1: {result['setting_key']} = {result['setting_value']}")
        else:
            print("✗ setting_id=1 없음")
    
    # 존재 여부 확인
    print("\n[존재 여부 확인]")
    if base.table_exists('user_settings'):
        exists = base.exists('user_settings', 'setting_id', 1)
        print(f"✓ setting_id=1 존재 여부: {exists}")
    
    # UPDATE 쿼리 빌더 테스트
    print("\n[UPDATE 쿼리 빌더]")
    query, params = base._build_update_query(
        'words', 'word_id', 1,
        english='test',
        korean='테스트',
        memo='업데이트 테스트'
    )
    if query:
        print(f"✓ Query: {query}")
        print(f"  Params: {params}")
    
    print("\n" + "=" * 50)
    print("BaseModel 테스트 완료")
    print("=" * 50)