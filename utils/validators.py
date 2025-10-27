# 2025-10-20 - 스마트 단어장 - 입력 검증
# 파일 위치: C:\dev\word\utils\validators.py - v1.0

"""
사용자 입력 데이터 검증
- 단어 입력 검증
- 숫자 범위 검증
- 설정값 검증
"""

import sys
import os
# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import config


def validate_word(english, korean, memo=None):
    """
    단어 입력 검증
    
    Args:
        english (str): 영어 단어
        korean (str): 한국어 뜻
        memo (str, optional): 메모
    
    Returns:
        tuple: (bool, error_message)
            - (True, None): 검증 성공
            - (False, "오류 메시지"): 검증 실패
    """
    # 영어 단어 검증
    if not english or not english.strip():
        return (False, "영어 단어를 입력해주세요")
    
    english = english.strip()
    if len(english) > config.MAX_ENGLISH_LENGTH:
        return (False, f"영어 단어는 최대 {config.MAX_ENGLISH_LENGTH}자까지 입력 가능합니다")
    
    # 한국어 뜻 검증
    if not korean or not korean.strip():
        return (False, "한국어 뜻을 입력해주세요")
    
    korean = korean.strip()
    if len(korean) > config.MAX_KOREAN_LENGTH:
        return (False, f"한국어 뜻은 최대 {config.MAX_KOREAN_LENGTH}자까지 입력 가능합니다")
    
    # 메모 검증 (선택사항)
    if memo and len(memo) > config.MAX_MEMO_LENGTH:
        return (False, f"메모는 최대 {config.MAX_MEMO_LENGTH}자까지 입력 가능합니다")
    
    return (True, None)


def validate_positive_integer(value, min_val=1, max_val=None, field_name="값"):
    """
    양의 정수 검증
    
    Args:
        value: 검증할 값
        min_val (int): 최소값
        max_val (int, optional): 최대값
        field_name (str): 필드 이름 (오류 메시지용)
    
    Returns:
        tuple: (bool, error_message)
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        return (False, f"{field_name}은(는) 숫자여야 합니다")
    
    if int_value < min_val:
        return (False, f"{field_name}은(는) {min_val} 이상이어야 합니다")
    
    if max_val is not None and int_value > max_val:
        return (False, f"{field_name}은(는) {max_val} 이하여야 합니다")
    
    return (True, None)


def validate_percentage(value, field_name="백분율"):
    """
    백분율 검증 (0-100)
    
    Args:
        value: 검증할 값
        field_name (str): 필드 이름
    
    Returns:
        tuple: (bool, error_message)
    """
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        return (False, f"{field_name}은(는) 숫자여야 합니다")
    
    if float_value < 0 or float_value > 100:
        return (False, f"{field_name}은(는) 0-100 사이여야 합니다")
    
    return (True, None)


def validate_setting_value(key, value, setting_type):
    """
    설정 값 검증
    
    Args:
        key (str): 설정 키
        value: 설정 값
        setting_type (str): 'string', 'integer', 'boolean', 'float'
    
    Returns:
        tuple: (bool, error_message)
    """
    if setting_type == 'integer':
        try:
            int(value)
            return (True, None)
        except (ValueError, TypeError):
            return (False, f"{key} 값은 정수여야 합니다")
    
    elif setting_type == 'float':
        try:
            float(value)
            return (True, None)
        except (ValueError, TypeError):
            return (False, f"{key} 값은 실수여야 합니다")
    
    elif setting_type == 'boolean':
        if value.lower() not in ('true', 'false', '1', '0'):
            return (False, f"{key} 값은 true/false 또는 1/0 이어야 합니다")
        return (True, None)
    
    elif setting_type == 'string':
        if not isinstance(value, str):
            return (False, f"{key} 값은 문자열이어야 합니다")
        return (True, None)
    
    return (False, f"알 수 없는 설정 타입: {setting_type}")


def sanitize_string(text, max_length=None):
    """
    문자열 정제 (앞뒤 공백 제거, 길이 제한)
    
    Args:
        text (str): 원본 문자열
        max_length (int, optional): 최대 길이
    
    Returns:
        str: 정제된 문자열
    """
    if text is None:
        return ""
    
    text = str(text).strip()
    
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_exam_settings(exam_type, question_mode, total_questions, time_limit=None):
    """
    시험 설정 검증
    
    Args:
        exam_type (str): 'short_answer' or 'multiple_choice'
        question_mode (str): 'en_to_ko', 'ko_to_en', 'mixed'
        total_questions (int): 총 문항 수
        time_limit (int, optional): 제한 시간 (초)
    
    Returns:
        tuple: (bool, error_message)
    """
    # 시험 유형 검증
    if exam_type not in ('short_answer', 'multiple_choice'):
        return (False, "시험 유형은 'short_answer' 또는 'multiple_choice'여야 합니다")
    
    # 출제 모드 검증
    if question_mode not in ('en_to_ko', 'ko_to_en', 'mixed'):
        return (False, "출제 모드는 'en_to_ko', 'ko_to_en', 'mixed' 중 하나여야 합니다")
    
    # 문항 수 검증
    is_valid, error_msg = validate_positive_integer(
        total_questions, 
        min_val=config.MIN_EXAM_QUESTIONS,
        max_val=config.MAX_EXAM_QUESTIONS,
        field_name="문항 수"
    )
    if not is_valid:
        return (False, error_msg)
    
    # 제한 시간 검증 (선택사항)
    if time_limit is not None and time_limit > 0:
        is_valid, error_msg = validate_positive_integer(
            time_limit,
            min_val=1,
            field_name="제한 시간"
        )
        if not is_valid:
            return (False, error_msg)
    
    return (True, None)


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("입력 검증 테스트")
    print("=" * 50)
    
    # 단어 검증 테스트
    print("\n[단어 검증]")
    test_cases = [
        ("apple", "사과", None, True),
        ("", "사과", None, False),
        ("a" * 101, "사과", None, False),
        ("book", "", None, False),
        ("book", "책", "a" * 501, False),
        ("computer", "컴퓨터", "IT 관련", True),
    ]
    
    for english, korean, memo, expected in test_cases:
        is_valid, error = validate_word(english, korean, memo)
        status = "✓" if is_valid == expected else "✗"
        print(f"{status} validate_word('{english[:20]}', '{korean[:20]}', {memo is not None})")
        if error:
            print(f"  → {error}")
    
    # 정수 검증 테스트
    print("\n[정수 검증]")
    print(f"✓ validate_positive_integer(10, 1, 20): {validate_positive_integer(10, 1, 20)}")
    print(f"✗ validate_positive_integer(0, 1, 20): {validate_positive_integer(0, 1, 20)}")
    print(f"✗ validate_positive_integer('abc', 1, 20): {validate_positive_integer('abc', 1, 20)}")
    
    # 백분율 검증 테스트
    print("\n[백분율 검증]")
    print(f"✓ validate_percentage(75.5): {validate_percentage(75.5)}")
    print(f"✗ validate_percentage(150): {validate_percentage(150)}")
    
    # 시험 설정 검증 테스트
    print("\n[시험 설정 검증]")
    print(f"✓ validate_exam_settings('short_answer', 'en_to_ko', 20): {validate_exam_settings('short_answer', 'en_to_ko', 20)}")
    print(f"✗ validate_exam_settings('invalid', 'en_to_ko', 20): {validate_exam_settings('invalid', 'en_to_ko', 20)}")
    
    print("\n" + "=" * 50)