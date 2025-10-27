# 2025-10-20 - 스마트 단어장 - 로깅 시스템
# 파일 위치: C:\dev\word\utils\logger.py - v1.0

"""
애플리케이션 전역 로깅 시스템
- 콘솔 + 파일 로그 동시 출력
- 로그 레벨별 포매팅
- 로그 파일 로테이션
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import config


def setup_logger(name, log_file=None, level=None):
    """
    로거 설정 및 반환
    
    Args:
        name (str): 로거 이름 (일반적으로 __name__ 사용)
        log_file (str, optional): 로그 파일 경로. None이면 config.LOG_FILE 사용
        level (int, optional): 로그 레벨. None이면 config.LOG_LEVEL 사용
    
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    # 로거 생성
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있으면 반환 (중복 방지)
    if logger.handlers:
        return logger
    
    # 로그 레벨 설정
    if level is None:
        level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 포매터 생성
    formatter = logging.Formatter(
        fmt=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT
    )
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 설정
    if log_file is None:
        log_file = config.LOG_FILE
    
    # 로그 디렉토리가 없으면 생성
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로테이팅 파일 핸들러 (10MB, 5개 백업)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 상위 로거로 전파 방지 (중복 로그 방지)
    logger.propagate = False
    
    return logger


def get_logger(name):
    """
    설정된 로거 반환
    setup_logger가 호출되지 않았으면 자동으로 설정
    
    Args:
        name (str): 로거 이름
    
    Returns:
        logging.Logger: 로거 객체
    """
    logger = logging.getLogger(name)
    
    # 핸들러가 없으면 setup_logger 호출
    if not logger.handlers:
        logger = setup_logger(name)
    
    return logger


def log_exception(logger, exception, message="예외 발생"):
    """
    예외 정보를 로그에 기록
    
    Args:
        logger (logging.Logger): 로거 객체
        exception (Exception): 예외 객체
        message (str): 추가 메시지
    """
    logger.error(f"{message}: {type(exception).__name__}: {str(exception)}", exc_info=True)


# 테스트 코드 (직접 실행 시에만 동작)
if __name__ == "__main__":
    # 테스트 로거 생성
    test_logger = get_logger(__name__)
    
    print("=" * 50)
    print("로거 테스트 시작")
    print("=" * 50)
    
    # 각 레벨별 로그 테스트
    test_logger.debug("DEBUG 메시지 - 개발용 상세 정보")
    test_logger.info("INFO 메시지 - 정상 동작 정보")
    test_logger.warning("WARNING 메시지 - 경고")
    test_logger.error("ERROR 메시지 - 오류 발생")
    test_logger.critical("CRITICAL 메시지 - 치명적 오류")
    
    # 예외 로그 테스트
    try:
        result = 10 / 0
    except Exception as e:
        log_exception(test_logger, e, "테스트 예외")
    
    print("\n로그 파일 위치:", config.LOG_FILE)
    print("로거 테스트 완료")
    print("=" * 50)