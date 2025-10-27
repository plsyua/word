# 2025-10-20 - 스마트 단어장 - CSV 처리
# 파일 위치: C:\dev\word\utils\csv_handler.py - v1.0

"""
CSV 파일 임포트/엑스포트
- 단어 데이터 읽기/쓰기
- CSV 구조 검증
- 에러 처리
"""

import csv
import sys
import os
# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import config
from utils.logger import get_logger
from utils.validators import sanitize_string

logger = get_logger(__name__)


def read_csv(file_path):
    """
    CSV 파일 읽기
    
    Args:
        file_path (str): CSV 파일 경로
    
    Returns:
        list: 단어 데이터 리스트 [{'english': '...', 'korean': '...', 'memo': '...'}, ...]
              None: 읽기 실패 시
    """
    if not os.path.exists(file_path):
        logger.error(f"CSV 파일을 찾을 수 없습니다: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding=config.CSV_ENCODING, newline='') as f:
            reader = csv.DictReader(f, delimiter=config.CSV_DELIMITER)
            
            # 헤더 검증
            if not reader.fieldnames:
                logger.error("CSV 파일에 헤더가 없습니다")
                return None
            
            # 필수 컬럼 확인
            required_cols = set(config.CSV_REQUIRED_COLUMNS)
            file_cols = set(reader.fieldnames)
            
            missing_cols = required_cols - file_cols
            if missing_cols:
                logger.error(f"필수 컬럼이 누락되었습니다: {missing_cols}")
                return None
            
            # 데이터 읽기
            data = []
            for row_num, row in enumerate(reader, start=2):  # 헤더 다음 줄부터
                # 필수 컬럼 값 확인
                if not row.get('english') or not row.get('korean'):
                    logger.warning(f"행 {row_num}: 영어 또는 한국어 값이 비어있습니다. 건너뜁니다.")
                    continue
                
                # 데이터 정제
                word_data = {
                    'english': sanitize_string(row['english'], config.MAX_ENGLISH_LENGTH),
                    'korean': sanitize_string(row['korean'], config.MAX_KOREAN_LENGTH),
                    'memo': sanitize_string(row.get('memo', ''), config.MAX_MEMO_LENGTH)
                }
                
                data.append(word_data)
            
            logger.info(f"CSV 파일 읽기 완료: {len(data)}개 단어")
            return data
            
    except UnicodeDecodeError:
        logger.error(f"파일 인코딩 오류. UTF-8 형식으로 저장해주세요: {file_path}")
        return None
    except Exception as e:
        logger.error(f"CSV 파일 읽기 실패: {e}")
        return None


def write_csv(file_path, data):
    """
    CSV 파일 쓰기
    
    Args:
        file_path (str): CSV 파일 경로
        data (list): 단어 데이터 리스트 [{'english': '...', 'korean': '...', 'memo': '...'}, ...]
    
    Returns:
        bool: 성공 여부
    """
    if not data:
        logger.warning("저장할 데이터가 없습니다")
        return False
    
    try:
        # 디렉토리가 없으면 생성
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding=config.CSV_ENCODING, newline='') as f:
            # 헤더 정의
            fieldnames = ['english', 'korean', 'memo']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=config.CSV_DELIMITER)
            
            # 헤더 쓰기
            writer.writeheader()
            
            # 데이터 쓰기
            for item in data:
                row = {
                    'english': item.get('english', ''),
                    'korean': item.get('korean', ''),
                    'memo': item.get('memo', '')
                }
                writer.writerow(row)
        
        logger.info(f"CSV 파일 저장 완료: {file_path} ({len(data)}개 단어)")
        return True
        
    except Exception as e:
        logger.error(f"CSV 파일 쓰기 실패: {e}")
        return False


def validate_csv_structure(file_path, preview_lines=5):
    """
    CSV 구조 검증 및 미리보기 (임포트 전 확인용)
    
    Args:
        file_path (str): CSV 파일 경로
        preview_lines (int): 미리보기 행 수
    
    Returns:
        tuple: (bool, error_message, preview_data)
            - bool: 유효성 여부
            - error_message: 오류 메시지 (없으면 None)
            - preview_data: 미리보기 데이터 리스트
    """
    if not os.path.exists(file_path):
        return (False, "파일을 찾을 수 없습니다", [])
    
    try:
        with open(file_path, 'r', encoding=config.CSV_ENCODING, newline='') as f:
            reader = csv.DictReader(f, delimiter=config.CSV_DELIMITER)
            
            # 헤더 검증
            if not reader.fieldnames:
                return (False, "CSV 파일에 헤더가 없습니다", [])
            
            # 필수 컬럼 확인
            required_cols = set(config.CSV_REQUIRED_COLUMNS)
            file_cols = set(reader.fieldnames)
            
            missing_cols = required_cols - file_cols
            if missing_cols:
                return (False, f"필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}", [])
            
            # 미리보기 데이터 읽기
            preview_data = []
            for i, row in enumerate(reader):
                if i >= preview_lines:
                    break
                
                preview_data.append({
                    'english': row.get('english', ''),
                    'korean': row.get('korean', ''),
                    'memo': row.get('memo', '')
                })
            
            return (True, None, preview_data)
            
    except UnicodeDecodeError:
        return (False, "파일 인코딩 오류. UTF-8 형식으로 저장해주세요", [])
    except Exception as e:
        return (False, f"파일 읽기 오류: {str(e)}", [])


