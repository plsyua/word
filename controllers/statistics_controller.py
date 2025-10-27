# 2025-10-27 - 스마트 단어장 - 통계 컨트롤러
# 파일 위치: word/controllers/statistics_controller.py - v1.0

"""
통계 계산 및 분석 컨트롤러

주요 기능:
- 요약 통계 (오늘/주간)
- 학습 진척도 및 추세
- 목표 달성률 계산
- 오답 분석
- 연속 학습 일수 계산
"""

import sys
import os
from datetime import datetime, timedelta

# 프로젝트 루트를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.statistics_model import StatisticsModel
from models.learning_model import LearningModel
from models.exam_model import ExamModel
from models.settings_model import SettingsModel
from utils.logger import get_logger
from utils.datetime_helper import get_current_datetime, get_date_range

logger = get_logger(__name__)


class StatisticsController:
    """통계 컨트롤러"""
    
    def __init__(self):
        """컨트롤러 초기화"""
        self.statistics_model = StatisticsModel()
        self.learning_model = LearningModel()
        self.exam_model = ExamModel()
        self.settings_model = SettingsModel()
        self.logger = logger
    
    # === 요약 통계 ===
    
    def get_today_summary(self):
        """
        오늘의 학습 요약
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 요약 데이터)
            {
                'words_learned': 50,
                'sessions': 3,
                'accuracy': 85.0,
                'goal_achievement': 100.0,
                'streak_days': 7
            }
        """
        try:
            # 1. 오늘의 통계
            today_stats = self.statistics_model.get_today_statistics()
            
            # 2. 목표 달성률
            goal_success, goal_msg, goal_data = self.calculate_goal_achievement()
            
            # 3. 연속 학습 일수
            streak_success, streak_msg, streak_days = self.calculate_streak_days()
            
            # 4. 요약 데이터 구성
            summary = {
                'words_learned': today_stats.get('total_words', 0),
                'sessions': today_stats.get('sessions', 0),
                'accuracy': today_stats.get('accuracy', 0.0),
                'goal_achievement': goal_data.get('daily_word_achievement', 0.0) if goal_success else 0.0,
                'streak_days': streak_days if streak_success else 0
            }
            
            self.logger.debug(f"오늘의 요약 조회: {summary['words_learned']}개 학습")
            return (True, "오늘의 학습 요약", summary)
            
        except Exception as e:
            self.logger.error(f"오늘의 요약 조회 실패: {e}", exc_info=True)
            return (False, "통계 조회 중 오류가 발생했습니다.", None)
    
    def get_weekly_summary(self):
        """
        주간 학습 요약
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 주간 요약)
        """
        try:
            # 최근 7일 날짜 범위
            end_date = get_current_datetime()
            start_date = (datetime.fromisoformat(end_date) - timedelta(days=6)).isoformat()
            
            # 주간 통계
            weekly_stats = self.statistics_model.get_weekly_statistics(start_date, end_date)
            
            # 주간 합계 계산
            total_words = sum(day.get('total_words', 0) for day in weekly_stats)
            total_sessions = sum(day.get('sessions', 0) for day in weekly_stats)
            
            # 평균 정답률 계산
            accuracies = [day.get('accuracy', 0) for day in weekly_stats if day.get('total_words', 0) > 0]
            avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
            
            # 활동 일수
            active_days = sum(1 for day in weekly_stats if day.get('total_words', 0) > 0)
            
            summary = {
                'total_words': total_words,
                'total_sessions': total_sessions,
                'avg_accuracy': round(avg_accuracy, 1),
                'active_days': active_days,
                'daily_average': round(total_words / 7, 1)
            }
            
            self.logger.debug(f"주간 요약 조회: {total_words}개 학습, {active_days}일 활동")
            return (True, "주간 학습 요약", summary)
            
        except Exception as e:
            self.logger.error(f"주간 요약 조회 실패: {e}", exc_info=True)
            return (False, "통계 조회 중 오류가 발생했습니다.", None)
    
    # === 학습 진척도 ===
    
    def get_learning_trend(self, days=7):
        """
        학습 추세 (차트용 데이터)
        
        Args:
            days (int): 조회 일수
        
        Returns:
            Tuple[bool, str, List[Dict]]: (성공여부, 메시지, 일별 데이터)
            [
                {'date': '2025-10-20', 'words': 50, 'accuracy': 80.0},
                {'date': '2025-10-21', 'words': 45, 'accuracy': 85.0},
                ...
            ]
        """
        try:
            # 날짜 범위
            end_date = get_current_datetime()
            start_date = (datetime.fromisoformat(end_date) - timedelta(days=days-1)).isoformat()
            
            # 통계 조회
            stats = self.statistics_model.get_weekly_statistics(start_date, end_date)
            
            # 데이터 포맷팅
            trend_data = []
            for stat in stats:
                trend_data.append({
                    'date': stat.get('date', ''),
                    'words': stat.get('total_words', 0),
                    'accuracy': stat.get('accuracy', 0.0)
                })
            
            self.logger.debug(f"학습 추세 조회: {days}일간")
            return (True, f"최근 {days}일 학습 추세", trend_data)
            
        except Exception as e:
            self.logger.error(f"학습 추세 조회 실패: {e}", exc_info=True)
            return (False, "통계 조회 중 오류가 발생했습니다.", [])
    
    def get_mastery_distribution(self):
        """
        숙지도 분포
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 분포 데이터)
            {0: 10, 1: 20, 2: 30, 3: 25, 4: 10, 5: 5}
        """
        try:
            distribution = self.statistics_model.get_mastery_distribution()
            
            self.logger.debug(f"숙지도 분포 조회")
            return (True, "숙지도 분포", distribution)
            
        except Exception as e:
            self.logger.error(f"숙지도 분포 조회 실패: {e}", exc_info=True)
            return (False, "통계 조회 중 오류가 발생했습니다.", {})
    
    # === 목표 달성 ===
    
    def calculate_goal_achievement(self):
        """
        학습 목표 달성률 계산
        
        Returns:
            Tuple[bool, str, Dict]: (성공여부, 메시지, 달성률 데이터)
            {
                'daily_word_goal': 50,
                'daily_word_actual': 45,
                'daily_word_achievement': 90.0,
                'daily_time_goal': 30,
                'daily_time_actual': 25,
                'daily_time_achievement': 83.3
            }
        """
        try:
            # 1. 목표 설정 조회
            word_goal = self.settings_model.get_setting('daily_word_goal')
            time_goal = self.settings_model.get_setting('daily_time_goal')  # 분
            
            # 2. 오늘의 실제 달성
            today_stats = self.statistics_model.get_today_statistics()
            actual_words = today_stats.get('total_words', 0)
            
            # 시간은 세션 기반으로 계산 (향후 개선 가능)
            # 현재는 간단히 세션당 평균 시간으로 추정
            sessions = today_stats.get('sessions', 0)
            estimated_time = sessions * 10  # 세션당 10분 가정
            
            # 3. 달성률 계산
            word_achievement = (actual_words / word_goal * 100) if word_goal > 0 else 0.0
            time_achievement = (estimated_time / time_goal * 100) if time_goal > 0 else 0.0
            
            result = {
                'daily_word_goal': word_goal,
                'daily_word_actual': actual_words,
                'daily_word_achievement': round(word_achievement, 1),
                'daily_time_goal': time_goal,
                'daily_time_actual': estimated_time,
                'daily_time_achievement': round(time_achievement, 1)
            }
            
            self.logger.debug(
                f"목표 달성률: 단어 {word_achievement:.1f}%, "
                f"시간 {time_achievement:.1f}%"
            )
            return (True, "목표 달성률 계산 완료", result)
            
        except Exception as e:
            self.logger.error(f"목표 달성률 계산 실패: {e}", exc_info=True)
            return (False, "목표 달성률 계산 중 오류가 발생했습니다.", None)
    
    # === 오답 분석 ===
    
    def get_top_wrong_words(self, limit=20):
        """
        오답률 높은 단어 Top N
        
        Args:
            limit (int): 조회할 개수
        
        Returns:
            Tuple[bool, str, List[Dict]]: (성공여부, 메시지, 단어 목록)
        """
        try:
            words = self.statistics_model.get_top_wrong_words(limit)
            
            self.logger.debug(f"오답 단어 Top {limit} 조회: {len(words)}개")
            return (True, f"오답률 높은 단어 {len(words)}개", words)
            
        except Exception as e:
            self.logger.error(f"오답 단어 조회 실패: {e}", exc_info=True)
            return (False, "통계 조회 중 오류가 발생했습니다.", [])
    
    def get_improvement_suggestions(self):
        """
        학습 개선 제안
        
        Returns:
            Tuple[bool, str, List[str]]: (성공여부, 메시지, 제안 목록)
        """
        try:
            suggestions = []
            
            # 1. 연속 학습 일수 확인
            streak_success, _, streak_days = self.calculate_streak_days()
            if streak_success and streak_days > 0:
                if streak_days >= 7:
                    suggestions.append(f"🔥 {streak_days}일 연속 학습 중! 대단해요!")
                elif streak_days >= 3:
                    suggestions.append(f"👍 {streak_days}일 연속 학습 중입니다. 계속 유지하세요!")
                else:
                    suggestions.append(f"연속 {streak_days}일째 학습 중입니다.")
            
            # 2. 오늘의 목표 달성률
            goal_success, _, goal_data = self.calculate_goal_achievement()
            if goal_success:
                word_achievement = goal_data.get('daily_word_achievement', 0)
                if word_achievement >= 100:
                    suggestions.append("✨ 오늘의 학습 목표를 달성했습니다!")
                elif word_achievement >= 50:
                    remaining = goal_data['daily_word_goal'] - goal_data['daily_word_actual']
                    suggestions.append(f"목표까지 {remaining}개 단어 남았습니다. 조금만 더!")
                else:
                    suggestions.append("오늘의 학습 목표를 향해 시작해보세요!")
            
            # 3. 오답률 높은 단어
            wrong_success, _, wrong_words = self.get_top_wrong_words(10)
            if wrong_success and wrong_words:
                suggestions.append(f"📝 오답률이 높은 단어 {len(wrong_words)}개를 집중 학습하세요.")
            
            # 4. 숙지도 분포 확인
            mastery_success, _, distribution = self.get_mastery_distribution()
            if mastery_success:
                low_mastery = distribution.get(0, 0) + distribution.get(1, 0)
                if low_mastery > 0:
                    suggestions.append(f"숙지도가 낮은 단어 {low_mastery}개를 복습하세요.")
            
            if not suggestions:
                suggestions.append("학습을 시작해보세요!")
            
            return (True, "학습 개선 제안", suggestions)
            
        except Exception as e:
            self.logger.error(f"개선 제안 생성 실패: {e}", exc_info=True)
            return (False, "제안 생성 중 오류가 발생했습니다.", [])
    
    # === 연속 학습 일수 ===
    
    def calculate_streak_days(self):
        """
        연속 학습 일수 계산
        
        Returns:
            Tuple[bool, str, int]: (성공여부, 메시지, 연속 일수)
        """
        try:
            # 오늘부터 거꾸로 계산
            streak = 0
            current_date = datetime.now()
            
            # 최대 30일까지만 확인
            for i in range(30):
                check_date = (current_date - timedelta(days=i)).isoformat()
                day_stats = self.statistics_model.get_daily_statistics(check_date)
                
                if day_stats and day_stats.get('total_words', 0) > 0:
                    streak += 1
                else:
                    # 학습하지 않은 날 발견 시 중단
                    break
            
            self.logger.debug(f"연속 학습 일수: {streak}일")
            
            if streak > 0:
                return (True, f"{streak}일 연속 학습 중", streak)
            else:
                return (True, "연속 학습 기록 없음", 0)
            
        except Exception as e:
            self.logger.error(f"연속 학습 일수 계산 실패: {e}", exc_info=True)
            return (False, "계산 중 오류가 발생했습니다.", 0)