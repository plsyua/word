# 2025-10-20 - 스마트 단어장 - 데이터베이스 연결 관리
# 파일 위치: C:\dev\word\database\db_connection.py - v1.0

"""
SQLite 데이터베이스 연결 관리 (Singleton 패턴)
- 단일 연결 보장
- 최초 실행 시 스키마 자동 생성
- 트랜잭션 관리
"""

import sqlite3
import os
import sys

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import config
from utils.logger import get_logger

logger = get_logger(__name__)


class DBConnection:
    """
    데이터베이스 연결 관리 클래스 (Singleton)
    """
    _instance = None
    _connection = None
    
    def __new__(cls):
        """
        Singleton 패턴 구현
        """
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        최초 한번만 초기화
        """
        if self._connection is None:
            self._initialize_database()
    
    def _initialize_database(self):
        """
        데이터베이스 초기화
        - DB 파일이 없으면 생성
        - 스키마 및 초기 데이터 실행
        """
        try:
            # resources 디렉토리 생성
            db_dir = os.path.dirname(config.DATABASE_PATH)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logger.info(f"데이터베이스 디렉토리 생성: {db_dir}")
            
            # DB 파일 존재 여부 확인
            db_exists = os.path.exists(config.DATABASE_PATH)
            
            # 데이터베이스 연결
            self._connection = sqlite3.connect(
                config.DATABASE_PATH,
                timeout=config.DB_TIMEOUT,
                check_same_thread=config.DB_CHECK_SAME_THREAD,
                isolation_level=config.DB_ISOLATION_LEVEL
            )
            
            # Row를 dict처럼 사용 가능하도록 설정
            self._connection.row_factory = sqlite3.Row
            
            # 외래키 제약조건 활성화
            self._connection.execute("PRAGMA foreign_keys = ON")
            
            logger.info(f"데이터베이스 연결 성공: {config.DATABASE_PATH}")
            
            # 최초 실행 시 스키마 및 초기 데이터 생성
            if not db_exists:
                logger.info("최초 실행 감지 - 스키마 생성 시작")
                self._create_schema()
                self._insert_initial_data()
                logger.info("데이터베이스 초기화 완료")
            
        except sqlite3.Error as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def _create_schema(self):
        """
        스키마 생성 (schema.sql 실행)
        """
        schema_file = os.path.join(
            os.path.dirname(__file__),
            'schema.sql'
        )
        
        if not os.path.exists(schema_file):
            logger.error(f"schema.sql 파일을 찾을 수 없습니다: {schema_file}")
            raise FileNotFoundError(f"schema.sql not found: {schema_file}")
        
        self.execute_script(schema_file)
        logger.info("스키마 생성 완료")
    
    def _insert_initial_data(self):
        """
        초기 데이터 삽입 (init_data.sql 실행)
        """
        init_file = os.path.join(
            os.path.dirname(__file__),
            'init_data.sql'
        )
        
        if not os.path.exists(init_file):
            logger.warning(f"init_data.sql 파일을 찾을 수 없습니다: {init_file}")
            return
        
        self.execute_script(init_file)
        logger.info("초기 데이터 삽입 완료")
    
    def get_connection(self):
        """
        데이터베이스 연결 객체 반환
        
        Returns:
            sqlite3.Connection: 연결 객체
        """
        if self._connection is None:
            self._initialize_database()
        return self._connection
    
    def execute_script(self, sql_file_path):
        """
        SQL 스크립트 파일 실행
        
        Args:
            sql_file_path (str): SQL 파일 경로
        
        Returns:
            bool: 성공 여부
        """
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            cursor = self._connection.cursor()
            cursor.executescript(sql_script)
            self._connection.commit()
            
            logger.info(f"SQL 스크립트 실행 완료: {sql_file_path}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"SQL 스크립트 실행 실패: {e}")
            return False
        except IOError as e:
            logger.error(f"파일 읽기 실패: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """
        SELECT 쿼리 실행
        
        Args:
            query (str): SQL 쿼리
            params (tuple, optional): 파라미터
        
        Returns:
            list: 결과 행 리스트 (dict 형태)
        """
        try:
            cursor = self._connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Row 객체를 dict로 변환
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            
            if config.SHOW_SQL_QUERIES:
                logger.debug(f"Query: {query}, Params: {params}, Rows: {len(result)}")
            
            return result
            
        except sqlite3.Error as e:
            logger.error(f"쿼리 실행 실패: {e}\nQuery: {query}\nParams: {params}")
            return []
    
    def execute_update(self, query, params=None):
        """
        INSERT/UPDATE/DELETE 쿼리 실행
        
        Args:
            query (str): SQL 쿼리
            params (tuple, optional): 파라미터
        
        Returns:
            int: lastrowid (INSERT) 또는 rowcount (UPDATE/DELETE)
        """
        try:
            cursor = self._connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self._connection.commit()
            
            # INSERT의 경우 lastrowid, 나머지는 rowcount
            result = cursor.lastrowid if cursor.lastrowid > 0 else cursor.rowcount
            
            if config.SHOW_SQL_QUERIES:
                logger.debug(f"Update: {query}, Params: {params}, Result: {result}")
            
            return result
            
        except sqlite3.Error as e:
            logger.error(f"업데이트 실행 실패: {e}\nQuery: {query}\nParams: {params}")
            self._connection.rollback()
            return None
    
    def execute_many(self, query, params_list):
        """
        여러 행 일괄 처리
        
        Args:
            query (str): SQL 쿼리
            params_list (list): 파라미터 리스트
        
        Returns:
            int: 처리된 행 수
        """
        try:
            cursor = self._connection.cursor()
            cursor.executemany(query, params_list)
            self._connection.commit()
            
            logger.debug(f"Batch update: {cursor.rowcount} rows affected")
            return cursor.rowcount
            
        except sqlite3.Error as e:
            logger.error(f"일괄 처리 실패: {e}\nQuery: {query}")
            self._connection.rollback()
            return 0
    
    def begin_transaction(self):
        """
        트랜잭션 시작
        """
        try:
            self._connection.execute("BEGIN")
            logger.debug("트랜잭션 시작")
        except sqlite3.Error as e:
            logger.error(f"트랜잭션 시작 실패: {e}")
    
    def commit(self):
        """
        트랜잭션 커밋
        """
        try:
            self._connection.commit()
            logger.debug("트랜잭션 커밋")
        except sqlite3.Error as e:
            logger.error(f"커밋 실패: {e}")
            raise
    
    def rollback(self):
        """
        트랜잭션 롤백
        """
        try:
            self._connection.rollback()
            logger.debug("트랜잭션 롤백")
        except sqlite3.Error as e:
            logger.error(f"롤백 실패: {e}")
    
    def close(self):
        """
        데이터베이스 연결 종료
        """
        if self._connection:
            try:
                self._connection.close()
                logger.info("데이터베이스 연결 종료")
                self._connection = None
            except sqlite3.Error as e:
                logger.error(f"연결 종료 실패: {e}")
    
    def get_table_names(self):
        """
        데이터베이스의 모든 테이블 이름 조회
        
        Returns:
            list: 테이블 이름 리스트
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        result = self.execute_query(query)
        return [row['name'] for row in result]
    
    def table_exists(self, table_name):
        """
        테이블 존재 여부 확인
        
        Args:
            table_name (str): 테이블 이름
        
        Returns:
            bool: 존재 여부
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute_query(query, (table_name,))
        return len(result) > 0


# Singleton 인스턴스 가져오기 함수
def get_db_connection():
    """
    DBConnection 싱글톤 인스턴스 반환
    
    Returns:
        DBConnection: 데이터베이스 연결 관리 객체
    """
    return DBConnection()


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("데이터베이스 연결 테스트")
    print("=" * 50)
    
    try:
        # 연결 생성
        db = get_db_connection()
        print(f"\n✓ 데이터베이스 연결 성공")
        print(f"  경로: {config.DATABASE_PATH}")
        
        # 테이블 목록 조회
        tables = db.get_table_names()
        print(f"\n✓ 테이블 목록 ({len(tables)}개):")
        for table in tables:
            print(f"  - {table}")
        
        # 간단한 쿼리 테스트
        if db.table_exists('user_settings'):
            result = db.execute_query("SELECT COUNT(*) as count FROM user_settings")
            print(f"\n✓ user_settings 테이블: {result[0]['count']}개 행")
        
        print("\n" + "=" * 50)
        print("데이터베이스 연결 테스트 완료")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {e}")