def parse_csv_row(row):
    """
    CSV 행 파싱 및 검증
    
    Args:
        row (dict): CSV 행 데이터
    
    Returns:
        tuple: (bool, word_data or error_message)
            - (True, word_data): 파싱 성공
            - (False, error_message): 파싱 실패
    """
    english = row.get('english', '').strip()
    korean = row.get('korean', '').strip()
    
    # 필수 값 확인
    if not english:
        return (False, "영어 단어가 비어있습니다")
    if not korean:
        return (False, "한국어 뜻이 비어있습니다")
    
    # 길이 검증
    if len(english) > config.MAX_ENGLISH_LENGTH:
        return (False, f"영어 단어가 너무 깁니다 (최대 {config.MAX_ENGLISH_LENGTH}자)")
    if len(korean) > config.MAX_KOREAN_LENGTH:
        return (False, f"한국어 뜻이 너무 깁니다 (최대 {config.MAX_KOREAN_LENGTH}자)")
    
    memo = row.get('memo', '').strip()
    if memo and len(memo) > config.MAX_MEMO_LENGTH:
        memo = memo[:config.MAX_MEMO_LENGTH]
    
    word_data = {
        'english': english,
        'korean': korean,
        'memo': memo if memo else None
    }
    
    return (True, word_data)


def count_csv_rows(file_path):
    """
    CSV 파일의 행 수 계산 (헤더 제외)
    
    Args:
        file_path (str): CSV 파일 경로
    
    Returns:
        int: 행 수 (오류 시 0)
    """
    if not os.path.exists(file_path):
        return 0
    
    try:
        with open(file_path, 'r', encoding=config.CSV_ENCODING, newline='') as f:
            reader = csv.reader(f, delimiter=config.CSV_DELIMITER)
            # 헤더 건너뛰기
            next(reader, None)
            # 행 수 계산
            return sum(1 for row in reader if any(row))  # 빈 행 제외
    except Exception as e:
        logger.error(f"행 수 계산 실패: {e}")
        return 0


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("CSV 처리 테스트")
    print("=" * 50)
    
    # 테스트 데이터 생성
    test_file = "test_words.csv"
    test_data = [
        {'english': 'apple', 'korean': '사과', 'memo': '과일 종류'},
        {'english': 'book', 'korean': '책', 'memo': ''},
        {'english': 'computer', 'korean': '컴퓨터', 'memo': 'IT 관련'},
        {'english': 'dog', 'korean': '개', 'memo': '동물'},
        {'english': 'elephant', 'korean': '코끼리', 'memo': '큰 동물'},
    ]
    
    # CSV 쓰기 테스트
    print(f"\n[CSV 쓰기 테스트]")
    if write_csv(test_file, test_data):
        print(f"✓ {test_file} 생성 완료 ({len(test_data)}개 단어)")
    else:
        print(f"✗ CSV 쓰기 실패")
    
    # CSV 구조 검증 테스트
    print(f"\n[CSV 구조 검증 테스트]")
    is_valid, error, preview = validate_csv_structure(test_file, preview_lines=3)
    if is_valid:
        print(f"✓ CSV 구조 유효")
        print(f"  미리보기 ({len(preview)}개 행):")
        for i, row in enumerate(preview, 1):
            print(f"  {i}. {row['english']} → {row['korean']}")
    else:
        print(f"✗ CSV 구조 오류: {error}")
    
    # CSV 읽기 테스트
    print(f"\n[CSV 읽기 테스트]")
    loaded_data = read_csv(test_file)
    if loaded_data:
        print(f"✓ CSV 읽기 완료 ({len(loaded_data)}개 단어)")
        for i, word in enumerate(loaded_data[:3], 1):
            print(f"  {i}. {word['english']} → {word['korean']}")
    else:
        print(f"✗ CSV 읽기 실패")
    
    # 행 수 계산 테스트
    print(f"\n[행 수 계산 테스트]")
    row_count = count_csv_rows(test_file)
    print(f"✓ 총 {row_count}개 행")
    
    # 테스트 파일 삭제
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\n✓ 테스트 파일 삭제: {test_file}")
    
    print("\n" + "=" * 50)