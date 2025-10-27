# 2025-10-20 - 스마트 단어장 - 통계 모델
# 파일 위치: C:\dev\word\models\statistics_model.py - v1.0

"""
학습 통계 관리
- 단어별 통계 조회/업데이트
- 일일/주간 통계
- 개인화 점수 계산
- 숙지도 관리
"""

import sys
import os

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.base_model import BaseModel
from utils.datetime_helper import get_current_datetime, get_today_start_end, calculate_days_between, parse_datetime
import config


class StatisticsModel(BaseModel):
    """
    통계 모델 클래스
    word_statistics 테이블 관리
    """
    
    def get_word_statistics(self, word_id):
        """
        단어별 통계 조회
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            dict: 통계 정보 또는 None
        """
        query = "SELECT * FROM word_statistics WHERE word_id = ?"
        result = self.execute_query(query, (word_id,))
        return result[0] if result else None
    
    def update_word_statistics(self, word_id, is_correct):
        """
        단어 통계 업데이트 (학습 후 호출)
        
        Args:
            word_id (int): 단어 ID
            is_correct (bool): 정답 여부
        
        Returns:
            bool: 성공 여부
        """
        # 현재 통계 조회
        stats = self.get_word_statistics(word_id)
        
        if not stats:
            # 통계가 없으면 초기화
            self.initialize_word_statistics(word_id)
            stats = self.get_word_statistics(word_id)
        
        # 통계 계산
        total_attempts = stats['total_attempts'] + 1
        
        if is_correct:
            correct_count = stats['correct_count'] + 1
            wrong_count = stats['wrong_count']
            consecutive_correct = stats['consecutive_correct'] + 1
        else:
            correct_count = stats['correct_count']
            wrong_count = stats['wrong_count'] + 1
            consecutive_correct = 0
        
        # 오답률 계산
        wrong_rate = (wrong_count / total_attempts * 100) if total_attempts > 0 else 0.0
        
        # 숙지도 자동 조정
        mastery_level = self._calculate_mastery_level(
            stats['mastery_level'],
            consecutive_correct,
            wrong_rate
        )
        
        # 업데이트
        query = """
            UPDATE word_statistics
            SET total_attempts = ?,
                correct_count = ?,
                wrong_count = ?,
                wrong_rate = ?,
                last_study_date = ?,
                mastery_level = ?,
                consecutive_correct = ?
            WHERE word_id = ?
        """
        params = (
            total_attempts,
            correct_count,
            wrong_count,
            round(wrong_rate, 2),
            get_current_datetime(),
            mastery_level,
            consecutive_correct,
            word_id
        )
        
        result = self.execute_update(query, params)
        
        if result and result > 0:
            self.logger.info(f"통계 업데이트: word_id={word_id}, 정답={is_correct}, 숙지도={mastery_level}")
            return True
        else:
            return False
    
    def initialize_word_statistics(self, word_id):
        """
        새 단어의 통계 초기화
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            bool: 성공 여부
        """
        query = """
            INSERT OR IGNORE INTO word_statistics (word_id)
            VALUES (?)
        """
        result = self.execute_update(query, (word_id,))
        
        if result:
            self.logger.info(f"통계 초기화: word_id={word_id}")
            return True
        else:
            return False
    
    def get_daily_statistics(self, date):
        """
        특정 날짜의 학습 통계
        
        Args:
            date (str): ISO 8601 형식 날짜
        
        Returns:
            dict: {'total_words': 50, 'study_time': 25, 'accuracy': 80.0, 'sessions': 3}
        """
        # 해당 날짜의 시작/종료 시간 계산
        date_obj = parse_datetime(date)
        if not date_obj:
            return None
        
        start = date_obj.replace(hour=0, minute=0, second=0).strftime(config.ISO8601_FORMAT)
        end = date_obj.replace(hour=23, minute=59, second=59).strftime(config.ISO8601_FORMAT)
        
        # 학습 세션 통계
        query = """
            SELECT 
                COUNT(*) as session_count,
                SUM(total_words) as total_words,
                SUM(correct_count) as correct_count,
                SUM(wrong_count) as wrong_count,
                AVG(accuracy_rate) as avg_accuracy
            FROM learning_sessions
            WHERE start_time >= ? AND start_time <= ?
        """
        result = self.execute_query(query, (start, end))
        
        if result and result[0]['total_words']:
            data = result[0]
            return {
                'total_words': data['total_words'] or 0,
                'correct_count': data['correct_count'] or 0,
                'wrong_count': data['wrong_count'] or 0,
                'accuracy': round(data['avg_accuracy'] or 0.0, 2),
                'sessions': data['session_count'] or 0
            }
        else:
            return {
                'total_words': 0,
                'correct_count': 0,
                'wrong_count': 0,
                'accuracy': 0.0,
                'sessions': 0
            }
    
    def get_today_statistics(self):
        """
        오늘의 학습 통계
        
        Returns:
            dict: 통계 정보
        """
        return self.get_daily_statistics(get_current_datetime())
    
    def get_weekly_statistics(self, start_date, end_date):
        """
        주간 학습 통계
        
        Args:
            start_date (str): 시작 날짜
            end_date (str): 종료 날짜
        
        Returns:
            list: 날짜별 통계 리스트
        """
        query = """
            SELECT 
                DATE(start_time) as date,
                COUNT(*) as session_count,
                SUM(total_words) as total_words,
                SUM(correct_count) as correct_count,
                AVG(accuracy_rate) as avg_accuracy
            FROM learning_sessions
            WHERE start_time >= ? AND start_time <= ?
            GROUP BY DATE(start_time)
            ORDER BY date
        """
        
        result = self.execute_query(query, (start_date, end_date))
        
        # 결과 포맷팅
        stats = []
        for row in result:
            stats.append({
                'date': row['date'],
                'total_words': row['total_words'] or 0,
                'correct_count': row['correct_count'] or 0,
                'accuracy': round(row['avg_accuracy'] or 0.0, 2),
                'sessions': row['session_count'] or 0
            })
        
        return stats
    
    def get_top_wrong_words(self, limit=20):
        """
        오답률 높은 단어 Top N
        
        Args:
            limit (int): 조회 개수
        
        Returns:
            list: 단어 정보 + 통계
        """
        query = """
            SELECT 
                w.word_id,
                w.english,
                w.korean,
                ws.wrong_rate,
                ws.wrong_count,
                ws.total_attempts,
                ws.mastery_level
            FROM word_statistics ws
            JOIN words w ON ws.word_id = w.word_id
            WHERE ws.total_attempts > 0
            ORDER BY ws.wrong_rate DESC, ws.wrong_count DESC
            LIMIT ?
        """
        
        result = self.execute_query(query, (limit,))
        self.logger.info(f"오답률 Top {limit} 조회: {len(result)}개")
        return result
    
    def get_mastery_distribution(self):
        """
        숙지도 레벨별 단어 수 분포
        
        Returns:
            dict: {0: 10, 1: 20, 2: 30, ...}
        """
        query = """
            SELECT 
                mastery_level,
                COUNT(*) as count
            FROM word_statistics
            GROUP BY mastery_level
            ORDER BY mastery_level
        """
        
        result = self.execute_query(query)
        
        # 0~5 레벨 모두 포함 (없으면 0으로)
        distribution = {i: 0 for i in range(6)}
        
        for row in result:
            level = row['mastery_level']
            if 0 <= level <= 5:
                distribution[level] = row['count']
        
        return distribution
    
    def calculate_personalization_score(self, word_id):
        """
        개인화 우선순위 점수 계산
        
        Args:
            word_id (int): 단어 ID
        
        Returns:
            float: 우선순위 점수 (높을수록 우선 출제)
        """
        stats = self.get_word_statistics(word_id)
        
        if not stats or stats['total_attempts'] == 0:
            # 미학습 단어는 중간 우선순위
            return 50.0
        
        # 마지막 학습일로부터 경과 일수
        if stats['last_study_date']:
            days_since = calculate_days_between(stats['last_study_date'], get_current_datetime())
        else:
            days_since = 999  # 매우 오래됨
        
        # 가중치 적용 점수 계산
        weights = config.PERSONALIZATION_WEIGHTS
        
        score = (
            stats['wrong_rate'] * weights['wrong_rate'] +
            min(days_since, 30) * weights['days_since_last_study'] +  # 최대 30일
            (5 - stats['mastery_level']) * 20 * weights['mastery_level'] +
            min(stats['wrong_count'], 10) * 10 * weights['wrong_count']  # 최대 10회
        )
        
        return round(score, 2)
    
    def get_personalized_word_list(self, limit=None):
        """
        개인화된 단어 목록 (우선순위 순)
        
        Args:
            limit (int, optional): 조회 개수
        
        Returns:
            list: 단어 ID 리스트 (우선순위 순)
        """
        query = """
            SELECT 
                w.word_id,
                ws.wrong_rate,
                ws.mastery_level,
                ws.wrong_count,
                ws.last_study_date,
                ws.total_attempts
            FROM words w
            LEFT JOIN word_statistics ws ON w.word_id = ws.word_id
        """
        
        words = self.execute_query(query)
        
        # 각 단어의 우선순위 점수 계산
        word_scores = []
        for word in words:
            score = self.calculate_personalization_score(word['word_id'])
            word_scores.append((word['word_id'], score))
        
        # 점수 순으로 정렬 (높은 점수 우선)
        word_scores.sort(key=lambda x: x[1], reverse=True)
        
        # word_id만 추출
        word_ids = [word_id for word_id, score in word_scores]
        
        if limit:
            word_ids = word_ids[:limit]
        
        self.logger.info(f"개인화 단어 목록: {len(word_ids)}개")
        return word_ids
    
    def _calculate_mastery_level(self, current_level, consecutive_correct, wrong_rate):
        """
        숙지도 레벨 자동 조정 (내부 메서드)
        
        Args:
            current_level (int): 현재 레벨 (0-5)
            consecutive_correct (int): 연속 정답 횟수
            wrong_rate (float): 오답률
        
        Returns:
            int: 새로운 레벨 (0-5)
        """
        new_level = current_level
        
        # 레벨 상승 조건: 연속 N회 정답
        if consecutive_correct >= config.MASTERY_LEVEL_UP_CONSECUTIVE:
            new_level = min(current_level + 1, 5)
        
        # 레벨 하락 조건: 오답률이 높은 경우
        elif wrong_rate > 50 and current_level > 0:
            new_level = max(current_level - 1, 0)
        
        return new_level


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("StatisticsModel 테스트")
    print("=" * 50)
    
    from models.word_model import WordModel
    
    model = StatisticsModel()
    word_model = WordModel()
    
    # 테스트용 단어 추가
    print("\n[테스트 단어 추가]")
    test_word_id = word_model.add_word("statistics", "통계", "테스트용")
    if test_word_id:
        print(f"✓ 테스트 단어 추가: statistics (ID: {test_word_id})")
    
    # 통계 초기화
    print("\n[통계 초기화]")
    model.initialize_word_statistics(test_word_id)
    print(f"✓ 통계 초기화 완료")
    
    # 통계 조회
    print("\n[통계 조회]")
    stats = model.get_word_statistics(test_word_id)
    if stats:
        print(f"✓ word_id={test_word_id}")
        print(f"  총 시도: {stats['total_attempts']}")
        print(f"  정답/오답: {stats['correct_count']}/{stats['wrong_count']}")
        print(f"  숙지도: {stats['mastery_level']}")
    
    # 통계 업데이트 테스트
    print("\n[통계 업데이트]")
    model.update_word_statistics(test_word_id, True)  # 정답
    model.update_word_statistics(test_word_id, True)  # 정답
    model.update_word_statistics(test_word_id, False) # 오답
    print(f"✓ 3회 학습 (정답 2, 오답 1)")
    
    stats = model.get_word_statistics(test_word_id)
    if stats:
        print(f"  총 시도: {stats['total_attempts']}")
        print(f"  오답률: {stats['wrong_rate']}%")
        print(f"  연속 정답: {stats['consecutive_correct']}")
    
    # 오늘의 통계
    print("\n[오늘의 통계]")
    today_stats = model.get_today_statistics()
    print(f"✓ 총 단어: {today_stats['total_words']}개")
    print(f"  정답률: {today_stats['accuracy']}%")
    print(f"  세션: {today_stats['sessions']}개")
    
    # 숙지도 분포
    print("\n[숙지도 분포]")
    distribution = model.get_mastery_distribution()
    for level, count in distribution.items():
        level_name = config.MASTERY_LEVELS.get(level, "알 수 없음")
        print(f"  레벨 {level} ({level_name}): {count}개")
    
    # 개인화 점수
    print("\n[개인화 점수]")
    score = model.calculate_personalization_score(test_word_id)
    print(f"✓ word_id={test_word_id} 우선순위 점수: {score}")
    
    # 테스트 단어 삭제
    print("\n[정리]")
    word_model.delete_word(test_word_id)
    print(f"✓ 테스트 단어 삭제")
    
    print("\n" + "=" * 50)
    print("StatisticsModel 테스트 완료")
    print("=" * 50)