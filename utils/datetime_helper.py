# 2025-10-20 - 스마트 단어장 - 날짜/시간 유틸리티
# 파일 위치: C:\dev\word\utils\datetime_helper.py - v1.0

"""
날짜/시간 관련 유틸리티 함수
SQLite는 TEXT로 날짜를 저장하므로 ISO 8601 형식 사용
"""

from datetime import datetime, timedelta
import config


def get_current_datetime():
    """
    현재 시간을 ISO 8601 형식으로 반환
    
    Returns:
        str: 현재 시간 문자열 (예: '2025-10-20T14:30:00')
    """
    return datetime.now().strftime(config.ISO8601_FORMAT)


def parse_datetime(datetime_str):
    """
    ISO 8601 문자열을 datetime 객체로 변환
    
    Args:
        datetime_str (str): ISO 8601 형식 문자열
    
    Returns:
        datetime: datetime 객체 또는 None (파싱 실패 시)
    """
    if not datetime_str:
        return None
    
    try:
        return datetime.strptime(datetime_str, config.ISO8601_FORMAT)
    except ValueError:
        try:
            # 초 단위까지만 있는 경우 처리
            return datetime.fromisoformat(datetime_str)
        except ValueError:
            return None


def format_datetime(dt, format_type='full'):
    """
    datetime 객체를 포맷팅된 문자열로 변환
    
    Args:
        dt (datetime): datetime 객체
        format_type (str): 포맷 타입
            - 'full': '2025-10-20 14:30:00'
            - 'date': '2025-10-20'
            - 'time': '14:30:00'
            - 'short': '10-20 14:30'
            - 'iso': '2025-10-20T14:30:00'
    
    Returns:
        str: 포맷팅된 문자열
    """
    if dt is None:
        return ""
    
    if isinstance(dt, str):
        dt = parse_datetime(dt)
        if dt is None:
            return ""
    
    format_map = {
        'full': config.DATETIME_FORMAT,
        'date': config.DATE_FORMAT,
        'time': config.TIME_FORMAT,
        'short': '%m-%d %H:%M',
        'iso': config.ISO8601_FORMAT
    }
    
    format_str = format_map.get(format_type, config.DATETIME_FORMAT)
    return dt.strftime(format_str)


def get_date_range(days=7, end_date=None):
    """
    최근 N일 날짜 범위 반환
    
    Args:
        days (int): 일수 (기본값: 7)
        end_date (datetime, optional): 종료 날짜. None이면 오늘
    
    Returns:
        tuple: (start_date, end_date) - ISO 8601 형식 문자열
    """
    if end_date is None:
        end_date = datetime.now()
    elif isinstance(end_date, str):
        end_date = parse_datetime(end_date)
    
    start_date = end_date - timedelta(days=days - 1)
    
    return (
        start_date.strftime(config.ISO8601_FORMAT),
        end_date.strftime(config.ISO8601_FORMAT)
    )


def calculate_days_between(date1, date2):
    """
    두 날짜 간 일수 차이 계산
    
    Args:
        date1 (str or datetime): 첫 번째 날짜
        date2 (str or datetime): 두 번째 날짜
    
    Returns:
        int: 일수 차이 (절댓값)
    """
    if isinstance(date1, str):
        date1 = parse_datetime(date1)
    if isinstance(date2, str):
        date2 = parse_datetime(date2)
    
    if date1 is None or date2 is None:
        return 0
    
    delta = abs((date2 - date1).days)
    return delta


def get_today_start_end():
    """
    오늘의 시작/종료 시간 반환
    
    Returns:
        tuple: (start, end) - ISO 8601 형식 문자열
            - start: 오늘 00:00:00
            - end: 오늘 23:59:59
    """
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    
    return (
        start.strftime(config.ISO8601_FORMAT),
        end.strftime(config.ISO8601_FORMAT)
    )


def get_week_start_end(week_offset=0):
    """
    특정 주의 시작/종료 날짜 반환 (월요일 시작)
    
    Args:
        week_offset (int): 주 오프셋 (0: 이번주, -1: 지난주, 1: 다음주)
    
    Returns:
        tuple: (start, end) - ISO 8601 형식 문자열
    """
    today = datetime.now()
    
    # 이번 주 월요일
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    
    # 오프셋 적용
    target_monday = monday + timedelta(weeks=week_offset)
    target_sunday = target_monday + timedelta(days=6)
    
    # 시작: 월요일 00:00:00, 종료: 일요일 23:59:59
    start = datetime.combine(target_monday.date(), datetime.min.time())
    end = datetime.combine(target_sunday.date(), datetime.max.time())
    
    return (
        start.strftime(config.ISO8601_FORMAT),
        end.strftime(config.ISO8601_FORMAT)
    )


def is_today(datetime_str):
    """
    주어진 날짜가 오늘인지 확인
    
    Args:
        datetime_str (str): ISO 8601 형식 문자열
    
    Returns:
        bool: 오늘이면 True
    """
    if not datetime_str:
        return False
    
    dt = parse_datetime(datetime_str)
    if dt is None:
        return False
    
    return dt.date() == datetime.now().date()


def get_relative_time_string(datetime_str):
    """
    상대적 시간 문자열 반환 (예: '2시간 전', '3일 전')
    
    Args:
        datetime_str (str): ISO 8601 형식 문자열
    
    Returns:
        str: 상대적 시간 문자열
    """
    if not datetime_str:
        return "알 수 없음"
    
    dt = parse_datetime(datetime_str)
    if dt is None:
        return "알 수 없음"
    
    now = datetime.now()
    delta = now - dt
    
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return "방금 전"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}분 전"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}시간 전"
    elif seconds < 2592000:  # 30일
        days = int(seconds / 86400)
        return f"{days}일 전"
    elif seconds < 31536000:  # 365일
        months = int(seconds / 2592000)
        return f"{months}개월 전"
    else:
        years = int(seconds / 31536000)
        return f"{years}년 전"


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("날짜/시간 유틸리티 테스트")
    print("=" * 50)
    
    # 현재 시간
    now = get_current_datetime()
    print(f"\n현재 시간 (ISO 8601): {now}")
    
    # 파싱
    dt = parse_datetime(now)
    print(f"파싱 결과: {dt}")
    
    # 포맷팅
    print(f"\nFull: {format_datetime(dt, 'full')}")
    print(f"Date: {format_datetime(dt, 'date')}")
    print(f"Time: {format_datetime(dt, 'time')}")
    print(f"Short: {format_datetime(dt, 'short')}")
    
    # 날짜 범위
    start, end = get_date_range(7)
    print(f"\n최근 7일: {start} ~ {end}")
    
    # 오늘 범위
    today_start, today_end = get_today_start_end()
    print(f"오늘: {today_start} ~ {today_end}")
    
    # 이번 주 범위
    week_start, week_end = get_week_start_end()
    print(f"이번 주: {week_start} ~ {week_end}")
    
    # 상대 시간
    past_time = "2025-10-19T10:00:00"
    rel_time = get_relative_time_string(past_time)
    print(f"\n{past_time} → {rel_time}")
    
    print("\n" + "=" * 50)